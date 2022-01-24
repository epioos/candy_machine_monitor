import datetime
import json
import os
import re
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


def get_image_url(url):
    response = requests.get(url)
    # print(response.status_code, response.reason)
    # print(response.text)
    results = re.findall("avatarUrl\":\"(.*?)\"", response.text)
    if results:
        return results[0]
    return None


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
        floor_currency = new_data["data"]["floorPrice"]["currency"]
        changed_amount = float(new_data["data"]["floorPrice"]["changeAmount"]).__round__(2)
        volume_currency = new_data["data"]["dailyTradePrice"]["currency"]
        volume = float(new_data["data"]["dailyTradePrice"]["amount"]).__round__(2)
        latest_price = float(new_data["data"]["lastTransaction"]["amount"]).__round__(2)
        latest_price_currency = new_data["data"]["lastTransaction"]["currency"]
        items_number = new_data["data"]["totalAsset"]["itemCount"]
        return floor_price, floor_currency, up_or_down, changed_amount, volume_currency, volume, latest_price, latest_price_currency, items_number
    else:
        return None, None, None, None, None, None, None, None, None


def send_to_discord(floor_price, floor_currency, up_or_down, changed_amount, volume_currency, volume, latest_price,
                    latest_price_currency, items_number, collection_name,
                    collection_id, image):
    if up_or_down:
        dc_changed_amount = f"+{changed_amount}%"
    else:
        dc_changed_amount = f"-{changed_amount}%"
    webhook = DiscordWebhook(
        url=webhook_url,
        username="Binance Marketplace",
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
    if floor_currency is None:
        floor_currency = " "
    if volume_currency is None:
        volume_currency = " "
    if latest_price_currency is None:
        latest_price_currency = " "
    if volume is None:
        volume = "not found"
    if latest_price is None:
        latest_price = "not found"
    if items_number is None:
        items_number = "not found"
    # add fields to embed
    embed.add_embed_field(
        name='Floor Price',
        value=f"{floor_price} {floor_currency} ({dc_changed_amount})",
        inline=False
    )
    embed.add_embed_field(
        name='Total Volume',
        value=f"{volume} {volume_currency}",
        inline=False
    )
    embed.add_embed_field(
        name='Last Sale Price',
        value=f"{latest_price} {latest_price_currency}",
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

    if image is not None:
        embed.set_thumbnail(
            url=image
        )
    embed.set_timestamp(
        timestamp=datetime.datetime.now().__str__()
    )
    webhook.add_embed(embed)
    response = webhook.execute()
    print(response.request.body)


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
                # todo check if old_data is none
                collection_changed = check_if_collection_changes(old_data, collection_new)  # error here
                if collection_changed:
                    floor_price, up_or_down, changed_amount, volume, latest_price, items_number = check_collection_changes(
                        old_data, collection_new)
                    image = get_image_url(collection_url)
                    print(floor_price, up_or_down, changed_amount, volume, latest_price, items_number,
                          collection_name, product_id, image)
                    send_to_discord(
                        floor_price,
                        up_or_down,
                        changed_amount,
                        volume,
                        latest_price,
                        items_number,
                        collection_name,
                        product_id,
                        image
                    )
                    save_single_collection_to_file(collection_new, product_id)
            else:
                save_single_collection_to_file(collection_new, product_id)
            time.sleep(5)


if __name__ == '__main__':
    main()
