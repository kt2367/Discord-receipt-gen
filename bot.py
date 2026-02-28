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

ROLE_ID = 1472751333286350981  # Your special role ID

if not all([BOT_TOKEN, SENDER_EMAIL, SENDGRID_API_KEY]):
    print("Missing env vars!")
    exit(1)

BRANDS = ['Cartier', 'Denim Tears', 'Ksubi', 'Balenciaga', 'Sp5der', 'Nike', 'Adidas', 'Lululemon', 'Lanvin', 'Creed', 'Baccarat', 'Sephora', 'Apple']

brand_display = {  # same as before
    'Cartier': "Cartier",
    # ... (keep your full dict)
}

brand_info = {  # same logos
    'Cartier': {"logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Cartier_logo.svg/512px-Cartier_logo.svg.png"},
    # ... keep full
}

# Fake data (same as yours + more addresses for variety)
FAKE_NAMES = [...]  # your list
FAKE_ADDRESSES = [...]  # your list with states
FAKE_PAYMENT_METHODS = [...]  # your list

STATE_TAX_RATES = {  # 2026 rates, same
    "AL": 0.0946, # etc.
}

def get_state_from_address(address):
    # same regex function

user_emails = {}

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot online: {client.user}")

# New /role command
@tree.command(name="role", description="Give user the special role for a duration (e.g. 1d, 2w, 3m)")
@app_commands.describe(user="The user", duration="Time: e.g. 1d, 2w, 3m")
async def role_command(interaction: discord.Interaction, user: discord.Member, duration: str):
    if not interaction.user.guild_permissions.administrator:  # or check your role
        await interaction.response.send_message("You don't have permission.", ephemeral=True)
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
        delta = datetime.timedelta(days=months * 30)  # approx
    else:
        await interaction.response.send_message("Invalid duration (use 1d, 2w, 3m etc.)", ephemeral=True)
        return

    role = interaction.guild.get_role(ROLE_ID)
    if not role:
        await interaction.response.send_message("Role not found.", ephemeral=True)
        return

    await user.add_roles(role)
    await interaction.response.send_message(f"Gave {user.mention} the role for {duration}.", ephemeral=True)

    await asyncio.sleep(delta.total_seconds())
    await user.remove_roles(role)
    print(f"Removed role from {user} after {duration}")

# /setup and /generate same as before...

