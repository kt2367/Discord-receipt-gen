import discord
from discord.ext import commands
import os

INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.members = True

bot = commands.Bot(command_prefix="$", intents=INTENTS)

ALLOWED_ROLE_ID = 1472751333286350981

TEMPLATE_LINK = "https://discord.com/channels/@me/1472744860212658218/1472750462930522268"

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def bad(ctx, *, product_name: str):
    if product_name.lower() != "boy woody leather":
        return

    if not any(role.id == ALLOWED_ROLE_ID for role in ctx.author.roles):
        await ctx.send("❌ You do not have permission to use this command.")
        return

    try:
        await ctx.author.send(
            f"📄 **Your template for _Bad Boy Woody Leather_**\n\n{TEMPLATE_LINK}"
        )
        await ctx.send("✅ Check your DMs!")
    except discord.Forbidden:
        await ctx.send("❌ I can’t DM you. Please enable DMs from server members.")

bot.run(os.getenv("DISCORD_TOKEN"))
