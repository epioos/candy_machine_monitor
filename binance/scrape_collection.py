import json
import os
import time
from urllib.parse import urlparse, parse_qs
import requests
from discord_webhook import DiscordWebhook, DiscordEmbed

from binance_filehandler import BinanceFileHandler
from settings import webhook_url


def get_collection_data(product_id):
    try:
        json_url = f"https://www.binance.com/bapi/nft/v1/public/nft/home-layer-price?collectionId={product_id}"
        response = requests.get(json_url)
        print(response.json())
        return response.json()
    except Exception as e:
        print("error getting response of binance header url", e)


def get_pid_and_name_from_url(url):
    parsed_url = urlparse(url)
    try:
        collection_name = parsed_url.path.split("collection/")[1]
        return parse_qs(parsed_url.query)["id"][0], collection_name
    except:
        return None, None


def save_single_collection_to_file(collection, product_id):
    if not os.path.exists("./collection/"):
        os.mkdir("./collection/")
    with open("./collection/" + product_id + ".json", "w") as file:
        file.write(json.dumps(collection, indent=4))


def load_from_file(product_id):
    with open("./collection/" + product_id + ".json", "r") as file:
        return json.loads(file.read())


def check_if_pid_exists(product_id):
    if os.path.isfile("./collection/" + product_id + ".json"):
        return True
    else:
        return False


def check_if_collection_changes(old_data, new_data):
    if new_data["data"]["floorPrice"]["amount"] != old_data["data"]["floorPrice"]["amount"]:
        return True
    else:
        return False


def check_collection_changes(old_data, new_data):
    collection_changed = check_if_collection_changes(old_data, new_data)
    if collection_changed:
        floor_price = float(new_data["data"]["floorPrice"]["amount"]).__round__(2)
        up_or_down = new_data["data"]["floorPrice"]["up"]
        changed_amount = float(new_data["data"]["floorPrice"]["changeAmount"]).__round__(2)
        volume = float(new_data["data"]["dailyTradePrice"]["amount"]).__round__(2)
        latest_price = float(new_data["data"]["lastTransaction"]["amount"]).__round__(2)
        items_number = new_data["data"]["totalAsset"]["itemCount"]
        return floor_price, up_or_down, changed_amount, volume, latest_price, items_number
    else:
        return None, None, None, None, None, None


def send_to_discord(floor_price, up_or_down, changed_amount, volume, latest_price, items_number, collection_name,
                    collection_id):
    if up_or_down:
        dc_changed_amount = f"+{changed_amount}%"
    else:
        dc_changed_amount = f"-{changed_amount}%"
    webhook = DiscordWebhook(
        url=webhook_url,
        name="Binance Marketplace",
        avatar_url="https://cdn.discordapp.com/attachments/907443660717719612/928263386603589682/Q0bOuU6.png",
    )

    embed = DiscordEmbed(
        title=collection_name,
        url=f"https://www.binance.com/en/nft/collection/-?id={collection_id}",
        color=0xFCD535,
    )
    embed.set_author(
        name="Floor Price Changed",
        icon_url="https://i.imgur.com/rgexpCw.png"
    )
    if floor_price is None:
        floor_price = "not found"
    if volume is None:
        volume = "not found"
    if latest_price is None:
        latest_price = "not found"
    if items_number is None:
        items_number = "not found"
    # add fields to embed
    embed.add_embed_field(
        name='Floor Price',
        value=f"{floor_price} BUSD ({dc_changed_amount})",
        inline=False
    )
    embed.add_embed_field(
        name='Total Volume',
        value=f"{volume} BUSD",
        inline=False
    )
    embed.add_embed_field(
        name='Last Sale Price',
        value=f"{latest_price} BUSD",
        inline=False
    )
    embed.add_embed_field(
        name='Total Items in Collection',
        value=f"{items_number}",
        inline=False
    )
    embed.set_footer(
        text="MetaMint",
        icon_url="https://cdn.discordapp.com/attachments/907443660717719612/928263386603589682/Q0bOuU6.png"
    )
    embed.set_timestamp()
    webhook.add_embed(embed)
    response = webhook.execute()


def main():
    bn_fh = BinanceFileHandler()
    while 1:
        collections_to_monitor = bn_fh.read_file()
        for collection_url in collections_to_monitor:
            product_id, collection_name = get_pid_and_name_from_url(collection_url)
            if product_id is None:
                continue
            collection_new = get_collection_data(product_id)
            file_exists = check_if_pid_exists(product_id)
            if file_exists:
                old_data = load_from_file(product_id)
                collection_changed = check_if_collection_changes(old_data, collection_new)
                if collection_changed:
                    floor_price, up_or_down, changed_amount, volume, latest_price, items_number = check_collection_changes(
                        old_data, collection_new)
                    send_to_discord(floor_price, up_or_down, changed_amount, volume, latest_price, items_number,
                                    collection_name, product_id)
            save_single_collection_to_file(collection_new, product_id)
            time.sleep(5)


if __name__ == '__main__':
    main()