class GenerateModal(ui.Modal, title="Receipt Details"):
    # same inputs...

    async def on_submit(self, interaction: discord.Interaction):
        # ... same defer, email check, try block...

        # Randomization (same + delivery random)
        customer_name = random.choice(FAKE_NAMES)
        shipping_address = random.choice(FAKE_ADDRESSES)
        state = get_state_from_address(shipping_address)
        tax_rate = STATE_TAX_RATES.get(state, 0.0749)

        subtotal = price * quantity
        delivery = round(random.uniform(0, 25), 2)
        sales_tax = round(subtotal * tax_rate, 2)
        total = round(subtotal + delivery + sales_tax, 2)

        # ... order_id, tracking, payment, gift_wrapping same...

        # Updated hyper-realistic HTML (tiny fancy font, top banner, bottom footer)
        html_body = f"""
        <html>
        <body style="font-family: Georgia, 'Times New Roman', serif; background:#f8f8f8; color:#111; margin:0; padding:0; font-size:11px; line-height:1.4;">
        <div style="max-width:580px; margin:20px auto; background:#fff; border:1px solid #ccc; box-shadow:0 2px 10px rgba(0,0,0,0.1);">
        
        <!-- Top Banner: Red-to-black gradient with Cartier text -->
        <div style="background: linear-gradient(to right, #8B0000, #000000); padding:30px 20px; text-align:center;">
            <h1 style="color:#fff; margin:0; font-size:28px; font-weight:400; letter-spacing:2px;">Cartier</h1>
        </div>
        
        <div style="padding:25px 30px;">
            <h2 style="text-align:center; font-size:16px; margin:0 0 15px;">Acknowledgment of your order</h2>
            <p style="text-align:center; margin:0 0 20px;">Dear {customer_name},</p>
            <p style="margin:0 0 15px;">Thank you for shopping online with {self.brand}. We are pleased to acknowledge receipt of your order, the main details of which are set out below. Please check this email to ensure the details are accurate.</p>
            <p style="font-style:italic; font-size:10px; color:#555; margin:0 0 20px;">Please note: This acknowledgment is not a confirmation of your order. You will receive another email confirming acceptance at the time of shipment.</p>
            
            <p style="text-align:center; margin:10px 0;"><a href="#" style="color:#000; text-decoration:underline; font-size:12px;">To track your order online from your MyCartier account, click here: track order</a></p>
            
            <div style="background:#000; color:#fff; padding:12px; text-align:center; margin:20px 0;">
                ORDER N° {order_id}
            </div>
            
            <div style="background:#111; color:#eee; padding:15px; margin:15px 0;">
                <p style="margin:0 0 5px;"><strong>{self.item.value.strip()}</strong></p>
                <p style="margin:0 0 5px;">Silver / 52</p>
                <p style="margin:0 0 5px;">Gift wrapping added</p>
                <p style="text-align:right; margin:5px 0 0;">${price:,.2f} x {quantity}</p>
            </div>
            
            <table style="width:100%; font-size:11px; border-collapse:collapse;">
                <tr><td style="padding:4px 0;">Estimated delivery date:</td><td style="text-align:right;">{shipping_date}</td></tr>
                <tr><td style="padding:4px 0;">Payment Method:</td><td style="text-align:right;">{payment_method}</td></tr>
                <tr><td colspan="2" style="padding:10px 0 0; border-top:1px solid #aaa;"></td></tr>
                <tr><td style="padding:4px 0;"><strong>SUBTOTAL incl. tax</strong></td><td style="text-align:right;">${subtotal:,.2f}</td></tr>
                <tr><td style="padding:4px 0;"><strong>DELIVERY incl. tax</strong></td><td style="text-align:right;">${delivery:,.2f}</td></tr>
                <tr><td style="padding:4px 0;"><strong>Sales Tax ({tax_rate*100:.1f}%)</strong></td><td style="text-align:right;">${sales_tax:,.2f}</td></tr>
                <tr style="font-weight:bold; font-size:12px;"><td style="padding:8px 0 0;">TOTAL incl. tax</td><td style="text-align:right; padding:8px 0 0;">${total:,.2f}</td></tr>
            </table>
            
            <div style="margin:30px 0 0; padding:15px 0; border-top:1px solid #000; border-bottom:1px solid #000; background:#000; color:#fff;">
                <table style="width:100%; color:#fff; font-size:11px;">
                    <tr style="background:#800000;">
                        <th style="padding:8px;">DELIVERY ADDRESS</th>
                        <th style="padding:8px;">BILLING ADDRESS</th>
                        <th style="padding:8px;">NOTE</th>
                    </tr>
                    <tr>
                        <td style="padding:8px;">{customer_name}<br>{shipping_address}</td>
                        <td style="padding:8px;">{customer_name}<br>{shipping_address}</td>
                        <td style="padding:8px;">Shipping customized via modal during checkout.</td>
                    </tr>
                </table>
            </div>
            
            <p style="text-align:center; margin:20px 0; font-size:12px;">If you need further information please visit the <a href="#" style="color:#000; text-decoration:underline;">Contact us</a> page.</p>
            
            <div style="text-align:center; background:#111; color:#aaa; padding:10px; font-size:10px;">
                Stay Connected<br>
                Latest news • Cartier Official Channel • Mobile Applications
            </div>
            
            <div style="text-align:center; font-size:10px; color:#555; margin:15px 0;">
                TERMS OF USE • CONDITIONS OF SALE • CONTACT AN AMBASSADOR
            </div>
            
            <div style="font-size:10px; color:#444; text-align:center; line-height:1.3;">
                RLG Europe BV<br>PO Box 2967<br>NL-1000 CZ Amsterdam<br>Netherlands<br><br>
                Cartier Customer Contact Centre<br>+41 22 334 18 123<br>Email: CustomerService.RNE@cartier.com
            </div>
            
            <p style="font-size:9px; color:#777; text-align:center; margin:20px 0;">
                By clicking the links provided, you consent to our Privacy Notice & Conditions of Sale.<br>
                Copyright © 2025 Cartier
            </p>
        </div>
        </body>
        </html>
        """

        # Send via SendGrid (same as before)
        message = Mail(
            from_email=(SENDER_EMAIL, brand_display.get(self.brand, self.brand)),
            to_emails=email,
            subject=f"Your {self.brand} Order Confirmation",
            html_content=html_body
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Sent: {response.status_code}")

        await interaction.followup.send(embed=Embed(title="Sent!", description=f"Receipt to {email}", color=Colour.green()), ephemeral=True)

client.run(BOT_TOKEN)