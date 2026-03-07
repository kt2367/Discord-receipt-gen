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

# ==================== BRAND DATA ====================
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
    'Lululemon': "lululemon",
    'Lanvin': "Lanvin",
    'Creed': "Creed",
    'Baccarat': "Baccarat",
    'Sephora': "Sephora",
    'Apple': "Apple",
}

# Brand websites for footer links
brand_websites = {
    'Cartier': "www.cartier.com",
    'Denim Tears': "www.denimtears.com",
    'Ksubi': "www.ksubi.com",
    'Balenciaga': "www.balenciaga.com",
    'Sp5der': "www.sp5der.com",
    'Nike': "www.nike.com",
    'Adidas': "www.adidas.com",
    'Lululemon': "shop.lululemon.com",
    'Lanvin': "www.lanvin.com",
    'Creed': "www.creedboutique.com",
    'Baccarat': "www.baccarat.com",
    'Sephora': "www.sephora.com",
    'Apple': "www.apple.com",
}

# Brand customer service emails
brand_support = {
    'Cartier': "contact@cartier.com",
    'Denim Tears': "support@denimtears.com",
    'Ksubi': "help@ksubi.com",
    'Balenciaga': "customer.service@balenciaga.com",
    'Sp5der': "support@sp5der.com",
    'Nike': "service@nike.com",
    'Adidas': "customer.service@adidas.com",
    'Lululemon': "gea@lululemon.com",
    'Lanvin': "customer.service@lanvin.com",
    'Creed': "info@creedboutique.com",
    'Baccarat': "contact@baccarat.com",
    'Sephora': "customerservice@sephora.com",
    'Apple': "orderstatus@apple.com",
}

# Brand colors for headers
brand_colors = {
    'Cartier': '#8B0000',
    'Denim Tears': '#1A2E3F',
    'Ksubi': '#2C2C2C',
    'Balenciaga': '#000000',
    'Sp5der': '#D4AF37',
    'Nike': '#000000',
    'Adidas': '#000000',
    'Lululemon': '#4B6E5E',
    'Lanvin': '#0A1A2A',
    'Creed': '#1E2F4A',
    'Baccarat': '#8B6B4D',
    'Sephora': '#000000',
    'Apple': '#1D1D1F',
}

