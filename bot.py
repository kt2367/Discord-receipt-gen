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

# ==================== BRAND ASSETS (Real logos & links) ====================
BRANDS = [
    'Cartier', 'Denim Tears', 'Ksubi', 'Balenciaga', 'Sp5der',
    'Nike', 'Adidas', 'Lululemon', 'Lanvin', 'Creed',
    'Baccarat', 'Sephora', 'Apple'
]

brand_assets = {
    'Cartier': {
        'name': 'Cartier',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Cartier_logo.svg/512px-Cartier_logo.svg.png',
        'logo_svg': 'https://brandfetch.com/cartier.mx/logo.svg',
        'website': 'https://www.cartier.com',
        'customer_service': 'https://www.cartier.com/customer-service',
        'color_primary': '#8B0000',  # Burgundy
        'color_secondary': '#D4AF37',  # Gold
        'font': 'Georgia, Times New Roman, serif'
    },
    'Denim Tears': {
        'name': 'Denim Tears',
        'logo': 'https://denimtears.co/wp-content/uploads/2024/logo.png',  # Placeholder - use actual when available
        'website': 'https://denimtears.co',
        'customer_service': 'https://denimtears.co/contact',
        'color_primary': '#1A2E3F',  # Dark blue
        'color_secondary': '#C4A962',  # Gold
        'font': 'Arial, Helvetica, sans-serif'
    },
    'Ksubi': {
        'name': 'Ksubi',
        'logo': 'https://brandfetch.com/ksubi.com/logo.png',
        'website': 'https://www.ksubi.com',
        'customer_service': 'https://www.ksubi.com/pages/contact-us',
        'color_primary': '#2C2C2C',  # Dark gray
        'color_secondary': '#8B8B8B',  # Light gray
        'font': 'Arial, Helvetica, sans-serif'
    },
    'Balenciaga': {
        'name': 'Balenciaga',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/8/8f/Balenciaga_logo.svg',
        'website': 'https://www.balenciaga.com',
        'customer_service': 'https://www.balenciaga.com/en-us/customer-service',
        'color_primary': '#000000',
        'color_secondary': '#FFFFFF',
        'font': 'Arial, Helvetica, sans-serif'
    },
    'Sp5der': {
        'name': 'Sp5der',
        'logo': 'https://i.imgur.com/sp5der-logo.png',  # Placeholder - replace with actual
        'website': 'https://sp5der.com',
        'customer_service': 'https://sp5der.com/pages/contact',
        'color_primary': '#D4AF37',  # Gold
        'color_secondary': '#1A1A1A',  # Black
        'font': 'Impact, Arial Black, sans-serif'
    },
    'Nike': {
        'name': 'Nike',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Logo_NIKE.svg/512px-Logo_NIKE.svg.png',
        'logo_svg': 'https://commons.wikimedia.org/wiki/File:Logo_NIKE.svg',
        'website': 'https://www.nike.com',
        'customer_service': 'https://www.nike.com/help',
        'color_primary': '#000000',
        'color_secondary': '#FFFFFF',
        'font': 'Helvetica, Arial, sans-serif'
    },
    'Adidas': {
        'name': 'adidas',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Adidas_Logo.svg/512px-Adidas_Logo.svg.png',
        'website': 'https://www.adidas.com',
        'customer_service': 'https://www.adidas.com/help',
        'color_primary': '#000000',
        'color_secondary': '#00FF00',  # Lime green
        'font': 'Arial, sans-serif'
    },
    'Lululemon': {
        'name': 'lululemon',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Lululemon_logo.svg/512px-Lululemon_logo.svg.png',
        'website': 'https://shop.lululemon.com',
        'customer_service': 'https://shop.lululemon.com/help/contact-us',
        'color_primary': '#4B6E5E',  # Sage green
        'color_secondary': '#F0E9E0',  # Cream
        'font': 'Arial, sans-serif'
    },
    'Lanvin': {
        'name': 'Lanvin',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/5/5f/Lanvin_logo.svg',
        'website': 'https://www.lanvin.com',
        'customer_service': 'https://www.lanvin.com/en-int/customer-service',
        'color_primary': '#0A1A2A',  # Navy
        'color_secondary': '#B89C7A',  # Gold/taupe
        'font': 'Georgia, Times New Roman, serif'
    },
    'Creed': {
        'name': 'Creed',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Creed_logo.svg/512px-Creed_logo.svg.png',
        'website': 'https://www.creedboutique.com',
        'customer_service': 'https://www.creedboutique.com/customer-service',
        'color_primary': '#1E2F4A',  # Navy
        'color_secondary': '#C5B4A3',  # Beige
        'font': 'Georgia, Times New Roman, serif'
    },
    'Baccarat': {
        'name': 'Baccarat',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/0/0f/Baccarat_logo.svg',
        'website': 'https://www.baccarat.com',
        'customer_service': 'https://www.baccarat.com/en_int/customer-service.html',
        'color_primary': '#8B6B4D',  # Brown/gold
        'color_secondary': '#E5D3C1',  # Cream
        'font': 'Georgia, Times New Roman, serif'
    },
    'Sephora': {
        'name': 'Sephora',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Sephora_logo.svg/512px-Sephora_logo.svg.png',
        'website': 'https://www.sephora.com',
        'customer_service': 'https://www.sephora.com/customer-service',
        'color_primary': '#000000',
        'color_secondary': '#FFFFFF',
        'font': 'Arial, sans-serif'
    },
    'Apple': {
        'name': 'Apple',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg',
        'website': 'https://www.apple.com',
        'customer_service': 'https://support.apple.com/contact',
        'color_primary': '#1D1D1F',  # Dark gray
        'color_secondary': '#86868B',  # Light gray
        'font': '-apple-system, BlinkMacSystemFont, sans-serif'
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
            modal = CartierModal(brand, interaction.user.id)  # Jewelry: size, metal color
        elif brand in ["Nike", "Adidas"]:
            modal = SportswearModal(brand, interaction.user.id)  # Shoes/clothing: size, color
        elif brand == "Sephora":
            modal = BeautyModal(brand, interaction.user.id)  # Beauty: shade, size
        elif brand == "Apple":
            modal = TechModal(brand, interaction.user.id)  # Tech: storage, color
        elif brand == "Lululemon":
            modal = AthleisureModal(brand, interaction.user.id)  # Athletic wear: size, inseam
        elif brand in ["Baccarat", "Creed"]:
            modal = FragranceModal(brand, interaction.user.id)  # Fragrance: ml size, concentration
        elif brand in ["Denim Tears", "Ksubi", "Sp5der"]:
            modal = StreetwearModal(brand, interaction.user.id)  # Streetwear: size, fit
        elif brand in ["Balenciaga", "Lanvin"]:
            modal = LuxuryModal(brand, interaction.user.id)  # Luxury fashion: size, color
        else:
            modal = BasicModal(brand, interaction.user.id)  # Default fallback
        
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

# ==================== CARTIER MODAL (Jewelry) ====================
class CartierModal(discord.ui.Modal, title="Cartier Receipt Details"):
    def __init__(self, brand: str, user_id: int):
        super().__init__(timeout=600)
        self.brand = brand
        self.user_id = user_id
        self.assets = brand_assets[brand]

        self.item = TextInput(label="Item name", style=discord.TextStyle.short, required=True, max_length=100, placeholder="e.g. Love Bracelet, Tank Watch")
        self.metal = TextInput(label="Metal/Color", style=discord.TextStyle.short, required=True, max_length=30, placeholder="e.g. Rose Gold, Yellow Gold, Platinum")
        self.size = TextInput(label="Size", style=discord.TextStyle.short, required=True, max_length=20, placeholder="e.g. 52, 54, 56 (for bracelets)")
        self.price = TextInput(label="Price in USD", style=discord.TextStyle.short, required=True, max_length=20, placeholder="e.g. 6500")
        self.shipping_date = TextInput(label="Delivery date", style=discord.TextStyle.short, required=True, max_length=30, placeholder="e.g. March 20, 2025")

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
            
            asyncio.create_task(self.send_cartier_receipt(
                interaction, email, 
                self.item.value, self.metal.value, self.size.value, price,
                self.shipping_date.value
            ))
            
        except Exception as e:
            logger.error(f"Error: {e}")
            await interaction.followup.send(embed=Embed(title="Error", description=str(e), color=Colour.red()), ephemeral=True)
    
    async def send_cartier_receipt(self, interaction, email, item_name, metal, size, price, est_date):
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

            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: '{self.assets['font']}'; background-color: #f5f5f5; margin: 0; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e0d6c6; }}
                    .header {{ background: linear-gradient(135deg, {self.assets['color_primary']} 0%, #4a0000 100%); padding: 40px 20px; text-align: center; }}
                    .header img {{ max-width: 200px; }}
                    .content {{ padding: 40px; }}
                    .order-number {{ background-color: #f8f5f0; padding: 15px; text-align: center; border: 1px solid {self.assets['color_secondary']}; margin: 20px 0; }}
                    .order-number p {{ margin: 0; color: {self.assets['color_primary']}; font-size: 18px; }}
                    .details {{ margin: 30px 0; }}
                    .details table {{ width: 100%; border-collapse: collapse; }}
                    .details td {{ padding: 12px 0; border-bottom: 1px solid #e0d6c6; }}
                    .total {{ font-weight: bold; font-size: 18px; color: {self.assets['color_primary']}; }}
                    .footer {{ border-top: 2px solid {self.assets['color_secondary']}; padding: 30px 0 0; text-align: center; color: #666; font-size: 12px; }}
                    .footer a {{ color: {self.assets['color_primary']}; text-decoration: none; }}
                    .footer a:hover {{ text-decoration: underline; }}
                    .red-box {{ background-color: {self.assets['color_primary']}; color: white; padding: 20px; text-align: center; margin: 30px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="{self.assets['logo']}" alt="{self.brand}" style="max-width: 200px;">
                    </div>
                    <div class="content">
                        <p style="font-size: 20px; color: #333;">Dear {customer_name},</p>
                        <p style="color: #666; line-height: 1.6;">Thank you for your purchase. We are pleased to confirm your order.</p>
                        
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
                            <p style="margin:0; font-size: 16px;">Magic inside every red box</p>
                        </div>
                        
                        <div class="footer">
                            <p>Track your order: <a href="{self.assets['website']}/track/{order_id}">{self.assets['website']}/track</a></p>
                            <p style="margin: 10px 0;">Customer Service: <a href="{self.assets['customer_service']}">Contact Us</a> | <a href="mailto:{self.assets['website'].replace('https://', '')}">support@{self.assets['website'].replace('https://www.', '')}</a></p>
                            <p><a href="{self.assets['website']}">{self.assets['website'].replace('https://', '')}</a></p>
                            <p style="margin-top: 20px;">© Cartier 2025. All rights reserved.</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """

            message = Mail(
                from_email=(SENDER_EMAIL, "Cartier"),
                to_emails=email,
                subject=f"Your Cartier Order Confirmation #{order_id}",
                html_content=html_body
            )

            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
            
            await interaction.followup.send(embed=Embed(title="Success!", description=f"✅ Cartier receipt sent to {email}!", color=Colour.green()), ephemeral=True)
            
        except Exception as e:
            logger.error(f"Email error: {e}")
            await interaction.followup.send(embed=Embed(title="Error", description=f"Failed: {str(e)}", color=Colour.red()), ephemeral=True)

# ==================== SPORTSWEAR MODAL (Nike/Adidas) ====================
class SportswearModal(discord.ui.Modal, title="Sportswear Receipt Details"):
    def __init__(self, brand: str, user_id: int):
        super().__init__(timeout=600)
        self.brand = brand
        self.user_id = user_id
        self.assets = brand_assets[brand]

        self.item = TextInput(label="Item name", style=discord.TextStyle.short, required=True, max_length=100, placeholder="e.g. Air Max 97, Ultraboost")
        self.size = TextInput(label="Size", style=discord.TextStyle.short, required=True, max_length=10, placeholder="e.g. 9, 10.5, M, L, XL")
        self.color = TextInput(label="Color", style=discord.TextStyle.short, required=True, max_length=30, placeholder="e.g. Black/White")
        self.price = TextInput(label="Price in USD", style=discord.TextStyle.short, required=True, max_length=20, placeholder="e.g. 190")
        self.shipping_date = TextInput(label="Delivery date", style=discord.TextStyle.short, required=True, max_length=30, placeholder="e.g. March 20, 2025")

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

            if self.brand == "Nike":
                html_body = f"""
                <!DOCTYPE html>
                <html>
                <head><style>
                    body {{ font-family: '{self.assets['font']}'; background: #f5f5f5; margin: 0; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; }}
                    .header {{ background: {self.assets['color_primary']}; padding: 30px; text-align: center; }}
                    .header img {{ max-width: 100px; filter: brightness(0) invert(1); }}
                    .content {{ padding: 30px; }}
                    .order-box {{ background: #f8f8f8; padding: 20px; margin: 20px 0; border-left: 4px solid {self.assets['color_primary']}; }}
                    .price {{ font-size: 24px; font-weight: bold; }}
                    .footer {{ background: {self.assets['color_primary']}; color: {self.assets['color_secondary']}; padding: 20px; text-align: center; }}
                    .footer a {{ color: {self.assets['color_secondary']}; }}
                </style></head>
                <body>
                    <div class="container">
                        <div class="header">
                            <img src="{self.assets['logo']}" alt="NIKE">
                        </div>
                        <div class="content">
                            <h2>THANKS FOR YOUR ORDER, {customer_name.upper()}!</h2>
                            <p>YOUR GEAR IS ON THE WAY.</p>
                            <div class="order-box">
                                <p><strong>ORDER #{order_id}</strong></p>
                                <p>{item_name}</p>
                                <p>Size: {size} | Color: {color}</p>
                                <p>Price: ${price:,.2f}</p>
                                <p>Shipping: ${delivery:,.2f}</p>
                                <p>Tax: ${sales_tax:,.2f}</p>
                                <p class="price">TOTAL: ${total:,.2f}</p>
                            </div>
                            <p><strong>DELIVERY TO:</strong> {address}</p>
                            <p><strong>EST. DELIVERY:</strong> {est_date}</p>
                            <p><strong>PAYMENT:</strong> {payment}</p>
                            <p style="text-align:center;"><a href="{self.assets['website']}/orders" style="background:{self.assets['color_primary']}; color:{self.assets['color_secondary']}; padding:10px 20px; text-decoration:none;">TRACK ORDER</a></p>
                        </div>
                        <div class="footer">
                            <p>JUST DO IT. | <a href="{self.assets['website']}">nike.com</a> | <a href="{self.assets['customer_service']}">Help</a></p>
                        </div>
                    </div>
                </body>
                </html>
                """
            else:  # ADIDAS
                html_body = f"""
                <!DOCTYPE html>
                <html>
                <head><style>
                    body {{ font-family: '{self.assets['font']}'; background: #fff; margin: 0; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: #fff; border: 1px solid #e5e5e5; }}
                    .header {{ background: {self.assets['color_primary']}; padding: 25px; text-align: center; border-bottom: 3px solid {self.assets['color_secondary']}; }}
                    .header img {{ max-width: 100px; filter: brightness(0) invert(1); }}
                    .stripes {{ height: 3px; background: linear-gradient(90deg, {self.assets['color_primary']} 33%, {self.assets['color_secondary']} 33%, {self.assets['color_secondary']} 66%, {self.assets['color_primary']} 66%); }}
                    .content {{ padding: 30px; }}
                    .order-detail {{ border: 1px solid #ddd; padding: 20px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; }}
                    .footer a {{ color: {self.assets['color_primary']}; }}
                </style></head>
                <body>
                    <div class="container">
                        <div class="header">
                            <img src="{self.assets['logo']}" alt="adidas">
                        </div>
                        <div class="stripes"></div>
                        <div class="content">
                            <p style="font-size: 18px;">Hey {customer_name},</p>
                            <p>Your order is confirmed.</p>
                            <div class="order-detail">
                                <p><strong>ORDER #{order_id}</strong></p>
                                <p>{item_name} | Size: {size} | {color}</p>
                                <p>Subtotal: ${price:,.2f}</p>
                                <p>Shipping: ${delivery:,.2f}</p>
                                <p>Tax: ${sales_tax:,.2f}</p>
                                <p style="font-size:20px;"><strong>TOTAL: ${total:,.2f}</strong></p>
                            </div>
                            <p><strong>Shipping to:</strong> {address}</p>
                            <p><strong>Delivery by:</strong> {est_date}</p>
                            <p><strong>Payment:</strong> {payment}</p>
                            <p style="text-align:center;"><a href="{self.assets['website']}/order-tracking" style="color:{self.assets['color_primary']};">Track Order →</a></p>
                        </div>
                        <div class="footer">
                            <p><a href="{self.assets['website']}">adidas.com</a> | IMPOSSIBLE IS NOTHING | <a href="{self.assets['customer_service']}">Help</a></p>
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

# ==================== BEAUTY MODAL (Sephora) ====================
class BeautyModal(discord.ui.Modal, title="Sephora Receipt Details"):
    def __init__(self, brand: str, user_id: int):
        super().__init__(timeout=600)
        self.brand = brand
        self.user_id = user_id
        self.assets = brand_assets[brand]

        self.item = TextInput(label="Product name", style=discord.TextStyle.short, required=True, max_length=100, placeholder="e.g. Rare Beauty Mascara")
        self.shade = TextInput(label="Shade/Color", style=discord.TextStyle.short, required=True, max_length=30, placeholder="e.g. Black, Perfect Shade")
        self.size = TextInput(label="Size", style=discord.TextStyle.short, required=False, max_length=20, placeholder="e.g. 0.5 oz, full size")
        self.price = TextInput(label="Price in USD", style=discord.TextStyle.short, required=True, max_length=20, placeholder="e.g. 24")
        self.shipping_date = TextInput(label="Delivery date", style=discord.TextStyle.short, required=True, max_length=30)

        self.add_item(self.item)
        self.add_item(self.shade)
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
            await interaction.followup.send(embed=Embed(title="Processing...", description=f"⏳ Your Sephora receipt is being generated.", color=Colour.blue()), ephemeral=True)
            
            asyncio.create_task(self.send_receipt(
                interaction, email, 
                self.item.value, self.shade.value, self.size.value, price,
                self.shipping_date.value
            ))
        except Exception as e:
            await interaction.followup.send(embed=Embed(title="Error", description=str(e), color=Colour.red()), ephemeral=True)

    async def send_receipt(self, interaction, email, item_name, shade, size, price, est_date):
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

            order_id = f"SEP-{random.randint(100000, 999999)}"
            payment = random.choice(FAKE_PAYMENT_METHODS)
            
            beauty_tips = [
                "✨ Try layering with moisturizer for extra glow",
                "💄 Store in a cool, dry place",
                "🧴 Patch test before use",
                "🌸 Apply with a damp sponge for dewy finish",
                "✨ Set with setting spray for all-day wear"
            ]

            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head><style>
                body {{ font-family: '{self.assets['font']}'; background: #fff; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #fff; }}
                .header {{ background: {self.assets['color_primary']}; padding: 30px; text-align: center; }}
                .header img {{ max-width: 150px; filter: brightness(0) invert(1); }}
                .stripes {{ background: repeating-linear-gradient(45deg, {self.assets['color_primary']}, {self.assets['color_primary']} 10px, {self.assets['color_secondary']} 10px, {self.assets['color_secondary']} 20px); height: 10px; }}
                .content {{ padding: 30px; }}
                .beauty-tip {{ background: #f8f8f8; padding: 15px; margin: 20px 0; border-left: 4px solid {self.assets['color_primary']}; }}
                .footer {{ text-align: center; padding: 20px; background: #f8f8f8; }}
                .footer a {{ color: {self.assets['color_primary']}; }}
            </style></head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="{self.assets['logo']}" alt="SEPHORA">
                    </div>
                    <div class="stripes"></div>
                    <div class="content">
                        <h2 style="color: {self.assets['color_primary']};">Hi {customer_name},</h2>
                        <p>Your beauty order is confirmed! Get ready to glow.</p>
                        
                        <div style="border: 1px solid #000; padding: 20px; margin: 20px 0;">
                            <p><strong>ORDER #{order_id}</strong></p>
                            <p>{item_name} - Shade: {shade} {f'| Size: {size}' if size else ''}</p>
                            <p>Price: ${price:,.2f}</p>
                            <p>Shipping: ${delivery:,.2f}</p>
                            <p>Tax: ${sales_tax:,.2f}</p>
                            <p style="font-size:20px;"><strong>TOTAL: ${total:,.2f}</strong></p>
                        </div>
                        
                        <div class="beauty-tip">
                            <p>{random.choice(beauty_tips)}</p>
                        </div>
                        
                        <p><strong>Shipping to:</strong><br>{address}</p>
                        <p><strong>Arrives:</strong> {est_date}</p>
                        <p><strong>Payment:</strong> {payment}</p>
                    </div>
                    <div class="footer">
                        <p>Track: <a href="{self.assets['website']}/orderstatus">sephora.com/orderstatus</a></p>
                        <p>BEAUTY INSIDER | <a href="{self.assets['website']}">sephora.com</a> | <a href="{self.assets['customer_service']}">Help</a></p>
                    </div>
                </div>
            </body>
            </html>
            """

            message = Mail(
                from_email=(SENDER_EMAIL, "Sephora"),
                to_emails=email,
                subject=f"Your Sephora Order #{order_id}",
                html_content=html_body
            )

            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
            
            await interaction.followup.send(embed=Embed(title="Success!", description=f"✅ Sephora receipt sent!", color=Colour.green()), ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(embed=Embed(title="Error", description=str(e), color=Colour.red()), ephemeral=True)

# ==================== TECH MODAL (Apple) ====================
class TechModal(discord.ui.Modal, title="Apple Receipt Details"):
    def __init__(self, brand: str, user_id: int):
        super().__init__(timeout=600)
        self.brand = brand
        self.user_id = user_id
        self.assets = brand_assets[brand]

        self.item = TextInput(label="Product name", style=discord.TextStyle.short, required=True, max_length=100, placeholder="e.g. MacBook Pro 14-inch")
        self.storage = TextInput(label="Storage", style=discord.TextStyle.short, required=True, max_length=30, placeholder="e.g. 512GB, 1TB")
        self.color = TextInput(label="Color", style=discord.TextStyle.short, required=True, max_length=30, placeholder="e.g. Space Gray, Silver")
        self.price = TextInput(label="Price in USD", style=discord.TextStyle.short, required=True, max_length=20, placeholder="e.g. 1999")
        self.shipping_date = TextInput(label="Delivery date", style=discord.TextStyle.short, required=True, max_length=30)

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

            order_id = f"APL-{random.randint(100000, 999999)}"
            payment = random.choice(FAKE_PAYMENT_METHODS)

            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head><style>
                body {{ font-family: '{self.assets['font']}'; background: #f5f5f7; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 18px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                .header {{ padding: 40px 30px 20px; text-align: center; }}
                .header img {{ max-width: 80px; }}
                .content {{ padding: 0 30px 30px; }}
                .order-item {{ border-bottom: 1px solid #d2d2d7; padding: 20px 0; }}
                .total {{ font-size: 24px; font-weight: 400; margin: 20px 0; color: {self.assets['color_primary']}; }}
                .footer {{ background: #f5f5f7; padding: 20px; text-align: center; color: {self.assets['color_secondary']}; }}
                .footer a {{ color: {self.assets['color_primary']}; text-decoration: none; }}
            </style></head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="{self.assets['logo']}" alt="Apple">
                    </div>
                    <div class="content">
                        <p style="font-size: 20px;">{customer_name}, thank you for your order.</p>
                        <p style="color: {self.assets['color_secondary']};">Order #{order_id}</p>
                        
                        <div class="order-item">
                            <p style="font-size: 18px;">{item_name}</p>
                            <p style="color: {self.assets['color_secondary']};">{storage} | {color}</p>
                            <p style="text-align: right;">${price:,.2f}</p>
                        </div>
                        
                        <p>Shipping: Free</p>
                        <p>Tax: ${sales_tax:,.2f}</p>
                        <p class="total">Total: ${total:,.2f}</p>
                        
                        <p><strong>Delivers to:</strong><br>{address}</p>
                        <p><strong>Estimated delivery:</strong> {est_date}</p>
                        <p><strong>Payment:</strong> {payment}</p>
                        
                        <p style="text-align: center;">
                            <a href="{self.assets['website']}/orderstatus" style="color:{self.assets['color_primary']};">Track your order →</a>
                        </p>
                    </div>
                    <div class="footer">
                        <p><a href="{self.assets['website']}">apple.com</a>/orderstatus</p>
                        <p style="font-size: 12px;"><a href="{self.assets['customer_service']}">Contact Support</a></p>
                        <p style="font-size: 10px;">© 2025 Apple Inc. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            message = Mail(
                from_email=(SENDER_EMAIL, "Apple"),
                to_emails=email,
                subject=f"Your Apple Order #{order_id}",
                html_content=html_body
            )

            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
            
            await interaction.followup.send(embed=Embed(title="Success!", description=f"✅ Apple receipt sent!", color=Colour.green()), ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(embed=Embed(title="Error", description=str(e), color=Colour.red()), ephemeral=True)

# ==================== ATHLEISURE MODAL (Lululemon) ====================
class AthleisureModal(discord.ui.Modal, title="Lululemon Receipt Details"):
    def __init__(self, brand: str, user_id: int):
        super().__init__(timeout=600)
        self.brand = brand
        self.user_id = user_id
        self.assets = brand_assets[brand]

        self.item = TextInput(label="Item name", style=discord.TextStyle.short, required=True, max_length=100, placeholder="e.g. Align Leggings, Define Jacket")
        self.size = TextInput(label="Size", style=discord.TextStyle.short, required=True, max_length=10, placeholder="e.g. 2, 4, 6, 8, 10")
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

            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head><style>
                body {{ font-family: '{self.assets['font']}'; background: #faf9f6; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; }}
                .header {{ background: {self.assets['color_primary']}; padding: 30px; text-align: center; }}
                .header img {{ max-width: 150px; filter: brightness(0) invert(1); }}
                .content {{ padding: 30px; }}
                .sweatlife {{ background: {self.assets['color_secondary']}; padding: 20px; margin: 20px 0; }}
                .footer {{ background: {self.assets['color_primary']}; color: white; padding: 20px; text-align: center; }}
                .footer a {{ color: white; }}
            </style></head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="{self.assets['logo']}" alt="lululemon">
                    </div>
                    <div class="content">
                        <p style="font-size: 18px;">Thanks for moving with us, {customer_name}.</p>
                        
                        <div style="margin: 30px 0;">
                            <p><strong>Order #{order_id}</strong></p>
                            <p>{item_name} | Size: {size} | Color: {color}</p>
                            <p>Price: ${price:,.2f}</p>
                            <p>Shipping: ${delivery:,.2f}</p>
                            <p>Tax: ${sales_tax:,.2f}</p>
                            <p style="font-size: 20px; color: {self.assets['color_primary']};">Total: ${total:,.2f}</p>
                        </div>
                        
                        <div class="sweatlife">
                            <p>🧘 Join us for a free yoga class at your local store</p>
                        </div>
                        
                        <p><strong>Delivery to:</strong><br>{address}</p>
                        <p><strong>Est. delivery:</strong> {est_date}</p>
                        <p><strong>Payment:</strong> {payment}</p>
                    </div>
                    <div class="footer">
                        <p><a href="mailto:{self.assets['customer_service'].replace('https://', '')}">sweatlife@lululemon.com</a> | <a href="{self.assets['website']}">shop.lululemon.com</a></p>
                    </div>
                </div>
            </body>
            </html>
            """

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

# ==================== FRAGRANCE MODAL (Baccarat/Creed) ====================
class FragranceModal(discord.ui.Modal, title="Fragrance Receipt Details"):
    def __init__(self, brand: str, user_id: int):
        super().__init__(timeout=600)
        self.brand = brand
        self.user_id = user_id
        self.assets = brand_assets[brand]

        self.item = TextInput(label="Fragrance name", style=discord.TextStyle.short, required=True, max_length=100, placeholder="e.g. Baccarat Rouge 540, Aventus")
        self.size = TextInput(label="Size (ml)", style=discord.TextStyle.short, required=True, max_length=20, placeholder="e.g. 70ml, 100ml, 200ml")
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
            delivery = round(random.uniform(10, 20), 2)
            sales_tax = round(subtotal * tax_rate, 2)
            total = round(subtotal + delivery + sales_tax, 2)

            order_id = f"{self.brand[:3].upper()}-{random.randint(100000, 999999)}"
            payment = random.choice(FAKE_PAYMENT_METHODS)

            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head><style>
                body {{ font-family: '{self.assets['font']}'; background: #f8f8f8; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border: 1px solid #ddd; }}
                .header {{ background: {self.assets['color_primary']}; padding: 30px; text-align: center; }}
                .header img {{ max-width: 150px; filter: brightness(0) invert(1); }}
                .content {{ padding: 30px; }}
                .footer {{ border-top: 1px solid {self.assets['color_primary']}; padding: 20px; text-align: center; color: #666; }}
                .footer a {{ color: {self.assets['color_primary']}; }}
            </style></head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="{self.assets['logo']}" alt="{self.brand}">
                    </div>
                    <div class="content">
                        <p style="font-size: 18px;">Dear {customer_name},</p>
                        <p>Thank you for your fragrance order.</p>
                        
                        <div style="margin: 30px 0; padding: 20px; background: #f9f9f9;">
                            <p><strong>Order #{order_id}</strong></p>
                            <p>{item_name}</p>
                            <p>Size: {size} | {concentration}</p>
                            <p>Price: ${price:,.2f}</p>
                            <p>Shipping: ${delivery:,.2f}</p>
                            <p>Tax: ${sales_tax:,.2f}</p>
                            <p style="font-size: 20px;"><strong>Total: ${total:,.2f}</strong></p>
                        </div>
                        
                        <p><strong>Shipping to:</strong><br>{address}</p>
                        <p><strong>Estimated delivery:</strong> {est_date}</p>
                        <p><strong>Payment:</strong> {payment}</p>
                    </div>
                    <div class="footer">
                        <p><a href="{self.assets['website']}">{self.assets['website'].replace('https://', '')}</a> | <a href="{self.assets['customer_service']}">Customer Service</a></p>
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

# ==================== STREETWEAR MODAL (Denim Tears/Ksubi/Sp5der) ====================
class StreetwearModal(discord.ui.Modal, title="Streetwear Receipt Details"):
    def __init__(self, brand: str, user_id: int):
        super().__init__(timeout=600)
        self.brand = brand
        self.user_id = user_id
        self.assets = brand_assets[brand]

        self.item = TextInput(label="Item name", style=discord.TextStyle.short, required=True, max_length=100, placeholder="e.g. Hoodie, Jeans, Shorts")
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

            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head><style>
                body {{ font-family: '{self.assets['font']}'; background: #f5f5f5; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; }}
                .header {{ background: {self.assets['color_primary']}; padding: 30px; text-align: center; }}
                .header img {{ max-width: 150px; }}
                .content {{ padding: 30px; }}
                .order-box {{ border: 2px solid {self.assets['color_primary']}; padding: 20px; margin: 20px 0; }}
                .footer {{ background: #111; color: white; padding: 20px; text-align: center; }}
                .footer a {{ color: {self.assets['color_primary']}; }}
            </style></head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="{self.assets['logo']}" alt="{self.brand}" style="max-width: 150px;">
                    </div>
                    <div class="content">
                        <h2>ORDER CONFIRMED</h2>
                        <p>Thanks {customer_name}</p>
                        
                        <div class="order-box">
                            <p><strong>Order #{order_id}</strong></p>
                            <p>{item_name}</p>
                            <p>Size: {size} | Color: {color}</p>
                            <p>Subtotal: ${price:,.2f}</p>
                            <p>Shipping: ${delivery:,.2f}</p>
                            <p>Tax: ${sales_tax:,.2f}</p>
                            <p style="font-size: 24px;"><strong>Total: ${total:,.2f}</strong></p>
                        </div>
                        
                        <p><strong>Shipping to:</strong><br>{address}</p>
                        <p><strong>Delivery by:</strong> {est_date}</p>
                    </div>
                    <div class="footer">
                        <p><a href="{self.assets['website']}">shop</a> | <a href="{self.assets['customer_service']}">contact</a></p>
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

# ==================== LUXURY FASHION MODAL (Balenciaga/Lanvin) ====================
class LuxuryModal(discord.ui.Modal, title="Luxury Fashion Receipt Details"):
    def __init__(self, brand: str, user_id: int):
        super().__init__(timeout=600)
        self.brand = brand
        self.user_id = user_id
        self.assets = brand_assets[brand]

        self.item = TextInput(label="Item name", style=discord.TextStyle.short, required=True, max_length=100, placeholder="e.g. Dress, Suit, Bag")
        self.size = TextInput(label="Size", style=discord.TextStyle.short, required=True, max_length=10, placeholder="e.g. 38, 40, S, M")
        self.color = TextInput(label="Color", style=discord.TextStyle.short, required=True, max_length=30, placeholder="e.g. Black, Navy")
        self.price = TextInput(label="Price in USD", style=discord.TextStyle.short, required=True, max_length=20, placeholder="e.g. 2150")
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
            delivery = round(random.uniform(25, 40), 2)  # Luxury shipping
            sales_tax = round(subtotal * tax_rate, 2)
            total = round(subtotal + delivery + sales_tax, 2)

            order_id = f"{self.brand[:3].upper()}-{random.randint(100000, 999999)}"
            payment = random.choice(FAKE_PAYMENT_METHODS)

            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head><style>
                body {{ font-family: '{self.assets['font']}'; background: #f8f8f8; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border: 1px solid #ddd; }}
                .header {{ background: {self.assets['color_primary']}; padding: 40px; text-align: center; }}
                .header img {{ max-width: 180px; filter: brightness(0) invert(1); }}
                .content {{ padding: 40px; }}
                .details {{ border-top: 1px solid {self.assets['color_secondary']}; border-bottom: 1px solid {self.assets['color_secondary']}; padding: 20px 0; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 30px; background: #f8f8f8; }}
                .footer a {{ color: {self.assets['color_primary']}; }}
            </style></head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="{self.assets['logo']}" alt="{self.brand}">
                    </div>
                    <div class="content">
                        <p>Dear {customer_name},</p>
                        <p>Thank you for your order from {self.brand}.</p>
                        
                        <div class="details">
                            <p style="font-size: 18px;"><strong>Order #{order_id}</strong></p>
                            <p>{item_name}</p>
                            <p>Size: {size} | Color: {color}</p>
                            <p>Price: ${price:,.2f}</p>
                            <p>Shipping: ${delivery:,.2f}</p>
                            <p>Tax: ${sales_tax:,.2f}</p>
                            <p style="font-size: 20px;"><strong>Total: ${total:,.2f}</strong></p>
                        </div>
                        
                        <p><strong>Delivery Address:</strong><br>{address}</p>
                        <p><strong>Estimated Delivery:</strong> {est_date}</p>
                    </div>
                    <div class="footer">
                        <p><a href="{self.assets['website']}">{self.assets['website'].replace('https://', '')}</a> | <a href="{self.assets['customer_service']}">Client Services</a></p>
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

# ==================== BASIC MODAL (Fallback) ====================
class BasicModal(discord.ui.Modal, title="Receipt Details"):
    def __init__(self, brand: str, user_id: int):
        super().__init__(timeout=600)
        self.brand = brand
        self.user_id = user_id
        self.assets = brand_assets.get(brand, {
            'logo': '',
            'website': '#',
            'customer_service': '#',
            'color_primary': '#000000',
            'color_secondary': '#FFFFFF',
            'font': 'Arial, sans-serif'
        })

        self.item = TextInput(label="Item name", style=discord.TextStyle.short, required=True, max_length=100)
        self.price = TextInput(label="Price in USD", style=discord.TextStyle.short, required=True, max_length=20)
        self.shipping_date = TextInput(label="Estimated delivery date", style=discord.TextStyle.short, required=True, max_length=30)

        self.add_item(self.item)
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
            await interaction.followup.send(embed=Embed(title="Processing...", description=f"⏳ Your receipt is being generated.", color=Colour.blue()), ephemeral=True)
            
            asyncio.create_task(self.send_receipt(
                interaction, email, 
                self.item.value, price,
                self.shipping_date.value
            ))
        except Exception as e:
            await interaction.followup.send(embed=Embed(title="Error", description=str(e), color=Colour.red()), ephemeral=True)

    async def send_receipt(self, interaction, email, item_name, price, est_date):
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

            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; }}
                    .header {{ background: {self.assets['color_primary']}; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .footer {{ background: #f5f5f5; padding: 15px; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>{self.brand}</h1>
                    </div>
                    <div class="content">
                        <h2>Order Confirmation</h2>
                        <p>Thank you for your order, {customer_name}!</p>
                        
                        <p><strong>Order #:</strong> {order_id}</p>
                        <p><strong>Item:</strong> {item_name}</p>
                        <p><strong>Price:</strong> ${price:,.2f}</p>
                        <p><strong>Shipping:</strong> ${delivery:,.2f}</p>
                        <p><strong>Tax:</strong> ${sales_tax:,.2f}</p>
                        <p><strong>Total:</strong> ${total:,.2f}</p>
                        
                        <p><strong>Shipping to:</strong><br>{address}</p>
                        <p><strong>Estimated delivery:</strong> {est_date}</p>
                    </div>
                    <div class="footer">
                        <p><a href="{self.assets['website']}">Visit our website</a> | <a href="{self.assets['customer_service']}">Contact Us</a></p>
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

# Run the bot
client.run(BOT_TOKEN)