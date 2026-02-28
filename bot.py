import discord
from discord import app_commands, ui, Embed, Colour, ButtonStyle
import datetime
import random
import asyncio
import os
import re
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# === CONFIG FROM ENV VARS ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

if not all([BOT_TOKEN, SENDER_EMAIL, SENDGRID_API_KEY]):
    print("Missing BOT_TOKEN, SENDER_EMAIL, or SENDGRID_API_KEY!")
    exit(1)

print("BOT STARTING - ENV VARS OK")
print(f"SENDER_EMAIL: {SENDER_EMAIL}")

ROLE_ID = 1472751333286350981

BRANDS = [
    'Cartier', 'Denim Tears', 'Ksubi', 'Balenciaga', 'Sp5der',
    'Nike', 'Adidas', 'Lululemon', 'Lanvin', 'Creed',
    'Baccarat', 'Sephora', 'Apple'
]

# Brand display names for inbox "From"
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

# Brand logos (public URLs)
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

# Fake data
FAKE_NAMES = [
    "George Love", "Alex Rivera", "Jordan Lee", "Taylor Brooks", "Morgan Ellis",
    "Casey Quinn", "Riley Harper", "Jamie Knox", "Parker Reese", "Cameron Blake"
]

FAKE_ADDRESSES = [
    "030 Tyler Ridge, East Roberts Shire, GA 30301",
    "123 Main St, New York, NY 10001",
    "456 Oak Ave, Los Angeles, CA 90001",
    "789 Pine Rd, Chicago, IL 60601",
    "321 Elm St, Miami, FL 33101",
    "654 Maple Dr, Houston, TX 77001",
    "987 Cedar Ln, Seattle, WA 98101",
    "147 Birch Blvd, Boston, MA 02101",
    "258 Willow Way, Denver, CO 80201",
    "369 Spruce Ct, Atlanta, GA 30301",
    "1122 Bourbon St, New Orleans, LA 70116",  # high tax example
    "4455 Massachusetts Ave, Boston, MA 02115"
]

FAKE_PAYMENT_METHODS = [
    "Visa ending in 4823", "Mastercard ending in 7192", "Amex ending in 1122",
    "Discover ending in 4456", "Apple Pay", "PayPal"
]

# 2026 Combined sales tax rates (Tax Foundation Jan 2026 - population-weighted avg)
STATE_TAX_RATES = {
    "AL": 0.0946, "AK": 0.0182, "AZ": 0.0852, "AR": 0.0946, "CA": 0.0899,
    "CO": 0.0789, "CT": 0.0635, "DE": 0.0000, "FL": 0.0698, "GA": 0.0749,
    "HI": 0.0450, "ID": 0.0603, "IL": 0.0896, "IN": 0.0700, "IA": 0.0694,
    "KS": 0.0869, "KY": 0.0600, "LA": 0.1011, "ME": 0.0550, "MD": 0.0600,
    "MA": 0.0625, "MI": 0.0600, "MN": 0.0814, "MS": 0.0706, "MO": 0.0844,
    "MT": 0.0000, "NE": 0.0698, "NV": 0.0824, "NH": 0.0000, "NJ": 0.0660,
    "NM": 0.0767, "NY": 0.0854, "NC": 0.0700, "ND": 0.0709, "OH": 0.0729,
    "OK": 0.0906, "OR": 0.0000, "PA": 0.0634, "RI": 0.0700, "SC": 0.0749,
    "SD": 0.0611, "TN": 0.0961, "TX": 0.0820, "UT": 0.0742, "VT": 0.0639,
    "VA": 0.0577, "WA": 0.0951, "WV": 0.0659, "WI": 0.0572, "WY": 0.0556,
    "DC": 0.0600
}

def get_state_from_address(address):
    addr_upper = address.upper()
    matches = re.findall(r'\b([A-Z]{2})\b', addr_upper)
    for state in reversed(matches):
        if state in STATE_TAX_RATES:
            return state
    return "GA"  # fallback

user_emails = {}

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot online as {client.user} 🚀 - Ready for commands!")

