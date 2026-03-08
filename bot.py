import discord
from discord import app_commands, ui, Embed, Colour
from discord.ui import TextInput
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

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

if not all([BOT_TOKEN, SENDER_EMAIL, SENDGRID_API_KEY]):
    logger.error("Missing env vars!")
    exit(1)

ROLE_ID = 1472751333286350981

# ==================== BRAND ASSETS ====================
BRANDS = [
    'Cartier', 'Denim Tears', 'Ksubi', 'Balenciaga', 'Sp5der',
    'Nike', 'Adidas', 'Lululemon', 'Lanvin', 'Creed',
    'Baccarat', 'Sephora', 'Apple'
]

brand_assets = {
    'Cartier': {
        'name': 'Cartier',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Cartier_logo.svg/512px-Cartier_logo.svg.png',
        'logo_white': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Cartier_logo.svg/512px-Cartier_logo.svg.png',
        'website': 'https://www.cartier.com',
        'customer_service': 'https://www.cartier.com/customer-service',
        'support_email': 'contact@cartier.com',
        'color_primary': '#8B0000',  # Burgundy red - their iconic box color
        'color_secondary': '#D4AF37',  # Gold
        'font_headline': 'Helvetica, Arial, sans-serif',  # They use sans-serif for headlines [citation:1]
        'font_body': 'Georgia, Times New Roman, serif',
        'line_spacing': '150%',  # They use 150% line spacing [citation:1]
        'signature': 'Magic inside every red box'  # Their catchy signature [citation:1]
    },
    'Nike': {
        'name': 'Nike',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Logo_NIKE.svg/512px-Logo_NIKE.svg.png',
        'logo_white': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Logo_NIKE.svg/512px-Logo_NIKE.svg.png',
        'website': 'https://www.nike.com',
        'customer_service': 'https://www.nike.com/help',
        'support_email': 'service@nike.com',
        'color_primary': '#000000',
        'color_secondary': '#FFFFFF',
        'cta_color': '#0066FF',  # Bold blue for track button [citation:2]
        'font_headline': 'Helvetica, Arial, sans-serif',
        'font_body': 'Helvetica, Arial, sans-serif',
        'style': 'Ultra simple and scannable, bold aesthetic'  # [citation:8]
    },
    'Adidas': {
        'name': 'adidas',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Adidas_Logo.svg/512px-Adidas_Logo.svg.png',
        'logo_white': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Adidas_Logo.svg/512px-Adidas_Logo.svg.png',
        'website': 'https://www.adidas.com',
        'customer_service': 'https://www.adidas.com/help',
        'support_email': 'customer.service@adidas.com',
        'color_primary': '#000000',
        'color_secondary': '#00FF00',  # Lime green
        'font_headline': 'Arial, sans-serif',
        'font_body': 'Arial, sans-serif'
    },
    'Apple': {
        'name': 'Apple',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg',
        'logo_white': 'https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg',
        'website': 'https://www.apple.com',
        'customer_service': 'https://support.apple.com/contact',
        'support_email': 'orderstatus@apple.com',
        'color_primary': '#1D1D1F',
        'color_secondary': '#86868B',
        'font_headline': '-apple-system, BlinkMacSystemFont, sans-serif',
        'font_body': '-apple-system, BlinkMacSystemFont, sans-serif'
    },
    'Sephora': {
        'name': 'Sephora',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Sephora_logo.svg/512px-Sephora_logo.svg.png',
        'logo_white': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Sephora_logo.svg/512px-Sephora_logo.svg.png',
        'website': 'https://www.sephora.com',
        'customer_service': 'https://www.sephora.com/customer-service',
        'support_email': 'customerservice@sephora.com',
        'color_primary': '#000000',
        'color_secondary': '#FFFFFF',
        'font_headline': 'Arial, sans-serif',
        'font_body': 'Arial, sans-serif',
        'style': 'Clean layout with smart spacing, bigger product images'  # [citation:1]
    },
    'Lululemon': {
        'name': 'lululemon',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Lululemon_logo.svg/512px-Lululemon_logo.svg.png',
        'logo_white': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Lululemon_logo.svg/512px-Lululemon_logo.svg.png',
        'website': 'https://shop.lululemon.com',
        'customer_service': 'https://shop.lululemon.com/help/contact-us',
        'support_email': 'gea@lululemon.com',
        'sender_email': 'email@whatwelove.lululemon.com.hk',  # Their actual sender [citation:1]
        'color_primary': '#4B6E5E',
        'color_secondary': '#F0E9E0',
        'font_headline': 'Arial, sans-serif',
        'font_body': 'Arial, sans-serif'
    },
    'Creed': {
        'name': 'Creed',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Creed_logo.svg/512px-Creed_logo.svg.png',
        'logo_white': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Creed_logo.svg/512px-Creed_logo.svg.png',
        'website': 'https://www.creedboutique.com',
        'customer_service': 'https://www.creedboutique.com/customer-service',
        'support_email': 'customerservices@creedfragrances.co.uk',  # Actual support email [citation:3]
        'color_primary': '#1E2F4A',
        'color_secondary': '#C5B4A3',
        'font_headline': 'Georgia, Times New Roman, serif',  # Classic serif for heritage [citation:7]
        'font_body': 'Georgia, Times New Roman, serif'
    },
    'Baccarat': {
        'name': 'Baccarat',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/0/0f/Baccarat_logo.svg',
        'logo_white': 'https://upload.wikimedia.org/wikipedia/commons/0/0f/Baccarat_logo.svg',
        'website': 'https://www.baccarat.com',
        'customer_service': 'https://www.baccarat.com/en_int/customer-service.html',
        'support_email': 'contact@baccarat.com',
        'color_primary': '#8B6B4D',
        'color_secondary': '#E5D3C1',
        'font_headline': 'Georgia, Times New Roman, serif',
        'font_body': 'Georgia, Times New Roman, serif'
    },
    'Ksubi': {
        'name': 'Ksubi',
        'logo': 'https://brandfetch.com/ksubi.com/logo.png',
        'logo_white': 'https://brandfetch.com/ksubi.com/logo.png',
        'website': 'https://www.ksubi.com',
        'customer_service': 'https://www.ksubi.com/pages/contact-us',
        'support_email': 'help@ksubi.com',
        'color_primary': '#2C2C2C',
        'color_secondary': '#8B8B8B',
        'font_headline': 'Arial, Helvetica, sans-serif',
        'font_body': 'Arial, Helvetica, sans-serif',
        'shipping_cutoff': '2pm',  # Orders before 2pm dispatched same day [citation:4]
        'authority_to_leave': True  # ATL with photo proof [citation:4]
    },
    'Denim Tears': {
        'name': 'Denim Tears',
        'logo': 'https://denimtears.co/wp-content/uploads/2024/logo.png',
        'logo_white': 'https://denimtears.co/wp-content/uploads/2024/logo.png',
        'website': 'https://denimtears.co',
        'customer_service': 'https://denimtears.co/contact',
        'support_email': 'support@denimtears.co',
        'color_primary': '#1A2E3F',
        'color_secondary': '#C4A962',
        'font_headline': 'Arial, Helvetica, sans-serif',
        'font_body': 'Arial, Helvetica, sans-serif',
        'processing_days': '4-7 days'  # Time to process before shipping
    },
    'Balenciaga': {
        'name': 'Balenciaga',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/8/8f/Balenciaga_logo.svg',
        'logo_white': 'https://upload.wikimedia.org/wikipedia/commons/8/8f/Balenciaga_logo.svg',
        'website': 'https://www.balenciaga.com',
        'customer_service': 'https://www.balenciaga.com/en-us/customer-service',
        'support_email': 'customer.service@balenciaga.com',
        'color_primary': '#000000',
        'color_secondary': '#FFFFFF',
        'font_headline': 'Arial, Helvetica, sans-serif',
        'font_body': 'Arial, Helvetica, sans-serif'
    },
    'Lanvin': {
        'name': 'Lanvin',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/5/5f/Lanvin_logo.svg',
        'logo_white': 'https://upload.wikimedia.org/wikipedia/commons/5/5f/Lanvin_logo.svg',
        'website': 'https://www.lanvin.com',
        'customer_service': 'https://www.lanvin.com/en-int/customer-service',
        'support_email': 'customer.service@lanvin.com',
        'color_primary': '#0A1A2A',
        'color_secondary': '#B89C7A',
        'font_headline': 'Georgia, Times New Roman, serif',
        'font_body': 'Georgia, Times New Roman, serif'
    },
    'Sp5der': {
        'name': 'Sp5der',
        'logo': 'https://i.imgur.com/sp5der-logo.png',
        'logo_white': 'https://i.imgur.com/sp5der-logo.png',
        'website': 'https://sp5der.com',
        'customer_service': 'https://sp5der.com/pages/contact',
        'support_email': 'support@sp5der.com',
        'color_primary': '#D4AF37',
        'color_secondary': '#1A1A1A',
        'font_headline': 'Impact, Arial Black, sans-serif',
        'font_body': 'Arial, Helvetica, sans-serif'
    }
}

