import discord

import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import ui, app_commands

from random import choice

from datetime import datetime

# Load discord token from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Set all permissions for discord bot
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Set bot prefix as slash
client = commands.Bot(command_prefix='/', intents=intents)

# init makeshift server DB
# TODO: change discord.User.id : dict[discord.user.id] : list] -> discord.User.id : dict[discord.user.id] : tuple]
servers: dict[discord.Guild.id : dict[discord.User.id : list[str , list[str] , list[str]]]] = dict()
serversdistributed: dict[discord.Guild.id : bool] = dict()

def isparticipant(interaction : discord.Interaction) -> True | False:
    try:
        if interaction.user.name == getparticipant(interaction):
            return True
    except KeyError:
        return False
    except:
        print('caught excpetion in isparticipant')
        return False

def addparticipant(interaction : discord.Interaction) -> None:
    servers[interaction.guild.id][interaction.user.id][0] = interaction.user.name

def addinterest(interest : str, interaction : discord.Interaction) -> None:
    servers[interaction.guild.id][interaction.user.id][1].append(interest)

def addwishlist(wish : str, interaction : discord.Interaction) -> None:
    servers[interaction.guild.id][interaction.user.id][2].append(wish)

def getparticipant(interaction : discord.Interaction) -> str:
    return servers[interaction.guild.id][interaction.user.id][0]

def getinterest(interaction : discord.Interaction, name) -> list[str]:
    for key, value in servers[interaction.guild.id].items():
        if value[0] == name:
            return servers[interaction.guild.id][key][1]

def getwishlist(interaction : discord.Interaction, name) -> list[str]:    
    for key, value in servers[interaction.guild.id].items():
        if value[0] == name:
            return servers[interaction.guild.id][key][2]

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
        print(F'Error removing {guild.name} from servers.')

# Set bot status online
@client.event
async def on_ready():
    print(F'Logged in as {client.user}!')
    synced = await client.tree.sync()
    print(F'Slash Commands synced {str(len(synced))} commands! Waiting for active server sync...')
    serverslen = len(client.guilds)
    counter = 0
    for guild in client.guilds:
        try:
            servers[guild.id] = dict()
            counter += 1
            print(F'Added {guild.name} to active servers. ({counter}/{serverslen})')
        except:
            print(F'Error adding {guild.name} to active servers.')
    print(F'{counter}/{serverslen} active servers synced!')


# Removes the user from the secret santa list ( /remove )
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
    if len(servers[interaction.guild.id]) == 0:
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
    elif len(servers[interaction.guild.id]) == 0:
        await interaction.response.send_message(content="There are no participants in the Secret Santa List!", ephemeral=True)
    else:
        servers[interaction.guild.id].clear()
        del serversdistributed[interaction.guild.id] # can still be distributed but not yet cleared, forms cant be made though
        await interaction.response.send_message(content="I cleared the Secret Santa List!", ephemeral=True)
    

# Modal to fill out the wishlist form ( /form )
class Form(ui.Modal, title="Secret Santa Form"):
    interest = ui.TextInput(label='List your interests', placeholder="Pokemon, programming, typing...", style=discord.TextStyle.short)
    wishlist = ui.TextInput(label='List your wishlist items', placeholder="Socks, Java textbook, gaming mouse...", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        addinterest(f'{self.interest}', interaction)
        addwishlist(f'{self.wishlist}', interaction)
        await interaction.response.send_message(F"Interests: {self.interest}\nWishlist: {self.wishlist}", ephemeral=True)
    

# Modal to fill out the wishlist form ( /form )
@client.tree.command(name="form", description="Fill out the form to participate in Secret Santa!")
async def form(interaction: discord.Interaction):
    if interaction.guild.id in serversdistributed.keys():
        await interaction.response.send_message(F'Form creation for {interaction.guild.name} is disabled right now', ephemeral=True)
    elif isparticipant(interaction):
        await interaction.response.send_modal(Form())
    else:
        servers[interaction.guild.id][interaction.user.id] = [interaction.user.name, [], []]
        await interaction.response.send_modal(Form())


@client.tree.command(name="distribute", description="distribute secret santas")
@app_commands.describe(month="Month", day="Day", year="Year", time='time', timezone='timezone')
async def distribute(interaction: discord.Interaction, month : str, day : str, year : str, time : str, timezone : str):
    
    participants = [x[0] for x in servers[interaction.guild.id].values()] # discord user names can't be duplicated.
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(content="You don't have permission (Administrator) to distribute Secret Santas!", ephemeral=True)
    elif len(participants) <= 1:
        await interaction.response.send_message(content="There are not enough participants in the Secret Santa List!", ephemeral=True)
    else:
        # command that has a dropdown menu if you want to distribute (Yes or No) and forms will be closed
        print(participants)
        # init dict of participants and their assignees
        assigned : dict[discord.User.name : discord.User.name] = dict()
        # dms will be sent, data structs in here do not need to persist participants can just refer to dms.

        # iterate through list and for each participant assign a random participant from the list.
        for participant in participants:
            if participant in assigned:
                continue
            else:
                # get random participant from list.
                randsanta : str = choice(participants)

                # check if random participant is same as participant.
                while randsanta == participant:
                    randsanta = choice(participants)

                assigned[participant] = randsanta

        # send message to each participant with their assigned participant.    
        for membername in participants:
            emb = discord.Embed(
                title='Secret Santa Info',
                color=discord.Color.green()
            )
            emb.add_field(name='Gift Reciever', value=F'Your **__assigned secret santa__** is `@{assigned[membername]}`!')
            emb.add_field(name='Date and Time', value=F'{month}/{day}/{year} at {time}{timezone}!')
            emb.add_field(name='Their Interests', value=F'{getinterest(interaction, assigned[membername])}')
            emb.add_field(name='Their Wishlist', value=F'{getwishlist(interaction, assigned[membername])}')

            await interaction.guild.get_member_named(membername).send(embed=emb)
        
        serversdistributed[interaction.guild.id] = True


client.run(TOKEN)

# TODO: 
# TODO: 
# TODO: 
# TODO: 
# TODO: 