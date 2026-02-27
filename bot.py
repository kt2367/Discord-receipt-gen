import discord
from discord import app_commands, ui
import datetime
import random
import asyncio
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sqlalchemy import create_engine, Column, Integer, String, BigInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# === CONFIG FROM ENV VARS (Railway) ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")  # AppleReceipts@outlook.com
APP_PASSWORD = os.getenv("APP_PASSWORD")  # RoseThea81
DATABASE_URL = os.getenv("DATABASE_URL")
ROLE_ID = 1472751333286350981

if not all([BOT_TOKEN, SENDER_EMAIL, APP_PASSWORD, DATABASE_URL]):
    print("Missing required env vars!")
    exit(1)

# DB Setup
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class UserEmail(Base):
    __tablename__ = 'user_emails'
    user_id = Column(BigInteger, primary_key=True)
    email = Column(String)

class RoleTimer(Base):
    __tablename__ = 'role_timers'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    guild_id = Column(BigInteger)
    role_id = Column(BigInteger)
    remove_at = Column(DateTime)

Base.metadata.create_all(engine)

# Brands (simple list; HTML customized per brand in send function)
BRANDS = [
    'Cartier', 'Denim Tears', 'Ksubi', 'Balenciaga', 'Sp5der',
    'Nike', 'Adidas', 'Lululemon', 'Lanvin', 'Creed',
    'Baccarat', 'Sephora', 'Apple'
]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot online as {client.user} 🚀")
    await load_timers()

# Role timer functions (same as before)
async def load_timers():
    session = Session()
    try:
        now = datetime.datetime.utcnow()
        timers = session.query(RoleTimer).filter(RoleTimer.remove_at > now).all()
        for timer in timers:
            delay = (timer.remove_at - now).total_seconds()
            asyncio.create_task(schedule_role_removal(timer.user_id, timer.guild_id, timer.role_id, delay))
        expired = session.query(RoleTimer).filter(RoleTimer.remove_at <= now).all()
        for exp in expired:
            guild = client.get_guild(exp.guild_id)
            if guild:
                member = guild.get_member(exp.user_id)
                role = guild.get_role(exp.role_id)
                if member and role:
                    await member.remove_roles(role)
        session.query(RoleTimer).filter(RoleTimer.remove_at <= now).delete()
        session.commit()
    except Exception as e:
        print(f"Timer load error: {e}")
    finally:
        session.close()

async def schedule_role_removal(user_id, guild_id, role_id, delay):
    await asyncio.sleep(delay)
    guild = client.get_guild(guild_id)
    if guild:
        member = guild.get_member(user_id)
        role = guild.get_role(role_id)
        if member and role:
            await member.remove_roles(role)
    session = Session()
    try:
        timer = session.query(RoleTimer).filter_by(user_id=user_id, guild_id=guild_id, role_id=role_id).first()
        if timer:
            session.delete(timer)
            session.commit()
    finally:
        session.close()

def parse_duration(dur: str) -> int:
    if not dur or not dur[0].isdigit():
        return 0
    num = int(''.join(filter(str.isdigit, dur)))
    unit = dur.lower()[-2:] if dur.lower().endswith(('mo', 'wk')) else dur.lower()[-1]
    if unit in ['s', 'sec']: return num
    if unit in ['m', 'min']: return num * 60
    if unit in ['h', 'hr']: return num * 3600
    if unit == 'd': return num * 86400
    if unit in ['w', 'wk']: return num * 604800
    if unit in ['mo', 'mth']: return num * 2592000
    return 0