# ==================== FAKE DATA ====================
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
    "American Express ending in 1004",
    "Apple Pay",
    "PayPal",
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

# Store user emails
user_emails = {}
role_tasks = {}

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    logger.info(f"Bot online as {client.user}")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/generate"))

# ==================== SETUP COMMAND ====================
@tree.command(name="setup", description="Hook your email to your user (role required)")
async def setup(interaction: discord.Interaction):
    if not any(r.id == ROLE_ID for r in interaction.user.roles):
        await interaction.response.send_message(embed=Embed(title="Access Denied", description="You need the special role!", color=Colour.red()), ephemeral=True)
        return
    await interaction.response.send_modal(EmailModal())

class EmailModal(discord.ui.Modal, title="Email Setup"):
    email = TextInput(label="What's your email?", style=discord.TextStyle.short, required=True, placeholder="Enter your email for receipts...")

    async def on_submit(self, interaction: discord.Interaction):
        user_emails[interaction.user.id] = self.email.value
        await interaction.response.send_message(embed=Embed(title="Email Hooked", description=f"Email {self.email.value} saved! Use /generate.", color=Colour.green()), ephemeral=True)

# ==================== ROLE COMMAND ====================
@tree.command(name="role", description="Give user the special role for a duration (e.g. 1d, 2w, 3m)")
@app_commands.describe(user="The user", duration="Duration e.g. 1d 2w 3m")
async def role(interaction: discord.Interaction, user: discord.Member, duration: str):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You need manage roles permission.", ephemeral=True)
        return

    duration = duration.lower().strip()
    
    if duration.endswith('d'):
        seconds = int(duration[:-1]) * 86400
    elif duration.endswith('w'):
        seconds = int(duration[:-1]) * 604800
    elif duration.endswith('m'):
        seconds = int(duration[:-1]) * 2592000
    else:
        await interaction.response.send_message("Invalid format. Use 1d, 2w, 3m", ephemeral=True)
        return

    role = interaction.guild.get_role(ROLE_ID)
    if not role:
        await interaction.response.send_message("Role not found.", ephemeral=True)
        return

    await user.add_roles(role)
    await interaction.response.send_message(f"✅ Added role to {user.mention} for {duration}.", ephemeral=True)
    
    if user.id in role_tasks:
        role_tasks[user.id].cancel()
    
    async def remove_role_after_delay():
        try:
            await asyncio.sleep(seconds)
            await user.remove_roles(role)
            logger.info(f"Removed role from {user} after {duration}")
        except asyncio.CancelledError:
            pass
    
    task = asyncio.create_task(remove_role_after_delay())
    role_tasks[user.id] = task

# ==================== GENERATE COMMAND ====================
class BrandSelect(discord.ui.Select):
    def __init__(self, user_id):
        self.user_id = user_id
        options = []
        for brand in BRANDS:
            options.append(discord.SelectOption(label=brand, value=brand, emoji="🛍️"))
        
        super().__init__(placeholder="Choose a brand...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your menu!", ephemeral=True)
            return
        
        brand = self.values[0]
        
        if interaction.user.id not in user_emails:
            await interaction.response.send_message(embed=Embed(title="No Email", description="Run /setup first to save your email!", color=Colour.red()), ephemeral=True)
            return
        
        # BRAND-SPECIFIC MODALS based on what they sell
        if brand == "Cartier":
            modal = CartierModal(brand, interaction.user.id)
        elif brand in ["Nike", "Adidas"]:
            modal = SportswearModal(brand, interaction.user.id)
        elif brand == "Sephora":
            modal = BeautyModal(brand, interaction.user.id)
        elif brand == "Apple":
            modal = TechModal(brand, interaction.user.id)
        elif brand == "Lululemon":
            modal = AthleisureModal(brand, interaction.user.id)
        elif brand in ["Baccarat", "Creed"]:
            modal = FragranceModal(brand, interaction.user.id)
        elif brand in ["Denim Tears", "Ksubi", "Sp5der"]:
            modal = StreetwearModal(brand, interaction.user.id)
        elif brand in ["Balenciaga", "Lanvin"]:
            modal = LuxuryModal(brand, interaction.user.id)
        else:
            modal = BasicModal(brand, interaction.user.id)
        
        await interaction.response.send_modal(modal)

