import json
import os.path
import time

from cms_nft import get_cms_nft
from get_all_cm import compare_for_new_cm
from webhook_monitor import send_minted_counter, send_new_unmited_nfts
from discord_webhook import DiscordWebhook, DiscordEmbed
from cms_nft import get_cms_nft, get_data_of_uri

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
        what_changed = "items"
        return old_metadata["items_available"], new_metadata["items_available"], what_changed
    elif old_metadata["gatekeeper"]["gatekeeper_network"] != new_metadata["gatekeeper"]["gatekeeper_network"]:
        what_changed = "gatekeeper"
        if new_metadata["gatekeeper"]["gatekeeper_network"] is None:
            gatekeeper = "off"
        else:
            gatekeeper = "on"
        return gatekeeper, None, what_changed
    elif old_metadata["whitelist"]["mint"] != new_metadata["whitelist"]["mint"]:
        what_changed = "whitelist"
        if new_metadata["whitelist"]["mint"] is None:
            whitelist = "off"
        else:
            whitelist = "on"
        return whitelist, None, what_changed
    else:
        return None, None, None



def send_metadata_change_to_discord(cm_id, return_one, return_two, name, image, what_changed):
    title = "Something changed"
    if what_changed == "items":
        title = "Available items changed"
    elif what_changed == "whitelist":
        title = "Whitelist status changed"
    elif what_changed == "gatekeeper":
        title = "Gatekeeper status changed"
    webhook = DiscordWebhook(url=webhook_url_cm)
    if return_one is None:
        return_one = "not found"
    embed = DiscordEmbed(title=title, description=name, color='03b2f8')
    embed.add_embed_field(name='CM ID', value=cm_id, inline=False)
    if what_changed == "items":
        embed.add_embed_field(name='Stock change', value=f"{return_one} -> {return_two}", inline=False)
    elif what_changed == "whitelist":
        embed.add_embed_field(name='Whitelist status', value=return_one, inline=False)
    elif what_changed == "gatekeeper":
        embed.add_embed_field(name='Gatekeeper status', value=return_one, inline=False)
    if image is not None:
        embed.set_thumbnail(url=image)

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
            return_one, return_two, what_changed = compare_metadata(old_metadata, new_metadata)
            if what_changed is None:
                continue
            cms_nfts = get_cms_nft(cm_id, version)
            nft_name = "not found"
            if cms_nfts:
                try:
                    nft_name = cms_nfts["minted_nfts"][0]["nft_metadata"]["data"]["name"]
                    nft_uri = cms_nfts["minted_nfts"][0]["nft_metadata"]["data"]["uri"]
                except:
                    nft_name = cms_nfts["all_nfts"][0]["name"]
                    nft_uri = cms_nfts["all_nfts"][0]["uri"]
                image, description = get_data_of_uri(nft_uri)
            else:
                image, description = None, None
            send_metadata_change_to_discord(cm_id, return_one, return_two, nft_name, image, what_changed)
            save_metadata_to_file(new_metadata)
        time.sleep(60)


if __name__ == '__main__':
    main()
