import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)

# Allowed role ID
ALLOWED_ROLE_ID = 1472751333286350981

# Prefixes and their view-only links
template_links = {
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
    "$dior sauvage elixir": "https://docs.google.com/document/d/1lItxoHzfhTzjKmXWufkfvHC9N97_w6rt/view",
    "$tom ford tobacco vanille": "https://docs.google.com/document/d/1_YSwRXVqKj-4Sg9IXqRuZsAHonQLTnIB/view",
    "$chanel bleu de parfum": "https://docs.google.com/document/d/1hgOok9BJ93-6o-Dyz0ajDKmqC_I-Obw7/view",
    "$baccarat rouge 540": "https://docs.google.com/document/d/19jF2xAPoJyusTEZiYCnoJQ4WbDBsv_x3/view",
    "$creed aventus": "https://docs.google.com/document/d/1Bo_RX-gkINMAuzFma3AfnZYnL1wtTLXn/view",
    "$valentino born in roma intense": "https://docs.google.com/document/d/19clwFpnzrkjiViqbvmcvC43cYJg4KORN/view",
    "$ysl libre eau de parfum": "https://docs.google.com/document/d/1bTYQL__VvgS2VX_qosal2joGT95hhsM2/view",
    "$ysl black opium eau de parfum": "https://docs.google.com/document/d/1O4OamiTa2zZP8gByh1TkADvRb572XjFx/view",
    "$carolina herrara very good girl eau de parfum": "https://docs.google.com/document/d/17Y2SqOu8WL3VrKo7OpoXKm-mV3v_msIz/view",
    "$versace eros parfum": "https://docs.google.com/document/d/1dQ75K5xYoAb-eRp6hYPGI-4FSNaX685z/view",
    "$ysl y eau de parfum": "https://docs.google.com/document/d/1DEOSa8v8o_l9kgktaSSEm7Fr9SJDfWNf/view",
    "$valentino born in roma eau de toilette": "https://docs.google.com/document/d/1xyg6DUid9TGHa3oxZHKvop84ZNZbaOx1/view",
    "$lv imagination": "https://docs.google.com/document/d/1nMSFDW3rj4pfRovPEYhHMeaisHxtrSaz/view",
    "$rabanne 1 million eau de toilette": "https://docs.google.com/document/d/1gOidbpQTQocT2K6a-Krs2cWaoCmE4OyA/view",
    "$xerjoff erba pura": "https://docs.google.com/document/d/1JZG_458O6vQFWsJ1SnTCyOFjpiEWoDmY/view",
    "$jpg le male elixir": "https://docs.google.com/document/d/1MToEn7BbVIL77KVujmPL2FqQSiVNAhGL/view",
    "$lv pacific chill": "https://docs.google.com/document/d/1De9c0n27XdpQDzDf9Iz3VblJB5_ffW7W/view"
}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

def has_role(user):
    """Check if user has the allowed role"""
    return any(role.id == ALLOWED_ROLE_ID for role in user.roles)

# $receipts command to list all prefixes
@bot.command()
async def receipts(ctx):
    if not has_role(ctx.author):
        await ctx.send("receipt/gen access denied")
        return
    prefixes = "\n".join(template_links.keys())
    await ctx.author.send(f"Available templates:\n{prefixes}")
    await ctx.send("Success! Check your DMs.")

# Factory function to create individual prefix commands
def create_template_command(prefix, link):
    cmd_name = prefix[1:].replace(" ", "_")  # remove $ and spaces
    @bot.command(name=cmd_name)
    async def command(ctx):
        if not has_role(ctx.author):
            await ctx.send("receipt/gen access denied")
            return
        await ctx.author.send(link)
        await ctx.send("Success! Check your DMs.")
    return command

# Generate all prefix commands
for prefix, link in template_links.items():
    create_template_command(prefix, link)

bot.run(os.getenv("DISCORD_TOKEN"))
