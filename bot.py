import discord
from discord import app_commands, ui, Embed, Colour, ButtonStyle
import datetime
import random
import asyncio
import os
import re
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging

# Setup logging to see what's failing
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

brand_display = {b: b for b in BRANDS}  # simplified, add your custom if needed

brand_info = {
    'Cartier': {"logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Cartier_logo.svg/512px-Cartier_logo.svg.png"},
    # ... add the rest as before ...
}

FAKE_NAMES = [...]  # your list
FAKE_ADDRESSES = [...]  # your list
FAKE_PAYMENT_METHODS = [...]  # your list
STATE_TAX_RATES = {...}  # your tax dict

def get_state_from_address(address):
    # your function

user_emails = {}

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    logger.info(f"Bot online as {client.user}")
    while True:
        await asyncio.sleep(30)
        logger.info("Heartbeat")

@tree.command(name="generate", description="Generate a receipt (role required)")
async def generate(interaction: discord.Interaction):
    if not any(r.id == ROLE_ID for r in interaction.user.roles):
        await interaction.response.send_message(embed=Embed(title="Access Denied", color=Colour.red()), ephemeral=True)
        return

    embed = Embed(
        title="Choose Your Brand",
        description=f"{interaction.user.mention}, click a button below to select your brand.\n(Only you can use these buttons)",
        color=Colour.blue()
    )

    view = BrandView(interaction.user.id)

    # Public message
    await interaction.response.send_message(embed=embed, view=view)

class BrandButton(ui.Button):
    def __init__(self, brand, user_id):
        super().__init__(label=brand, style=ButtonStyle.primary, custom_id=f"brand_select_{user_id}_{brand}")
        self.brand = brand
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("These buttons are not for you!", ephemeral=True)
            return

        # Defer RIGHT AWAY - this is critical
        await interaction.response.defer(ephemeral=True)

        logger.info(f"User {interaction.user} clicked {self.brand}")

        try:
            modal = GenerateModal(brand=self.brand, user_id=self.user_id)
            await interaction.followup.send_modal(modal)
            logger.info("Modal sent successfully")
        except discord.HTTPException as http_err:
            logger.error(f"HTTP error sending modal: {http_err}")
            await interaction.followup.send(
                embed=Embed(title="Error", description="Failed to open modal (timeout or API issue). Run /generate again.", color=Colour.red()),
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Unexpected modal error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=Embed(title="Error", description="Something broke internally. Contact staff or try again.", color=Colour.red()),
                ephemeral=True
            )

class BrandView(ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)  # Persistent view - no auto timeout
        for brand in BRANDS:
            self.add_item(BrandButton(brand, user_id))

# Paste your full GenerateModal class + on_submit here (with color, size, shipping logic)
# Make sure on_submit has its own try/except and logging

client.run(BOT_TOKEN)