import asyncio

import discord
from discord.ext import commands

from binance_filehandler import BinanceFileHandler
from cm_filehandler import CmFileHandler
from magicden_filehandler import MagicEdenFileHandler
from settings import discord_bot_token

# intents = discord.Intents.default()
# intents.members = True
client = commands.Bot(command_prefix='!')  # , intents=intents)  # Bot Prefix
client.remove_command('help')

staff_roles = [
    913498058770227232,  # owner
    907433230402203689,  # devs
    907433175905611826,  # admin
    913185856326631516,  # mod
]


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


def get_help_help_embed():
    help_embed = discord.Embed(
        title='MetaMint Monitor',
        description='Manage MetaMint Monitors',
        color=0x00ff00
    )
    help_embed.add_field(
        name='!binance',
        value='Shows all commands for managing Binance Monitor',
        inline=False
    )
    help_embed.add_field(
        name='!me',
        value='Shows all commands for managing MagicEden Monitor',
        inline=False
    )
    help_embed.add_field(
        name='!cm',
        value='Shows all commands for managing candy machine Monitor',
        inline=False
    )
    help_embed.set_footer(
        text='MetaMint Monitors'
    )
    return help_embed


@client.command(
    name='help',
    description='Help overview',
    brief='Help overview',
    aliases=['h', 'halp', 'commands']
)
async def help_command(ctx):
    await ctx.send(embed=get_help_help_embed())


def get_binance_help_embed():
    help_embed = discord.Embed(
        title='Binance Monitor',
        description='Manage Binance Monitor',
        color=0x00ff00
    )
    help_embed.add_field(
        name='!binance add',
        value='Add a Collection from Monitor List',
        inline=False
    )
    help_embed.add_field(
        name='!binance remove',
        value='Remove a Collection from Monitor List',
        inline=False
    )
    help_embed.add_field(
        name='!binance list',
        value='List Collections that are being monitored',
        inline=False
    )
    help_embed.add_field(
        name='!binance help',
        value='Help overview',
        inline=False
    )
    help_embed.set_footer(
        text='Binance Monitor'
    )
    return help_embed


def get_magiceden_help_embed():
    help_embed = discord.Embed(
        title='MagicEden Monitor',
        description='Manage MagicEden Monitor',
        color=0x00ff00
    )
    help_embed.add_field(
        name='!me add',
        value='Add a Collection from Monitor List',
        inline=False
    )
    help_embed.add_field(
        name='!me remove',
        value='Remove a Collection from Monitor List',
        inline=False
    )
    help_embed.add_field(
        name='!me list',
        value='List Collections that are being monitored',
        inline=False
    )
    help_embed.add_field(
        name='!me help',
        value='Help overview',
        inline=False
    )
    help_embed.set_footer(
        text='MagicEden Monitor'
    )
    return help_embed

def get_cm_help_embed():
    help_embed = discord.Embed(
        title='Candy machine Monitor',
        description='Manage Candy Machine Monitor',
        color=0x00ff00
    )
    help_embed.add_field(
        name='!cm add',
        value='Add a candy machine ID to Monitor List',
        inline=False
    )
    help_embed.add_field(
        name='!cm remove',
        value='Remove a candy machine ID from Monitor List',
        inline=False
    )
    help_embed.add_field(
        name='!cm list',
        value='List candy machine ID\'s that are being monitored',
        inline=False
    )
    help_embed.add_field(
        name='!cm help',
        value='Help overview',
        inline=False
    )
    help_embed.set_footer(
        text='Candy machine Monitor'
    )
    return help_embed


async def await_message(ctx):
    def check_choice(m):
        return ctx.author.id == m.author.id and m.channel.id == ctx.channel.id

    try:
        msg = await client.wait_for("message", check=check_choice, timeout=60)
    except asyncio.TimeoutError:
        return None
    else:
        return msg.content


@client.command(
    name='magiceden',
    description='Manage MagicEden Monitor',
    brief='Manage MagicEden Monitor',
    aliases=['me'],
    pass_context=True
)
@commands.has_any_role(*staff_roles)
async def magiceden_manage_monitor_command(ctx, *args):
    if len(args) == 0:
        return await ctx.send(embed=get_magiceden_help_embed())
    elif len(args) == 1:
        me_fh = MagicEdenFileHandler()
        if args[0] == 'add':
            await ctx.send(
                "Enter a slug to add to the monitor list.\n"
                "Example:\nhttps://www.magiceden.io/launchpad/teddy_bears_club -> teddy_bears_club"
            )
            answer = await await_message(ctx)
            if answer is not None:
                slug = answer.strip()
                me_fh.add_to_list(slug)
                await ctx.send(f"Added {answer} to the monitor list.")
            else:
                await ctx.send("No answer received. Cancelling.")
        elif args[0] == 'remove':
            await ctx.send(
                "Enter a slug to remove it from the monitor list.\n"
                "Example:\nhttps://www.magiceden.io/launchpad/teddy_bears_club -> teddy_bears_club"
            )
            answer = await await_message(ctx)
            if answer is not None:
                slug = answer.strip()
                me_fh.remove_from_list(slug)
                await ctx.send(f"Removed {answer} from the monitor list.")
            else:
                await ctx.send("No answer received. Cancelling.")
        elif args[0] == 'list':
            list_of_all_collections = me_fh.read_file()
            if len(list_of_all_collections) == 0:
                return await ctx.send("No collections are being monitored.")
            await ctx.send('\n'.join(list_of_all_collections))
        else:
            return await ctx.send(embed=get_magiceden_help_embed())
    else:
        return await ctx.send(embed=get_magiceden_help_embed())


