import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import ui, app_commands

# Load discord token from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Set all permissions for discord bot
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Set bot prefix as slash
client = commands.Bot(command_prefix='/', intents=intents)

# dictionary of secret santa participants
participants: dict[int, str] = dict()
interests: dict[int, list[str]] = dict()
wishlist: dict[int, list[str]] = dict()


# Set bot status online
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    synced = await client.tree.sync()
    print(f'Slash Commands synced {str(len(synced))} Commands')

# Adds the user to the secret santa list ( /add )
@client.tree.command(name="add", description="Add yourself to the Secret Santa list!")
async def add(interaction: discord.Interaction):
    if not interaction.user.id in participants:
        participants[interaction.user.id] = interaction.user.nick if interaction.user.nick != None else interaction.user.name
        interests[interaction.user.id] = []
        wishlist[interaction.user.id] = []
        await interaction.response.send_message(content=F"I added you to the Secret Santa List!", ephemeral=True)
    else:
        await interaction.response.send_message(content="You're already on the Secret Santa List!", ephemeral=True)

# Removes the user from the secret santa list ( /remove )
@client.tree.command(name="remove", description="Remove yourself from the Secret Santa list!")
async def remove(interaction: discord.Interaction):
    if interaction.user.id in participants:
        del participants[interaction.user.id]
        del interests[interaction.user.id]
        del wishlist[interaction.user.id]
        await interaction.response.send_message(content="I took you off the Secret Santa List!", ephemeral=True)
    else:
        await interaction.response.send_message(content="You're not on the Secret Santa List!", ephemeral=True)

# Lists all participants in the secret santa list ( /list )
@client.tree.command(name="list", description="List all participants in the Secret Santa list!")
async def list(interaction: discord.Interaction):
    if len(participants) == 0:
        await interaction.response.send_message(content="There are no participants in the Secret Santa List!", ephemeral=True)
    else:
        current = ""
        for key, value in participants.items():
            current += F"{participants[key]}\n"
        await interaction.response.send_message(content=F"Here are the participants in the Secret Santa List!\n{current}", ephemeral=True)

# Clears all participants in the secret santa list ( /clear )
@client.tree.command(name="clear", description="Clear all participants in the Secret Santa list!")
async def clear(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(content="You don't have permission (Administrator) to clear the Secret Santa List!", ephemeral=True)
    elif len(participants) == 0:
        await interaction.response.send_message(content="There are no participants in the Secret Santa List!", ephemeral=True)
    else:
        participants.clear()
        wishlist.clear()
        await interaction.response.send_message(content="I cleared the Secret Santa List!", ephemeral=True)

# Listener if a users nickname was changed
@client.event
async def on_member_update(before, after):
    if before.nick != after.nick:
        if after.id in participants:
            participants[after.id] = after.nick

# Modal practice --> input into dictionary?
class Form(ui.Modal, title="Secret Santa Form"):
    name = ui.TextInput(label='Enter your name', placeholder="My name is...", style=discord.TextStyle.short)
    interest = ui.TextInput(label='List your interests', placeholder="Pokemon, programming, typing...", style=discord.TextStyle.paragraph)
    wishlist = ui.TextInput(label='List your wishlist items', placeholder="Socks, Java textbook, gaming mouse...", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Name: {self.name}\nInterests: {self.interest}\nWishlist: {self.wishlist}", ephemeral=True)
        wishlist[interaction.user.id].append(F'{self.wishlist}')
        interests[interaction.user.id].append(F'{self.interest}')


# Modal to fill out the wishlist form ( /form )
@client.tree.command(name="form", description="Fill out form to participate in Secret Santa!")
async def form(interaction: discord.Interaction):
    if not interaction.user.id in participants:
        await interaction.response.send_message(content="You're not on the Secret Santa List! Please run `/add`", ephemeral=True)
    else:
        await interaction.response.send_modal(Form())

# Close Secret Santa Submissions ( /close )
@client.tree.command(name="close", description="Stop form creation!")
async def stop(interaction: discord.Interaction):
    # need to make class have an active attribute
    pass

client.run(TOKEN)
