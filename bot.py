import discord
from discord import app_commands, ui, Embed, Colour
import datetime
import random
import asyncio
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# === CONFIG FROM ENV VARS ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")  # yourgmail@gmail.com
APP_PASSWORD = os.getenv("APP_PASSWORD")  # 16-char Gmail app password (no spaces)

if not all([BOT_TOKEN, SENDER_EMAIL, APP_PASSWORD]):
    print("Missing BOT_TOKEN, SENDER_EMAIL, or APP_PASSWORD!")
    exit(1)

print("BOT STARTING - ENV VARS OK")
print(f"SENDER_EMAIL: {SENDER_EMAIL}")

ROLE_ID = 1472751333286350981

BRANDS = [
    'Cartier', 'Denim Tears', 'Ksubi', 'Balenciaga', 'Sp5der',
    'Nike', 'Adidas', 'Lululemon', 'Lanvin', 'Creed',
    'Baccarat', 'Sephora', 'Apple'
]

# Brand-specific From settings for realistic sender line
brand_from = {
    'Cartier': {"display": "Cartier", "from_email": "concierge@cartier.com"},
    'Nike': {"display": "Nike", "from_email": "orders@nike.com"},
    'Adidas': {"display": "adidas", "from_email": "service@adidas.com"},
    'Sephora': {"display": "Sephora", "from_email": "customerservice@sephora.com"},
    'Lululemon': {"display": "lululemon athletica", "from_email": "support@lululemon.com"},
    'Apple': {"display": "Apple Store", "from_email": "no-reply@apple.com"},
    'Balenciaga': {"display": "Balenciaga", "from_email": "contact@balenciaga.com"},
    'Creed': {"display": "Creed Boutique", "from_email": "info@creedboutique.com"},
    'Lanvin': {"display": "Lanvin", "from_email": "contact@lanvin.com"},
    'Baccarat': {"display": "Baccarat", "from_email": "service@baccarat.com"},
    'Denim Tears': {"display": "Denim Tears", "from_email": "support@denimtears.com"},
    'Ksubi': {"display": "Ksubi", "from_email": "hello@ksubi.com"},
    'Sp5der': {"display": "Sp5der", "from_email": "support@sp5der.com"},
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

def parse_duration(dur: str) -> int:
    if not dur or not dur[0].isdigit():
        return 0
    num = int(''.join(filter(str.isdigit, dur)))
    unit = dur.lower()[-2:] if dur.lower().endswith(('mo', 'wk')) else dur.lower()[-1]
    if unit in ['s', 'sec']: return num
    if unit in ['m', 'min']: return num * 60
    if unit in ['h', 'hr']: return num * 3600
    if unit == 'd': return num * 86400
    if unit in ['w', 'wk']: return num * 604800
    if unit in ['mo', 'mth']: return num * 2592000
    return 0

async def remove_role_after_delay(member: discord.Member, role: discord.Role, seconds: int):
    await asyncio.sleep(seconds)
    await member.remove_roles(role)
    print(f"Removed role {role.name} from {member} after {seconds} seconds")

@tree.command(name="role", description="Give temp role (admin only)")
@app_commands.describe(member="User", duration="e.g. 1d 2w 3m")
@app_commands.checks.has_permissions(administrator=True)
async def assign_role(interaction: discord.Interaction, member: discord.Member, duration: str):
    if any(r.id == ROLE_ID for r in member.roles):
        embed = Embed(title="Error", description=f"{member.mention} already has the role!", color=Colour.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    role = interaction.guild.get_role(ROLE_ID)
    if not role:
        embed = Embed(title="Error", description="Role not found!", color=Colour.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await member.add_roles(role)
    seconds = parse_duration(duration)
    if seconds > 0:
        asyncio.create_task(remove_role_after_delay(member, role, seconds))
    embed = Embed(
        title="Role Assigned",
        description=f"Gave {role.name} to {member.mention} for {duration} (auto-remove after time)",
        color=Colour.green()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

class EmailModal(ui.Modal, title="Email Hook"):
    email = ui.TextInput(label="What's your email?", style=discord.TextStyle.long, required=True, placeholder="Enter your email for receipts...")

    async def on_submit(self, interaction: discord.Interaction):
        user_emails[interaction.user.id] = self.email.value
        embed = Embed(
            title="Email Hooked",
            description=f"Email {self.email.value} saved! Use /generate to create receipts.",
            color=Colour.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="setup", description="Hook your email to your user (role required)")
async def setup(interaction: discord.Interaction):
    if not any(r.id == ROLE_ID for r in interaction.user.roles):
        embed = Embed(title="Access Denied", description="You need the special role!", color=Colour.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await interaction.response.send_modal(EmailModal())

class BrandSelect(ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=brand) for brand in BRANDS]
        super().__init__(placeholder="Select a brand...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        brand = self.values[0]
        await interaction.response.defer(ephemeral=True)  # Critical: gives time for modal
        await interaction.message.delete()  # Clean up dropdown
        modal = GenerateModal(brand=brand, user_id=interaction.user.id)
        await interaction.followup.send_modal(modal)  # Sends modal after defer

class BrandView(ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(BrandSelect())

@tree.command(name="generate", description="Generate a receipt (role required)")
async def generate(interaction