@tree.command(name="role", description="Give temp role (admin only)")
@app_commands.describe(member="User", duration="e.g. 1d 2w 3m")
@app_commands.checks.has_permissions(administrator=True)
async def assign_role(interaction: discord.Interaction, member: discord.Member, duration: str):
    role = interaction.guild.get_role(ROLE_ID)
    if not role:
        await interaction.response.send_message("Role not found!", ephemeral=True)
        return
    await member.add_roles(role)
    seconds = parse_duration(duration)
    if seconds <= 0:
        await interaction.response.send_message("Invalid duration!", ephemeral=True)
        return
    remove_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)
    session = Session()
    try:
        new_timer = RoleTimer(user_id=member.id, guild_id=interaction.guild_id, role_id=ROLE_ID, remove_at=remove_at)
        session.add(new_timer)
        session.commit()
        asyncio.create_task(schedule_role_removal(member.id, interaction.guild_id, ROLE_ID, seconds))
        await interaction.response.send_message(f"Gave {role.name} to {member} for {duration}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
    finally:
        session.close()

class EmailModal(ui.Modal, title="Enter Your Email"):
    email = ui.TextInput(label="Email for receipts", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        session = Session()
        try:
            existing = session.query(UserEmail).filter_by(user_id=interaction.user.id).first()
            if existing:
                existing.email = self.email.value
            else:
                session.add(UserEmail(user_id=interaction.user.id, email=self.email.value))
            session.commit()
            await interaction.response.send_message("Email saved! Starting setup in DMs...", ephemeral=True)
            await start_setup(interaction.user, self.email.value)
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
        finally:
            session.close()

@tree.command(name="setup", description="Start receipt generator (role required)")
async def setup(interaction: discord.Interaction):
    if not any(r.id == ROLE_ID for r in interaction.user.roles):
        await interaction.response.send_message("You need the special role!", ephemeral=True)
        return
    session = Session()
    try:
        user_email = session.query(UserEmail).filter_by(user_id=interaction.user.id).first()
        if user_email:
            await interaction.response.send_message("Using saved email. DMing setup...", ephemeral=True)
            await start_setup(interaction.user, user_email.email)
        else:
            await interaction.response.send_modal(EmailModal())
    except Exception as e:
        await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
    finally:
        session.close()

async def start_setup(user: discord.User, email: str):
    dm = await user.create_dm()
    try:
        await dm.send(f"Brands: {', '.join(BRANDS)}")
        await dm.send("Which brand?")
        msg = await client.wait_for('message', check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel), timeout=300)
        brand = msg.content.strip().title()
        if brand not in BRANDS:
            await dm.send("Invalid brand. Try again with /setup.")
            return

        await dm.send("Item name?")
        msg = await client.wait_for('message', check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel), timeout=300)
        item = msg.content.strip()

        await dm.send("Price in USD?")
        msg = await client.wait_for('message', check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel), timeout=300)
        price = float(msg.content.strip())

        await dm.send("Quantity? (enter for 1)")
        msg = await client.wait_for('message', check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel), timeout=300)
        quantity = int(msg.content.strip() or 1)

        await dm.send("Shipping address? (optional, enter for N/A)")
        msg = await client.wait_for('message', check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel), timeout=300)
        shipping = msg.content.strip() or "N/A"

        await dm.send("Generating & sending branded receipt... ⏳")

        # Receipt details
        order_id = f"{brand.upper()}-{random.randint(10000000,99999999)}"
        today = datetime.date.today().strftime("%B %d, %Y")
        subtotal = price * quantity
        tax = subtotal * 0.08
        total = subtotal + tax

        # Brand-specific HTML (customize as needed; fallback generic)
        if brand == 'Apple':
            html_body = f"""
            <html><body style="font-family: -apple-system, sans-serif; color:#000; background:#fff; padding:20px;">
            <h2>Apple Order Confirmation</h2>
            <p>Order ID: {order_id}<br>Date: {today}<br>Billed to: {email}</p>
            <p>Item: {item}<br>Qty: {quantity}<br>Price: ${price:,.2f}</p>
            <p>Subtotal: ${subtotal:,.2f}<br>Tax: ${tax:,.2f}<br>Total: ${total:,.2f}</p>
            <p>Questions? support.apple.com</p>
            </body></html>
            """
        elif brand == 'Nike':
            html_body = f"""
            <html><body style="font-family: Helvetica, sans-serif; color:#000; background:#fff; padding:20px;">
            <h2>Nike Order Received</h2>
            <p>Order #{order_id} on {today}</p>
            <p>Item: {item}<br>Qty: {quantity}<br>Price: ${price:,.2f}</p>
            <p>Total: ${total:,.2f}</p>
            <p>Thank you! Track at nike.com</p>
            </body></html>
            """
        else:
            # Generic fallback for other brands
            html_body = f"""
            <html><body style="font-family: Arial, sans-serif; padding:20px;">
            <h2>{brand} Order Confirmation</h2>
            <p>Order ID: {order_id}<br>Date: {today}<br>Billed to: {email}</p>
            <p>Item: {item} x{quantity} - ${price:,.2f}</p>
            <p>Subtotal: ${subtotal:,.2f}<br>Tax: ${tax:,.2f}<br>Total: ${total:,.2f}</p>
            <p>Thank you for shopping with {brand}!</p>
            </body></html>
            """

        # Build email
        msg = MIMEMultipart("alternative")
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        msg['Subject'] = f"Your {brand} Order Confirmation"

        plain_text = f"Order ID: {order_id}\nItem: {item}\nTotal: ${total:,.2f}\nThank you!"
        msg.attach(MIMEText(plain_text, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        # Send via Outlook SMTP
        try:
            with smtplib.SMTP('smtp-mail.outlook.com', 587) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(SENDER_EMAIL, APP_PASSWORD)
                server.send_message(msg)
            await dm.send(f"Receipt sent to {email}! Check inbox/spam. 🔥 (Edu demo only)")
        except Exception as e:
            await dm.send(f"Email failed: {str(e)}. Check env vars or Outlook settings.")

    except asyncio.TimeoutError:
        await dm.send("Timed out – run /setup again.")
    except ValueError:
        await dm.send("Invalid input (price/qty) – retry.")
    except Exception as e:
        await dm.send(f"Error: {str(e)}")

client.run(BOT_TOKEN)