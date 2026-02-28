import discord
from discord import app_commands, ui, Embed, Colour, ButtonStyle
import datetime
import random
import asyncio
import os
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

# Brand info with logos + dummy contacts for EVERY brand (no KeyError)
brand_info = {
    'Cartier': {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Cartier_logo.svg/1280px-Cartier_logo.svg.png",
        "website": "https://www.cartier.com/contact-us",
        "email": "support@cartier.com",
        "phone": "+1-800-227-8437"
    },
    'Denim Tears': {
        "logo": "https://i.imgur.com/denimtearslogo.png",
        "website": "https://denimtears.com/pages/contact",
        "email": "support@denimtears.com",
        "phone": "+1-800-555-1234"
    },
    'Ksubi': {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Ksubi_logo.svg/1280px-Ksubi_logo.svg.png",
        "website": "https://ksubi.com/pages/contact",
        "email": "support@ksubi.com",
        "phone": "+1-800-555-5678"
    },
    'Balenciaga': {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Balenciaga_logo.svg/1280px-Balenciaga_logo.svg.png",
        "website": "https://www.balenciaga.com/us/contact-us",
        "email": "support@balenciaga.com",
        "phone": "+1-800-555-9012"
    },
    'Sp5der': {
        "logo": "https://i.imgur.com/sp5derlogo.png",
        "website": "https://sp5der.com/pages/contact",
        "email": "support@sp5der.com",
        "phone": "+1-800-555-3456"
    },
    'Nike': {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Logo_NIKE.svg/1280px-Logo_NIKE.svg.png",
        "website": "https://www.nike.com/help",
        "email": "support@nike.com",
        "phone": "+1-800-344-6453"
    },
    'Adidas': {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Adidas_Logo.svg/1280px-Adidas_Logo.svg.png",
        "website": "https://www.adidas.com/us/help",
        "email": "support@adidas.com",
        "phone": "+1-800-982-9337"
    },
    'Lululemon': {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Lululemon_logo.svg/1280px-Lululemon_logo.svg.png",
        "website": "https://shop.lululemon.com/contact",
        "email": "support@lululemon.com",
        "phone": "+1-877-263-9300"
    },
    'Lanvin': {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Lanvin_logo.svg/1280px-Lanvin_logo.svg.png",
        "website": "https://www.lanvin.com/contact-us",
        "email": "support@lanvin.com",
        "phone": "+1-800-555-7890"
    },
    'Creed': {
        "logo": "https://i.imgur.com/creedlogo.png",
        "website": "https://www.creedboutique.com/contact",
        "email": "info@creedboutique.com",
        "phone": "+1-800-555-2345"
    },
    'Baccarat': {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Baccarat_logo.svg/1280px-Baccarat_logo.svg.png",
        "website": "https://www.baccarat.com/contact-us",
        "email": "service@baccarat.com",
        "phone": "+1-800-555-6789"
    },
    'Sephora': {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Sephora_Logo.svg/1280px-Sephora_Logo.svg.png",
        "website": "https://www.sephora.com/beauty/customer-service",
        "email": "customerservice@sephora.com",
        "phone": "+1-877-737-4672"
    },
    'Apple': {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/1280px-Apple_logo_black.svg.png",
        "website": "https://support.apple.com/contact",
        "email": "support@apple.com",
        "phone": "+1-800-275-2273"
    }
}

