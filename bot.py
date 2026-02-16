
import discord
from discord.ext import commands
import os

# ----------------- CONFIG -----------------
INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.members = True

bot = commands.Bot(command_prefix="$", intents=INTENTS)

# Role allowed to use the command
ALLOWED_ROLE_ID = 1472751333286350981

# Link to the template file in your Discord server
TEMPLATE_LINK = "https://cdn.discordapp.com/attachments/1472762776723390504/1472762918088081559/yourfile.pdf"

# ----------------- READY EVENT -----------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ----------------- COMMAND -----------------
@bot.command(name="bad")
async def bad(ctx, *, product_name: str):
    if product_name.lower() != "boy woody leather":
        return

    # Check if user has the allowed role
    if not any(role.id == ALLOWED_ROLE_ID for role in ctx.author.roles):
        await ctx.send("❌ You do not have permission to use this command.")
        return

    try:
        # Send DM with the template link
        await ctx.author.send(
            f"📄 **Your template for _Bad Boy Woody Leather_**\n\n{TEMPLATE_LINK}"
        )
        await ctx.send("✅ Check your DMs!")
    except discord.Forbidden:
        await ctx.send("❌ I can’t DM you. Please enable DMs from server members.")

# ----------------- RUN BOT -----------------
bot.run(os.getenv("DISCORD_TOKEN"))
