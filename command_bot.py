import asyncio

import discord
import helheim
from discord.ext import commands

from ME.magiceden import MagicEden
from binance.get_information_on_command import send_binance_information
from binance_filehandler import BinanceFileHandler
from cm_filehandler import CmFileHandler
from cm_get_info_on_command import send_cm_information
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

helheim.auth('3aa9eba5-40f0-4e7e-836e-82661398430f')


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
    help_embed.add_field(
        name='!os',
        value='Shows all commands for managing open sea Monitor',
        inline=False
    )
    help_embed.add_field(
        name='!check',
        value='Shows all commands to get information about a collection',
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


def get_check_help_embed():
    help_embed = discord.Embed(
        title='Information check',
        description='Check Collection information for Magic Eden, Binance or Candy machine',
        color=0x00ff00
    )
    help_embed.add_field(
        name='!check binance [url]',
        value='Providing information about a collection on Binance',
        inline=False
    )
    help_embed.add_field(
        name='!check me [url path eg. https://magiceden.io/marketplace/botborgs -> botborgs]',
        value='Providing information about a collection on Magic Eden',
        inline=False
    )
    help_embed.add_field(
        name='!check cm [candy machine id]',
        value='Providing information about a collection on Candy machine',
        inline=False
    )
    return help_embed


def get_binance_help_embed():
    help_embed = discord.Embed(
        title='Binance Monitor',
        description='Manage Binance Monitor',
        color=0x00ff00
    )
    help_embed.add_field(
        name='!binance add',
        value='Add a Collection to Monitor List',
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
        value='Add a Collection to Monitor List',
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

def get_opensea_help_embed():
    help_embed = discord.Embed(
        title='Open Sea Monitor',
        description='Manage Open Sea Monitor',
        color=0x00ff00
    )
    help_embed.add_field(
        name='!os add [collection_name]',
        value='Add a Collection to Monitor List',
        inline=False
    )
    help_embed.add_field(
        name='!os remove [collection_name]',
        value='Remove a Collection from Monitor List',
        inline=False
    )
    help_embed.add_field(
        name='!os list',
        value='List Collections that are being monitored',
        inline=False
    )
    help_embed.add_field(
        name='!os help',
        value='Help overview',
        inline=False
    )
    help_embed.set_footer(
        text='Open Sea Monitor'
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


@client.command(
    name='check information',
    description='Check Collection information for Magic Eden, Binance or Candy machine',
    brief='Checking collection data',
    aliases=['check'],
    pass_context=True
)
async def check_information_command(ctx, *args):
    if len(args) == 0:
        return await ctx.send(embed=get_check_help_embed())
    elif len(args) == 2:
        if args[0] == 'binance':
            print("doing binance stuff")
            url = args[1]
            try:
                binance_embed = send_binance_information(url)
                print(binance_embed)
                return await ctx.send(embed=binance_embed)
            except Exception as e:
                print(e)
                return await ctx.send("Failed getting collection information")
        elif args[0] == 'me':
            try:
                me_monitor = MagicEden()
                me_embed = me_monitor.get_collection_info_for_command(args[1])
                print("me_embed", me_embed)
                return await ctx.send(embed=me_embed)
            except:
                return await ctx.send("Failed getting collection information")
        elif args[0] == 'cm':
            cm_id = args[1]
            cm_embed = send_cm_information(cm_id)
            if cm_embed is None:
                return await ctx.send("Failed getting collection information")
            return await ctx.send(embed=cm_embed)
        else:
            await ctx.send("No valid input")
            return await ctx.send(embed=get_check_help_embed())
    else:
        return await ctx.send(embed=get_check_help_embed())

@client.command(
    name='opensea',
    description='Manage OpenSea Monitor',
    brief='Manage OpenSea Monitor',
    aliases=['os'],
    pass_context=True
)
@commands.has_any_role(*staff_roles)
async def opensea_manage_monitor_command(ctx, *args):
    if len(args) == 0:
        return await ctx.send(embed=get_opensea_help_embed())
    elif len(args) == 1:
        if args[0] == "list":
            print("beep list stuff")
            return 0
    elif len(args) == 2:
        if args[0] == 'add':

            return 0
        elif args[0] == 'remove':
            print("doing remove stuff")
            return 0
        else:
            return await ctx.send(embed=get_opensea_help_embed())
    else:
        return await ctx.send(embed=get_opensea_help_embed())


client.run(discord_bot_token)
