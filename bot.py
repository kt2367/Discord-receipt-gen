import os
import discord
from discord.ext import commands

# Load bot token from Railway environment variable
TOKEN = os.getenv("DISCORD_TOKEN")

# Role ID allowed to access templates
ALLOWED_ROLE_ID = 1472751333286350981  # <-- Your role ID

# Templates dictionary: prefix -> link
templates = {
    "$gen 2 pros": "https://docs.google.com/document/d/1wzMcQjWDtxqG00oeyrEa8WNKsjULhu--/view",
    "$gen 1 pros": "https://docs.google.com/document/d/1o2w9cTM9wZXWJ2wHV5DFhs75fegfNcxc/view",
    "$maxes": "https://docs.google.com/document/d/1Im6pR2eeGI8R534HO_6tPTOx1va8lcy6/view",
    "$gen 4": "https://docs.google.com/document/d/1HnOsvNIIbZW17czsNvwXOzLPcqGjdDxY/view",
    "$gen 2": "https://docs.google.com/document/d/1PEchU2wLeB9O_Gu5d619_LF4gzAvsV8F/view",
    "$burberry her elixir": "https://docs.google.com/document/d/1HBdeft5grbTDyyQenGY3dJL0XSVDKdDz/view",
    "$gucci guilty pour home toilette": "https://docs.google.com/document/d/1DEEcspmYVGDevUrzQXDB39dcP68x9tRI/view",
    "$gucci guilty pour homme eau de": "https://docs.google.com/document/d/1hDwGZRcoa5saZxgydbBBCAXRDxS7HRW5/view",
    "$good girl floral vanilla": "https://docs.google.com/document/d/1sONH0wNcsFCnCE5Mn4qPWYUwsVaz3m0e/view",
    "$creed virgin island": "https://drive.google.com/file/d/1mVFtQnJM_mkKD3Bn5N4Wa3jmQz8f8ETl/view",
    "$dior sauvage pafum": "https://docs.google.com/document/d/1j9oeoxg8Rdk-ipIE2f0h0nc0pB7UuNGw/view",
    "$tom ford tobacco vanille": "https://docs.google.com/document/d/1_YSwRXVqKj-4Sg9IXqRuZsAHonQLTnIB/view",
    "$chanel bleu de parfum": "https://docs.google.com/document/d/1hgOok9BJ93-6o-Dyz0ajDKmqC_I-Obw7/view"
}

# Discord intents
intents = discord.Intents.default()
intents.members = True  # Needed to check roles
intents.message_content = True  # Needed to read messages

bot = commands.Bot(command_prefix="$", intents=intents)

# Helper function to check role
def has_allowed_role(member):
    return any(role.id == ALLOWED_ROLE_ID for role in member.roles)

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

@bot.command()
async def receipts(ctx):
    """DM the user a list of all available prefixes"""
    member = ctx.author
    if has_allowed_role(member):
        prefixes_text = "\n".join(templates.keys())
        try:
            await member.send(f"Here are all available templates:\n{prefixes_text}")
            await ctx.send(f"{member.mention}, success! Check your DMs.")
        except discord.Forbidden:
            await ctx.send(f"{member.mention}, I cannot DM you. Check your privacy settings.")
    else:
        await ctx.send("receipt/gen access denied")

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore bot messages

    member = message.author
    content = message.content.lower()  # Make prefix check case-insensitive

    if content in templates:
        if has_allowed_role(member):
            try:
                await member.send(f"Here’s your template link for {content}:\n{templates[content]}")
                await message.channel.send(f"{member.mention}, success! Check your DMs.")
            except discord.Forbidden:
                await message.channel.send(f"{member.mention}, I cannot DM you. Check your privacy settings.")
        else:
            await message.channel.send("receipt/gen access denied")

    await bot.process_commands(message)  # Keep other commands like $receipts working

bot.run(TOKEN)
