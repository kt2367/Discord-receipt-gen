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

# Brand-specific display names for inbox "From" (shows as "Cartier Order Confirmation" etc.)
brand_display = {
    'Cartier': "Cartier Order Confirmation",
    'Denim Tears': "Denim Tears",
    'Ksubi': "Ksubi",
    'Balenciaga': "Balenciaga",
    'Sp5der': "Sp5der",
    'Nike': "Nike Order Confirmation",
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
        embed