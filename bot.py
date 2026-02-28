import discord
from discord import app_commands, ui, Embed, Colour, ButtonStyle
import datetime
import random
import asyncio
import os
import re
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

if not all([BOT_TOKEN, SENDER_EMAIL, SENDGRID_API_KEY]):
    print("Missing env vars!")
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
    print(f"Bot online as {client.user} 🚀 - Ready for commands!")
    # Heartbeat for Railway
    while True:
        await asyncio.sleep(30)
        print("Heartbeat - bot alive")

@tree.command(name="setup", description="Hook your email to your user (role required)")
async def setup(interaction: discord.Interaction):
    if not any(r.id == ROLE_ID for r in interaction.user.roles):
        await interaction.response.send_message(embed=Embed(title="Access Denied", description="You need the special role!", color=Colour.red()), ephemeral=True)
        return
    await interaction.response.send_modal(EmailModal())

class EmailModal(ui.Modal, title="Email Setup"):
    email = ui.TextInput(label="What's your email?", style=discord.TextStyle.long, required=True, placeholder="Enter your email for receipts...")

    async def on_submit(self, interaction: discord.Interaction):
        user_emails[interaction.user.id] = self.email.value
        await interaction.response.send_message(embed=Embed(title="Email Hooked", description=f"Email {self.email.value} saved!", color=Colour.green()), ephemeral=True)

@tree.command(name="role", description="Give user the special role for a duration (e.g. 1d, 2w, 3m)")
@app_commands.describe(user="The user", duration="Duration e.g. 1d 2w 3m")
async def role(interaction: discord.Interaction, user: discord.Member, duration: str):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You need manage roles permission.", ephemeral=True)
        return

    duration = duration.lower().strip()
    if duration.endswith('d'):
        days = int(duration[:-1])
        delta = datetime.timedelta(days=days)
    elif duration.endswith('w'):
        weeks = int(duration[:-1])
        delta = datetime.timedelta(weeks=weeks)
    elif duration.endswith('m'):
        months = int(duration[:-1])
        delta = datetime.timedelta(days=months * 30)
    else:
        await interaction.response.send_message("Invalid format. Use e.g. 1d, 2w, 3m", ephemeral=True)
        return

    role = interaction.guild.get_role(ROLE_ID)
    if not role:
        await interaction.response.send_message("Role not found.", ephemeral=True)
        return

    await user.add_roles(role)
    await interaction.response.send_message(f"Added role to {user.mention} for {duration}.", ephemeral=True)

    await asyncio.sleep(delta.total_seconds())
    await user.remove_roles(role)
    print(f"Removed role from {user} after {duration}")

class BrandButton(ui.Button):
    def __init__(self, brand, user_id):
        super().__init__(label=brand, style=ButtonStyle.primary, custom_id=f"brand_{brand}_{user_id}")
        self.brand = brand
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        # Only allow the original user to click
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This button is not for you!", ephemeral=True)
            return

        # Defer immediately to prevent "interaction failed"
        await interaction.response.defer(ephemeral=True)

        try:
            modal = GenerateModal(brand=self.brand, user_id=self.user_id)
            await interaction.followup.send_modal(modal)
        except discord.errors.HTTPException as e:
            print(f"Modal failed: {e}")
            await interaction.followup.send(embed=Embed(title="Error", description="Failed to open modal. Try /generate again.", color=Colour.red()), ephemeral=True)
        except Exception as e:
            print(f"Unexpected error in button: {e}")
            await interaction.followup.send(embed=Embed(title="Error", description="Something went wrong. Contact staff.", color=Colour.red()), ephemeral=True)

class BrandView(ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)  # 3 minutes
        for brand in BRANDS:
            self.add_item(BrandButton(brand, user_id))

@tree.command(name="generate", description="Generate a receipt (role required)")
async def generate(interaction: discord.Interaction):
    if not any(r.id == ROLE_ID for r in interaction.user.roles):
        await interaction.response.send_message(embed=Embed(title="Access Denied", description="You need the special role!", color=Colour.red()), ephemeral=True)
        return

    embed = Embed(
        title="Choose Your Brand",
        description=f"{interaction.user.mention}, click the button for the brand you want.\n(Only you can use these buttons)",
        color=Colour.blue()
    )

    view = BrandView(interaction.user.id)

    # Send PUBLIC message in channel
    await interaction.response.send_message(embed=embed, view=view)  # NO ephemeral=True

# === Your GenerateModal class goes here ===
# (Paste your full GenerateModal class with color/size/shipping logic from the previous version)

client.run(BOT_TOKEN)