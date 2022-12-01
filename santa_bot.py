import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import ui, app_commands

# Load discord token from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Set all permissions for discord bot
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Set bot prefix as slash
client = commands.Bot(command_prefix='/', intents=intents)

# Set bot status online
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    synced = await client.tree.sync()
    print(f'Slash Commands synced {str(len(synced))} Commands')

# Basic slash command ( /test )
@client.tree.command(name="test", description="Basic test command")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message(content="Testing slash commands")

# Modal practice --> input into dictionary?
class Form(ui.Modal, title="Secret Santa Form"):
    name = ui.TextInput(label='Enter your name', placeholder="My name is...", style=discord.TextStyle.short)
    interest = ui.TextInput(label='List your interests', placeholder="Pokemon, programming, typing...", style=discord.TextStyle.paragraph)
    wishlist = ui.TextInput(label='List your wishlist items', placeholder="Socks, Java textbook, gaming mouse...", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Name: {self.name}\nInterests: {self.interest}\nWishlist: {self.wishlist}")

@client.tree.command()
async def modal(interaction: discord.Interaction):
    await interaction.response.send_modal(Form())

client.run(TOKEN)
