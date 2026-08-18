
from flask import Flask
import threading

app = Flask('')

@app.route('/')
def home():
    return "Bot online 24/7"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

























import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

class TicketModal(discord.ui.Modal):
    def __init__(self, category_name):
        super().__init__(title=category_name)
        self.category_name = category_name

        self.bug_report = discord.ui.TextInput(
            label="Details",
            style=discord.TextStyle.long,
            placeholder="Please expand on what the issue is, so staff are able to deal with it swiftly.",
            required=True,
            max_length=1000
        )
        self.add_item(self.bug_report)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user

        channel_name = f"ticket-{member.name}"
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
        await interaction.response.send_message(f"Your ticket has been created in {channel.mention}!", ephemeral=True)
        
        embed_ticket = discord.Embed(
            title="Issue",
            description=f"{self.bug_report.value}\n\n*Thank you for reaching out. A staff member will receive prioritized support from our team!* 🌟",
            color=discord.Color.blue()
        )
        await channel.send(embed=embed_ticket, view=TicketStaffActionsView(member_id=member.id))

class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Scam Report", description="Scamming a token is prohibited.", emoji="💰"),
            discord.SelectOption(label="Player Unfair Play", description="The use of external software or hardware modifications.", emoji="🎯"),
            discord.SelectOption(label="Gameplay or Map Glitches", description="Do not exploit game or map bugs.", emoji="⚙️"),
            discord.SelectOption(label="Mid-Match Forfeit", description="Quitting during a match (round awarded to opponent).", emoji="🏳️")
        ]
        super().__init__(placeholder="Select Your Issue", min_values=1, max_values=1, custom_id="ticket_dropdown", options=options)

    async def callback(self, interaction: discord.Interaction):
        category_selected = self.values[0] if isinstance(self.values, list) else self.values
        await interaction.response.send_modal(TicketModal(category_name=category_selected))

class TicketDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

class TicketStaffActionsView(discord.ui.View):
    def __init__(self, member_id):
        super().__init__(timeout=None)
        self.member_id = member_id

    @discord.ui.button(label="🛑 Close", style=discord.ButtonStyle.danger, custom_id="close_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("This ticket will close in 5 seconds...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

    @discord.ui.button(label="📌 Claim", style=discord.ButtonStyle.success, custom_id="claim_btn")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        staff_member = interaction.user
        ticket_creator = guild.get_member(self.member_id)

        if not staff_member.guild_permissions.manage_channels and not staff_member.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only staff members can claim tickets!", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            staff_member: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        if ticket_creator:
            overwrites[ticket_creator] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            
        await interaction.channel.edit(overwrites=overwrites)
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.channel.send(f"👥 {staff_member.mention} will be assisting you.")

@bot.event
async def on_ready():
    bot.add_view(TicketDropdownView())
    print(f"Bot conectado como {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_tickets(ctx):
    embed = discord.Embed(
        title="T-10 Support",
        description="If you need assistance, please open a ticket by selecting the option below.\n\nChoose the category that best matches your issue, and our staff will help you as quickly as possible.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=TicketDropdownView())

keep_alive()
bot.run(os.environ.get("DISCORD_TOKEN"))

