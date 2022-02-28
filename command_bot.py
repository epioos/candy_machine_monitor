import asyncio
import datetime
import json
import os

import discord
# import helheim
from discord.ext import commands

from ME.magiceden import MagicEden
from binance.get_information_on_command import send_binance_information
from binance_filehandler import BinanceFileHandler
from cm_filehandler import CmFileHandler
from cm_get_info_on_command import send_cm_information
from eth_stuff.api import Backend
from magicden_filehandler import MagicEdenFileHandler
from opensea_filehandler import OpenSeaFileHandler
from nifty_filehandler import NiftyFileHandler
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


# helheim.auth('3aa9eba5-40f0-4e7e-836e-82661398430f')


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
        name='!nifty',
        value='Shows all commands for Nifty Gateway Monitor',
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
    help_embed.add_field(
        name='!cm remove_all',
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


def get_nifty_help_embed():
    help_embed = discord.Embed(
        title='Nifty Gateway Monitor',
        description='Manage Nifty Gateway Monitor',
        color=0x00ff00
    )
    help_embed.add_field(
        name='!nifty add',
        value='Add a Collection ID to Monitor List',
        inline=False
    )
    help_embed.add_field(
        name='!nifty remove',
        value='Remove a Collection ID from Monitor List',
        inline=False
    )
    help_embed.add_field(
        name='!nifty list',
        value='List Collections ID\'s that are being monitored',
        inline=False
    )
    help_embed.add_field(
        name='!nifty help',
        value='Help overview',
        inline=False
    )
    help_embed.set_footer(
        text='Nifty Gateway Monitor'
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
    me_fh = MagicEdenFileHandler()
    if len(args) == 0:
        return await ctx.send(embed=get_magiceden_help_embed())
    elif len(args) == 1:
        if args[0] == 'list':
            list_of_all_collections = me_fh.read_file()
            if len(list_of_all_collections) == 0:
                return await ctx.send("No collections are being monitored.")
            await ctx.send('\n'.join(list_of_all_collections))
        else:
            return await ctx.send(embed=get_magiceden_help_embed())
    elif len(args) == 2:
        if args[0] == 'add':
            answer = args[1]
            if answer is not None:
                slug = answer.strip()
                me_fh.add_to_list(slug)
                await ctx.send(f"Added {answer} to the monitor list.")
            else:
                await ctx.send("No answer received. Cancelling.")
        elif args[0] == 'remove':
            answer = args[1]
            if answer is not None:
                slug = answer.strip()
                me_fh.remove_from_list(slug)
                await ctx.send(f"Removed {answer} from the monitor list.")
            else:
                await ctx.send("No answer received. Cancelling.")
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
    bn_fh = BinanceFileHandler()
    if len(args) == 0:
        return await ctx.send(embed=get_binance_help_embed())
    elif len(args) == 1:
        if args[0] == 'list':
            list_of_all_collections = bn_fh.read_file()
            if len(list_of_all_collections) == 0:
                return await ctx.send("No collections are being monitored.")
            await ctx.send('\n'.join(list_of_all_collections))
        else:
            return await ctx.send(embed=get_binance_help_embed())
    elif len(args) == 2:
        if args[0] == 'add':
            answer = args[1]
            if answer is not None:
                binance_collection_url = answer.strip()
                bn_fh.add_to_list(binance_collection_url)
                await ctx.send(f"Added {answer} to the monitor list.")
            else:
                await ctx.send("No answer received. Cancelling.")
        elif args[0] == 'remove':
            answer = args[1]
            if answer is not None:
                binance_collection_url = answer.strip()
                bn_fh.remove_from_list(binance_collection_url)
                await ctx.send(f"Removed {answer} from the monitor list.")
            else:
                await ctx.send("No answer received. Cancelling.")
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
    cm_fh = CmFileHandler()
    if len(args) == 0:
        return await ctx.send(embed=get_cm_help_embed())
    if len(args) == 1:
        if args[0] == 'list':
            list_of_all_collections = cm_fh.read_file()
            if len(list_of_all_collections) == 0:
                return await ctx.send("No collections are being monitored.")
            await ctx.send('\n'.join(list_of_all_collections))
        elif args[0] == 'remove_all':
            cm_fh.remove_all_from_list()
            await ctx.send("All CM Id's removed from list")
        else:
            return await ctx.send(embed=get_cm_help_embed())
    elif len(args) == 2:
        if args[0] == 'add':
            answer = args[1]
            if answer is not None:
                cm_id = answer.strip()
                cm_fh.add_to_list(cm_id)
                await ctx.send(f"Added {answer} to the monitor list.")
            else:
                await ctx.send("No answer received. Cancelling.")
        elif args[0] == 'remove':
            answer = args[1]
            if answer is not None:
                cm_id = answer.strip()
                cm_fh.remove_from_list(cm_id)
                await ctx.send(f"Removed {answer} from the monitor list.")
            else:
                await ctx.send("No answer received. Cancelling.")
        else:
            return await ctx.send(embed=get_cm_help_embed())
    else:
        return await ctx.send(embed=get_cm_help_embed())


@client.command(
    name='opensea',
    description='Manage OpenSea Monitor',
    brief='Manage OpenSea Monitor',
    aliases=['os'],
    pass_context=True
)
@commands.has_any_role(*staff_roles)
async def opensea_manage_monitor_command(ctx, *args):
    os_fh = OpenSeaFileHandler()
    if len(args) == 0:
        return await ctx.send(embed=get_opensea_help_embed())
    if len(args) == 1:
        if args[0] == 'list':
            list_of_all_collections = os_fh.read_file()
            if len(list_of_all_collections) == 0:
                return await ctx.send("No collections are being monitored.")
            await ctx.send('\n'.join(list_of_all_collections))
        else:
            return await ctx.send(embed=get_opensea_help_embed())
    elif len(args) == 2:
        if args[0] == 'add':
            answer = args[1]
            if answer is not None:
                collection_name = answer.strip()
                os_fh.add_to_list(collection_name)
                await ctx.send(f"Added {answer} to the monitor list.")
            else:
                await ctx.send("No answer received. Cancelling.")
        elif args[0] == 'remove':
            answer = args[1]
            if answer is not None:
                collection_name = answer.strip()
                os_fh.remove_from_list(collection_name)
                await ctx.send(f"Removed {answer} from the monitor list.")
            else:
                await ctx.send("No answer received. Cancelling.")
        else:
            return await ctx.send(embed=get_opensea_help_embed())
    else:
        return await ctx.send(embed=get_opensea_help_embed())

@client.command(
    name='nifty',
    description='Manage Nifty Gateway Monitor',
    brief='Manage Nifty Gateway Monitor',
    aliases=[],
    pass_context=True
)
@commands.has_any_role(*staff_roles)
async def nifty_manage_monitor_command(ctx, *args):
    nifty_fh = NiftyFileHandler()
    if len(args) == 0:
        return await ctx.send(embed=get_nifty_help_embed())
    elif len(args) == 1:
        if args[0] == 'list':
            list_of_all_collections = nifty_fh.read_file()
            if len(list_of_all_collections) == 0:
                return await ctx.send("No collections are being monitored.")
            await ctx.send('\n'.join(list_of_all_collections))
        else:
            return await ctx.send(embed=get_nifty_help_embed())
    elif len(args) == 2:
        if args[0] == 'add':
            answer = args[1]
            if answer is not None:
                nifty_collection_url = answer.strip()
                nifty_fh.add_to_list(nifty_collection_url)
                await ctx.send(f"Added {answer} to the monitor list.")
            else:
                await ctx.send("No answer received. Cancelling.")
        elif args[0] == 'remove':
            answer = args[1]
            if answer is not None:
                nifty_collection_url = answer.strip()
                nifty_fh.remove_from_list(nifty_collection_url)
                await ctx.send(f"Removed {answer} from the monitor list.")
            else:
                await ctx.send("No answer received. Cancelling.")
        else:
            return await ctx.send(embed=get_nifty_help_embed())
    else:
        return await ctx.send(embed=get_nifty_help_embed())


@client.command(
    name='check',
    description='Check Collection information for Magic Eden, Binance or Candy machine',
    brief='Checking collection data',
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
    name='eth',
    description='Check ETH Contract information',
    brief='Check ETH Contract information',
    aliases=['contract', 'ethereum'],
    pass_context=True
)
async def eth_command(ctx, contract_address):
    backend = Backend()
    target_contract_address = contract_address.strip()
    contract_checksum = backend.get_checksum(target_contract_address)
    contract_abi = backend.get_contract_abi_from_etherscan(contract_checksum)
    contract = backend.web3.eth.contract(address=contract_checksum, abi=contract_abi)
    all_events = backend.get_events_from_contract(contract)
    # print(all_events)
    all_functions = backend.get_functions_from_contract(contract)
    # print(all_functions)
    if all_functions is not None:
        current_work_dir = os.getcwd()
        func_file = os.path.join(current_work_dir, f'functions_{contract_checksum}.json')
        with open(func_file, 'w') as f:
            json.dump(all_functions, f, indent=4)
    contract_creator = backend.get_contract_creator(contract)
    # print(contract_creator)
    possible_flip_sale_functions = backend.get_possible_flip_sale_functions(all_functions)
    # print(possible_flip_sale_functions)
    possible_mint_functions = backend.get_possible_mint_functions(all_functions)

    pending_transactions = backend.get_pending_transactions_for_address(contract_checksum)
    # print(possible_mint_functions)
    # await ctx.send(f"Contract creator: {contract_creator}")
    # await ctx.send(f"Contract address: {contract_checksum}")
    # await ctx.send(f"Contract ABI: {contract_abi}")
    # await ctx.send(f"Events: {all_events}")
    # await ctx.send(f"Functions: {all_functions}")
    if all_functions is not None:
        embed = discord.Embed(
            title=f"ETH Contract {contract_checksum}",
            description=f"**Contract creator**: [{contract_creator}](https://etherscan.io/address/{contract_creator})\n"
                        f"**Possible Mint Functions:** {', '.join(possible_mint_functions)}\n"
                        f"**Possible Flip Sale Functions:** {', '.join(possible_flip_sale_functions)}\n"
                        f"**Events**: {', '.join(all_events)}\n"
                        f"**Pending Transactions**: {pending_transactions}\n",
            color=0x83eaca,
            url=f"https://etherscan.io/address/{contract_address}"
        )
        embed.set_footer(
            text=f"MetaMint",
            icon_url="https://media.discordapp.net/attachments/907443660717719612/928263386603589682/Q0bOuU6.png"
        )
        embed.timestamp = datetime.datetime.now()

        batch_size = 8
        read_functions = []
        write_functions = []
        for i in range(0, len(all_functions), batch_size):
            todo = all_functions[i:i + batch_size]
            funcs_str = ""
            for x in todo:
                function_name = x['name']
                inputs = x['inputs']
                outputs = x['outputs']
                inputs_str = ""
                outputs_str = ""
                for y in inputs:
                    inputs_str += f"{function_name} ({y['type']}), "
                if len(outputs) > 0:
                    for z in outputs:
                        outputs_str += f"{function_name}({z['type']}), "
                funcs_str += f"`{function_name}({inputs_str[:-2]})`"
                if len(outputs) > 0:
                    read_functions.append(f"`{function_name}({inputs_str[:-2]})`")
                else:
                    write_functions.append(f"`{function_name}({inputs_str[:-2]})`")

        for i in range(0, len(read_functions), batch_size):
            todo = read_functions[i:i + batch_size]
            read_str = ""
            for x in todo:
                read_str += f"{x}\n"
            embed.add_field(name=f"Read Functions {i}-{i + batch_size}", value=read_str, inline=False)

        for i in range(0, len(write_functions), batch_size):
            todo = write_functions[i:i + batch_size]
            write_str = ""
            for x in todo:
                write_str += f"{x}\n"
            embed.add_field(name=f"Write Functions {i}-{i + batch_size}", value=write_str, inline=False)
        # embed.add_field(name=f"Functions {i}-{i + batch_size}", value=funcs_str, inline=False)
        current_work_dir = os.getcwd()
        func_file = os.path.join(current_work_dir, f'functions_{contract_checksum}.json')
        await ctx.send(
            file=discord.File(func_file),
            embed=embed
        )
        os.remove(func_file)


client.run(discord_bot_token)