@client.command(
    name='binance',
    description='Manage Binance Monitor',
    brief='Manage Binance Monitor',
    aliases=[],
    pass_context=True
)
@commands.has_any_role(*staff_roles)
async def binance_manage_monitor_command(ctx, *args):
    if len(args) == 0:
        return await ctx.send(embed=get_binance_help_embed())
    elif len(args) == 1:
        bn_fh = BinanceFileHandler()
        if args[0] == 'add':
            await ctx.send(
                "Enter a url to add a collection to the monitor list.\n"
                "Example:\nhttps://www.binance.com/en/nft/collection/DeRace?orderBy=list_time&orderType=-1&isBack=0&id=503115233992523776&order=list_time%40-1"
            )
            answer = await await_message(ctx)
            if answer is not None:
                binance_collection_url = answer.strip()
                bn_fh.add_to_list(binance_collection_url)
                await ctx.send(f"Added {answer} to the monitor list.")
            else:
                await ctx.send("No answer received. Cancelling.")
        elif args[0] == 'remove':
            await ctx.send(
                "Enter a url to remove a collection to the monitor list.\n"
                "Example:\nhttps://www.binance.com/en/nft/collection/DeRace?orderBy=list_time&orderType=-1&isBack=0&id=503115233992523776&order=list_time%40-1"
            )
            answer = await await_message(ctx)
            if answer is not None:
                binance_collection_url = answer.strip()
                bn_fh.remove_from_list(binance_collection_url)
                await ctx.send(f"Removed {answer} from the monitor list.")
            else:
                await ctx.send("No answer received. Cancelling.")
        elif args[0] == 'list':
            list_of_all_collections = bn_fh.read_file()
            if len(list_of_all_collections) == 0:
                return await ctx.send("No collections are being monitored.")
            await ctx.send('\n'.join(list_of_all_collections))
        else:
            return await ctx.send(embed=get_magiceden_help_embed())
    else:
        return await ctx.send(embed=get_magiceden_help_embed())

@client.command(
    name='candy machine',
    description='Manage candy machine Monitor',
    brief='Manage candy machine Monitor',
    aliases=['cm'],
    pass_context=True
)
@commands.has_any_role(*staff_roles)
async def cm_manage_monitor_command(ctx, *args):
    if len(args) == 0:
        return await ctx.send(embed=get_cm_help_embed())
    elif len(args) == 1:
        cm_fh = CmFileHandler()
        if args[0] == 'add':
            await ctx.send(
                "Enter a candy machine id to add it to the monitor list.\n"
                "Example:\nGWe3Thk4XPyxBVKrSt3px1EfDjiBtPNUaEpv5DeX7XfY"
            )
            answer = await await_message(ctx)
            if answer is not None:
                cm_id = answer.strip()
                cm_fh.add_to_list(cm_id)
                await ctx.send(f"Added {answer} to the monitor list.")
            else:
                await ctx.send("No answer received. Cancelling.")
        elif args[0] == 'remove':
            await ctx.send(
                "Enter a candy machine id to remove it from the monitor list.\n"
                "Example:\nGWe3Thk4XPyxBVKrSt3px1EfDjiBtPNUaEpv5DeX7XfY"
            )
            answer = await await_message(ctx)
            if answer is not None:
                cm_id = answer.strip()
                cm_fh.remove_from_list(cm_id)
                await ctx.send(f"Removed {answer} from the monitor list.")
            else:
                await ctx.send("No answer received. Cancelling.")
        elif args[0] == 'list':
            list_of_all_collections = cm_fh.read_file()
            if len(list_of_all_collections) == 0:
                return await ctx.send("No collections are being monitored.")
            await ctx.send('\n'.join(list_of_all_collections))
        else:
            return await ctx.send(embed=get_cm_help_embed())
    else:
        return await ctx.send(embed=get_cm_help_embed())


client.run(discord_bot_token)
