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
APP_PASSWORD = os.getenv("APP_PASSWORD")  # 16-char Gmail app password (no spaces)

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

# In-memory storage for emails (user_id: email) - resets on restart
user_emails = {}

intents = discord.Intents.default()
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

async def remove_role_after_delay(member: discord.Member, role: discord.Role, seconds: int):
    await asyncio.sleep(seconds)
    await member.remove_roles(role)
    print(f"Removed role {role.name} from {member} after {seconds} seconds")

@tree.command(name="role", description="Give temp role (admin only)")
@app_commands.describe(member="User", duration="e.g. 1d 2w 3m")
@app_commands.checks.has_permissions(administrator=True)
async def assign_role(interaction: discord.Interaction, member: discord.Member, duration: str):
    if any(r.id == ROLE_ID for r in member.roles):
        embed = Embed(title="Error", description=f"{member.mention} already has the role!", color=Colour.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    role = interaction.guild.get_role(ROLE_ID)
    if not role:
        embed = Embed(title="Error", description="Role not found!", color=Colour.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await member.add_roles(role)
    seconds = parse_duration(duration)
    if seconds > 0:
        asyncio.create_task(remove_role_after_delay(member, role, seconds))
    embed = Embed(
        title="Role Assigned",
        description=f"Gave {role.name} to {member.mention} for {duration} (auto-remove after time)",
        color=Colour.green()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

class EmailModal(ui.Modal, title="Email Hook"):
    email = ui.TextInput(label="What's your email?", style=discord.TextStyle.long, required=True, placeholder="Enter your email for receipts...")

    async def on_submit(self, interaction: discord.Interaction):
        user_emails[interaction.user.id] = self.email.value
        embed = Embed(
            title="Email Hooked",
            description=f"Email {self.email.value} saved! Use /generate to create receipts.",
            color=Colour.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="setup", description="Hook your email to your user (role required)")
async def setup(interaction: discord.Interaction):
    if not any(r.id == ROLE_ID for r in interaction.user.roles):
        embed = Embed(title="Access Denied", description="You need the special role!", color=Colour.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await interaction.response.send_modal(EmailModal())

class BrandSelect(ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=brand) for brand in BRANDS]
        super().__init__(placeholder="Select a brand...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        brand = self.values[0]
        await interaction.response.defer(ephemeral=True)
        modal = GenerateModal(brand=brand, user_id=interaction.user.id)
        await interaction.followup.send_modal(modal)
        await interaction.message.delete()  # Delete dropdown last

class BrandView(ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(BrandSelect())

@tree.command(name="generate", description="Generate a receipt (role required)")
async def generate(interaction: discord.Interaction):
    if not any(r.id == ROLE_ID for r in interaction.user.roles):
        embed = Embed(title="Access Denied", description="You need the special role!", color=Colour.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    embed = Embed(title="Select Brand", description="Choose from the dropdown below (private to you).", color=Colour.blue())
    await interaction.response.send_message(embed=embed, view=BrandView(), ephemeral=True)

class GenerateModal(ui.Modal, title="Receipt Details"):
    def __init__(self, brand, user_id):
        self.brand = brand
        self.user_id = user_id
        super().__init__()
        self.item = ui.TextInput(label="Item name", style=discord.TextStyle.long, required=True, placeholder="e.g. iPhone 16 Pro Max")
        self.price = ui.TextInput(label="Price in USD", style=discord.TextStyle.short, required=True, placeholder="e.g. 1199.00")
        self.quantity = ui.TextInput(label="Quantity (default 1)", style=discord.TextStyle.short, required=False, placeholder="1")
        self.shipping = ui.TextInput(label="Shipping address (optional, N/A)", style=discord.TextStyle.long, required=False, placeholder="N/A")

    async def on_submit(self, interaction: discord.Interaction):
        email = user_emails.get(self.user_id)
        if not email:
            embed = Embed(title="No Email Hooked", description="Run /setup first to hook your email!", color=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        brand = self.brand
        try:
            price = float(self.price.value.strip())
            quantity = int(self.quantity.value.strip() or 1)
            shipping = self.shipping.value.strip() or "N/A"
            item = self.item.value.strip()

            dm = await interaction.user.create_dm()
            embed = Embed(title="Email Being Sent", description=f"Sending branded {brand} receipt to {email}...", color=Colour.orange())
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

            info = brand_from.get(brand, {"display": brand, "from_email": f"no-reply@{brand.lower()}.com"})

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
                print(f"SMTP full error: {str(e)}")

        except ValueError:
            embed = Embed(title="Invalid Input", description="Price/qty must be numbers. Retry.", color=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = Embed(title="Error", description=f"Something broke: {str(e)}", color=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

client.run(BOT_TOKEN)