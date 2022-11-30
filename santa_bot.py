import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

# Load discord token from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Set all permissions for discord bot
intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)

# Set bot prefix as slash
client = commands.Bot(command_prefix='/', intents=intents)

# Set bot status online
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

# Basic slash command ( /test )
@client.command()
async def test(ctx):
    await ctx.send("test")

client.run(TOKEN)
