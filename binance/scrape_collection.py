import json
import os
import time
from urllib.parse import urlparse, parse_qs
import requests
from discord_webhook import DiscordWebhook, DiscordEmbed
from settings import webhook_url

url = "https://www.binance.com/en/nft/collection/MetaRim?orderBy=list_time&orderType=-1&isBack=0&id=531414973044391937&order=list_time%40-1"


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
        floor_price = new_data["data"]["floorPrice"]["amount"]
        up_or_down = new_data["data"]["floorPrice"]["up"]
        changed_amount = new_data["data"]["floorPrice"]["changeAmount"]
        volume = new_data["data"]["dailyTradePrice"]["amount"]
        latest_price = new_data["data"]["lastTransaction"]["amount"]
        items_number = new_data["data"]["totalAsset"]["itemCount"]
        return floor_price, up_or_down, changed_amount, volume, latest_price, items_number
    else:
        return None, None, None, None, None, None

def send_to_discord(floor_price, up_or_down, changed_amount, volume, latest_price, items_number, collection_name):
    if up_or_down:
        dc_changed_amount = f"+{changed_amount}%"
    else:
        dc_changed_amount = f"-{changed_amount}%"
    webhook = DiscordWebhook(url=webhook_url)

    embed = DiscordEmbed(title=f'changes found for {collection_name}')
    if floor_price is None:
        floor_price = "not found"
    if volume is None:
        volume = "not found"
    if latest_price is None:
        latest_price = "not found"
    if items_number is None:
        items_number = "not found"
    # add fields to embed
    embed.add_embed_field(name='floor price', value=str(floor_price) + " BUSD")
    embed.add_embed_field(name='floor price change', value=str(dc_changed_amount))
    embed.add_embed_field(name='volume', value=str(volume) + " BUSD")
    embed.add_embed_field(name='latest price', value=str(latest_price) + " BUSD")
    embed.add_embed_field(name='items', value=str(items_number))

    webhook.add_embed(embed)

    response = webhook.execute()


def main():
    while 1:
        product_id, collection_name = get_pid_and_name_from_url(url)
        if product_id is None:
            continue
        collection_new = get_collection_data(product_id)
        file_exists = check_if_pid_exists(product_id)
        if file_exists:
            old_data = load_from_file(product_id)
            collection_changed = check_if_collection_changes(old_data, collection_new)
            if collection_changed:
                floor_price, up_or_down, changed_amount, volume, latest_price, items_number = check_collection_changes(old_data, collection_new)
                send_to_discord(floor_price, up_or_down, changed_amount, volume, latest_price, items_number,
                            collection_name)
        save_single_collection_to_file(collection_new, product_id)
        time.sleep(60*5)


if __name__ == '__main__':
    main()
