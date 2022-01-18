import json
import os.path

from webhook_monitor import send_minted_counter, send_new_unmited_nfts

from cm_change_files import read_from_file

from theblockchainapi import TheBlockchainAPIResource, SolanaNetwork, SolanaCandyMachineContractVersion
from settings import API_ID_KEY, API_SECRET_KEY

BLOCKCHAIN_API_RESOURCE = TheBlockchainAPIResource(
    api_key_id=API_ID_KEY,
    api_secret_key=API_SECRET_KEY
)


def get_cms_nft(cm_id, version, verbose=False, current_try=0):
    max_retries = 5
    if current_try >= max_retries:
        print("too many retries", cm_id)
        return None
    current_try += 1
    try:
        assert API_ID_KEY is not None
        assert API_SECRET_KEY is not None
    except AssertionError:
        raise Exception("Api key pair not found")
    if version == "v1":
        print(f"Retrieving all NFTs from the V1 candy machine with ID {cm_id}... "
              f"This API call can take around 45 seconds...")
        try:
            result = BLOCKCHAIN_API_RESOURCE.get_all_nfts_from_candy_machine(
                candy_machine_id=cm_id,
                network=SolanaNetwork.MAINNET_BETA
            )
            return result
        except:
            print("error getting cm nft info", cm_id)
            return get_cms_nft(cm_id, version, verbose, current_try)

    elif version == "v2":
        # NOTE: With v2 candy machines, more work is required... see below.
        print(f"Retrieving all NFTs from the V2 candy machine with ID {cm_id}... "
              f"This API call can take around 45 seconds...")
        try:
            result = BLOCKCHAIN_API_RESOURCE.get_all_nfts_from_candy_machine(
                candy_machine_id=cm_id,
                network=SolanaNetwork.MAINNET_BETA
            )
            return result
        except:
            print("error getting cm nft info", cm_id)
            return get_cms_nft(cm_id, version, verbose, current_try)
    else:
        print("Version not matching")


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


def compare_nfts(old_version, new_version):
    list_new_nfts_unminted = []
    if len(new_version["unminted_nfts"]) > len(old_version["unminted_nfts"]):
        for new_nft in new_version["unminted_nfts"]:
            if new_nft not in old_version["unminted_nfts"]:
                list_new_nfts_unminted.append(new_nft)
    return
    # todo dont use this until we have a solution for project name
    for x in range(0, len(list_new_nfts_unminted), 8):
        todo_list = list_new_nfts_unminted[x:x + 8]
        send_new_unmited_nfts(todo_list)
    number_all_nfts = len(new_version["minted_nfts"]) + len(new_version["unminted_nfts"])
    if len(new_version["minted_nfts"]) > len(old_version["minted_nfts"]):
        send_minted_counter(number_all_nfts, len(new_version["minted_nfts"]))


def save_nfts_to_file(cm_id, data):
    with open(f"./cms_nfts/{cm_id}.json", "w") as file:
        file.write(json.dumps(data))


def main():
    list_cm_to_monitor = read_from_file()
    for cm in list_cm_to_monitor:
        cm_version = get_version_of_cm(cm)
        if cm_version is None:
            continue
        cm_nft_list = get_cms_nft(cm, cm_version, verbose=True)
        old_nft_list = get_old_data(cm)
        save_nfts_to_file(cm, cm_nft_list)
        if old_nft_list is None:
            print("no old nft data found")
            continue
        compare_nfts(old_nft_list, cm_nft_list)


if __name__ == '__main__':
    main()
