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

# dictionary of servers with each server having its own santa dict
# multi server support --> dict[server_id : tuple[participants, interests, wishlist]]
servers: dict[discord.Guild.id : tuple[dict[discord.User.id : str | list[str]]]] = dict()
#participants: dict[discord.User.id : str] = dict()
#interests: dict[discord.User.id : list[str]] = dict()
#wishlist: dict[discord.User.id : list[str]] = dict()

def isparticipant(interaction : discord.Interaction) -> True | False:
    for key, value in servers[interaction.guild.id][0].items():
        if key == interaction.user.id:
            return True
    return False

def addparticipant(interaction : discord.Interaction) -> None:
    # server[id][0].update({interaction.user.id : interaction.user.name}) ???
    servers[interaction.guild.id][0] = {interaction.user.id : interaction.user.name}

def addinterest(interest : str, interaction : discord.Interaction) -> None:
    servers[interaction.guild.id][1][interaction.user.id].append(interest)

def addwishlist(wish : str, interaction : discord.Interaction) -> None:
    servers[interaction.guild.id][2][interaction.user.id].append(wish)

def getparticipant(interaction : discord.Interaction) -> str:
    return servers[interaction.guild.id][0][interaction.user.id]

def getinterest(interaction : discord.Interaction) -> list[str]:
    return servers[interaction.guild.id][1][interaction.user.id]

def getwishlist(interaction : discord.Interaction) -> list[str]:    
    return servers[interaction.guild.id][2][interaction.user.id]

@client.event
async def on_guild_join(guild):
    try:
        servers[guild.id] = (dict(), dict(), dict())
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
    print(f'We have logged in as {client.user}')
    synced = await client.tree.sync()
    print(f'Slash Commands synced {str(len(synced))} Commands')

# Adds the user to the secret santa list ( /add )
# TODO
# TODO TAKE OUT AND JUST HAVE IT AL BE DONE IN THE MODAL
# TODO
@client.tree.command(name="add", description="Add yourself to the Secret Santa list!")
async def add(interaction: discord.Interaction):
    if isparticipant(interaction):
        addparticipant(interaction) #TODO
        addinterest(interaction) #TODO
        addwishlist(interaction) #TODO

        #make 3 dicts named participants, interests, and wishlist
        p = dict()
        i = dict()
        w = dict()

        #add to servers dict
        
        servers[interaction.guild.id] = []
        await interaction.response.send_message(content=F"I added you to the Secret Santa List!", ephemeral=True)
    else:
        await interaction.response.send_message(content="You're already on the Secret Santa List!", ephemeral=True)

# Removes the user from the secret santa list ( /remove )
@client.tree.command(name="remove", description="Remove yourself from the Secret Santa list!")
async def remove(interaction: discord.Interaction):
    if isparticipant(interaction):
        del servers[interaction.guild.id][0][interaction.user.id]
        del servers[interaction.guild.id][1][interaction.user.id]
        del servers[interaction.guild.id][2][interaction.user.id]
        await interaction.response.send_message(content="I took you off the Secret Santa List!", ephemeral=True)
    else:
        await interaction.response.send_message(content="You're not on the Secret Santa List!", ephemeral=True)

# Lists all participants in the secret santa list ( /list )
@client.tree.command(name="list", description="List all participants in the Secret Santa list!")
async def list(interaction: discord.Interaction):
    if len(servers[interaction.guild.id][0].keys()) == 0:
        await interaction.response.send_message(content="There are no participants in the Secret Santa List!", ephemeral=True)
    else:
        current = ""
        for key, value in servers[interaction.guild.id][0].items():
            current += F"{key}:{value}\n"
        await interaction.response.send_message(content=F"Here are the participants in the Secret Santa List!\n{current}", ephemeral=True)

# Clears all participants in the secret santa list ( /clear )
@client.tree.command(name="clear", description="Clear the Secret Santa list for the server!")
async def clear(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(content="You don't have permission (Administrator) to clear the Secret Santa List!", ephemeral=True)
    elif len(servers[interaction.guild.id][0].keys()) == 0:
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
        await interaction.response.send_message(f"Name: {self.name}\nInterests: {self.interest}\nWishlist: {self.wishlist}", ephemeral=True)
        addinterest(self.interest, interaction)
        addwishlist(self.wishlist, interaction)
        


# Modal to fill out the wishlist form ( /form )
@client.tree.command(name="form", description="Fill out form to participate in Secret Santa!")
async def form(interaction: discord.Interaction):
    if isparticipant(interaction):
        await interaction.response.send_message(content="You're not on the Secret Santa List! Please run `/add`", ephemeral=True)
    else:
        await interaction.response.send_modal(Form())

# Close Secret Santa Submissions ( /close )
@client.tree.command(name="close", description="Stop form creation!")
async def stop(interaction: discord.Interaction):
    # need to make class have an active attribute
    pass

client.run(TOKEN)
