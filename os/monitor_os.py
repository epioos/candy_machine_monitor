# import the OpenseaAPI object from the opensea module
import datetime
import json
import os
import random
import time

import requests

from opensea_filehandler import OpenSeaFileHandler


class OpenSea:
    def __init__(self):
        self.api_key = "88dadb89c3404dfea8a0ee31f95b11cd"
        self.logo_url = "https://cdn.discordapp.com/attachments/907443660717719612/928263386603589682/Q0bOuU6.png"

        self.webhook_url = "https://discord.com/api/webhooks/938528705221910548/MiqUFWTIyV2xX1_0yvdxSn142ExFf0RdgrpadKo9ucxi4sSxJtOxRVuEmZ1S8uUFFZyi"

        self.asset_folder_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets"
        )
        self.collection_folder_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "collections"
        )
        self.proxy_list = self.get_proxies()
        self.rotate_proxy()

    def get_proxies(self):
        file_name = "proxies.txt"
        current_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            file_name
        )
        if not os.path.isfile(current_file_path):
            print("proxies file not found")
            return []
        with open(current_file_path, "r") as file:
            return file.read().splitlines()

    def rotate_proxy(self):
        try:
            proxy = random.choice(self.proxy_list).split(":")
            proxy_dict = {
                "http": f"http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}",
                "https": f"http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}"
            }
        except IndexError:
            proxy_dict = None
        print(f"Using proxy: {proxy_dict}")
        self.proxy = proxy_dict

    def get_collection_info(self, collection_slug: str) -> dict:
        response = requests.get(
            url=f"https://api.opensea.io/api/v1/collection/{collection_slug}",
            headers={
                'User-Agent': 'Chrome API',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': '*/*',
                'Connection': 'keep-alive',
                'X-API-KEY': self.api_key
            },
            proxies=self.proxy,
        )
        result = response.json()
        if result.get("collection", None) is None:
            print(result)
        return result

    def save_collection_info(self, collection_slug: str, collection_info: dict) -> None:
        if not os.path.exists(self.collection_folder_path):
            os.makedirs(self.collection_folder_path)
        collection_info_file_path = os.path.join(
            self.collection_folder_path,
            f"{collection_slug}.json"
        )
        # if os.path.isfile(collection_info_file_path):
        with open(collection_info_file_path, "w") as f:
            collection_info["last_updated"] = datetime.datetime.now().timestamp()
            json.dump(collection_info, f, indent=4)
            print(f"Saved collection info to {collection_info_file_path}")

    def load_collection_info(self, collection_slug: str) -> [dict, None]:
        collection_info_file_path = os.path.join(
            self.collection_folder_path,
            f"{collection_slug}.json"
        )
        if not os.path.isfile(collection_info_file_path):
            return None
        with open(collection_info_file_path, "r") as f:
            collection_info = json.load(f)
        print(f"Loaded collection info from {collection_slug}")
        return collection_info

    def get_events(self, collection_slug: str, **kwargs):
        response = requests.get(
            url=f"https://api.opensea.io/api/v1/events?collection_slug={collection_slug}&event_type=created&only_opensea=False&offset=0&limit=10",
            headers={
                'User-Agent': 'Chrome API',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': '*/*',
                'Connection': 'keep-alive',
                'X-API-KEY': self.api_key
            },
            proxies=self.proxy,
        )
        print("Got events", response.status_code, response.reason, response.url)
        result = response.json()
        return result

    def parse_asset(self, listing: dict):
        # print("listing", json.dumps(listing, indent=4))
        asset = listing.get("asset", None)
        if asset is None:
            return None
        asset_contract = asset.get("asset_contract", None)
        # print("event_type:", listing.get("event_type", None))
        currency = listing["payment_token"]["symbol"]
        decimals = listing["payment_token"]["decimals"]
        # print(f"currency: {currency}")
        # print(f"decimals: {decimals}")
        price = int(listing.get("ending_price", None))
        # print(f"price: {price}")
        float_price = float(price / (10 ** decimals)).__round__(2)
        actual_price = "{price} {currency}".format(
            price=float_price,
            currency=currency
        )
        # print("actual price", actual_price)
        _ = {
            "id": str(asset.get("id", None)),
            "token_id": asset.get("token_id", None),
            "name": "",
            "image": asset.get("image_url", None),
            "asset_contract_address": asset_contract.get("address", None),
            "collection_name": asset_contract.get("name", None),
            "link": asset.get("permalink", None),
            "price": float_price,
            "currency": currency,
            "real_price": actual_price,
        }
        return _

    def save_asset(self, asset: dict):
        if not os.path.exists(self.asset_folder_path):
            os.makedirs(self.asset_folder_path)
        asset_id = asset.get("id", None)
        if asset_id is None:
            print("No asset id found")
            return
        asset_id = asset_id.replace("-", "")
        asset_file_path = os.path.join(
            self.asset_folder_path,
            f"{asset_id}.json"
        )
        asset["last_updated"] = datetime.datetime.now().timestamp()
        with open(asset_file_path, "w") as f:
            json.dump(asset, f, indent=4)

    def load_asset(self, asset_id: str) -> dict:
        asset_id = asset_id.replace("-", "")
        asset_file_path = os.path.join(
            self.asset_folder_path,
            f"{asset_id}.json"
        )
        if os.path.isfile(asset_file_path):
            with open(asset_file_path, "r") as f:
                print("found old asset", asset_id)
                return json.load(f)

    def send_webhook(self, event, text, author, url, image, target_webhook, fields):
        print("Sending webhook", event, text, author, url, image, target_webhook, fields)
        time_now = datetime.datetime.now()
        data = {
            "content": None,
            "username": "OpenSea",
            "avatar_url": self.logo_url,
            "embeds": [
                {
                    "title": None if event is None else event,
                    "description": None if text is None else text,
                    "url": None if url is None else url,
                    "color": 0x2081E2,
                    "fields": [],
                    "timestamp": f"{time_now}",
                    "author": {
                        "name": None if author is None else author,
                        #     "url": "https://www.reddit.com/r/cats/",
                        "icon_url": "https://seeklogo.com/images/O/opensea-logo-7DE9D85D62-seeklogo.com.png"
                    },
                    "footer": {
                        "text": "MetaMint",
                        "icon_url": self.logo_url
                    }
                }
            ]
        }
        if image is not None:
            data["embeds"][0]["thumbnail"] = {
                "url": image
            }
        for f in fields:
            if fields[f] is None:
                real_value = "-"
            elif f == "Launch Date":
                real_value = fields[f]
            elif type(fields[f]) == str:
                if fields[f] == "":
                    real_value = f"-"
                else:
                    real_value = f"{fields[f]}"
            elif type(fields[f]) == int:
                real_value = f"`{fields[f]}`"
            elif type(fields[f]) == float:
                real_value = f"`{fields[f]}`"
            elif type(fields[f]) == bool:
                real_value = "✅" if fields[f] is True else "❌"
            elif type(fields[f]) == list:
                real_value = f"`{fields[f]}`"
            elif type(fields[f]) == dict:
                real_value = f"`{fields[f]}`"
            else:
                real_value = str(fields[f])
            a = {
                "name": f,
                "value": real_value,
                "inline": False
            }
            data["embeds"][0]["fields"].append(a)

        # print(json.dumps(data, indent=4))
        response = requests.post(target_webhook, json=data)
        print(response.status_code, response.reason, response.elapsed.total_seconds(),
              response.url, response.text, text)
        if response.status_code == 429:
            print("magiceden webhook rate limit 429")
            retry_after = response.json()["retry_after"]
            time.sleep((retry_after // 1000) + 1)
            self.send_webhook(event, text, author, url, image, target_webhook, fields)

    def check_new_listings(self, listings, **kwargs):
        floor_price = kwargs.get("floor_price", None)
        for listing in listings["asset_events"]:
            # print(f"Checking listing: {json.dumps(listing, indent=4)}")
            parsed_asset = self.parse_asset(listing)
            if parsed_asset is None:
                continue
            # print(f"Parsed asset: {json.dumps(parsed_asset, indent=4)}")
            print(parsed_asset["collection_name"], parsed_asset["token_id"], parsed_asset["real_price"])
            asset = self.load_asset(parsed_asset["id"])
            if parsed_asset["price"] < floor_price:
                print(f"Price is below floor price: {parsed_asset['price']}")
                if asset is None:
                    print("Asset is not in database, adding it")
                    self.send_webhook(
                        f"{parsed_asset['collection_name']}#{parsed_asset['token_id']}",
                        f"This Asset has been listed below Floor Price",
                        author=f"OpenSea Steals Monitor",
                        url=parsed_asset.get("link", None),
                        image=parsed_asset.get("image", None),
                        target_webhook=self.webhook_url,
                        fields={
                            "Listed Price": f"{parsed_asset['real_price']}",
                            "Floor Price": f"{floor_price} ETH"
                        }
                    )
                    self.save_asset(parsed_asset)
                elif parsed_asset['real_price'] != asset['real_price']:
                    print(f"Price has changed: {parsed_asset['real_price']}")
                    last_updated_from_timestamp = datetime.datetime.fromtimestamp(
                        asset.get("last_updated", 0)
                    )
                    future_timestamp = (datetime.datetime.now() + datetime.timedelta(minutes=5))
                    print(last_updated_from_timestamp)
                    print(future_timestamp)
                    if last_updated_from_timestamp > future_timestamp:
                        self.send_webhook(
                            f"{parsed_asset['collection_name']}#{parsed_asset['token_id']}",
                            f"This Asset has been listed below Floor Price",
                            author=f"OpenSea Steals Monitor",
                            url=parsed_asset.get("link", None),
                            image=parsed_asset.get("image", None),
                            target_webhook=self.webhook_url,
                            fields={
                                "Listed Price": f"{parsed_asset['real_price']}",
                                "Floor Price": f"{floor_price} ETH"
                            }
                        )
                        self.save_asset(parsed_asset)
                    else:
                        print("Asset has been updated recently, not sending webhook")
            time.sleep(0.25)

    def check_collection(self, collection_slug: str):
        print(f"Checking collection: {collection_slug}")
        collection_info = self.get_collection_info(collection_slug)
        # print(f"Collection info: {json.dumps(collection_info, indent=4)}")
        if collection_info is None:
            print(f"Collection not found: {collection_slug}")
            return
        old_collection_info = self.load_collection_info(collection_slug)
        if old_collection_info is None:
            self.save_collection_info(collection_slug, collection_info)
            print(f"Saved collection info: {collection_slug}")
            # todo post discord
        elif old_collection_info["collection"]["stats"]["floor_price"] \
                != collection_info["collection"]["stats"]["floor_price"]:
            last_updated_from_timestamp = datetime.datetime.fromtimestamp(
                old_collection_info.get("last_updated", 0)
            )
            future_timestamp = (datetime.datetime.now() + datetime.timedelta(minutes=15))
            print(last_updated_from_timestamp)
            print(future_timestamp)
            if last_updated_from_timestamp > future_timestamp:
                self.send_webhook(
                    f"{collection_info['collection']['name']}",
                    f"Floor price changed: {old_collection_info['collection']['stats']['floor_price']} ETH -> {collection_info['collection']['stats']['floor_price']} ETH",
                    author=f"OpenSea Collection Monitor",
                    url=f"https://opensea.io/collection/{collection_slug}",
                    image=collection_info["collection"]["image_url"],
                    target_webhook=self.webhook_url,
                    fields={}
                )
                self.save_collection_info(collection_slug, collection_info)
                print(f"Updated collection info: {collection_slug}")
            else:
                print(f"Collection info has been updated recently, not sending webhook")
        return collection_info


def main():
    opensea = OpenSea()
    opensea_fh = OpenSeaFileHandler()
    while 1:
        for collection_slug in opensea_fh.read_file():
            try:
                collection_stats = opensea.check_collection(collection_slug)
                # print(f"Collection stats: {json.dumps(collection_stats, indent=4)}")
                floor_price = collection_stats["collection"]["stats"]["floor_price"]
                print(f"Floor price: {floor_price}")
                # total_supply = collection_stats["collection"]["stats"]["total_supply"]
                # asset_contract_address = collection_stats["collection"]["primary_asset_contracts"][0]["address"]
            except Exception as e:
                print("failed getting collection info", e, e.__class__.__name__, collection_slug)
                opensea.rotate_proxy()
            else:
                try:
                    listings = opensea.get_events(
                        collection_slug=collection_slug,
                        limit=10,
                        event_type="created"
                    )
                    if listings.get("asset_events", None) is not None:
                        opensea.check_new_listings(listings, floor_price=floor_price)
                except Exception as e:
                    print("failed getting listings", e, e.__class__.__name__, collection_slug)
                    opensea.rotate_proxy()
            time.sleep(0.25)


if __name__ == "__main__":
    main()