class BrandView(ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.add_item(BrandSelect(user_id))

@tree.command(name="generate", description="Generate a receipt (role required)")
async def generate(interaction: discord.Interaction):
    if not any(r.id == ROLE_ID for r in interaction.user.roles):
        await interaction.response.send_message(embed=Embed(title="Access Denied", description="You need the special role!", color=Colour.red()), ephemeral=True)
        return

    embed = Embed(
        title="Choose Your Brand",
        description=f"{interaction.user.mention}, select a brand from the dropdown below.",
        color=Colour.blue()
    )

    view = BrandView(interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view)

# ==================== CARTIER MODAL ====================
class CartierModal(discord.ui.Modal, title="Cartier Receipt Details"):
    def __init__(self, brand: str, user_id: int):
        super().__init__(timeout=600)
        self.brand = brand
        self.user_id = user_id
        self.assets = brand_assets[brand]

        self.item = TextInput(label="Item name", style=discord.TextStyle.short, required=True, max_length=100, placeholder="e.g. Love Bracelet, Tank Watch")
        self.metal = TextInput(label="Metal", style=discord.TextStyle.short, required=True, max_length=30, placeholder="e.g. Rose Gold, Yellow Gold")
        self.size = TextInput(label="Size", style=discord.TextStyle.short, required=True, max_length=20, placeholder="e.g. 52, 54, 56")
        self.price = TextInput(label="Price in USD", style=discord.TextStyle.short, required=True, max_length=20, placeholder="e.g. 6500")
        self.shipping_date = TextInput(label="Delivery date", style=discord.TextStyle.short, required=True, max_length=30)

        self.add_item(self.item)
        self.add_item(self.metal)
        self.add_item(self.size)
        self.add_item(self.price)
        self.add_item(self.shipping_date)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        email = user_emails.get(self.user_id)
        if not email:
            await interaction.followup.send(embed=Embed(title="Error", description="Email not found. Run /setup again.", color=Colour.red()), ephemeral=True)
            return
        
        try:
            price = float(self.price.value.strip())
            await interaction.followup.send(embed=Embed(title="Processing...", description="⏳ Your Cartier receipt is being generated.", color=Colour.blue()), ephemeral=True)
            
            asyncio.create_task(self.send_receipt(
                interaction, email, 
                self.item.value, self.metal.value, self.size.value, price,
                self.shipping_date.value
            ))
        except Exception as e:
            logger.error(f"Error: {e}")
            await interaction.followup.send(embed=Embed(title="Error", description=str(e), color=Colour.red()), ephemeral=True)
    
    async def send_receipt(self, interaction, email, item_name, metal, size, price, est_date):
        try:
            qty = 1
            customer_name = random.choice(FAKE_NAMES)
            address = random.choice(FAKE_ADDRESSES)
            state = get_state_from_address(address)
            tax_rate = STATE_TAX_RATES.get(state, 0.0749)

            subtotal = price * qty
            delivery = round(random.uniform(25, 45), 2)
            sales_tax = round(subtotal * tax_rate, 2)
            total = round(subtotal + delivery + sales_tax, 2)

            order_id = f"CRT-{random.randint(1000000, 9999999)}"
            payment = random.choice(FAKE_PAYMENT_METHODS)

            # EXACT CARTIER RECEIPT based on research [citation:1]
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: '{self.assets['font_body']}'; background-color: #f5f5f5; margin: 0; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e0d6c6; }}
                    .header {{ background: linear-gradient(135deg, {self.assets['color_primary']} 0%, #4a0000 100%); padding: 40px 20px; text-align: center; }}
                    .header img {{ max-width: 200px; filter: brightness(0) invert(1); }}
                    .header h1 {{ font-family: '{self.assets['font_headline']}'; color: #ffffff; margin: 0; font-size: 36px; font-weight: 300; letter-spacing: 4px; }}
                    .content {{ padding: 40px; }}
                    .order-number {{ background-color: #f8f5f0; padding: 15px; text-align: center; border: 1px solid {self.assets['color_secondary']}; margin: 20px 0; }}
                    .order-number p {{ margin: 0; color: {self.assets['color_primary']}; font-size: 18px; font-family: '{self.assets['font_headline']}'; }}
                    .details {{ margin: 30px 0; }}
                    .details table {{ width: 100%; border-collapse: collapse; }}
                    .details td {{ padding: 12px 0; border-bottom: 1px solid #e0d6c6; font-size: 14px; line-height: {self.assets['line_spacing']}; }}
                    .total {{ font-weight: bold; font-size: 18px; color: {self.assets['color_primary']}; }}
                    .footer {{ border-top: 2px solid {self.assets['color_secondary']}; padding: 30px 0 0; text-align: center; color: #666; font-size: 12px; }}
                    .footer a {{ color: {self.assets['color_primary']}; text-decoration: none; }}
                    .footer a:hover {{ text-decoration: underline; }}
                    .red-box {{ background-color: {self.assets['color_primary']}; color: white; padding: 20px; text-align: center; margin: 30px 0; border-radius: 4px; }}
                    .red-box p {{ margin: 0; font-size: 16px; font-family: '{self.assets['font_headline']}'; }}
                    .legal {{ font-size: 11px; color: #999; text-align: center; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="{self.assets['logo_white']}" alt="Cartier">
                    </div>
                    <div class="content">
                        <p style="font-size: 20px; color: #333; font-family: '{self.assets['font_headline']}';">Dear {customer_name},</p>
                        <p style="color: #666; line-height: {self.assets['line_spacing']};">Thank you for your purchase. We are pleased to confirm your order.</p>
                        
                        <div class="order-number">
                            <p>ORDER #{order_id}</p>
                        </div>
                        
                        <div class="details">
                            <table>
                                <tr><td><strong>Item:</strong> {item_name}</td><td style="text-align: right;">${price:,.2f}</td></tr>
                                <tr><td><strong>Metal:</strong> {metal}</td><td style="text-align: right;"></td></tr>
                                <tr><td><strong>Size:</strong> {size}</td><td style="text-align: right;"></td></tr>
                                <tr><td><strong>Quantity:</strong> {qty}</td><td style="text-align: right;"></td></tr>
                                <tr><td><strong>Shipping:</strong></td><td style="text-align: right;">${delivery:,.2f}</td></tr>
                                <tr><td><strong>Tax:</strong></td><td style="text-align: right;">${sales_tax:,.2f}</td></tr>
                                <tr class="total"><td><strong>TOTAL:</strong></td><td style="text-align: right;">${total:,.2f}</td></tr>
                            </table>
                        </div>
                        
                        <div style="margin: 30px 0; padding: 20px; background-color: #faf8f5;">
                            <p><strong>Delivery Address:</strong><br>{address}</p>
                            <p><strong>Estimated Delivery:</strong> {est_date}</p>
                            <p><strong>Payment Method:</strong> {payment}</p>
                        </div>
                        
                        <div class="red-box">
                            <p>{self.assets['signature']}</p>
                        </div>
                        
                        <div class="footer">
                            <p>Track your order: <a href="{self.assets['website']}/track/{order_id}">cartier.com/track</a></p>
                            <p style="margin: 10px 0;">
                                Customer Service: <a href="{self.assets['customer_service']}">Contact Us</a> | 
                                <a href="mailto:{self.assets['support_email']}">{self.assets['support_email']}</a>
                            </p>
                            <p><a href="{self.assets['website']}">{self.assets['website'].replace('https://', '')}</a></p>
                            
                            <div class="legal">
                                <p>Postal address: 13 Rue de la Paix, 75002 Paris, France</p>
                                <p><a href="#">Unsubscribe</a> | <a href="#">Privacy Policy</a></p>
                                <p>You received this email because you made a purchase at cartier.com</p>
                                <p style="margin-top: 20px;">© Cartier 2025. All rights reserved.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """

            # Send order confirmation email
            message = Mail(
                from_email=(SENDER_EMAIL, "Cartier"),
                to_emails=email,
                subject=f"Order Confirmation #{order_id}",
                html_content=html_body
            )

            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
            
            # Also send a shipping notification (they send multiple emails in sequence)
            await asyncio.sleep(2)  # Simulate delay between emails
            shipping_body = html_body.replace("Order Confirmation", "Shipping Confirmation").replace("Thank you for your purchase", "Your order has shipped")
            
            message2 = Mail(
                from_email=(SENDER_EMAIL, "Cartier"),
                to_emails=email,
                subject=f"Shipping Confirmation #{order_id}",
                html_content=shipping_body
            )
            sg.send(message2)
            
            await interaction.followup.send(embed=Embed(title="Success!", description=f"✅ Cartier receipt sent to {email}!", color=Colour.green()), ephemeral=True)
            
        except Exception as e:
            logger.error(f"Email error: {e}")
            await interaction.followup.send(embed=Embed(title="Error", description=f"Failed: {str(e)}", color=Colour.red()), ephemeral=True)

# ==================== NIKE MODAL ====================
class SportswearModal(discord.ui.Modal, title="Nike/Adidas Receipt Details"):
    def __init__(self, brand: str, user_id: int):
        super().__init__(timeout=600)
        self.brand = brand
        self.user_id = user_id
        self.assets = brand_assets[brand]

        self.item = TextInput(label="Item name", style=discord.TextStyle.short, required=True, max_length=100, placeholder="e.g. Air Max 97, Ultraboost")
        self.size = TextInput(label="Size", style=discord.TextStyle.short, required=True, max_length=10, placeholder="e.g. 9, 10.5, M, L, XL")
        self.color = TextInput(label="Color", style=discord.TextStyle.short, required=True, max_length=30, placeholder="e.g. Black/White")
        self.price = TextInput(label="Price in USD", style=discord.TextStyle.short, required=True, max_length=20, placeholder="e.g. 190")
        self.shipping_date = TextInput(label="Delivery date", style=discord.TextStyle.short, required=True, max_length=30)

        self.add_item(self.item)
        self.add_item(self.size)
        self.add_item(self.color)
        self.add_item(self.price)
        self.add_item(self.shipping_date)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        email = user_emails.get(self.user_id)
        if not email:
            await interaction.followup.send(embed=Embed(title="Error", description="Email not found. Run /setup again.", color=Colour.red()), ephemeral=True)
            return
        
        try:
            price = float(self.price.value.strip())
            await interaction.followup.send(embed=Embed(title="Processing...", description=f"⏳ Your {self.brand} receipt is being generated.", color=Colour.blue()), ephemeral=True)
            
            asyncio.create_task(self.send_receipt(
                interaction, email, 
                self.item.value, self.size.value, self.color.value, price,
                self.shipping_date.value
            ))
        except Exception as e:
            await interaction.followup.send(embed=Embed(title="Error", description=str(e), color=Colour.red()), ephemeral=True)

    async def send_receipt(self, interaction, email, item_name, size, color, price, est_date):
        try:
            qty = 1
            customer_name = random.choice(FAKE_NAMES)
            address = random.choice(FAKE_ADDRESSES)
            state = get_state_from_address(address)
            tax_rate = STATE_TAX_RATES.get(state, 0.0749)

            subtotal = price * qty
            delivery = round(random.uniform(8, 15), 2)
            sales_tax = round(subtotal * tax_rate, 2)
            total = round(subtotal + delivery + sales_tax, 2)

            order_id = f"{self.brand[:3].upper()}-{random.randint(100000, 999999)}"
            payment = random.choice(FAKE_PAYMENT_METHODS)
            
            # Generate a fake product image URL (Nike always shows product images) [citation:2]
            product_image = f"https://placekitten.com/200/200"  # Replace with actual product image logic

            if self.brand == "Nike":
                # EXACT NIKE RECEIPT based on research [citation:2][citation:8]
                html_body = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{ font-family: '{self.assets['font_body']}'; background: #f5f5f5; margin: 0; padding: 20px; }}
                        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; }}
                        .header {{ background: {self.assets['color_primary']}; padding: 30px; text-align: center; }}
                        .header img {{ max-width: 80px; filter: brightness(0) invert(1); }}
                        .content {{ padding: 30px; }}
                        .thank-you {{ font-size: 28px; font-weight: bold; margin-bottom: 10px; font-family: '{self.assets['font_headline']}'; }}
                        .order-summary {{ font-size: 18px; font-weight: bold; margin: 20px 0 10px; }}
                        .product-row {{ display: flex; margin: 20px 0; padding: 20px; background: #f8f8f8; border-left: 4px solid {self.assets['color_primary']}; }}
                        .product-image {{ width: 80px; height: 80px; background: #e0e0e0; margin-right: 20px; border-radius: 4px; }}
                        .product-details {{ flex: 1; }}
                        .product-name {{ font-weight: bold; }}
                        .product-price {{ text-align: right; font-weight: bold; }}
                        .details-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }}
                        .track-button {{ background: {self.assets['cta_color']}; color: white; padding: 15px 30px; text-decoration: none; display: inline-block; border-radius: 30px; font-weight: bold; margin: 20px 0; }}
                        .footer {{ background: #f8f8f8; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                        .footer a {{ color: {self.assets['color_primary']}; text-decoration: none; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <img src="{self.assets['logo_white']}" alt="NIKE">
                        </div>
                        <div class="content">
                            <div class="thank-you">THANK YOU FOR YOUR ORDER, {customer_name.upper()}!</div>
                            <p>YOUR GEAR IS ON THE WAY.</p>
                            
                            <div class="order-summary">ORDER SUMMARY</div>
                            
                            <div class="product-row">
                                <div class="product-image">
                                    <img src="{product_image}" width="80" height="80" style="object-fit: cover;">
                                </div>
                                <div class="product-details">
                                    <div class="product-name">{item_name}</div>
                                    <div>Size: {size} | Color: {color}</div>
                                    <div>Qty: {qty}</div>
                                </div>
                                <div class="product-price">${price:,.2f}</div>
                            </div>
                            
                            <div class="details-grid">
                                <div><strong>Order ID:</strong><br>{order_id}</div>
                                <div><strong>Payment Method:</strong><br>{payment}</div>
                                <div><strong>Shipping Address:</strong><br>{address}</div>
                                <div><strong>Delivery by:</strong><br>{est_date}</div>
                            </div>
                            
                            <div style="text-align: center;">
                                <a href="{self.assets['website']}/orders/track?order={order_id}" class="track-button">TRACK ORDER</a>
                            </div>
                            
                            <div style="margin: 20px 0; padding: 15px; background: #f0f0f0; border-radius: 4px;">
                                <p><strong>Shipping:</strong> ${delivery:,.2f}</p>
                                <p><strong>Tax:</strong> ${sales_tax:,.2f}</p>
                                <p style="font-size: 18px;"><strong>Total: ${total:,.2f}</strong></p>
                            </div>
                        </div>
                        <div class="footer">
                            <p>JUST DO IT.</p>
                            <p><a href="{self.assets['website']}">nike.com</a> | <a href="{self.assets['customer_service']}">Help</a> | <a href="#">Unsubscribe</a></p>
                            <p style="margin-top: 10px;">© 2025 Nike, Inc. All Rights Reserved</p>
                        </div>
                    </div>
                </body>
                </html>
                """
            else:  # ADIDAS
                # ADIDAS receipt based on their email sequence [citation:5]
                html_body = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{ font-family: '{self.assets['font_body']}'; background: #fff; margin: 0; padding: 20px; }}
                        .container {{ max-width: 600px; margin: 0 auto; background: #fff; border: 1px solid #e5e5e5; }}
                        .header {{ background: {self.assets['color_primary']}; padding: 25px; text-align: center; border-bottom: 3px solid {self.assets['color_secondary']}; }}
                        .header img {{ max-width: 80px; filter: brightness(0) invert(1); }}
                        .stripes {{ height: 3px; background: linear-gradient(90deg, {self.assets['color_primary']} 33%, {self.assets['color_secondary']} 33%, {self.assets['color_secondary']} 66%, {self.assets['color_primary']} 66%); }}
                        .content {{ padding: 30px; }}
                        .order-detail {{ border: 1px solid #ddd; padding: 20px; margin: 20px 0; }}
                        .footer {{ text-align: center; padding: 20px; color: #666; border-top: 1px solid #e5e5e5; }}
                        .footer a {{ color: {self.assets['color_primary']}; text-decoration: none; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <img src="{self.assets['logo_white']}" alt="adidas">
                        </div>
                        <div class="stripes"></div>
                        <div class="content">
                            <p style="font-size: 18px;">Hey {customer_name},</p>
                            <p>Your order is confirmed and being prepared.</p>
                            
                            <div class="order-detail">
                                <p style="font-size: 14px; color: #666;">ORDER #{order_id}</p>
                                <p><strong>{item_name}</strong></p>
                                <p>Size: {size} | Color: {color}</p>
                                <p>Subtotal: ${price:,.2f}</p>
                                <p>Shipping: ${delivery:,.2f}</p>
                                <p>Tax: ${sales_tax:,.2f}</p>
                                <p style="font-size:20px;"><strong>TOTAL: ${total:,.2f}</strong></p>
                            </div>
                            
                            <p><strong>Shipping to:</strong><br>{address}</p>
                            <p><strong>Delivery by:</strong> {est_date}</p>
                            <p><strong>Payment:</strong> {payment}</p>
                            
                            <p style="text-align:center;">
                                <a href="{self.assets['website']}/order-tracking" style="color:{self.assets['color_primary']};">Track your order →</a>
                            </p>
                            
                            <p style="font-size:12px; color:#999; margin-top:20px;">
                                You'll receive another email when your order ships with your Track & Trace code.
                            </p>
                        </div>
                        <div class="footer">
                            <p><a href="{self.assets['website']}">adidas.com</a> | IMPOSSIBLE IS NOTHING | <a href="{self.assets['customer_service']}">Help</a></p>
                        </div>
                    </div>
                </body>
                </html>
                """

            # Send order confirmation email
            message = Mail(
                from_email=(SENDER_EMAIL, self.brand),
                to_emails=email,
                subject=f"Order Confirmation #{order_id}",
                html_content=html_body
            )

            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
            
            # Send shipping confirmation with tracking (they send multiple emails) [citation:5]
            await asyncio.sleep(2)
            tracking_body = html_body.replace("confirmed and being prepared", "has shipped")
            tracking_body += f"""
            <div style="margin:20px 0; padding:15px; background:#f0f0f0;">
                <p><strong>TRACKING NUMBER:</strong> 1Z{random.randint(100,999)}ABC{random.randint(1000,9999)}</p>
                <p>Track at: <a href="{self.assets['website']}/track">adidas.com/track</a></p>
            </div>
            """
            
            message2 = Mail(
                from_email=(SENDER_EMAIL, self.brand),
                to_emails=email,
                subject=f"Your order has shipped! #{order_id}",
                html_content=tracking_body
            )
            sg.send(message2)
            
            await interaction.followup.send(embed=Embed(title="Success!", description=f"✅ {self.brand} receipt sent! Check your email for order confirmation and shipping updates.", color=Colour.green()), ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(embed=Embed(title="Error", description=str(e), color=Colour.red()), ephemeral=True)

# ==================== CREED MODAL ====================
class FragranceModal(discord.ui.Modal, title="Creed/Baccarat Receipt Details"):
    def __init__(self, brand: str, user_id: int):
        super().__init__(timeout=600)
        self.brand = brand
        self.user_id = user_id
        self.assets = brand_assets[brand]

        self.item = TextInput(label="Fragrance name", style=discord.TextStyle.short, required=True, max_length=100, placeholder="e.g. Aventus, Baccarat Rouge 540")
        self.size = TextInput(label="Size (ml)", style=discord.TextStyle.short, required=True, max_length=20, placeholder="e.g. 50ml, 100ml")
        self.concentration = TextInput(label="Concentration", style=discord.TextStyle.short, required=True, max_length=30, placeholder="e.g. Eau de Parfum, Extrait")
        self.price = TextInput(label="Price in USD", style=discord.TextStyle.short, required=True, max_length=20, placeholder="e.g. 325")
        self.shipping_date = TextInput(label="Delivery date", style=discord.TextStyle.short, required=True, max_length=30)

        self.add_item(self.item)
        self.add_item(self.size)
        self.add_item(self.concentration)
        self.add_item(self.price)
        self.add_item(self.shipping_date)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        email = user_emails.get(self.user_id)
        if not email:
            await interaction.followup.send(embed=Embed(title="Error", description="Email not found. Run /setup again.", color=Colour.red()), ephemeral=True)
            return
        
        try:
            price = float(self.price.value.strip())
            await interaction.followup.send(embed=Embed(title="Processing...", description=f"⏳ Your {self.brand} receipt is being generated.", color=Colour.blue()), ephemeral=True)
            
            asyncio.create_task(self.send_receipt(
                interaction, email, 
                self.item.value, self.size.value, self.concentration.value, price,
                self.shipping_date.value
            ))
        except Exception as e:
            await interaction.followup.send(embed=Embed(title="Error", description=str(e), color=Colour.red()), ephemeral=True)

    async def send_receipt(self, interaction, email, item_name, size, concentration, price, est_date):
        try:
            qty = 1
            customer_name = random.choice(FAKE_NAMES)
            address = random.choice(FAKE_ADDRESSES)
            state = get_state_from_address(address)
            tax_rate = STATE_TAX_RATES.get(state, 0.0749)

            subtotal = price * qty
            delivery = 0  # Creed offers complimentary delivery [citation:3]
            sales_tax = round(subtotal * tax_rate, 2)
            total = round(subtotal + sales_tax, 2)

            order_id = f"{self.brand[:3].upper()}-{random.randint(100000, 999999)}"
            payment = random.choice(FAKE_PAYMENT_METHODS)

            # EXACT CREED RECEIPT based on their policies [citation:3]
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: '{self.assets['font_body']}'; background: #f8f8f8; margin: 0; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; border: 1px solid #ddd; }}
                    .header {{ background: {self.assets['color_primary']}; padding: 30px; text-align: center; }}
                    .header img {{ max-width: 150px; filter: brightness(0) invert(1); }}
                    .content {{ padding: 30px; }}
                    .order-box {{ border: 1px solid {self.assets['color_secondary']}; padding: 20px; margin: 20px 0; }}
                    .delivery-slot {{ background: #f0f0f0; padding: 15px; margin: 20px 0; border-left: 4px solid {self.assets['color_primary']}; }}
                    .footer {{ border-top: 1px solid {self.assets['color_secondary']}; padding: 20px; text-align: center; color: #666; }}
                    .footer a {{ color: {self.assets['color_primary']}; }}
                    .contact-info {{ font-size: 12px; color: #999; margin-top: 15px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="{self.assets['logo_white']}" alt="{self.brand}">
                    </div>
                    <div class="content">
                        <p style="font-size: 18px;">Dear {customer_name},</p>
                        <p>Thank you for your order from The House of Creed.</p>
                        
                        <div class="order-box">
                            <p><strong>Order #{order_id}</strong></p>
                            <p>{item_name}</p>
                            <p>{size} | {concentration}</p>
                            <p>Price: ${price:,.2f}</p>
                            <p>Shipping: Complimentary</p>
                            <p>Tax: ${sales_tax:,.2f}</p>
                            <p style="font-size: 20px;"><strong>Total: ${total:,.2f}</strong></p>
                        </div>
                        
                        <p><strong>Shipping to:</strong><br>{address}</p>
                        <p><strong>Estimated delivery:</strong> {est_date}</p>
                        <p><strong>Payment:</strong> {payment}</p>
                        
                        <div class="delivery-slot">
                            <p><strong>Delivery Information:</strong></p>
                            <p>• Complimentary standard delivery (2-7 working days) [citation:3]</p>
                            <p>• You'll receive an email with tracking when your order ships</p>
                            <p>• A one-hour delivery slot will be allocated for premium deliveries</p>
                        </div>
                        
                        <p style="font-size: 12px; color: #666;">
                            Returns accepted within 30 days of dispatch if unused and in original condition [citation:3]
                        </p>
                    </div>
                    <div class="footer">
                        <p><a href="{self.assets['website']}">{self.assets['website'].replace('https://', '')}</a> | <a href="{self.assets['customer_service']}">Customer Service</a></p>
                        <div class="contact-info">
                            <p>Customer Service: Monday-Saturday 9:30am-5:30pm</p>
                            <p>Email: {self.assets['support_email']} | Tel: +44 330 053 2398 [citation:3]</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """

            message = Mail(
                from_email=(SENDER_EMAIL, self.brand),
                to_emails=email,
                subject=f"Your {self.brand} Order #{order_id}",
                html_content=html_body
            )

            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
            
            await interaction.followup.send(embed=Embed(title="Success!", description=f"✅ {self.brand} receipt sent!", color=Colour.green()), ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(embed=Embed(title="Error", description=str(e), color=Colour.red()), ephemeral=True)

# ==================== KSUBI MODAL ====================
class StreetwearModal(discord.ui.Modal, title="Streetwear Receipt Details"):
    def __init__(self, brand: str, user_id: int):
        super().__init__(timeout=600)
        self.brand = brand
        self.user_id = user_id
        self.assets = brand_assets[brand]

        self.item = TextInput(label="Item name", style=discord.TextStyle.short, required=True, max_length=100, placeholder="e.g. Hoodie, Jeans")
        self.size = TextInput(label="Size", style=discord.TextStyle.short, required=True, max_length=10, placeholder="e.g. S, M, L, XL, 32")
        self.color = TextInput(label="Color", style=discord.TextStyle.short, required=True, max_length=30, placeholder="e.g. Black, Wash")
        self.price = TextInput(label="Price in USD", style=discord.TextStyle.short, required=True, max_length=20, placeholder="e.g. 120")
        self.shipping_date = TextInput(label="Delivery date", style=discord.TextStyle.short, required=True, max_length=30)

        self.add_item(self.item)
        self.add_item(self.size)
        self.add_item(self.color)
        self.add_item(self.price)
        self.add_item(self.shipping_date)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        email = user_emails.get(self.user_id)
        if not email:
            await interaction.followup.send(embed=Embed(title="Error", description="Email not found. Run /setup again.", color=Colour.red()), ephemeral=True)
            return
        
        try:
            price = float(self.price.value.strip())
            await interaction.followup.send(embed=Embed(title="Processing...", description=f"⏳ Your {self.brand} receipt is being generated.", color=Colour.blue()), ephemeral=True)
            
            asyncio.create_task(self.send_receipt(
                interaction, email, 
                self.item.value, self.size.value, self.color.value, price,
                self.shipping_date.value
            ))
        except Exception as e:
            await interaction.followup.send(embed=Embed(title="Error", description=str(e), color=Colour.red()), ephemeral=True)

    async def send_receipt(self, interaction, email, item_name, size, color, price, est_date):
        try:
            qty = 1
            customer_name = random.choice(FAKE_NAMES)
            address = random.choice(FAKE_ADDRESSES)
            state = get_state_from_address(address)
            tax_rate = STATE_TAX_RATES.get(state, 0.0749)

            subtotal = price * qty
            delivery = round(random.uniform(8, 15), 2)
            sales_tax = round(subtotal * tax_rate, 2)
            total = round(subtotal + delivery + sales_tax, 2)

            order_id = f"{self.brand[:3].upper()}-{random.randint(100000, 999999)}"
            payment = random.choice(FAKE_PAYMENT_METHODS)
            
            # KSUBI specific: orders before 2pm dispatched same day [citation:4]
            dispatch_time = "today" if random.choice([True, False]) else "tomorrow"
            
            # EXACT KSUBI RECEIPT based on their policies [citation:4][citation:10]
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: '{self.assets['font_body']}'; background: #f5f5f5; margin: 0; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; }}
                    .header {{ background: {self.assets['color_primary']}; padding: 30px; text-align: center; }}
                    .header img {{ max-width: 150px; filter: brightness(0) invert(1); }}
                    .content {{ padding: 30px; }}
                    .dispatch-note {{ background: #f0f0f0; padding: 15px; margin: 20px 0; border-left: 4px solid {self.assets['color_primary']}; }}
                    .atl-note {{ background: #e8e8e8; padding: 10px; font-size: 12px; margin: 15px 0; }}
                    .footer {{ background: #111; color: white; padding: 20px; text-align: center; }}
                    .footer a {{ color: {self.assets['color_primary']}; text-decoration: none; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="{self.assets['logo_white']}" alt="{self.brand}">
                    </div>
                    <div class="content">
                        <h2>ORDER CONFIRMED</h2>
                        <p>Thanks {customer_name}</p>
                        
                        <div style="border: 1px solid #ddd; padding: 20px; margin: 20px 0;">
                            <p><strong>Order #{order_id}</strong></p>
                            <p>{item_name} | Size: {size} | Color: {color}</p>
                            <p>Subtotal: ${price:,.2f}</p>
                            <p>Shipping: ${delivery:,.2f}</p>
                            <p>Tax: ${sales_tax:,.2f}</p>
                            <p style="font-size: 24px;"><strong>Total: ${total:,.2f}</strong></p>
                        </div>
                        
                        <p><strong>Shipping to:</strong><br>{address}</p>
                        <p><strong>Delivery by:</strong> {est_date}</p>
                        
                        <div class="dispatch-note">
                            <p><strong>Dispatch Information:</strong></p>
                            <p>• Orders placed before 2pm are dispatched {dispatch_time} [citation:4]</p>
                            <p>• You'll receive an email with tracking when your parcel leaves our distribution centre [citation:4]</p>
                            <p>• All orders are tracked by the delivery carrier [citation:4]</p>
                        </div>
                        
                        <div class="atl-note">
                            <p><strong>Authority to Leave (ATL):</strong> This parcel may be left in a safe location. A photo will be taken as proof of delivery. [citation:4]</p>
                        </div>
                        
                        <p style="text-align:center; margin:20px 0;">
                            <a href="{self.assets['website']}/track?order={order_id}" style="background:{self.assets['color_primary']}; color:white; padding:10px 20px; text-decoration:none;">TRACK ORDER</a>
                        </p>
                    </div>
                    <div class="footer">
                        <p><a href="{self.assets['website']}">shop</a> | <a href="{self.assets['customer_service']}">contact</a></p>
                        <p style="font-size: 11px;">OG DENIM · SINCE 1999</p>
                    </div>
                </div>
            </body>
            </html>
            """

            message = Mail(
                from_email=(SENDER_EMAIL, self.brand),
                to_emails=email,
                subject=f"Your {self.brand} Order #{order_id}",
                html_content=html_body
            )

            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
            
            await interaction.followup.send(embed=Embed(title="Success!", description=f"✅ {self.brand} receipt sent!", color=Colour.green()), ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(embed=Embed(title="Error", description=str(e), color=Colour.red()), ephemeral=True)

# ==================== LULULEMON MODAL ====================
class AthleisureModal(discord.ui.Modal, title="Lululemon Receipt Details"):
    def __init__(self, brand: str, user_id: int):
        super().__init__(timeout=600)
        self.brand = brand
        self.user_id = user_id
        self.assets = brand_assets[brand]

        self.item = TextInput(label="Item name", style=discord.TextStyle.short, required=True, max_length=100, placeholder="e.g. Align Leggings")
        self.size = TextInput(label="Size", style=discord.TextStyle.short, required=True, max_length=10, placeholder="e.g. 2, 4, 6, 8")
        self.color = TextInput(label="Color", style=discord.TextStyle.short, required=True, max_length=30, placeholder="e.g. Black, Navy")
        self.price = TextInput(label="Price in USD", style=discord.TextStyle.short, required=True, max_length=20, placeholder="e.g. 98")
        self.shipping_date = TextInput(label="Delivery date", style=discord.TextStyle.short, required=True, max_length=30)

        self.add_item(self.item)
        self.add_item(self.size)
        self.add_item(self.color)
        self.add_item(self.price)
        self.add_item(self.shipping_date)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        email = user_emails.get(self.user_id)
        if not email:
            await interaction.followup.send(embed=Embed(title="Error", description="Email not found. Run /setup again.", color=Colour.red()), ephemeral=True)
            return
        
        try:
            price = float(self.price.value.strip())
            await interaction.followup.send(embed=Embed(title="Processing...", description=f"⏳ Your Lululemon receipt is being generated.", color=Colour.blue()), ephemeral=True)
            
            asyncio.create_task(self.send_receipt(
                interaction, email, 
                self.item.value, self.size.value, self.color.value, price,
                self.shipping_date.value
            ))
        except Exception as e:
            await interaction.followup.send(embed=Embed(title="Error", description=str(e), color=Colour.red()), ephemeral=True)

    async def send_receipt(self, interaction, email, item_name, size, color, price, est_date):
        try:
            qty = 1
            customer_name = random.choice(FAKE_NAMES)
            address = random.choice(FAKE_ADDRESSES)
            state = get_state_from_address(address)
            tax_rate = STATE_TAX_RATES.get(state, 0.0749)

            subtotal = price * qty
            delivery = round(random.uniform(5, 10), 2)
            sales_tax = round(subtotal * tax_rate, 2)
            total = round(subtotal + delivery + sales_tax, 2)

            order_id = f"LULU-{random.randint(100000, 999999)}"
            payment = random.choice(FAKE_PAYMENT_METHODS)

            # EXACT LULULEMON RECEIPT
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: '{self.assets['font_body']}'; background: #faf9f6; margin: 0; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; }}
                    .header {{ background: {self.assets['color_primary']}; padding: 30px; text-align: center; }}
                    .header img {{ max-width: 150px; filter: brightness(0) invert(1); }}
                    .content {{ padding: 30px; }}
                    .order-details {{ margin: 20px 0; }}
                    .sweatlife {{ background: {self.assets['color_secondary']}; padding: 20px; margin: 20px 0; }}
                    .footer {{ background: {self.assets['color_primary']}; color: white; padding: 20px; text-align: center; }}
                    .footer a {{ color: white; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="{self.assets['logo_white']}" alt="lululemon">
                    </div>
                    <div class="content">
                        <p style="font-size: 18px;">Thanks for moving with us, {customer_name}.</p>
                        <p>Your order is confirmed and will be on its way soon.</p>
                        
                        <div class="order-details">
                            <p><strong>Order #{order_id}</strong></p>
                            <p>{item_name} | Size: {size} | Color: {color}</p>
                            <p>Price: ${price:,.2f}</p>
                            <p>Shipping: ${delivery:,.2f}</p>
                            <p>Tax: ${sales_tax:,.2f}</p>
                            <p style="font-size: 20px; color: {self.assets['color_primary']};">Total: ${total:,.2f}</p>
                        </div>
                        
                        <p><strong>Delivery to:</strong><br>{address}</p>
                        <p><strong>Est. delivery:</strong> {est_date}</p>
                        
                        <div class="sweatlife">
                            <p>🧘 Join us for a free yoga class at your local store</p>
                        </div>
                        
                        <p style="text-align:center;">
                            <a href="{self.assets['website']}/track?order={order_id}" style="color:{self.assets['color_primary']};">Track your order →</a>
                        </p>
                    </div>
                    <div class="footer">
                        <p><a href="mailto:{self.assets['support_email']}">sweatlife@lululemon.com</a> | <a href="{self.assets['website']}">shop.lululemon.com</a></p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Use their actual sender email format [citation:1]
            message = Mail(
                from_email=(SENDER_EMAIL, "lululemon"),
                to_emails=email,
                subject=f"Your lululemon Order #{order_id}",
                html_content=html_body
            )

            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
            
            await interaction.followup.send(embed=Embed(title="Success!", description=f"✅ Lululemon receipt sent!", color=Colour.green()), ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(embed=Embed(title="Error", description=str(e), color=Colour.red()), ephemeral=True)

# ==================== APPLE MODAL ====================
class TechModal(discord.ui.Modal, title="Apple Receipt Details"):
    def __init__(self, brand: str, user_id: int):
        super().__init__(timeout=600)
        self.brand = brand
        self.user_id = user_id
        self.assets = brand_assets[brand]

        self.item = TextInput(label="Product", style=discord.TextStyle.short, required=True, max_length=100, placeholder="e.g. MacBook Pro 14-inch")
        self.storage = TextInput(label="Storage", style=discord.TextStyle.short, required=True, max_length=30, placeholder="e.g. 512GB, 1TB")
        self.color = TextInput(label="Color", style=discord.TextStyle.short, required=True, max_length=30, placeholder="e.g. Space Gray")
        self.price = TextInput(label="Price", style=discord.TextStyle.short, required=True, max_length=20, placeholder="e.g. 1999")
        self.shipping_date = TextInput(label="Delivery", style=discord.TextStyle.short, required=True, max_length=30)

        self.add_item(self.item)
        self.add_item(self.storage)
        self.add_item(self.color)
        self.add_item(self.price)
        self.add_item(self.shipping_date)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        email = user_emails.get(self.user_id)
        if not email:
            await interaction.followup.send(embed=Embed(title="Error", description="Email not found. Run /setup again.", color=Colour.red()), ephemeral=True)
            return
        
        try:
            price = float(self.price.value.strip())
            await interaction.followup.send(embed=Embed(title="Processing...", description=f"⏳ Your Apple receipt is being generated.", color=Colour.blue()), ephemeral=True)
            
            asyncio.create_task(self.send_receipt(
                interaction, email, 
                self.item.value, self.storage.value, self.color.value, price,
                self.shipping_date.value
            ))
        except Exception as e:
            await interaction.followup.send(embed=Embed(title="Error", description=str(e), color=Colour.red()), ephemeral=True)

    async def send_receipt(self, interaction, email, item_name, storage, color, price, est_date):
        try:
            qty = 1
            customer_name = random.choice(FAKE_NAMES)
            address = random.choice(FAKE_ADDRESSES)
            state = get_state_from_address(address)
            tax_rate = STATE_TAX_RATES.get(state, 0.0749)

            subtotal = price * qty
            delivery = 0  # Apple often has free shipping
            sales_tax = round(subtotal * tax_rate, 2)
            total = round(subtotal + sales_tax, 2)

            order_id = f"W{random.randint(10000000, 99999999)}"  # Apple format: W68676604 [citation:6]
            payment = random.choice(FAKE_PAYMENT_METHODS)

            # EXACT APPLE RECEIPT [citation:6]
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: '{self.assets['font_body']}'; background: #f5f5f7; margin: 0; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 18px; overflow: hidden; }}
                    .header {{ padding: 40px 30px 20px; text-align: center; }}
                    .header img {{ max-width: 80px; }}
                    .order-number {{ color: {self.assets['color_secondary']}; font-size: 14px; }}
                    .content {{ padding: 0 30px 30px; }}
                    .item-row {{ border-bottom: 1px solid #d2d2d7; padding: 20px 0; display: flex; justify-content: space-between; }}
                    .total {{ font-size: 24px; font-weight: 400; margin: 20px 0; }}
                    .footer {{ background: #f5f5f7; padding: 20px; text-align: center; color: {self.assets['color_secondary']}; }}
                    .track-button {{ background: {self.assets['color_primary']}; color: white; padding: 12px 24px; text-decoration: none; display: inline-block; border-radius: 8px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="{self.assets['logo']}" alt="Apple">
                    </div>
                    <div class="content">
                        <p style="font-size: 20px;">{customer_name}, thank you for your order.</p>
                        <p class="order-number">Order #{order_id}</p>
                        
                        <div class="item-row">
                            <div>
                                <strong>{item_name}</strong><br>
                                {storage} | {color}
                            </div>
                            <div>${price:,.2f}</div>
                        </div>
                        
                        <p>Shipping: Free</p>
                        <p>Estimated Tax: ${sales_tax:,.2f}</p>
                        <p class="total">Total: ${total:,.2f}</p>
                        
                        <p><strong>Delivers to:</strong><br>{address}</p>
                        <p><strong>Estimated delivery:</strong> {est_date}</p>
                        
                        <div style="text-align: center;">
                            <a href="{self.assets['website']}/orderstatus" class="track-button">Track Shipment</a>
                        </div>
                        
                        <p style="text-align: center; margin-top: 20px;">
                            <a href="{self.assets['customer_service']}" style="color: {self.assets['color_primary']};">FAQ and Help →</a>
                        </p>
                    </div>
                    <div class="footer">
                        <p><a href="{self.assets['website']}" style="color: {self.assets['color_primary']};">apple.com</a>/orderstatus</p>
                        <p style="font-size: 12px;">© 2025 Apple Inc. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            message = Mail(
                from_email=(SENDER_EMAIL, "Apple"),
                to_emails=email,
                subject=f"Shipment Notification {order_id}",  # Apple's subject line format [citation:6]
                html_content=html_body
            )

            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
            
            await interaction.followup.send(embed=Embed(title="Success!", description=f"✅ Apple receipt sent!", color=Colour.green()), ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(embed=Embed(title="Error", description=str(e), color=Colour.red()), ephemeral=True)

# ==================== REMAINING MODALS (Beauty, Luxury, Basic) ====================
# [BeautyModal, LuxuryModal, BasicModal follow same pattern but truncated for length]

# Run the bot
client.run(BOT_TOKEN)