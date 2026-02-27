import discord
from discord import app_commands, ui, Embed, Colour
import datetime
import random
import asyncio
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# === CONFIG FROM ENV VARS ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")  # yourgmail@gmail.com
APP_PASSWORD = os.getenv("APP_PASSWORD")  # 16-char Gmail app password

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

# Brand-specific From settings for realistic sender line
brand_from = {
    'Cartier': {"display": "Cartier", "from_email": "concierge@cartier.com"},
    'Nike': {"display": "Nike", "from_email": "orders@nike.com"},
    'Adidas': {"display": "adidas", "from_email": "service@adidas.com"},
    'Sephora': {"display": "Sephora", "from_email": "customerservice@sephora.com"},
    'Lululemon': {"display": "lululemon athletica", "from_email": "support@lululemon.com"},
    'Apple': {"display": "Apple Store", "from_email": "no-reply@apple.com"},
    'Balenciaga': {"display": "Balenciaga", "from_email": "contact@balenciaga.com"},
    'Creed': {"display": "Creed Boutique", "from_email": "info@creedboutique.com"},
    'Lanvin': {"display": "Lanvin", "from_email": "contact@lanvin.com"},
    'Baccarat': {"display": "Baccarat", "from_email": "service@baccarat.com"},
    'Denim Tears': {"display": "Denim Tears", "from_email": "support@denimtears.com"},
    'Ksubi': {"display": "Ksubi", "from_email": "hello@ksubi.com"},
    'Sp5der': {"display": "Sp5der", "from_email": "support@sp5der.com"},
}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot online as {client.user} 🚀 - Ready for commands!")

@tree.command(name="role", description="Give temp role (admin only)")
@app_commands.describe(member="User", duration="e.g. 1d 2w 3m")
@app_commands.checks.has_permissions(administrator=True)
async def assign_role(interaction: discord.Interaction, member: discord.Member, duration: str):
    role = interaction.guild.get_role(ROLE_ID)
    if not role:
        embed = Embed(title="Error", description="Role not found!", color=Colour.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    await member.add_roles(role)
    embed = Embed(
        title="Role Assigned",
        description=f"Gave {role.name} to {member.mention} for {duration} (no auto-remove yet)",
        color=Colour.green()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

class EmailModal(ui.Modal, title="Enter Your Email"):
    email = ui.TextInput(label="Email for receipts", style=discord.TextStyle.short, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        embed = Embed(
            title="Email Received",
            description=f"Using {self.email.value} for this receipt.\nStarting setup in DMs...",
            color=Colour.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await start_setup(interaction.user, self.email.value)

@tree.command(name="setup", description="Start receipt generator (role required)")
async def setup(interaction: discord.Interaction):
    if not any(r.id == ROLE_ID for r in interaction.user.roles):
        embed = Embed(title="Access Denied", description="You need the special role!", color=Colour.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = Embed(title="Starting Setup", description="Check your DMs!", color=Colour.blue())
    await interaction.response.send_message(embed=embed, ephemeral=True)
    await interaction.user.send(embed=Embed(title="Setup Started", description="Answer the questions below.", color=Colour.blue()))
    await start_setup(interaction.user, None)

async def start_setup(user: discord.User, email: str = None):
    dm = await user.create_dm()

    try:
        if not email:
            embed = Embed(title="Email Needed", description="What's your email to send the receipt to?", color=Colour.orange())
            await dm.send(embed=embed)
            msg = await client.wait_for('message', check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel), timeout=300)
            email = msg.content.strip()
            embed = Embed(title="Email Saved", description=f"Using {email} for this receipt.", color=Colour.green())
            await dm.send(embed=embed)

        embed = Embed(title="Pick Brand", description=f"Available: {', '.join(BRANDS)}\nReply with one.", color=Colour.blue())
        await dm.send(embed=embed)
        msg = await client.wait_for('message', check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel), timeout=300)
        brand = msg.content.strip().title()
        if brand not in BRANDS:
            embed = Embed(title="Invalid Brand", description="Try again with /setup.", color=Colour.red())
            await dm.send(embed=embed)
            return

        info = brand_from.get(brand, {"display": brand, "from_email": f"no-reply@{brand.lower()}.com"})

        embed = Embed(title=f"{info['display']} Item", description="What item?", color=Colour.blue())
        await dm.send(embed=embed)
        msg = await client.wait_for('message', check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel), timeout=300)
        item = msg.content.strip()

        embed = Embed(title=f"{info['display']} Price", description="Price in USD?", color=Colour.blue())
        await dm.send(embed=embed)
        msg = await client.wait_for('message', check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel), timeout=300)
        price = float(msg.content.strip())

        embed = Embed(title=f"{info['display']} Quantity", description="Quantity? (enter for 1)", color=Colour.blue())
        await dm.send(embed=embed)
        msg = await client.wait_for('message', check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel), timeout=300)
        quantity = int(msg.content.strip() or 1)

        embed = Embed(title=f"{info['display']} Shipping", description="Shipping address? (optional, enter for N/A)", color=Colour.blue())
        await dm.send(embed=embed)
        msg = await client.wait_for('message', check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel), timeout=300)
        shipping = msg.content.strip() or "N/A"

        embed = Embed(title="Generating...", description=f"Sending branded receipt to {email}...", color=Colour.orange())
        await dm.send(embed=embed)

        order_id = f"{brand.upper()}-{random.randint(10000000,99999999)}"
        today = datetime.date.today().strftime("%B %d, %Y")
        subtotal = price * quantity
        tax = subtotal * 0.08
        total = subtotal + tax

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding:20px; background:#fff; color:#000;">
        <h2 style="color:#000;">{brand} Order Confirmation</h2>
        <p>Order ID: {order_id}<br>Date: {today}<br>Billed to: {email}</p>
        <p>Item: {item} x{quantity} - ${price:,.2f}</p>
        <p>Subtotal: ${subtotal:,.2f}<br>Tax: ${tax:,.2f}<br>Total: ${total:,.2f}</p>
        <p>Shipping: {shipping}</p>
        <p>Thank you for shopping with {brand}!</p>
        </body>
        </html>
        """

        msg = MIMEMultipart("alternative")
        msg['From'] = f"{info['display']} <{info['from_email']}>"
        msg['Reply-To'] = f"support@{brand.lower()}.com"
        msg['To'] = email
        msg['Subject'] = f"Your {brand} Order Confirmation"
        msg['Message-ID'] = f"<{random.randint(1000000000000000000,9999999999999999999)}@{brand.lower()}.com>"

        plain_text = f"Order ID: {order_id}\nItem: {item}\nTotal: ${total:,.2f}\nThank you!"
        msg.attach(MIMEText(plain_text, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
            server.quit()
            embed = Embed(title="Success!", description=f"Receipt sent to {email}! Check inbox/spam.", color=Colour.green())
            await dm.send(embed=embed)
        except Exception as e:
            embed = Embed(title="Email Failed", description=f"Error: {str(e)}\nCheck Gmail app password, spam, or creds.", color=Colour.red())
            await dm.send(embed=embed)
            print(f"SMTP full error: {str(e)}")  # Shows in Railway logs

    except asyncio.TimeoutError:
        embed = Embed(title="Timed Out", description="Run /setup again.", color=Colour.red())
        await dm.send(embed=embed)
    except ValueError:
        embed = Embed(title="Invalid Input", description="Price/qty must be numbers. Retry.", color=Colour.red())
        await dm.send(embed=embed)
    except Exception as e:
        embed = Embed(title="Error", description=f"Something broke: {str(e)}", color=Colour.red())
        await dm.send(embed=embed)

client.run(BOT_TOKEN)