# Brand secondary colors
brand_secondary = {
    'Cartier': '#D4AF37',
    'Denim Tears': '#C4A962',
    'Ksubi': '#8B8B8B',
    'Balenciaga': '#FFFFFF',
    'Sp5der': '#1A1A1A',
    'Nike': '#FFFFFF',
    'Adidas': '#00FF00',
    'Lululemon': '#F0E9E0',
    'Lanvin': '#B89C7A',
    'Creed': '#C5B4A3',
    'Baccarat': '#E5D3C1',
    'Sephora': '#FFFFFF',
    'Apple': '#86868B',
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
    await interaction.response.send_message(f"Added role to {user.mention} for {duration}.", ephemeral=True)
    
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
            options.append(discord.SelectOption(label=brand, value=brand))
        
        super().__init__(placeholder="Choose a brand...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your menu!", ephemeral=True)
            return
        
        brand = self.values[0]
        
        if interaction.user.id not in user_emails:
            await interaction.response.send_message(embed=Embed(title="No Email", description="Run /setup first to save your email!", color=Colour.red()), ephemeral=True)
            return
        
        if brand == "Cartier":
            modal = CartierModal(brand, interaction.user.id)
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

        self.item = TextInput(label="Item name", style=discord.TextStyle.short, required=True, max_length=100, placeholder="e.g. Love Bracelet")
        self.price = TextInput(label="Price per unit in USD", style=discord.TextStyle.short, required=True, max_length=20, placeholder="e.g. 6500")
        self.color = TextInput(label="Color", style=discord.TextStyle.short, required=True, max_length=20, placeholder="e.g. Rose Gold")
        self.size = TextInput(label="Size", style=discord.TextStyle.short, required=True, max_length=10, placeholder="e.g. 52")
        self.shipping_date = TextInput(label="Estimated delivery date", style=discord.TextStyle.short, required=True, max_length=30, placeholder="e.g. March 15, 2025")

        self.add_item(self.item)
        self.add_item(self.price)
        self.add_item(self.color)
        self.add_item(self.size)
        self.add_item(self.shipping_date)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        email = user_emails.get(self.user_id)
        if not email:
            await interaction.followup.send(embed=Embed(title="Error", description="Email not found. Run /setup again.", color=Colour.red()), ephemeral=True)
            return
        
        try:
            price = float(self.price.value.strip())
            await self.send_cartier_receipt(interaction, email, 
                                           self.item.value, price, 
                                           self.color.value, self.size.value, 
                                           self.shipping_date.value)
        except Exception as e:
            logger.error(f"Error: {e}")
            await interaction.followup.send(embed=Embed(title="Error", description=str(e), color=Colour.red()), ephemeral=True)
    
    async def send_cartier_receipt(self, interaction, email, item_name, price, color, size, est_date):
        qty = 1
        customer_name = random.choice(FAKE_NAMES)
        address = random.choice(FAKE_ADDRESSES)
        state = get_state_from_address(address)
        tax_rate = STATE_TAX_RATES.get(state, 0.0749)

        subtotal = price * qty
        base_shipping = random.uniform(25, 45)
        delivery = round(base_shipping, 2)
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
                body {{ font-family: 'Georgia', 'Times New Roman', serif; background-color: #f5f5f5; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e0d6c6; }}
                .header {{ background: linear-gradient(135deg, #8B0000 0%, #4a0000 100%); padding: 40px 20px; text-align: center; }}
                .header h1 {{ color: #ffffff; margin: 0; font-size: 48px; font-weight: 300; letter-spacing: 8px; font-family: 'Times New Roman', serif; }}
                .content {{ padding: 40px; }}
                .order-number {{ background-color: #f8f5f0; padding: 15px; text-align: center; border: 1px solid #d4b68a; margin: 20px 0; }}
                .order-number p {{ margin: 0; color: #8B0000; font-size: 18px; }}
                .details {{ margin: 30px 0; }}
                .details table {{ width: 100%; border-collapse: collapse; }}
                .details td {{ padding: 12px 0; border-bottom: 1px solid #e0d6c6; }}
                .total {{ font-weight: bold; font-size: 18px; color: #8B0000; }}
                .footer {{ border-top: 2px solid #d4b68a; padding: 30px 0 0; text-align: center; color: #666; font-size: 12px; }}
                a {{ color: #8B0000; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>CARTIER</h1>
                </div>
                <div class="content">
                    <p style="font-size: 24px; color: #333; margin: 0 0 10px;">Dear {customer_name},</p>
                    <p style="color: #666; line-height: 1.6;">Thank you for your purchase. We are pleased to confirm your order.</p>
                    
                    <div class="order-number">
                        <p>ORDER #{order_id}</p>
                    </div>
                    
                    <div class="details">
                        <table>
                            <tr>
                                <td><strong>Item:</strong> {item_name}</td>
                                <td style="text-align: right;">${price:,.2f}</td>
                            </tr>
                            <tr>
                                <td><strong>Color:</strong> {color}</td>
                                <td style="text-align: right;"></td>
                            </tr>
                            <tr>
                                <td><strong>Size:</strong> {size}</td>
                                <td style="text-align: right;"></td>
                            </tr>
                            <tr>
                                <td><strong>Quantity:</strong> {qty}</td>
                                <td style="text-align: right;"></td>
                            </tr>
                            <tr>
                                <td><strong>Shipping:</strong></td>
                                <td style="text-align: right;">${delivery:,.2f}</td>
                            </tr>
                            <tr>
                                <td><strong>Tax:</strong></td>
                                <td style="text-align: right;">${sales_tax:,.2f}</td>
                            </tr>
                            <tr class="total">
                                <td><strong>TOTAL:</strong></td>
                                <td style="text-align: right;">${total:,.2f}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="margin: 30px 0; padding: 20px; background-color: #faf8f5;">
                        <p><strong>Delivery Address:</strong><br>{address}</p>
                        <p><strong>Estimated Delivery:</strong><br>{est_date}</p>
                        <p><strong>Payment Method:</strong><br>{payment}</p>
                    </div>
                    
                    <div class="footer">
                        <p>Track your order: <a href="#">cartier.com/track/{order_id}</a></p>
                        <p style="margin: 10px 0;">Customer Service: +33 1 42 18 33 33 | {brand_support['Cartier']}</p>
                        <p>{brand_websites['Cartier']}</p>
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
            subject=f"Order Confirmation #{order_id}",
            html_content=html_body
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        await interaction.followup.send(embed=Embed(title="Success!", description=f"Cartier receipt sent to {email}!", color=Colour.green()), ephemeral=True)

# ==================== BASIC MODAL ====================
class BasicModal(discord.ui.Modal, title="Receipt Details"):
    def __init__(self, brand: str, user_id: int):
        super().__init__(timeout=600)
        self.brand = brand
        self.user_id = user_id

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
            
            # Generate data
            qty = 1
            customer_name = random.choice(FAKE_NAMES)
            address = random.choice(FAKE_ADDRESSES)
            state = get_state_from_address(address)
            tax_rate = STATE_TAX_RATES.get(state, 0.0749)

            subtotal = price * qty
            delivery = round(random.uniform(8, 18), 2)
            sales_tax = round(subtotal * tax_rate, 2)
            total = round(subtotal + delivery + sales_tax, 2)

            order_id = f"{self.brand.upper()[:3]}-{random.randint(100000, 999999)}"
            payment = random.choice(FAKE_PAYMENT_METHODS)

            # Brand-specific HTML templates
            html_body = self.get_brand_html(
                self.brand, customer_name, order_id, 
                self.item.value, price, qty, delivery, sales_tax, total,
                address, self.shipping_date.value, payment
            )

            message = Mail(
                from_email=(SENDER_EMAIL, brand_display.get(self.brand, self.brand)),
                to_emails=email,
                subject=f"Your {self.brand} Order #{order_id}",
                html_content=html_body
            )

            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
            
            await interaction.followup.send(embed=Embed(title="Success!", description=f"{self.brand} receipt sent to {email}!", color=Colour.green()), ephemeral=True)

        except Exception as e:
            logger.error(f"Error: {e}")
            await interaction.followup.send(embed=Embed(title="Error", description=str(e), color=Colour.red()), ephemeral=True)

    def get_brand_html(self, brand, customer_name, order_id, item_name, price, qty, delivery, tax, total, address, est_date, payment):
        
        # Get brand colors
        primary = brand_colors.get(brand, '#000000')
        secondary = brand_secondary.get(brand, '#FFFFFF')
        website = brand_websites.get(brand, 'www.example.com')
        support = brand_support.get(brand, 'support@example.com')
        
        # NIKE
        if brand == "Nike":
            return f"""
            <!DOCTYPE html>
            <html>
            <head><style>
                body {{ font-family: 'Helvetica', 'Arial', sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; }}
                .header {{ background: {primary}; padding: 30px; text-align: center; }}
                .header h1 {{ color: {secondary}; margin: 0; font-size: 42px; font-weight: 800; letter-spacing: 2px; }}
                .content {{ padding: 30px; }}
                .order-box {{ background: #f8f8f8; padding: 20px; margin: 20px 0; border-left: 4px solid {primary}; }}
                .price {{ font-size: 24px; font-weight: bold; color: {primary}; }}
                .footer {{ background: {primary}; color: {secondary}; padding: 20px; text-align: center; }}
                a {{ color: {secondary}; }}
                .track-link {{ background: {primary}; color: {secondary}; padding: 12px 24px; text-decoration: none; display: inline-block; margin: 20px 0; }}
            </style></head>
            <body>
                <div class="container">
                    <div class="header"><h1>NIKE</h1></div>
                    <div class="content">
                        <h2>THANKS FOR YOUR ORDER, {customer_name.upper()}!</h2>
                        <p>YOUR GEAR IS ON THE WAY.</p>
                        <div class="order-box">
                            <p><strong>ORDER #{order_id}</strong></p>
                            <p>{item_name} x{qty} - ${price:,.2f}</p>
                            <p>Shipping: ${delivery:,.2f}</p>
                            <p>Tax: ${tax:,.2f}</p>
                            <p class="price">TOTAL: ${total:,.2f}</p>
                        </div>
                        <p><strong>DELIVERY TO:</strong> {address}</p>
                        <p><strong>EST. DELIVERY:</strong> {est_date}</p>
                        <p><strong>PAYMENT:</strong> {payment}</p>
                        <a href="#" class="track-link">TRACK ORDER</a>
                    </div>
                    <div class="footer">
                        <p>JUST DO IT. | nike.com/orders</p>
                        <p style="font-size: 12px;">{support} | {website}</p>
                    </div>
                </div>
            </body>
            </html>
            """
        
        # ADIDAS
        elif brand == "Adidas":
            return f"""
            <!DOCTYPE html>
            <html>
            <head><style>
                body {{ font-family: 'Arial', sans-serif; background: #fff; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #fff; border: 1px solid #e5e5e5; }}
                .header {{ background: {primary}; padding: 25px; text-align: center; border-bottom: 3px solid {secondary}; }}
                .header h1 {{ color: {secondary}; margin: 0; font-size: 36px; font-weight: 600; }}
                .content {{ padding: 30px; }}
                .stripes {{ height: 3px; background: linear-gradient(90deg, {primary} 33%, {secondary} 33%, {secondary} 66%, {primary} 66%); }}
                .order-detail {{ border: 1px solid #ddd; padding: 20px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; border-top: 1px solid #e5e5e5; }}
                .total {{ font-size: 20px; font-weight: bold; color: {primary}; }}
            </style></head>
            <body>
                <div class="container">
                    <div class="header"><h1>adidas</h1></div>
                    <div class="stripes"></div>
                    <div class="content">
                        <p style="font-size: 18px;">Hey {customer_name},</p>
                        <p>Your order is confirmed and being prepared.</p>
                        <div class="order-detail">
                            <p style="font-size: 14px; color: #666;">ORDER #{order_id}</p>
                            <p><strong>{item_name}</strong> | ${price:,.2f}</p>
                            <p>Subtotal: ${price * qty:,.2f}</p>
                            <p>Shipping: ${delivery:,.2f}</p>
                            <p>Tax: ${tax:,.2f}</p>
                            <p class="total">TOTAL: ${total:,.2f}</p>
                        </div>
                        <p><strong>Shipping to:</strong> {address}</p>
                        <p><strong>Delivery by:</strong> {est_date}</p>
                        <p><strong>Payment:</strong> {payment}</p>
                    </div>
                    <div class="footer">
                        <p>{website} | IMPOSSIBLE IS NOTHING</p>
                        <p style="font-size: 12px;">Need help? {support}</p>
                    </div>
                </div>
            </body>
            </html>
            """
        
        # APPLE
        elif brand == "Apple":
            return f"""
            <!DOCTYPE html>
            <html>
            <head><style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f7; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 18px; overflow: hidden; }}
                .header {{ padding: 40px 30px 20px; text-align: center; }}
                .header h1 {{ color: {primary}; font-size: 32px; font-weight: 500; }}
                .content {{ padding: 0 30px 30px; }}
                .order-item {{ border-bottom: 1px solid #d2d2d7; padding: 20px 0; }}
                .total {{ font-size: 24px; font-weight: 400; margin: 20px 0; color: {primary}; }}
                .footer {{ background: #f5f5f7; padding: 20px; text-align: center; color: {secondary}; }}
                .track-link {{ color: {primary}; text-decoration: none; }}
            </style></head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Apple</h1>
                    </div>
                    <div class="content">
                        <p style="font-size: 20px;">{customer_name}, thank you for your order.</p>
                        <p style="color: {secondary};">Order #{order_id}</p>
                        
                        <div class="order-item">
                            <p style="font-size: 18px;">{item_name}</p>
                            <p style="color: {secondary};">Qty: {qty}</p>
                            <p style="text-align: right;">${price:,.2f}</p>
                        </div>
                        
                        <p>Shipping: ${delivery:,.2f}</p>
                        <p>Tax: ${tax:,.2f}</p>
                        <p class="total">Total: ${total:,.2f}</p>
                        
                        <p><strong>Delivers to:</strong><br>{address}</p>
                        <p><strong>Estimated delivery:</strong> {est_date}</p>
                        <p><strong>Payment:</strong> {payment}</p>
                        
                        <p style="text-align: center;">
                            <a href="#" class="track-link">Track your order →</a>
                        </p>
                    </div>
                    <div class="footer">
                        <p>{website}/orderstatus</p>
                        <p style="font-size: 12px;">{support}</p>
                        <p style="font-size: 10px;">© 2025 Apple Inc. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
        
        # SEPHORA
        elif brand == "Sephora":
            return f"""
            <!DOCTYPE html>
            <html>
            <head><style>
                body {{ font-family: 'Arial', sans-serif; background: #fff; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #fff; }}
                .header {{ background: {primary}; padding: 30px; text-align: center; }}
                .header h1 {{ color: {secondary}; margin: 0; font-size: 36px; letter-spacing: 2px; }}
                .stripes {{ background: repeating-linear-gradient(45deg, {primary}, {primary} 10px, {secondary} 10px, {secondary} 20px); height: 10px; }}
                .content {{ padding: 30px; }}
                .beauty-tip {{ background: #f8f8f8; padding: 15px; margin: 20px 0; border-left: 4px solid {primary}; }}
                .footer {{ text-align: center; padding: 20px; background: #f8f8f8; }}
                .price {{ font-weight: bold; color: {primary}; }}
            </style></head>
            <body>
                <div class="container">
                    <div class="header"><h1>SEPHORA</h1></div>
                    <div class="stripes"></div>
                    <div class="content">
                        <h2 style="color: {primary};">Hi {customer_name},</h2>
                        <p>Your beauty order is confirmed! Get ready to glow