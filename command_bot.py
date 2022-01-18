from discord.ext import commands

bot = commands.Bot(command_prefix='$')

@bot.command()
async def info_cm(ctx, cm_id):
    pass