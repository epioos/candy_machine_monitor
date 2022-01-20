import json
import os
from urllib.parse import urlparse, parse_qs
import requests
from currency_converter import CurrencyConverter

url = "https://www.binance.com/en/nft/collection/MetaRim?orderBy=list_time&orderType=-1&isBack=0&id=531414973044391937&order=list_time%40-1"
def get_collection_data(product_id):
    try:
        json_url = f"https://www.binance.com/bapi/nft/v1/public/nft/home-layer-price?collectionId={product_id}"
        response = requests.get(json_url)
        return response.json()
    except Exception as e:
        print("error getting response of binance header url", e)

def get_pid_from_url(url):
    parsed_url = urlparse(url)
    try:
        return parse_qs(parsed_url.query)["id"][0]
    except:
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

def check_for_collection_changes(old_data, new_data):
    if new_data["data"]["floorPrice"]["amount"] != old_data["data"]["floorPrice"]["amount"]:
        floor_price = new_data["data"]["floorPrice"]["amount"]
        up_or_down = new_data["data"]["floorPrice"]["up"]
        changed_amount = new_data["data"]["floorPrice"]["changeAmount"]
        volume = new_data["data"]["dailyTradePrice"]["amount"]
        latest_price = new_data["data"]["lastTransaction"]["amount"]
        items_number = new_data["data"]["totalAsset"]["itemCount"]
        return floor_price, up_or_down, changed_amount, volume, latest_price, items_number


def main():
    product_id = get_pid_from_url(url)
    collection = get_collection_data(product_id)
    file_exists = check_if_pid_exists(product_id)
    if file_exists:
        print("todo")
    save_single_collection_to_file(collection, product_id)



if __name__ == '__main__':
    main()