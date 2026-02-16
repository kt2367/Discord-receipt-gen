import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)

ALLOWED_ROLE_ID = 1472751333286350981

# All prefixes and their view-only links
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
    "$lv pacific chill": "https://docs.google.com/document/d/1De9c0n27XdpQDzDf9Iz3VblJB5_ffW7W/view",
    "$armani stronger with you absolutely": "https://docs.google.com/document/d/1lisfjaFTCpRg8jnVNxjqR2dOLUew1eBJ/view",
    "$parfums de marley layton": "https://docs.google.com/document/d/1fCDCNP2QP88lV2RCU5nE04J5b3yxG1zg/view",
    "$dior miss dior blooming": "https://docs.google.com/document/d/12SueYEAD8vrhe1DUys2v_EF5wL2E0-Av/view",
    "$carolina herrera good girl eau de parfum coffee": "https://docs.google.com/document/d/1HS4WDQu21ZloZL460uLcvIeqSDO45h0_/view",
    "$chanel coco mademoiselle eau de parfum intense": "https://docs.google.com/document/d/1621MnoqvDy7TGU9toVyZU5H4i1S7sfxm/view",
    "$gucci bloom eau de parfum": "https://docs.google.com/document/d/1hqS2D_iOcy2ZnWuRUtf8P-FgD6okXadg/view",
    "$valentino donna eau de parfum": "https://docs.google.com/document/d/1lrfv0QEDLkd8qI1RmoMzNgRNhCkBYQdW/view",
    "$armani acqua di gio eau de toilette": "https://docs.google.com/document/d/1Y10rQqZMTTcee1vINbJZf9cMRo3m7UMW/view",
    "$initio oud for greatness": "https://docs.google.com/document/d/1QfBjRlUyaofhFOh9-DkLqGoNKdm6hr9T/view",
    "$creed silver mountain water": "https://docs.google.com/document/d/1WWLWlEqN9ylO8rGu-V-D2BQ3ftZSf_YK/view",
    "$ysl myslf eau de parfum": "https://docs.google.com/document/d/1rr2B0ZsR2E_HYv45wivpyYrOKfW21v6s/view",
    "$armani armani code parfum": "https://docs.google.com/document/d/1l782JM-vQzvOdbeA1fEE2ZbaYyaUX0p9/view",
    "$kilian angels share eau de parfum": "https://docs.google.com/document/d/1Wv_we_8nesGjO61s0boIXrV4L9nvhSEj/view",
    "$parfums de marly althair": "https://docs.google.com/document/d/18WIJhLvpsgKPVl0tl7DzrKAgQu2aBpL_/view",
    "$parfums de marley delina": "https://docs.google.com/document/d/1_-4E8n1WNPIc_QNjQGSenIyscqn2NTWT/view",
    "$prada paradoxe intense eau de parfum": "https://docs.google.com/document/d/1gYOujvmA0feHNWzOtOwAtC5bMr_TlYFR/view",
    "$creed milesime imperial": "https://docs.google.com/document/d/1rzhfYGrwqS8KBsuRISFFk7_614XVHHjN/view",
    "$lv city of stars": "https://docs.google.com/document/d/1wSEYk1LW2v3LXefGDZLQSL5KHNGH5lLd/view",
    "$lv after swim": "https://docs.google.com/document/d/1LK0E-3kwzkcdIrSTRFuyKUxQvfuRlvNW/view",
    "$tom ford lost cherry eau de parfum": "https://docs.google.com/document/d/13gCWaFrarh9tP8MJZ9BedEtDWIxYj1yM/view",
    "$tom ford fucking fabulous eau de parfum": "https://docs.google.com/document/d/1PjdugI3F4Ef6qoRwBT9f0_MsWg6TPw4G/view",
    "$carolina herrera bad boy cobalt": "https://docs.google.com/document/d/1qMjZL_XpwX-_yCoCMCNFlD8LgI9wrnjH/view",
    "$carolina herrara bad boy elixir eau de parfum woody leather": "https://drive.google.com/file/d/1jcvGZoQnjq627vhTHar2BOsL5NEAtF76/view",
    "$carolina herrara nyc 212 men": "https://docs.google.com/document/d/1LvdDnEymiK-ZEWsvOlnpI_AeK-uKsHTN/view",
    "$valentino donna born in roma yellow dream": "https://docs.google.com/document/d/1zSeU9ko2uXWGh3r5oSj1SoJUWBO6MFPX/view",
    "$initio desire without limit love beyond reason": "https://docs.google.com/document/d/1Mex7h9QCYXLmGjYBXeqKWf-1Yt_47EHj/view",
    "$versace bright crystal": "https://docs.google.com/document/d/1VnqDR6wOiPTVtu8jUhTgopPRYe0cjO_C/view",
    "$ysl mon paris": "https://docs.google.com/document/d/18AXBm902PiiCGfv2nGU4ctnhYGEPa3Cj/view",
    "$maison francis oud silk mood": "https://docs.google.com/document/d/1WWCKzxc_Pxx7RIegfO6swUv_Ehuly5lB/view",
    "$gucci flora gorgeous jasmine": "https://docs.google.com/document/d/1UKj0TrBlrV1ibgp_1quGmxh9woS5rP3T/view",
    "$versace eros flame": "https://docs.google.com/document/d/1GqG1pNIbLrno9cv0LGB_k1GaCrAgNfHu/view",
    "$chanel chance eau splendide": "https://docs.google.com/document/d/1AV9EdiBEd16CDr7HvJ-8rbgJZ5d2sAX2/view",
    "$creed absolu aventus": "https://docs.google.com/document/d/1_cOx9m7qbPsoDd-ZpWgNnfUlGEVjlVwE/view",
    "$dior jadore": "https://docs.google.com/document/d/1O29hlEvP5p2Zi-Xn-iORxwB4-iws836P/view",
    "$jpg le male le parfum": "https://docs.google.com/document/d/12GAEWiiqjiiPS4EvBNZHhJbB0B15uMxX/view",
    "$jpg scandal pour homme": "https://docs.google.com/document/d/1GXHqRi8IUrafKgsF-zq3cYIGleq7ZMh7/view",
    "$jpg gaultier²": "https://docs.google.com/document/d/1UH6SZWqGVXek2-AZgFCvKpcOYsdl3b7l/view",
    "$jpg le beau": "https://docs.google.com/document/d/14trotWq7haf7v4LyLmxoNG4Dx09PlJYB/view",
    "$valentino uomo born in roma the gold": "https://docs.google.com/document/d/1vE_TkZN7aItBuwruJxO1nPDRSZczAWF2/view",
    "$valentino uomo born in roma green stravaganza": "https://docs.google.com/document/d/1pntMpeglHKm-BNFgzSrohh65XcaajuyV/view",
    "$rabanne invictus eau de toilette": "https://docs.google.com/document/d/1VNI95MOFWAI8tZoqNA5wZvYgnd4Eirg7/view",
    "$lancome la via est belle": "https://docs.google.com/document/d/14s9SUhVXeeS7P5Eb1x57UQ2TceLlfNDW/view",
    "$chanel n°5": "https://docs.google.com/document/d/16K805hE-ZQcb_GwoA2nxXcqToS5TkCUq/view",
    "$armani stronger with you intensely": "https://docs.google.com/document/d/1ZfHJ67SOgtgU-Y13enfNRipEgj0Cfav7/view",
    "$armani my way": "https://docs.google.com/document/d/1hTicol5fTutN0KMOj0hs1KxMu30C3MkQ/view",
    "$byredo rose of no man's land": "https://docs.google.com/document/d/1WjFN-TaQkpXjTL-eAbIXuD4-xJ1rV3Hz/view",
    "$tom ford eau dombre leather": "https://docs.google.com/document/d/1kSQRCW-jk2VwZgLG6XWp9jumEFuOj9C2/view",
    "$tom ford bitter peach": "https://docs.google.com/document/d/1EJ7onm88rHexUuKL2CdO2waCP4W9u0H6/view",
    "$tom ford rose prick": "https://docs.google.com/document/d/1TD-4awsTSZJSoew_cShLdzqEKvMOBX3T/view",
    "$tom ford oud wood": "https://docs.google.com/document/d/1wgjsa_0JM6GiOD8Ysq9FR6OX5mLuBOwf/view",
    "$tom ford black orchid": "https://docs.google.com/document/d/18wGWIbLFRnqOuoDDgi7QU7VhSZTLDXX_/view",
    "$maison francis grand soir": "https://docs.google.com/document/d/15QX8aZit256Q2QYoeYUtyJAqd3fYTmve/view",
    "$valentino donna born in roma green": "https://docs.google.com/document/d/1bn6xNrfqpvQLzWQc4mRUOxth9H8NBVDB/view"
}

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

def has_role(user):
    return any(role.id == ALLOWED_ROLE_ID for role in user.roles)

# $receipts command with embed
@bot.command()
async def receipts(ctx):
    if not has_role(ctx.author):
        await ctx.send("receipt/gen access denied")
        return

    embed = discord.Embed(
        title="Available Templates",
        description="\n".join(template_links.keys()),
        color=discord.Color.blue()
    )
    embed.set_footer(text="Select a template using its prefix")
    await ctx.author.send(embed=embed)
    await ctx.send("✅ Check your DMs for all templates!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # First process commands like $receipts
    await bot.process_commands(message)

    # Now handle template DMs
    content = message.content.lower()
    if content in template_links:
        if not has_role(message.author):
            await message.channel.send("receipt/gen access denied")
        else:
            await message.author.send(template_links[content])
            await message.channel.send("✅ Success! Check your DMs.")

bot.run(os.getenv("DISCORD_TOKEN"))
