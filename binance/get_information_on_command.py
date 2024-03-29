from discord import Embed

from binance.scrape_collection import get_pid_and_name_from_url, get_collection_data, get_image_url
from discord_webhook import DiscordWebhook, DiscordEmbed

from settings import webhook_url_binance


def get_relevant_info_from_response(collection_response_data):
    try:
        floor_price = float(collection_response_data["data"]["floorPrice"]["amount"]).__round__(2)
        up_or_down = collection_response_data["data"]["floorPrice"]["up"]
        floor_currency = collection_response_data["data"]["floorPrice"]["currency"]
        changed_amount = float(collection_response_data["data"]["floorPrice"]["changeAmount"]).__round__(2)
        volume_currency = collection_response_data["data"]["dailyTradePrice"]["currency"]
        volume = float(collection_response_data["data"]["dailyTradePrice"]["amount"]).__round__(2)
        latest_price = float(collection_response_data["data"]["lastTransaction"]["amount"]).__round__(2)
        latest_price_currency = collection_response_data["data"]["lastTransaction"]["currency"]
        items_number = collection_response_data["data"]["totalAsset"]["itemCount"]
        return floor_price, floor_currency, up_or_down, changed_amount, volume_currency, volume, latest_price, latest_price_currency, items_number
    except:
        print("couldnt get information from binance for information command")
        return None, None, None, None, None, None, None, None, None


def binance_information_embed(floor_price, floor_currency, up_or_down, changed_amount, volume_currency, volume,
                                latest_price, latest_price_currency, items_number, collection_name, collection_id,
                                image_url):
    try:
        if up_or_down:
            dc_changed_amount = f"+{changed_amount}%"
        else:
            dc_changed_amount = f"-{changed_amount}%"
        if collection_name is None:
            collection_name ="not found"
        embed = Embed(
            title=collection_name,
            url=f"https://www.binance.com/en/nft/collection/-?id={str(collection_id)}",
            color=0xFCD535,
        )
        embed.set_author(
            name="information found",
            icon_url="https://i.imgur.com/rgexpCw.png"
        )
        embed.add_field(name='Floor Price',
                        value=f"{floor_price} {floor_currency} ({dc_changed_amount})",
                        inline=False)

        embed.add_field(name='Total Volume',
                        value=f"{volume} {volume_currency}",
                        inline=False)

        embed.add_field(
            name='Last Sale Price',
            value=f"{latest_price} {latest_price_currency}",
            inline=False
        )
        embed.add_field(
            name='Total Items in Collection',
            value=f"{items_number}",
            inline=False
        )

        embed.set_footer(
            text="MetaMint",
            icon_url="https://cdn.discordapp.com/attachments/907443660717719612/928263386603589682/Q0bOuU6.png"
        )
        if image_url is not None:
            embed.set_image(url=image_url)
        return embed
    except Exception as e:
        print("couldnt get information for binance info command", e)
        return None


def send_binance_information(url):
    collection_id, collection_name = get_pid_and_name_from_url(url)
    collection_response_data = get_collection_data(collection_id)
    image_url = get_image_url(url)
    floor_price, floor_currency, up_or_down, changed_amount, volume_currency, volume, latest_price, latest_price_currency, items_number = get_relevant_info_from_response(
        collection_response_data)
    return binance_information_embed(floor_price, floor_currency, up_or_down, changed_amount, volume_currency, volume,
                                latest_price, latest_price_currency, items_number, collection_name, collection_id,
                                image_url)

