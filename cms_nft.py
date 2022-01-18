import json
import os

import requests

from settings import API_ID_KEY, API_SECRET_KEY
from theblockchainapi import TheBlockchainAPIResource, SolanaNetwork, SolanaCandyMachineContractVersion

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

def cms_nfts_to_file(cms_nfts,cm_id):
    try:
        os.mkdir("./cms_nfts/")
    except:
        pass
    try:
        with open(f"./cms_nfts/{cm_id}.json", "w") as file:
            json.dump(cms_nfts, file)
    except Exception as e:
        print("error saving cms_nfts to file", e)

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
