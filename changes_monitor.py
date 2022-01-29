import json
import os.path
import time

from webhook_monitor import send_minted_counter, send_new_unmited_nfts
from discord_webhook import DiscordWebhook, DiscordEmbed

from cm_change_files import read_from_file
from settings import webhook_url_cm
from theblockchainapi import TheBlockchainAPIResource, SolanaNetwork
from settings import API_ID_KEY, API_SECRET_KEY

BLOCKCHAIN_API_RESOURCE = TheBlockchainAPIResource(
    api_key_id=API_ID_KEY,
    api_secret_key=API_SECRET_KEY
)

from get_cm_metadata import get_metadata_of_cm, save_metadata_to_file


def get_version_of_cm(cm_id):
    with open("all_cm.json", "r") as file:
        json_data = json.loads(file.read())
        file.close()
        if cm_id in json_data["config_addresses_magic-eden-v1"] or cm_id in json_data["config_addresses_v1"]:
            return "v1"
        elif cm_id in json_data["config_addresses_v2"]:
            return "v2"
        else:
            return None


def get_old_data(cm_id):
    if not os.path.isfile(f"./cms_nfts/{cm_id}.json"):
        return None
    with open(f"./cms_nfts/{cm_id}.json", "r") as file:
        return json.loads(file.read())


def save_nfts_to_file(cm_id, data):
    with open(f"./cms_nfts/{cm_id}.json", "w") as file:
        file.write(json.dumps(data))


def read_metadata_from_file(cm_id):
    try:
        os.mkdir("./metadata/")
    except:
        pass
    try:
        with open(f"./metadata/{cm_id}.json", "r") as file:
            return json.loads(file.read())
    except Exception as e:
        print("error reading metadata to file", e)
        return None

def compare_metadata(old_metadata, new_metadata):
    if old_metadata["items_available"] != new_metadata["items_available"]:
        return old_metadata["items_available"], new_metadata["items_available"]
    else:
        return None, None

def send_metadata_change_to_discord(cm_id, old_availabe, new_available):
    webhook = DiscordWebhook(url=webhook_url_cm)
    if old_availabe is None:
        old_availabe = "not found"
    embed = DiscordEmbed(title='Available items changed', description=cm_id, color='03b2f8')
    embed.add_embed_field(name='Stock change', value=f"{old_availabe} -> {new_available}")

    # add embed object to webhook
    webhook.add_embed(embed)

    response = webhook.execute()

def main():
    while 1:
        print("hi")
        list_to_monitor = read_from_file()
        for cm_id in list_to_monitor:
            try:
                version = get_version_of_cm(cm_id)
            except:
                continue
            if version is None:
                continue
            old_metadata = read_metadata_from_file(cm_id)
            new_metadata = get_metadata_of_cm(cm_id, version)
            if old_metadata is None:
                save_metadata_to_file(new_metadata)
                continue
            if old_metadata is None:
                send_metadata_change_to_discord(cm_id, None, new_metadata["items_available"])
                save_metadata_to_file(new_metadata)
                continue
            old_availabe, new_available = compare_metadata(old_metadata, new_metadata)
            if old_availabe is None and new_available is None:
                continue
            send_metadata_change_to_discord(cm_id, old_availabe, new_available)
            save_metadata_to_file(new_metadata)
        time.sleep(60)


if __name__ == '__main__':
    main()

