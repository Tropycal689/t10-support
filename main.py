import os
import asyncio
from threading import Thread
from flask import Flask
import discord
from discord.ext import commands

# --- WEB SERVER TO KEEP BOT ALIVE ON RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Online!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# --- DISCORD BOT CONFIGURATION ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- CLOSE TICKET BUTTON ---
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="🔒", custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("The ticket will close in 5 seconds...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

# --- CATEGORY DROPDOWN MENU ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Report Scam", description="Report a scam attempt or user", emoji="⚠️"),
            discord.SelectOption(label="Token Unban", description="Request an unban for your account", emoji="🔓"),
            discord.SelectOption(label="Report Player", description="Report a player for breaking rules", emoji="🚨"),
            discord.SelectOption(label="Bug Report", description="Report a system bug or glitch", emoji="🐛"),
            discord.SelectOption(label="Other Support", description="General inquiries and other issues", emoji="❓")
        ]
        super().__init__(placeholder="Select a category to open a ticket...", min_values=1, max_values=1, options=options, custom_id="ticket_select_menu")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        user = interaction.user

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel_name = f"{self.values[0]}-{user.name}".lower().replace(" ", "-")
        channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)

        ticket_embed = discord.Embed(
            title=f"Ticket: {self.values[0].replace('-', ' ').title()}",
            description=f"Welcome {user.mention}!\n\nPlease explain your issue in detail and provide any relevant evidence (screenshots, clips, etc.). Our support team will assist you shortly.",
            color=discord.Color.blue()
        )

        await channel.send(content=f"{user.mention}", embed=ticket_embed, view=CloseTicketView())
        await interaction.followup.send(f"✅ Your ticket has been created in {channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

@bot.event
async def on_ready():
    print(f"Bot successfully connected as {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_tickets(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="T-10 Support",
        description="If you need assistance, please open a ticket by selecting the option below.\n\nChoose the category that best matches your issue, and our staff will help you as quickly as possible.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=TicketView())

# --- INITIALIZATION ---
keep_alive()

bot.run("MTUzODk2OTU2ODk3Mjc3MTM0OA.GwkJ46.7BlRp-NmYn3gdyc7TpEamLYIhrmLgXAJfWsw9k")
