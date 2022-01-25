import json

import requests
from discord_webhook import DiscordWebhook, DiscordEmbed
from settings import webhook_url_cm

webhook = DiscordWebhook(url=webhook_url_cm)


def send_minted_counter(number_all_nfts, current_number_nfts):
    embed = DiscordEmbed(title='Projects minted', description=f"{current_number_nfts} of {number_all_nfts} minted",
                         color='03b2f8')

    webhook.add_embed(embed)
    response = webhook.execute()


def get_data_of_uri(uri):
    try:
        response = requests.get(uri)
        if response.status_code == 200:
            response_json = json.loads(response.text)
            image = response_json["image"]
            description = response_json["description"]
            return image, description
        else:
            return None, None
    except Exception as e:
        print("error getting uri of nft", e)
        return None, None


def send_new_unmited_nfts(unminted_list_of_8):
    embed = DiscordEmbed(title='unminted projects', color='03b2f8')
    content = ""
    for x in unminted_list_of_8:
        image_uri = x["uri"]
        image, description = get_data_of_uri(image_uri)
        if image is not None:
            content += f"`{x['name']}`\n\n{image}\n\n"
        else:
            content += f"`{x['name']}`\n\n"
    embed.description = content
    webhook.add_embed(embed)
    response = webhook.execute()
