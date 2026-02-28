import discord
from discord import app_commands, ui, Embed, Colour, ButtonStyle
from discord.ui import TextInput  # Explicit import for discord.py 2.0+
import datetime
import random
import asyncio
import os
import re
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

if not all([BOT_TOKEN, SENDER_EMAIL, SENDGRID_API_KEY]):
    logger.error("Missing env vars!")
    exit(1)

ROLE_ID = 1472751333286350981

BRANDS = [
    'Cartier', 'Denim Tears', 'Ksubi', 'Balenciaga', 'Sp5der',
    'Nike', 'Adidas', 'Lululemon', 'Lanvin', 'Creed',
    'Baccarat', 'Sephora', 'Apple'
]

brand_display = {
    'Cartier': "Cartier",
    'Denim Tears': "Denim Tears",
    'Ksubi': "Ksubi",
    'Balenciaga': "Balenciaga",
    'Sp5der': "Sp5der",
    'Nike': "Nike",
    'Adidas': "adidas",
    'Lululemon': "lululemon athletica",
    'Lanvin': "Lanvin",
    'Creed': "Creed",
    'Baccarat': "Baccarat",
    'Sephora': "Sephora",
    'Apple': "Apple Store",
}

brand_info = {
    'Cartier': {"logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Cartier_logo.svg/512px-Cartier_logo.svg.png"},
    'Denim Tears': {"logo": "https://i.imgur.com/denimtearslogo.png"},
    'Ksubi': {"logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Ksubi_logo.svg/512px-Ksubi_logo.svg.png"},
    'Balenciaga': {"logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Balenciaga_logo.svg/512px-Balenciaga_logo.svg.png"},
    'Sp5der': {"logo": "https://i.imgur.com/sp5derlogo.png"},
    'Nike': {"logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Logo_NIKE.svg/512px-Logo_NIKE.svg.png"},
    'Adidas': {"logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Adidas_Logo.svg/512px-Adidas_Logo.svg.png"},
    'Lululemon': {"logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Lululemon_logo.svg/512px-Lululemon_logo.svg.png"},
    'Lanvin': {"logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Lanvin_logo.svg/512px-Lanvin_logo.svg.png"},
    'Creed': {"logo": "https://i.imgur.com/creedlogo.png"},
    'Baccarat': {"logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Baccarat_logo.svg/512px-Baccarat_logo.svg.png"},
    'Sephora': {"logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Sephora_Logo.svg/512px-Sephora_Logo.svg.png"},
    'Apple': {"logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/512px-Apple_logo_black.svg.png"},
}

FAKE_NAMES = [
    "George Love", "Alex Rivera", "Jordan Lee", "Taylor Brooks", "Morgan Ellis",
    "Casey Quinn", "Riley Harper", "Jamie Knox", "Parker Reese", "Cameron Blake"
]

FAKE_ADDRESSES = [
    "030 Tyler Ridge, East Roberts Shire, United States",
    "123 Main St, New York, NY 10001",
    "456 Oak Ave, Los Angeles, CA 90001",
    "789 Pine Rd, Chicago, IL 60601",
    "321 Elm St, Miami, FL 33101",
    "654 Maple Dr, Houston, TX 77001",
    "987 Cedar Ln, Seattle, WA 98101",
    "147 Birch Blvd, Boston, MA 02101",
    "258 Willow Way, Denver, CO 80201",
    "369 Spruce Ct, Atlanta, GA 30301"
]

FAKE_PAYMENT_METHODS = [
    "Visa ending in 4823",
    "Mastercard ending in 7192",
    "Apple Pay",
    "Cash on Delivery",
    "Visa ending in 5634",
    "Mastercard ending in 2941"
]

STATE_TAX_RATES = {
    "AL": 0.0946, "AK": 0.0182, "AZ": 0.0852, "AR": 0.0946,
    "CA": 0.0899, "CO": 0.0789, "CT": 0.0635, "DE": 0.0000,
    "FL": 0.0698, "GA": 0.0749, "HI": 0.0450, "ID": 0.0603,
    "IL": 0.0896, "IN": 0.0700, "IA": 0.0694, "KS": 0.0869,
    "KY": 0.0600, "LA": 0.1011, "ME": 0.0550, "MD": 0.0600,
    "MA": 0.0625, "MI": 0.0600, "MN": 0.0814, "MS": 0.0706,
    "MO": 0.0844, "MT": 0.0000, "NE": 0.0698, "NV": 0.0824,
    "NH": 0.0000, "NJ": 0.0660, "NM": 0.0767, "NY": 0.0854,
    "NC": 0.0700, "ND": 0.0709, "OH": 0.0729, "OK": 0.0906,
    "OR": 0.0000, "PA": 0.0634, "RI": 0.0700, "SC": 0.0749,
    "SD": 0.0611, "TN": 0.0961, "TX": 0.0820, "UT": 0.0742,
    "VT": 0.0639, "VA": 0.0577, "WA": 0.0951, "WV": 0.0659,
    "WI": 0.0572, "WY": 0.0556, "DC": 0.0600
}

