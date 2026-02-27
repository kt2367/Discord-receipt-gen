import discord
from discord import app_commands, ui
import datetime
import random
import asyncio
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# === CONFIG FROM ENV VARS ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")  # AppleReceipts@outlook.com
APP_PASSWORD = os.getenv("APP_PASSWORD")  # RoseThea81

if not all([BOT_TOKEN, SENDER_EMAIL, APP_PASSWORD]):
    print("Missing BOT_TOKEN, SENDER_EMAIL, or APP_PASSWORD!")
    exit(1)

print("BOT STARTING - ENV VARS OK")
print(f"SENDER_EMAIL: {SENDER_EMAIL}")

ROLE_ID = 1472751333286350981

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
    print(f"Bot online as {client.user} 🚀 - Ready for commands!")

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
    await interaction.response.send_message(f"Gave {role.name} to {member} for {duration} (no auto-remove yet)", ephemeral=True)

class EmailModal(ui.Modal, title="Enter Your Email"):
    email = ui.TextInput(label="Email for receipts", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Email saved for this session! Starting setup in DMs...", ephemeral=True)
        await start_setup(interaction.user, self.email.value)

@tree.command(name="setup", description="Start receipt generator (role required)")
async def setup(interaction: discord.Interaction):
    if not any(r.id == ROLE_ID for r in interaction.user.roles):
        await interaction.response.send_message("You need the special role!", ephemeral=True)
        return
    await interaction.response.send_modal(EmailModal())

async def start_setup(user: discord.User, email: str):
    dm = await user.create_dm()
    try:
        await dm.send(f"Brands: {', '.join(BRANDS)}")
        await dm.send("Which brand?")
        msg = await client.wait_for('message', check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel), timeout=300)
        brand = msg.content.strip().title()
        if brand not in BRANDS:
            await dm.send("Invalid brand. Run /setup again.")
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

        await dm.send("Generating & sending receipt... ⏳")

        order_id = f"{brand.upper()}-{random.randint(10000000,99999999)}"
        today = datetime.date.today().strftime("%B %d, %Y")
        subtotal = price * quantity
        tax = subtotal * 0.08
        total = subtotal + tax

        # Simple HTML receipt (customize per brand if you want)
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding:20px; background:#fff; color:#000;">
        <h2>{brand} Order Confirmation</h2>
        <p>Order ID: {order_id}<br>Date: {today}<br>Billed to: {email}</p>
        <p>Item: {item} x{quantity} - ${price:,.2f}</p>
        <p>Subtotal: ${subtotal:,.2f}<br>Tax: ${tax:,.2f}<br>Total: ${total:,.2f}</p>
        <p>Shipping: {shipping}</p>
        <p>Thank you for shopping with {brand}!</p>
        </body>
        </html>
        """

        msg = MIMEMultipart("alternative")
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        msg['Subject'] = f"Your {brand} Order Confirmation"

        plain_text = f"Order ID: {order_id}\nItem: {item}\nTotal: ${total:,.2f}\nThank you!"
        msg.attach(MIMEText(plain_text, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        try:
            with smtplib.SMTP('smtp-mail.outlook.com', 587) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(SENDER_EMAIL, APP_PASSWORD)
                server.send_message(msg)
            await dm.send(f"Receipt sent to {email}! Check inbox/spam. 🔥")
        except Exception as e:
            await dm.send(f"Email send failed: {str(e)}. Check vars or Outlook spam settings.")

    except asyncio.TimeoutError:
        await dm.send("Timed out - run /setup again.")
    except ValueError:
        await dm.send("Invalid price/qty - retry.")
    except Exception as e:
        await dm.send(f"Error: {str(e)}")

client.run(BOT_TOKEN)