import json
import os
import time

from discord_webhook import DiscordWebhook, DiscordEmbed

from settings import webhook_url

import requests


def get_header_response():
    try:
        url = "https://www.binance.com/bapi/nft/v1/public/nft/mystery-box/list?page=1&size=5"
        response = requests.get(url)
        return response.json()
    except Exception as e:
        print("error getting response of binance header url", e)


def save_collection_to_file(collection):
    if not os.path.exists("./headers/"):
        os.mkdir("./headers/")
    with open("./headers/" + collection["productId"] + ".json", "w") as file:
        file.write(json.dumps(collection, indent=4))


def load_from_file(product_id):
    with open("./headers/" + product_id + ".json", "r") as file:
        return json.loads(file.read())


def check_if_pid_exists(product_id):
    if os.path.isfile("./headers/" + product_id + ".json"):
        return True
    else:
        return False


def send_webhook(collection):
    start_time = int(collection['startTime']/1000)
    end_time = int(collection['endTime']/1000)
    webhook = DiscordWebhook(url=webhook_url)
    embed = DiscordEmbed(title='New Project found')
    embed.set_image(url=collection["image"])
    embed.add_embed_field(name='sale starts', value=f"<t:{start_time}:R>", inline=False)
    embed.add_embed_field(name='sale ends', value=f"<t:{end_time}:R>", inline=False)
    embed.add_embed_field(name='name', value=collection["name"], inline=False)
    embed.add_embed_field(name='product id', value=collection["productId"], inline=False)
    embed.add_embed_field(name='price', value=f"{collection['price']} BUSD", inline=False)
    embed.add_embed_field(name='link',
                          value=f"https://www.binance.com/en/nft/mystery-box/detail?number=1&productId={collection['productId']}")

    webhook.add_embed(embed)

    response = webhook.execute()


def main():
    while 1:
        response = get_header_response()
        if response is None:
            print("failed to get response")
            continue
        for collection in response["data"]:
            file_exists = check_if_pid_exists(collection["productId"])
            if file_exists:
                print("product already here")
                continue
            else:
                save_collection_to_file(collection)
                send_webhook(collection)
                print("new product found")
        time.sleep(60*5)


if __name__ == '__main__':
    main()