STATE_SHIPPING_MULTIPLIER = {
    "OH": 1.0, "PA": 1.1, "MI": 1.1, "IN": 1.2, "KY": 1.2,
    "NY": 1.3, "IL": 1.4, "GA": 1.5, "FL": 1.7, "TX": 1.9,
    "CA": 2.5, "WA": 2.8, "default": 1.5
}

def get_state_from_address(address):
    addr_upper = address.upper()
    matches = re.findall(r'\b([A-Z]{2})\b', addr_upper)
    for state in reversed(matches):
        if state in STATE_TAX_RATES:
            return state
    return "GA"

user_emails = {}

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    logger.info(f"Bot online as {client.user}")
    logger.info(f"discord.py version: {discord.__version__}")  # Log version for debugging
    while True:
        await asyncio.sleep(30)
        logger.info("Heartbeat - bot alive")

@tree.command(name="setup", description="Hook your email to your user (role required)")
async def setup(interaction: discord.Interaction):
    if not any(r.id == ROLE_ID for r in interaction.user.roles):
        await interaction.response.send_message(embed=Embed(title="Access Denied", description="You need the special role!", color=Colour.red()), ephemeral=True)
        return
    await interaction.response.send_modal(EmailModal())

class EmailModal(ui.Modal, title="Email Setup"):
    email = TextInput(label="What's your email?", style=discord.TextStyle.long, required=True, placeholder="Enter your email for receipts...")

    async def on_submit(self, interaction: discord.Interaction):
        user_emails[interaction.user.id] = self.email.value
        await interaction.response.send_message(embed=Embed(title="Email Hooked", description=f"Email {self.email.value} saved! Use /generate.", color=Colour.green()), ephemeral=True)

@tree.command(name="role", description="Give user the special role for a duration (e.g. 1d, 2w, 3m)")
@app_commands.describe(user="The user", duration="Duration e.g. 1d 2w 3m")
async def role(interaction: discord.Interaction, user: discord.Member, duration: str):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You need manage roles permission.", ephemeral=True)
        return

    duration = duration.lower().strip()
    if duration.endswith('d'):
        delta = datetime.timedelta(days=int(duration[:-1]))
    elif duration.endswith('w'):
        delta = datetime.timedelta(weeks=int(duration[:-1]))
    elif duration.endswith('m'):
        delta = datetime.timedelta(days=int(duration[:-1]) * 30)
    else:
        await interaction.response.send_message("Invalid format. Use 1d, 2w, 3m", ephemeral=True)
        return

    role = interaction.guild.get_role(ROLE_ID)
    if not role:
        await interaction.response.send_message("Role not found.", ephemeral=True)
        return

    await user.add_roles(role)
    await interaction.response.send_message(f"Added role to {user.mention} for {duration}.", ephemeral=True)

    await asyncio.sleep(delta.total_seconds())
    await user.remove_roles(role)
    logger.info(f"Removed role from {user} after {duration}")

class BrandButton(ui.Button):
    def __init__(self, brand, user_id):
        super().__init__(label=brand, style=ButtonStyle.primary, custom_id=f"brand_{user_id}_{brand}")
        self.brand = brand
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your button!", ephemeral=True)
            return

        logger.info(f"User {interaction.user} clicked {self.brand}")

        modal = GenerateModal(self.brand, self.user_id)

        try:
            await interaction.response.send_modal(modal)  # MUST be FIRST response
            logger.info("Modal sent successfully")
        except Exception as e:
            logger.error(f"Modal send failed: {str(e)}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    embed=Embed(title="Error", description="Failed to open form. Try /generate again.", color=Colour.red()),
                    ephemeral=True
                )

