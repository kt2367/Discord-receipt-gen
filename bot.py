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
SENDER_EMAIL = os.getenv("SENDER_EMAIL")  # Your verified SendGrid sender email
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

# Brand-specific display names (what shows in inbox)
brand_display = {
    'Cartier': "Cartier Concierge",
    'Denim Tears': "Denim Tears",
    'Ksubi': "Ksubi",
    'Balenciaga': "Balenciaga",
    'Sp5der': "Sp5der",
    'Nike': "Nike",
    'Adidas': "adidas",
    'Lululemon': "lululemon athletica",
    'Lanvin': "Lanvin",
    'Creed': "Creed Boutique",
    'Baccarat': "Baccarat",
    'Sephora': "Sephora",
    'Apple': "Apple Store",
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
        await interaction.response.send_modal(modal)  # Direct send_modal

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
            placeholder="e.g. iPhone 16 Pro Max",
            required=True,
            max_length=100
        )

        self.price = discord.ui.TextInput(
            label="Price in USD",
            style=discord.TextStyle.short,
            placeholder="e.g. 1199.00",
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

        self.shipping = discord.ui.TextInput(
            label="Shipping address (optional, N/A)",
            style=discord.TextStyle.paragraph,
            placeholder="N/A",
            required=False,
            max_length=300
        )

        self.add_item(self.item)
        self.add_item(self.price)
        self.add_item(self.quantity)
        self.add_item(self.shipping)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)  # Acknowledge immediately

        email = user_emails.get(self.user_id)
        if not email:
            await interaction.followup.send(
                embed=discord.Embed(
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
            shipping = self.shipping.value.strip() or "N/A"
            item = self.item.value.strip()

            dm = await interaction.user.create_dm()
            embed = Embed(title="Email Being Sent", description=f"Sending branded {brand} receipt to {email}...", color=Colour.orange())
            await dm.send(embed=embed)

            # Build SendGrid message
            from_display = brand_display.get(brand, brand)  # e.g. "Cartier Concierge"
            message = Mail(
                from_email=(SENDER_EMAIL, from_display),  # Verified email + brand display name
                to_emails=email,
                subject=f"Your {brand} Order Confirmation",
                html_content=f"""
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

            # Delete original buttons message after success
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