@tree.command(name="setup", description="Hook your email to your user (role required)")
async def setup(interaction: discord.Interaction):
    if not any(r.id == ROLE_ID for r in interaction.user.roles):
        embed = Embed(title="Access Denied", description="You need the special role!", color=Colour.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await interaction.response.send_modal(EmailModal())

class EmailModal(ui.Modal, title="Email Setup"):
    email = ui.TextInput(label="What's your email?", style=discord.TextStyle.long, required=True, placeholder="Enter your email for receipts...")

    async def on_submit(self, interaction: discord.Interaction):
        user_emails[interaction.user.id] = self.email.value
        embed = Embed(
            title="Email Hooked",
            description=f"Email {self.email.value} saved! Use /generate to create receipts.",
            color=Colour.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class BrandButton(ui.Button):
    def __init__(self, brand, user_id):
        super().__init__(label=brand, style=ButtonStyle.primary, custom_id=f"brand_{brand}")
        self.brand = brand
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your button!", ephemeral=True)
            return

        modal = GenerateModal(brand=self.brand, user_id=self.user_id)
        await interaction.response.send_modal(modal)

class BrandView(ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        for brand in BRANDS:
            self.add_item(BrandButton(brand, user_id))

@tree.command(name="generate", description="Generate a receipt (role required)")
async def generate(interaction: discord.Interaction):
    if not any(r.id == ROLE_ID for r in interaction.user.roles):
        embed = Embed(title="Access Denied", description="You need the special role!", color=Colour.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = Embed(
        title="Choose Your Brand",
        description="Click the button for the brand you want.",
        color=Colour.blue()
    )

    view = BrandView(interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view)

class GenerateModal(ui.Modal, title="Receipt Details"):
    def __init__(self, brand: str, user_id: int):
        super().__init__(title=f"{brand} Receipt Details")
        self.brand = brand
        self.user_id = user_id

        self.item = discord.ui.TextInput(
            label="Item name",
            style=discord.TextStyle.paragraph,
            placeholder="e.g. Trinity ring",
            required=True,
            max_length=100
        )

        self.price = discord.ui.TextInput(
            label="Price per unit in USD",
            style=discord.TextStyle.short,
            placeholder="e.g. 790.00",
            required=True,
            max_length=20
        )

        self.quantity = discord.ui.TextInput(
            label="Quantity (default 1)",
            style=discord.TextStyle.short,
            placeholder="1",
            required=False,
            max_length=5
        )

        self.shipping_date = discord.ui.TextInput(
            label="Estimated Delivery Date",
            style=discord.TextStyle.short,
            placeholder="e.g. March 15, 2026",
            required=True,
            max_length=30
        )

        self.add_item(self.item)
        self.add_item(self.price)
        self.add_item(self.quantity)
        self.add_item(self.shipping_date)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        email = user_emails.get(self.user_id)
        if not email:
            await interaction.followup.send(
                embed=Embed(title="No Email Hooked", description="Run /setup first!", color=Colour.red()),
                ephemeral=True
            )
            return

        try:
            price = float(self.price.value.strip())
            quantity = int(self.quantity.value.strip() or 1)
            shipping_date = self.shipping_date.value.strip()

            # Randomized realism
            customer_name = random.choice(FAKE_NAMES)
            shipping_address = random.choice(FAKE_ADDRESSES)
            state = get_state_from_address(shipping_address)
            tax_rate = STATE_TAX_RATES.get(state, 0.0749)  # GA fallback

            subtotal = price * quantity
            delivery = round(random.uniform(0, 25), 2)  # realistic shipping $0–25
            sales_tax = round(subtotal * tax_rate, 2)
            total = round(subtotal + delivery + sales_tax, 2)

            order_id = f"{self.brand.upper()}-{random.randint(1000000000000000, 9999999999999999)}"
            tracking_number = f"1Z{random.randint(1000000000, 9999999999)}{random.randint(10000,99999)}"
            payment_method = random.choice(FAKE_PAYMENT_METHODS)
            gift_wrapping = random.choice(["Gift wrapping added", "No gift wrapping"])

            dm = await interaction.user.create_dm()
            embed = Embed(title="Sending Receipt", description=f"Generating & sending {self.brand} receipt to {email}...", color=Colour.orange())
            await dm.send(embed=embed)

            # Hyper-realistic HTML (clean, brand-agnostic but looks luxury)
            html_body = f"""
            <html>
            <body style="font-family: 'Helvetica Neue', Arial, sans-serif; background:#fff; color:#000; margin:0; padding:0; font-size:12px; line-height:1.6;">
            <div style="max-width:600px; margin:0 auto; padding:30px 20px; border:1px solid #e0e0e0; background:#fff;">
            <img src="{brand_info.get(self.brand, {'logo': ''})['logo']}" style="max-width:160px; display:block; margin:0 auto 25px;" alt="{self.brand}">
            <h2 style="text-align:center; color:#000; margin:0 0 15px; font-size:18px; font-weight:500;">Order Acknowledgment</h2>
            <p style="text-align:center; font-size:14px; margin:0 0 20px;">Dear {customer_name},</p>
            <p style="text-align:center; font-size:13px; margin:0 0 25px;">Thank you for shopping with {self.brand}. We are pleased to confirm receipt of your order. Please review the details below.</p>

            <div style="background:#000; color:#fff; padding:12px; text-align:center; margin:20px 0; font-size:16px; font-weight:bold;">
            ORDER N° {order_id}
            </div>

            <div style="margin:20px 0; padding:15px; background:#f9f9f9; border:1px solid #eee;">
            <p style="font-size:14px; margin:0 0 8px;"><strong>{self.item.value.strip()}</strong></p>
            <p style="font-size:13px; margin:0 0 8px;">{gift_wrapping}</p>
            <p style="font-size:13px; margin:0; text-align:right;">${price:,.2f} × {quantity}</p>
            </div>

            <table style="width:100%; font-size:13px; border-collapse:collapse;">
            <tr><td style="padding:6px 0;"><strong>Subtotal</strong></td><td style="text-align:right;">${subtotal:,.2f}</td></tr>
            <tr><td style="padding:6px 0;"><strong>Delivery</strong></td><td style="text-align:right;">${delivery:,.2f}</td></tr>
            <tr><td style="padding:6px 0;"><strong>Sales Tax</strong> ({tax_rate*100:.2f}% for {state})</td><td style="text-align:right;">${sales_tax:,.2f}</td></tr>
            <tr style="font-weight:bold; border-top:1px solid #000;"><td style="padding:10px 0 0;">Total</td><td style="text-align:right; padding:10px 0 0;">${total:,.2f}</td></tr>
            </table>

            <p style="font-size:13px; margin:20px 0 10px;"><strong>Estimated Delivery:</strong> {shipping_date}</p>
            <p style="font-size:13px; margin:5px 0;"><strong>Tracking Number:</strong> {tracking_number} (available once shipped)</p>
            <p style="font-size:13px; margin:5px 0;"><strong>Payment Method:</strong> {payment_method}</p>

            <div style="margin-top:25px; padding-top:20px; border-top:1px solid #eee;">
            <p style="font-size:14px; margin:0 0 8px; font-weight:500;">DELIVERY ADDRESS</p>
            <p style="font-size:13px; margin:0;">{customer_name}<br>{shipping_address}</p>
            </div>

            <p style="font-size:13px; margin:25px 0; text-align:center;">Shipping preferences were customized during checkout (via the modal: carrier, speed, instructions).</p>

            <p style="font-size:14px; text-align:center; margin:30px 0;">Thank you for choosing {self.brand}.</p>

            <hr style="border:0; border-top:1px solid #eee; margin:25px 0;">
            <p style="font-size:11px; color:#555; text-align:center;">Questions? Visit {self.brand.lower()}.com/support • This is an automated receipt.</p>
            </div>
            </body>
            </html>
            """

            message = Mail(
                from_email=(SENDER_EMAIL, brand_display.get(self.brand, self.brand)),
                to_emails=email,
                subject=f"Your {self.brand} Order Confirmation - {order_id}",
                html_content=html_body
            )

            sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
            response = sg.send(message)
            print(f"SendGrid sent - status: {response.status_code}")

            await interaction.followup.send(
                embed=Embed(title="Sent!", description=f"Hyper-realistic {self.brand} receipt emailed to {email}. Check inbox/spam.", color=Colour.green()),
                ephemeral=True
            )

        except ValueError:
            await interaction.followup.send(
                embed=Embed(title="Invalid Input", description="Price must be a number. Try again.", color=Colour.red()),
                ephemeral=True
            )
        except Exception as e:
            print(f"Error: {str(e)}")
            await interaction.followup.send(
                embed=Embed(title="Failed", description=f"Error sending: {str(e)}", color=Colour.red()),
                ephemeral=True
            )

client.run(BOT_TOKEN)