import datetime
import json
import os
import time

import requests


class FileHandler:
    def __init__(self):
        self.file_path = os.getcwd()
        self.launchpad_folder_path = os.path.join(self.file_path, "launchpad")
        self.collections_folder_path = os.path.join(self.file_path, "collections")
        self.create_folders()

    def create_folders(self):
        if not os.path.exists(self.launchpad_folder_path):
            os.makedirs(self.launchpad_folder_path)
        if not os.path.exists(self.collections_folder_path):
            os.makedirs(self.collections_folder_path)

    def save_collection_to_file(self, collection_id, collection_data):
        collection_file_path = os.path.join(self.collections_folder_path, collection_id + ".json")
        with open(collection_file_path, "w") as collection_file:
            collection_file.write(json.dumps(collection_data, indent=4))

    def get_collection_from_file(self, collection_id):
        collection_file_path = os.path.join(self.collections_folder_path, collection_id + ".json")
        if not os.path.isfile(collection_file_path):
            return None
        with open(collection_file_path, "r") as collection_file:
            return json.loads(collection_file.read())

    def save_launchpad_release_to_file(self, release_id, release_data):
        release_file_path = os.path.join(self.launchpad_folder_path, release_id + ".json")
        with open(release_file_path, "w") as release_file:
            release_file.write(json.dumps(release_data, indent=4))

    def get_launchpad_release_from_file(self, release_id):
        release_file_path = os.path.join(self.launchpad_folder_path, release_id + ".json")
        if not os.path.isfile(release_file_path):
            return None
        with open(release_file_path, "r") as release_file:
            return json.loads(release_file.read())


