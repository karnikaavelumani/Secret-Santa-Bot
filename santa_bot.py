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

# init makeshift server DB
servers: dict[int : dict[int : list[str , list[str] , list[str]]]] = dict() 

def isparticipant(interaction : discord.Interaction) -> True | False:
    try:
        if interaction.user.name == servers[interaction.guild.id][interaction.user.id][0]:
            return True
    except:
        return False

def addparticipant(interaction : discord.Interaction) -> None:
    #.update() ???
    servers[interaction.guild.id][interaction.user.id][0] = interaction.user.name

def addinterest(interest : str, interaction : discord.Interaction) -> None:
    servers[interaction.guild.id][interaction.user.id][1].append(interest)

def addwishlist(wish : str, interaction : discord.Interaction) -> None:
    servers[interaction.guild.id][interaction.user.id][2].append(wish)

def getparticipant(interaction : discord.Interaction) -> str:
    return servers[interaction.guild.id][interaction.user.id][0]

def getinterest(interaction : discord.Interaction) -> list[str]:
    return servers[interaction.guild.id][interaction.user.id][1]

def getwishlist(interaction : discord.Interaction) -> list[str]:    
    return servers[interaction.guild.id][interaction.user.id][2]

@client.event
async def on_guild_join(guild):
    try:
        # TODO Use a shelve dict to make the server dict persistent
        servers[guild.id] = {guild.id : dict()}
        print(F'Bot joined {guild.name}. Added {guild.name} to servers.')
    except:
        print(F'Error adding {guild.name} to servers.')

@client.event
async def on_guild_remove(guild):
    try:
        name = guild.name
        del servers[guild.id]
        print(F'Bot left {name}. Removed {name} from servers.')
    except:
        print(F'Error removing {guild.name} from servers dict')

# Set bot status online
@client.event
async def on_ready():
    print(F'Logged in as {client.user}!')
    synced = await client.tree.sync()
    print(F'Slash Commands synced {str(len(synced))} commands!')
    servers[1156821909074358423] = dict()

# Removes the user from the secret santa list (/remove)
@client.tree.command(name="remove", description="Remove yourself from the Secret Santa list!")
async def remove(interaction: discord.Interaction):
    if isparticipant(interaction):
        del servers[interaction.guild.id][interaction.user.id]
        await interaction.response.send_message(content="I took you off the Secret Santa List!", ephemeral=True)
    else:
        await interaction.response.send_message(content="You're not on the Secret Santa List!", ephemeral=True)

# Lists all participants in the secret santa list ( /list )
@client.tree.command(name="list", description="List all participants in the Secret Santa list!")
async def list(interaction: discord.Interaction):
    if len(servers[interaction.guild.id].keys()) == 0:
        await interaction.response.send_message(content="There are no participants in the Secret Santa List!", ephemeral=True)
    else:
        current = ""
        for value in servers[interaction.guild.id].values():
            current += F"{value[0]}\n"
        await interaction.response.send_message(content=F"Here are the participants in the Secret Santa List!\n{current}", ephemeral=True)

# Clears all participants in the secret santa list ( /clear )
@client.tree.command(name="clear", description="Clear the Secret Santa list for the server!")
async def clear(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(content="You don't have permission (Administrator) to clear the Secret Santa List!", ephemeral=True)
    elif len(servers[interaction.guild.id][interaction.user.id].keys()) == 0:
        await interaction.response.send_message(content="There are no participants in the Secret Santa List!", ephemeral=True)
    else:
        servers[interaction.guild.id].clear()
        await interaction.response.send_message(content="I cleared the Secret Santa List!", ephemeral=True)


# # Listener if a users nickname was changed
# @client.event
# async def on_member_update(before, after):
#     if after.id in participants:
#         participants[before.id] = after.name if after.nick == None else after.nick
    

# Modal practice --> input into dictionary?
class Form(ui.Modal, title="Secret Santa Form"):
    name = ui.TextInput(label='Enter your name', placeholder="My name is...", style=discord.TextStyle.short)
    interest = ui.TextInput(label='List your interests', placeholder="Pokemon, programming, typing...", style=discord.TextStyle.paragraph)
    wishlist = ui.TextInput(label='List your wishlist items', placeholder="Socks, Java textbook, gaming mouse...", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        addinterest(f'{self.interest}', interaction)
        addwishlist(f'{self.wishlist}', interaction)
        await interaction.response.send_message(f"Name: {self.name}\nInterests: {self.interest}\nWishlist: {self.wishlist}", ephemeral=True)
        

# Modal to fill out the wishlist form ( /form )
@client.tree.command(name="form", description="Fill out form to participate in Secret Santa!")
async def form(interaction: discord.Interaction):
    if isparticipant(interaction):
        await interaction.response.send_modal(Form())
    else:
        servers[interaction.guild.id][interaction.user.id] = [interaction.user.name, [], []]
        await interaction.response.send_modal(Form())


client.run(TOKEN)