class BrandView(ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        for brand in BRANDS:
            self.add_item(BrandButton(brand, user_id))

@tree.command(name="generate", description="Generate a receipt (role required)")
async def generate(interaction: discord.Interaction):
    if not any(r.id == ROLE_ID for r in interaction.user.roles):
        await interaction.response.send_message(embed=Embed(title="Access Denied", description="You need the special role!", color=Colour.red()), ephemeral=True)
        return

    embed = Embed(
        title="Choose Your Brand",
        description=f"{interaction.user.mention}, click a button below.\n(Only you can use these buttons)",
        color=Colour.blue()
    )

    view = BrandView(interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view)  # Public

class GenerateModal(discord.ui.Modal, title="Receipt Details"):
    def __init__(self, brand: str, user_id: int):
        super().__init__()
        self.brand = brand
        self.user_id = user_id

        self.item = TextInput(label="Item name", style=discord.TextStyle.paragraph, required=True, max_length=100)
        self.price = TextInput(label="Price per unit in USD", style=discord.TextStyle.short, required=True, max_length=20)
        self.quantity = TextInput(label="Quantity (default 1)", style=discord.TextStyle.short, required=False, max_length=5)
        self.color = TextInput(label="Color (e.g. Silver, Gold)", style=discord.TextStyle.short, required=True, max_length=20)
        self.size = TextInput(label="Size (e.g. 52)", style=discord.TextStyle.short, required=True, max_length=10)
        self.shipping_date = TextInput(label="Estimated delivery date", style=discord.TextStyle.short, required=True, max_length=30)

        self.add_item(self.item)
        self.add_item(self.price)
        self.add_item(self.quantity)
        self.add_item(self.color)
        self.add_item(self.size)
        self.add_item(self.shipping_date)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        email = user_emails.get(self.user_id)
        if not email:
            await interaction.followup.send(embed=Embed(title="No Email", description="Run /setup first!", color=Colour.red()), ephemeral=True)
            return

        try:
            price = float(self.price.value.strip())
            qty = int(self.quantity.value.strip() or 1)
            color_choice = self.color.value.strip().title()
            size_choice = self.size.value.strip()
            est_date = self.shipping_date.value.strip()

            customer_name = random.choice(FAKE_NAMES)
            address = random.choice(FAKE_ADDRESSES)
            state = get_state_from_address(address)
            tax_rate = STATE_TAX_RATES.get(state, 0.0749)

            subtotal = price * qty

            base_shipping = random.uniform(8, 18)
            mult = STATE_SHIPPING_MULTIPLIER.get(state, 1.5)
            surcharge = random.uniform(0, 8) * (mult - 1)
            variance = random.uniform(-3, 3)
            delivery = round(max(5.00, base_shipping + surcharge + variance), 2)

            sales_tax = round(subtotal * tax_rate, 2)
            total = round(subtotal + delivery + sales_tax, 2)

            order_id = f"{self.brand.upper()}-{random.randint(1000000000000000,9999999999999999)}"
            payment = random.choice(FAKE_PAYMENT_METHODS)
            gift = random.choice(["Gift wrapping added", ""])

            html_body = f"""
            <html>
            <body style="font-family: Georgia, 'Times New Roman', serif; background:#f8f8f8; color:#111; margin:0; padding:0; font-size:11px; line-height:1.4;">
            <div style="max-width:580px; margin:20px auto; background:#fff; border:1px solid #ccc;">
                <div style="background: linear-gradient(to right, #8B0000, #000000); padding:40px 20px; text-align:center;">
                    <h1 style="color:#fff; margin:0; font-size:42px; font-weight:400; letter-spacing:4px; font-family: 'Playfair Display', Georgia, 'Times New Roman', serif; font-style:italic;">{self.brand}</h1>
                </div>

                <div style="padding:25px 30px;">
                    <h2 style="text-align:center; font-size:16px; margin:0 0 15px;">Acknowledgment of your order</h2>
                    <p style="text-align:center; margin:0 0 20px;">Dear {customer_name},</p>
                    <p style="margin:0 0 15px;">Thank you for shopping online with {self.brand}.</p>
                    <p style="margin:0 0 15px;">We are pleased to acknowledge receipt of your order, the main details of which are set out below. Please check this email to ensure the details are accurate.</p>
                    <p style="font-style:italic; font-size:10px; color:#555; margin:0 0 20px;">Please note that this acknowledgment is not a confirmation of your order. Once your order has been approved, you will receive another email confirming acceptance at the time of shipment.</p>

                    <p style="text-align:center; margin:10px 0;"><a href="#" style="color:#000; text-decoration:underline;">To track your order online from your My{self.brand} account, click here: track order</a></p>

                    <div style="background:#000; color:#fff; padding:12px; text-align:center; margin:20px 0;">
                        ORDER N° {order_id}
                    </div>

                    <div style="background:#111; color:#eee; padding:15px; margin:15px 0;">
                        <p style="margin:0 0 5px;"><strong>{self.item.value}</strong></p>
                        <p style="margin:0 0 5px;">Color: {color_choice}</p>
                        <p style="margin:0 0 5px;">Size: {size_choice}</p>
                        <p style="margin:0 0 5px;">{gift}</p>
                        <p style="margin:0 0 5px;">Shipping Cost: ${delivery:,.2f}</p>
                        <p style="text-align:right; margin:5px 0 0;">${price:,.2f} x {qty}</p>
                    </div>

                    <table style="width:100%; font-size:11px; border-collapse:collapse;">
                        <tr><td style="padding:4px 0;">Estimated delivery date:</td><td style="text-align:right;">{est_date}</td></tr>
                        <tr><td style="padding:4px 0;">Payment Method:</td><td style="text-align:right;">{payment}</td></tr>
                        <tr><td colspan="2" style="padding:10px 0 0; border-top:1px solid #aaa;"></td></tr>
                        <tr><td style="padding:4px 0;"><strong>SUBTOTAL</strong> incl. tax</td><td style="text-align:right;">${subtotal:,.2f}</td></tr>
                        <tr><td style="padding:4px 0;"><strong>DELIVERY</strong> incl. tax</td><td style="text-align:right;">${delivery:,.2f}</td></tr>
                        <tr><td style="padding:4px 0;"><strong>Sales Tax</strong> ({tax_rate*100:.1f}%)</td><td style="text-align:right;">${sales_tax:,.2f}</td></tr>
                        <tr style="font-weight:bold; font-size:12px;"><td style="padding:8px 0 0;">TOTAL</td><td style="text-align:right; padding:8px 0 0;">${total:,.2f} incl. tax</td></tr>
                    </table>

                    <div style="margin:30px 0 0; padding:0; border:1px solid #000;">
                        <table style="width:100%; font-size:11px; color:#fff; background:#000;">
                            <tr style="background:#800000;">
                                <th style="padding:8px;">DELIVERY ADDRESS</th>
                                <th style="padding:8px;">BILLING ADDRESS</th>
                                <th style="padding:8px;">NOTE</th>
                            </tr>
                            <tr style="color:#000; background:#fff;">
                                <td style="padding:8px;">{customer_name}<br>{address}</td>
                                <td style="padding:8px;">{customer_name}<br>{address}</td>
                                <td style="padding:8px;">Shipping preferences customized during checkout.</td>
                            </tr>
                        </table>
                    </div>

                    <p style="text-align:center; margin:20px 0; font-size:12px;">If you need further information please visit the <a href="#" style="color:#000; text-decoration:underline;">Contact us</a> page.</p>

                    <div style="text-align:center; background:#111; color:#aaa; padding:10px; font-size:10px;">
                        Stay Connected<br>
                        Latest news • {self.brand} Official Channel • Mobile Applications
                    </div>

                    <div style="text-align:center; font-size:10px; color:#555; margin:15px 0;">
                        TERMS OF USE • CONDITIONS OF SALE • CONTACT AN AMBASSADOR
                    </div>

                    <div style="font-size:10px; color:#444; text-align:center; line-height:1.3;">
                        RLG Europe BV<br>PO Box 2967<br>NL-1000 CZ Amsterdam<br>Netherlands<br><br>
                        {self.brand} Customer Contact Centre<br>+41 22 334 18 123<br>Email: CustomerService.RNE@{self.brand.lower()}.com
                    </div>

                    <p style="font-size:9px; color:#777; text-align:center; margin:20px 0;">
                        By clicking the links provided, you consent to our Privacy Notice & Conditions of Sale.<br>
                        Copyright © 2025 {self.brand}
                    </p>
                </div>
            </body>
            </html>
            """

            message = Mail(
                from_email=(SENDER_EMAIL, brand_display.get(self.brand, self.brand)),
                to_emails=email,
                subject=f"Your {self.brand} Order Confirmation",
                html_content=html_body
            )

            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
            logger.info(f"Email sent - status {response.status_code}")

            await interaction.followup.send(embed=Embed(title="Success!", description=f"Receipt sent to {email}!", color=Colour.green()), ephemeral=True)

        except Exception as e:
            logger.error(f"Submit error: {e}")
            await interaction.followup.send(embed=Embed(title="Error", description=str(e), color=Colour.red()), ephemeral=True)

client.run(BOT_TOKEN)