
# Set all permissions for discord bot
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Set bot prefix as slash
client = commands.Bot(command_prefix='/', intents=intents)

# dictionary of secret santa participants
participants: dict[int, str] = dict()
interests: dict[int, list[str]] = dict()