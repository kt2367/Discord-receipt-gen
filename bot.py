import discord
from discord.ext import commands

# Replace with your bot token
TOKEN = "YOUR_BOT_TOKEN_HERE"

# Replace with your role ID that can access templates
ALLOWED_ROLE_ID = 123456789012345678  # <-- put your role ID here

# Template links
templates = {
    "$Gen 2 pros": "https://docs.google.com/document/d/1wzMcQjWDtxqG00oeyrEa8WNKsjULhu--/view",
    "$Gen 1 pros": "https://docs.google.com/document/d/1o2w9cTM9wZXWJ2wHV5DFhs75fegfNcxc/view",
    "$maxes": "https://docs.google.com/document/d/1Im6pR2eeGI8R534HO_6tPTOx1va8lcy6/view",
    "$Gen 4": "https://docs.google.com/document/d/1HnOsvNIIbZW17czsNvwXOzLPcqGjdDxY/view",
    "$Gen 2": "https://docs.google.com/document/d/1PEchU2wLeB9O_Gu5d619_LF4gzAvsV8F/view",
    "$burberry her elixir": "https://docs.google.com/document/d/1HBdeft5grbTDyyQenGY3dJL0XSVDKdDz/view",
    "$gucci guilty pour home toilette": "https://docs.google.com/document/d/1DEEcspmYVGDevUrzQXDB39dcP68x9tRI/view",
    "$gucci guilty pour homme eau de": "https://docs.google.com/document/d/1hDwGZRcoa5saZxgydbBBCAXRDxS7HRW5/view",
    "$good girl floral vanilla": "https://docs.google.com/document/d/1sONH0wNcsFCnCE5Mn4qPWYUwsVaz3m0e/view",
    "$creed virgin island": "https://drive.google.com/file/d/1mVFtQnJM_mkKD3Bn5N4Wa3jmQz8f8ETl/view",
    "$dior sauvage pafum": "https://docs.google.com/document/d/1j9oeoxg8Rdk-ipIE2f0h0nc0pB7UuNGw/view",
    "$tom ford tobacco vanille": "https://docs.google.com/document/d/1_YSwRXVqKj-4Sg9IXqRuZsAHonQLTnIB/view",
    "$chanel bleu de parfum": "https://docs.google.com/document/d/1hgOok9BJ93-6o-Dyz0ajDKmqC_I-Obw7/view"
}

intents = discord.Intents.default()
intents.members = True  # Needed to check roles

bot = commands.Bot(command_prefix="$", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def template(ctx, *, name):
    """Send template link if user has the allowed role"""
    member = ctx.author
    template_link = templates.get(name)

    if not template_link:
        await ctx.send("Template not found.")
        return

    role = discord.utils.get(member.roles, id=ALLOWED_ROLE_ID)
    if role:
        await ctx.send(f"Here’s your template link: {template_link}")
    else:
        await ctx.send("You do not have permission to access this template.")

@bot.command()
async def receipts(ctx):
    """DM the user a list of all template prefixes"""
    member = ctx.author
    role = discord.utils.get(member.roles, id=ALLOWED_ROLE_ID)

    if role:
        prefixes = "\n".join(templates.keys())
        try:
            await member.send(f"Here are the available templates:\n{prefixes}")
            await ctx.send(f"{member.mention}, I’ve DM’d you the list of available templates!")
        except discord.Forbidden:
            await ctx.send(f"{member.mention}, I cannot DM you. Please check your privacy settings.")
    else:
        await ctx.send("You do not have permission to view the available templates.")

bot.run(TOKEN)
