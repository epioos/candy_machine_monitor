import json

from theblockchainapi import TheBlockchainAPIResource
import time
from settings import API_ID_KEY, API_SECRET_KEY


BLOCKCHAIN_API_RESOURCE = TheBlockchainAPIResource(
    api_key_id=API_ID_KEY,
    api_secret_key=API_SECRET_KEY
)


def write_all_cm_to_file(response_json):
    try:
        with open("all_cm.json", "w") as file:
            json.dump(response_json, file)
    except Exception as e:
        print("Error - writing all cm to file", e)


def read_all_cm_from_file():
    try:
        with open("all_cm.json", "r") as file:
            all_cm_from_file = json.load(file)
            return all_cm_from_file
    except Exception as e:
        print("Error - getting all cm from file", e)


def get_all_cm():
    try:
        assert API_ID_KEY is not None
        assert API_SECRET_KEY is not None
    except AssertionError:
        raise Exception("Api key pair not found")

    current_time = int(time.time())
    result = BLOCKCHAIN_API_RESOURCE.list_all_candy_machines()
    print(result.keys())
    print(f"Last updated approx. {(current_time - result['last_updated']) // 60} minutes ago.")
    print(f"There are a total of {len(result['config_addresses_v1'])} V1 candy machines.")
    print(f"There are a total of {len(result['config_addresses_v2'])} V2 candy machines.")
    print(f"There are a total of {len(result['config_addresses_magic-eden-v1'])} Magic Eden candy machines.")
    return result

def compare_for_new_cm(all_cm_new, all_cm_old):
    new_cm_list = []
    for new_cm_v1 in all_cm_new['config_addresses_v1']:
        if new_cm_v1 not in all_cm_old['config_addresses_v1']:
            new_cm_list.append(tuple((new_cm_v1,"v1", "v1")))
    for new_cm_v2 in all_cm_new ['config_addresses_v2']:
        if new_cm_v2 not in all_cm_old['config_addresses_v2']:
            new_cm_list.append(tuple((new_cm_v2,"v2", "v2")))
    for new_cm_me in all_cm_new ['config_addresses_magic-eden-v1']:
        if new_cm_me not in all_cm_old['config_addresses_magic-eden-v1']:
            new_cm_list.append(tuple((new_cm_me,"magic eden", "v1")))
    return new_cm_list