# Fake data for randomization
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
    "Visa ending in 1234",
    "Mastercard ending in 5678",
    "Apple Pay",
    "Cash on Delivery"
]

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
        super().__init__(title="Receipt Details")
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
            label="Price in USD",
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
            label="Shipping Date",
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
                embed=Embed(
                    title="No Email Hooked",
                    description="Run /setup first to hook your email!",
                    color=Colour.red()
                ),
                ephemeral=True
            )
            return

        brand = self.brand
        try:
            price = float(self.price.value.strip())
            quantity = int(self.quantity.value.strip() or 1)
            shipping_date = self.shipping_date.value.strip()

            # Randomized realism
            customer_name = random.choice(FAKE_NAMES)
            shipping_address = random.choice(FAKE_ADDRESSES)
            order_id = f"{brand.upper()}-{random.randint(1000000000000000000,9999999999999999999)}"
            tracking_number = f"1Z{random.randint(1000000000,9999999999)}"
            payment_method = random.choice(FAKE_PAYMENT_METHODS)

            dm = await interaction.user.create_dm()
            embed = Embed(title="Email Being Sent", description=f"Sending branded {brand} receipt to {email}...", color=Colour.orange())
            await dm.send(embed=embed)

            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background:#fff; color:#000; margin:0; padding:0;">
            <div style="max-width:600px; margin:0 auto; padding:20px; border:1px solid #ddd;">
            <img src="{brand_info.get(brand, {'logo': ''})['logo']}" style="max-width:200px; display:block; margin:0 auto 20px;" alt="{brand}">
            <h2 style="text-align:center; color:#000; margin-bottom:10px;">Acknowledgment of your order</h2>
            <p style="text-align:center; font-size:16px;">Dear {customer_name},</p>
            <p style="font-size:14px;">Thank you for shopping online with {brand}. We are pleased to acknowledge receipt of your order, the main details of which are set out below. Please check this email in order to ensure that the details are accurate.</p>
            <p style="font-size:14px;">Please note that this acknowledgment is not a confirmation of your order. Once your order has been approved, you will receive another email confirming acceptance of your order at the time of shipment.</p>
            <p style="text-align:center; font-size:14px;"><a href="{brand_info.get(brand, {'website': '#'})['website']}" style="color:#000; text-decoration:underline;">To track your order online from your My{brand} account, click here: track order</a></p>

            <div style="background:#000; color:#fff; padding:10px; text-align:center; margin:20px 0;">
            <strong>ORDER N° {order_id}</strong>
            </div>

            <table style="width:100%; border-collapse:collapse; margin:20px 0;">
            <tr style="background:#f0f0f0;"><th style="padding:10px; text-align:left;">Item</th><th style="padding:10px; text-align:right;">Qty</th><th style="padding:10px; text-align:right;">Price</th></tr>
            <tr><td style="padding:10px;">{self.item.value.strip()}</td><td style="padding:10px; text-align:right;">{quantity}</td><td style="padding:10px; text-align:right;">${price:,.2f}</td></tr>
            </table>

            <p style="font-size:14px;"><strong>Payment Method:</strong> {payment_method}</p>

            <p><strong>Subtotal:</strong> ${price*quantity:,.2f}<br>
            <strong>Delivery:</strong> $10.00<br>
            <strong>VAT:</strong> ${price*quantity*0.08:,.2f}<br>
            <strong>Total:</strong> ${(price*quantity*1.08 + 10):,.2f} incl. VAT</p>

            <p><strong>Estimated delivery date:</strong> {shipping_date}</p>
            <p><strong>Tracking Number:</strong> {tracking_number}</p>

            <div style="border-top:1px solid #000; padding-top:20px; margin-top:20px;">
            <p style="font-size:14px;">DELIVERY ADDRESS</p>
            <p>{customer_name}<br>{shipping_address}</p>
            </div>

            <p style="font-size:14px; text-align:center; margin-top:30px;">Thank you for shopping with {brand}!</p>

            <hr style="border:0; border-top:1px solid #eee; margin:20px 0;">
            <p style="font-size:12px; color:#666; text-align:center;">Questions? Contact {brand_display.get(brand, brand)} Support • This is an automated receipt.</p>

            <div style="text-align:center; margin-top:20px; font-size:14px;">
            <a href="{brand_info.get(brand, {'website': '#'})['website']}" style="color:#000; text-decoration:underline; margin:0 10px;">Contact Us</a> |
            <a href="mailto:{brand_info.get(brand, {'email': 'support@brand.com'})['email']}" style="color:#000; text-decoration:underline; margin:0 10px;">Email Support</a> |
            <a href="tel:{brand_info.get(brand, {'phone': '+1-800-555-0000'})['phone']}" style="color:#000; text-decoration:underline; margin:0 10px;">Call {brand_info.get(brand, {'phone': '+1-800-555-0000'})['phone']}</a>
            </div>
            </div>
            </body>
            </html>
            """

            message = Mail(
                from_email=(SENDER_EMAIL, brand_display.get(brand, brand)),
                to_emails=email,
                subject=f"Your {brand} Order Confirmation",
                html_content=html_body
            )

            sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
            response = sg.send(message)
            print(f"SendGrid success - status: {response.status_code}")

            await interaction.followup.send(
                embed=Embed(
                    title="Success!",
                    description=f"Receipt sent to {email}! Check inbox/spam.",
                    color=Colour.green()
                ),
                ephemeral=True
            )

            await interaction.message.delete()

        except Exception as e:
            print(f"SendGrid error: {str(e)}")
            await interaction.followup.send(
                embed=Embed(
                    title="Email Failed",
                    description=f"Error: {str(e)}\nCheck SendGrid dashboard, key, or spam folder.",
                    color=Colour.red()
                ),
                ephemeral=True
            )

        except ValueError:
            await interaction.followup.send(
                embed=Embed(
                    title="Invalid Input",
                    description="Price/qty must be numbers. Retry.",
                    color=Colour.red()
                ),
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                embed=Embed(
                    title="Error",
                    description=f"Something broke: {str(e)}",
                    color=Colour.red()
                ),
                ephemeral=True
            )

client.run(BOT_TOKEN)