class MagicEden:
    def __init__(self):
        self.upcoming_launches_url = "https://api-mainnet.magiceden.io/upcoming_launches"
        self.launchpad_collections_url = "https://api-mainnet.magiceden.io/launchpad_collections"
        self.all_collections_data_url = "https://api-mainnet.magiceden.io/all_collections_with_escrow_data"

        self.launchpad_releases_webhook_url = "https://discord.com/api/webhooks/933135796884623420/c7qWgRRfDTqteyTaxs2YRKZwqtumi0ZDNTsz5PgnKtqNoTZaI9QiMGbn8GhlMdASnDQL"
        self.launchpad_collections_webhook_url = "https://discord.com/api/webhooks/933135796884623420/c7qWgRRfDTqteyTaxs2YRKZwqtumi0ZDNTsz5PgnKtqNoTZaI9QiMGbn8GhlMdASnDQL"

        self.logo_url = "https://cdn.discordapp.com/attachments/907443660717719612/928263386603589682/Q0bOuU6.png"

        self.file_handler = FileHandler()

    def get_launchpad_releases(self):
        """
        Returns a list of all launchpad releases
        :return:
        """
        headers = {
            'authority': 'api-mainnet.magiceden.io',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'accept': 'application/json',
            'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,da;q=0.6,ja;q=0.5,und;q=0.4,ru;q=0.3,fr;q=0.2',
        }

        response = requests.request(
            method="GET",
            url=self.upcoming_launches_url,
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_launchpad_collections(self):
        headers = {
            'authority': 'api-mainnet.magiceden.io',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'accept': 'application/json',
            'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,da;q=0.6,ja;q=0.5,und;q=0.4,ru;q=0.3,fr;q=0.2',
        }

        response = requests.request(
            method="GET",
            url=self.launchpad_collections_url,
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_all_collections_data(self):
        headers = {
            'authority': 'api-mainnet.magiceden.io',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'accept': 'application/json',
            'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,da;q=0.6,ja;q=0.5,und;q=0.4,ru;q=0.3,fr;q=0.2',
        }

        response = requests.request(
            method="GET",
            url=self.all_collections_data_url,
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def check_launchpad_collections(self):
        """
        Checks the launchpad collections for new releases
        :return:
        """
        # Get the launchpad collections
        launchpad_collections = self.get_launchpad_collections()
        if launchpad_collections is None:
            print("fetching launchpad collections failed")
            return
        print(datetime.datetime.now(), "launchpad_collections", len(launchpad_collections))  # , launchpad_collections)
        for collection in launchpad_collections:
            old_collection = self.file_handler.get_collection_from_file(collection["_id"])
            if old_collection is None:
                print("collection not found", collection["_id"])
                self.file_handler.save_collection_to_file(collection["_id"], collection)
                fields = {
                    "Launch Date": collection.get("launchDate", "not found"),
                    "Price": collection.get("price", "not found").__str__() + " SOL",
                    "Candy Machine ID": collection["mint"]["candyMachineId"],
                    "Config ID": collection["mint"]["config"],
                    "Treasury": collection["mint"]["treasury"],
                }
                try:
                    fields["Tokens Available"] = collection["state"]["itemsAvailable"]
                    fields["Tokens Redeemed"] = collection["state"]["itemsRedeemed"]
                    fields["Tokens Remaining"] = collection["state"]["itemsRemaining"]
                    d_str = collection["state"]["goLiveDate"]
                    d = datetime.datetime.strptime(d_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    ts = int(d.timestamp())
                    fields["Launch Date"] = f"<t:{ts}:F> / <t:{ts}:R>"
                except:
                    pass
                self.send_webhook(
                    event=collection["name"],
                    text=collection["description"],
                    url=f"https://www.magiceden.io/launchpad/{collection['symbol']}",
                    author="ME Launchpad Activity detected",
                    image=collection.get("image", None),
                    target_webhook=self.launchpad_collections_webhook_url,
                    fields=fields
                )
            # todo check if collection has changed

    def check_launchpad_releases(self):
        launchpad_releases = self.get_launchpad_releases()
        if launchpad_releases is None:
            print("fetching launchpad releases failed")
            return
        print(datetime.datetime.now(), "launchpad_releases", len(launchpad_releases))  # , launchpad_releases)
        for lp_release in launchpad_releases:
            # print("lp_release", lp_release)
            old_release = self.file_handler.get_launchpad_release_from_file(lp_release['_id'])
            if old_release is None:
                print("new release found", lp_release['_id'])
                self.file_handler.save_launchpad_release_to_file(lp_release['_id'], lp_release)
                self.send_webhook(
                    event=lp_release.get("title", "name not found"),
                    text=None,
                    author="ME release found",
                    url=lp_release.get("url", None),
                    image=lp_release.get("image", None),
                    target_webhook=self.launchpad_releases_webhook_url,
                    fields={
                        "Launch Date": lp_release["launchDate"]
                    },
                )
            elif old_release != lp_release:
                print("release changed", lp_release['_id'])
                self.file_handler.save_launchpad_release_to_file(lp_release['_id'], lp_release)
                self.send_webhook(
                    event=lp_release.get("title", "name not found"),
                    text=None,
                    author="ME release changed",
                    url=lp_release.get("url", None),
                    image=lp_release.get("image", None),
                    target_webhook=self.launchpad_releases_webhook_url,
                    fields={
                        "Launch Date": f"`{lp_release['launchDate']}`"
                    },
                )

    def send_webhook(self, event, text, author, url, image, target_webhook, fields):
        print("send_webhook", event, text, target_webhook)
        time_now = datetime.datetime.now()
        data = {
            "content": None,
            "username": "MagicEden",
            "avatar_url": self.logo_url,
            "embeds": [
                {
                    "title": None if event is None else event,
                    "description": None if text is None else text,
                    "url": None if url is None else url,
                    "color": 0xF0258B,
                    "fields": [],
                    "timestamp": f"{time_now}",
                    "author": {
                        "name": None if author is None else author,
                        #     "url": "https://www.reddit.com/r/cats/",
                        "icon_url": "https://www.magiceden.io/img/favicon.png"
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
                    real_value = f"`{fields[f]}`"
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

        response = requests.post(target_webhook, json=data)
        print(response.status_code, response.reason, response.elapsed.total_seconds(),
              response.url, response.text)
        if response.status_code == 429:
            print("429")
            retry_after = response.json()["retry_after"]
            time.sleep((retry_after // 1000) + 1)
            self.send_webhook(event, text, author, url, image, target_webhook, fields)


def main():
    m = MagicEden()
    while 1:
        m.check_launchpad_releases()
        m.check_launchpad_collections()
        time.sleep(6)
    # launchpad_collections = m.get_launchpad_collections()


if __name__ == "__main__":
    main()
