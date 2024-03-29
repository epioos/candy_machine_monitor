import datetime
import json
import os
import random
import time

import csv
# import helheim
import requests
from discord import Embed

from settings import webhook_url_me, webhook_url_me_launchpad, webhook_url_me_interval
from tls_client import TlsClient


class FileHandler:
    def __init__(self):
        self.file_path = os.path.dirname(os.path.realpath(__file__))
        self.launchpad_folder_path = os.path.join(self.file_path, "launchpad")
        self.collections_folder_path = os.path.join(self.file_path, "collections")
        self.collection_data_folder_path = os.path.join(self.file_path, "collection_data")
        self.collection_info_folder_path = os.path.join(self.file_path, "collection_info")
        self.collections_interval_folder_path = os.path.join(self.file_path, "collections_interval")
        self.ranking_folder_path = os.path.join(self.file_path, "ranking")
        self.create_folders()

    def get_proxies(self):
        file_name = "proxies.txt"
        file_path = os.path.join(self.file_path, file_name)
        if not os.path.isfile(file_path):
            print("proxies file not found")
            return []
        with open(file_path, "r") as file:
            return file.read().splitlines()

    def create_folders(self):
        if not os.path.exists(self.launchpad_folder_path):
            os.makedirs(self.launchpad_folder_path)
        if not os.path.exists(self.collections_folder_path):
            os.makedirs(self.collections_folder_path)
        if not os.path.exists(self.collection_data_folder_path):
            os.makedirs(self.collection_data_folder_path)
        if not os.path.exists(self.collection_info_folder_path):
            os.makedirs(self.collection_info_folder_path)
        if not os.path.exists(self.collections_interval_folder_path):
            os.makedirs(self.collections_interval_folder_path)
        if not os.path.exists(self.ranking_folder_path):
            os.mkdir(self.ranking_folder_path)

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

    def save_collection_data_to_file(self, slug, collection_data):
        collection_file_path = os.path.join(self.collection_data_folder_path, slug + ".json")
        with open(collection_file_path, "w") as collection_file:
            collection_file.write(json.dumps(collection_data, indent=4))

    def get_collection_data_from_file(self, slug):
        collection_file_path = os.path.join(self.collection_data_folder_path, slug + ".json")
        if not os.path.isfile(collection_file_path):
            return None
        with open(collection_file_path, "r") as collection_file:
            return json.loads(collection_file.read())

    def save_collection_info_to_file(self, slug, collection_data):
        collection_info_file_path = os.path.join(self.collection_info_folder_path, slug + ".json")
        with open(collection_info_file_path, "w") as collection_info_file:
            collection_info_file.write(json.dumps(collection_data, indent=4))

    def get_collection_info_from_file(self, slug):
        collection_info_file_path = os.path.join(self.collection_info_folder_path, slug + ".json")
        if not os.path.isfile(collection_info_file_path):
            return None
        with open(collection_info_file_path, "r") as collection_info_file:
            return json.loads(collection_info_file.read())

    def save_collection_interval_to_file(self, slug, collection_data):
        collection_interval_file_path = os.path.join(self.collections_interval_folder_path, slug + ".json")
        with open(collection_interval_file_path, "w") as collection_interval_file:
            collection_interval_file.write(json.dumps(collection_data, indent=4))

    def get_collection_interval_from_file(self, slug):
        collection_interval_file_path = os.path.join(self.collections_interval_folder_path, slug + ".json")
        if not os.path.isfile(collection_interval_file_path):
            return None
        with open(collection_interval_file_path, "r") as collection_interval_file:
            return json.loads(collection_interval_file.read())

    def read_ranking_from_csv(self):
        mint_token_dict = {}
        with open('ranking.csv', newline='\n') as csvfile:
            spamreader = csv.DictReader(csvfile, delimiter=',')
            for row in spamreader:
                # mint_token_list.append((row["Token Mint Address"], row["Total Rank"]))
                mint_token_dict[row["Token Mint Address"]] = row["Total Rank"]
        return mint_token_dict

    def append_ranking(self, mint_address):
        ranking_file_path = os.path.join(self.ranking_folder_path, "ranking_found" + ".json")
        with open(ranking_file_path, "r") as reading_file:
            data = json.load(reading_file)
        data["mint_addresses"].append(mint_address)
        with open(ranking_file_path, "w") as writing_file:
            writing_file.write(json.dumps(data, indent=4))

    def get_ranking_from_file(self):
        ranking_file_path = os.path.join(self.ranking_folder_path, "ranking_found" + ".json")
        if not os.path.isfile(ranking_file_path):
            return None
        with open(ranking_file_path, "r") as collection_interval_file:
            return json.loads(collection_interval_file.read())


class MagicEden:
    def __init__(self):
        self.upcoming_launches_url = "https://api-mainnet.magiceden.io/upcoming_launches"
        self.launchpad_collections_url = "https://api-mainnet.magiceden.io/launchpad_collections"
        self.all_collections_data_url = "https://api-mainnet.magiceden.io/all_collections_with_escrow_data"
        self.collection_info_url = "https://api-mainnet.magiceden.io/collections/"
        self.collection_data_url = "https://api-mainnet.magiceden.io/rpc/getCollectionEscrowStats/"

        self.launchpad_releases_webhook_url = webhook_url_me_launchpad
        self.launchpad_collections_webhook_url = webhook_url_me_launchpad
        self.collection_monitor_webhook_url = webhook_url_me
        self.collection_interval_monitor_webhook_url = webhook_url_me_interval

        self.logo_url = "https://cdn.discordapp.com/attachments/907443660717719612/928263386603589682/Q0bOuU6.png"

        self.file_handler = FileHandler()

        self.session = TlsClient()

        self.proxy_list = self.file_handler.get_proxies()
        self.proxy = None
        self.rotate_proxy()

    def injection(self, session, response):
        if helheim.isChallenge(session, response):
            # solve(session, response, max_tries=5)
            return helheim.solve(session, response)
        else:
            return response

    def rotate_proxy(self):
        try:
            proxy = random.choice(self.proxy_list).split(":")
            proxy_dict = {
                "http": f"http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}",
                "https": f"http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}"
            }
            # self.session.proxies.update(proxy_dict)
            proxy_dict = f"http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}"
        except IndexError:
            proxy_dict = None
            # self.session.proxies.update(None)
        try:
            self.session.cookies.clear()
        except:
            pass
        print(f"Using proxy: {proxy_dict}")
        self.proxy = proxy_dict

    def get_launchpad_releases(self):
        """
        Returns a list of all launchpad releases
        :return:
        """
        headers = {
            'authority': 'api-mainnet.magiceden.io',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'accept': 'application/json',
            'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,da;q=0.6,ja;q=0.5,und;q=0.4,ru;q=0.3,fr;q=0.2',
        }

        response = self.session.request(
            method="GET",
            url=self.upcoming_launches_url,
            headers=headers,
            proxy=self.proxy,
            timeout=30,
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
            # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'accept': 'application/json',
            'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,da;q=0.6,ja;q=0.5,und;q=0.4,ru;q=0.3,fr;q=0.2',
        }

        response = self.session.request(
            method="GET",
            url=self.launchpad_collections_url,
            headers=headers,
            proxy=self.proxy,
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_collection_info(self, slug):
        headers = {
            'authority': 'api-mainnet.magiceden.io',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'accept': 'application/json',
            'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,da;q=0.6,ja;q=0.5,und;q=0.4,ru;q=0.3,fr;q=0.2',
        }

        response = self.session.request(
            method="GET",
            url=self.collection_info_url + slug,
            headers=headers,
            proxy=self.proxy,
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_collection_data(self, slug):
        headers = {
            'authority': 'api-mainnet.magiceden.io',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'accept': 'application/json',
            'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,da;q=0.6,ja;q=0.5,und;q=0.4,ru;q=0.3,fr;q=0.2',
        }

        response = self.session.request(
            method="GET",
            url=self.collection_data_url + slug,
            headers=headers,
            proxy=self.proxy,
            timeout=30,
        )
        # print(response.status_code, response.text)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_all_collections_data(self):
        headers = {
            'authority': 'api-mainnet.magiceden.io',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'accept': 'application/json',
            'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,da;q=0.6,ja;q=0.5,und;q=0.4,ru;q=0.3,fr;q=0.2',
        }

        response = self.session.request(
            method="GET",
            url=self.all_collections_data_url,
            headers=headers,
            proxy=self.proxy,
            timeout=30,
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
        try:
            launchpad_collections = self.get_launchpad_collections()
        except Exception as e:
            print("error get_launchpad_collections:", e)
            self.rotate_proxy()
            return
        if launchpad_collections is None:
            print("fetching launchpad collections failed")
            self.rotate_proxy()
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
                }
                try:
                    fields["Candy Machine ID"] = collection["mint"]["candyMachineId"]
                    fields["Config ID"] = collection["mint"]["config"]
                    fields["Treasury"] = collection["mint"]["treasury"]
                except:
                    pass
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
        try:
            launchpad_releases = self.get_launchpad_releases()
        except Exception as e:
            print("error get_launchpad_releases:", e)
            self.rotate_proxy()
            return
        if launchpad_releases is None:
            print("fetching launchpad releases failed")
            self.rotate_proxy()
            return
        print(datetime.datetime.now(), "launchpad_releases", len(launchpad_releases))  # , launchpad_releases)
        for lp_release in launchpad_releases:
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

    def check_collection_by_slug(self, slug):
        print(datetime.datetime.now(), "check_collection_by_slug", slug)
        collection_info = self.file_handler.get_collection_info_from_file(slug)
        if collection_info is None:
            try:
                collection_info = self.get_collection_info(slug)
            except Exception as e:
                print("error get_collection_info:", e)
                self.rotate_proxy()
                return
            self.file_handler.save_collection_info_to_file(slug, collection_info)
        try:
            collection_data = self.get_collection_data(slug)
        except Exception as e:
            print("error get_collection_data:", e)
            self.rotate_proxy()
            return
        if collection_data is None:
            print("failed getting collection data by slug", slug)
            self.rotate_proxy()
            return
        old_collection_data = self.file_handler.get_collection_data_from_file(slug)
        results = collection_data.get("results", None)
        if results is None:
            print("results failed", slug)
            return
        collection_data = results
        collection_data["lastChange"] = int(time.time())
        if old_collection_data is None:
            print("new collection found", slug)
            self.file_handler.save_collection_data_to_file(slug, collection_data)
            floor_price = float(collection_data["floorPrice"] / 1000000000).__round__(2)
            listedCount = collection_data["listedCount"]
            avgPrice24hr = float(collection_data["avgPrice24hr"] / 1000000000).__round__(2) \
                if collection_data.get("avgPrice24hr", None) is not None else 1
            volume24hr = float(collection_data["volume24hr"] / 1000000000).__round__(2) \
                if collection_data.get("volume24hr", None) is not None else 1

            fields = {
                "Floor Price": f"{floor_price} SOL",
                "Listed Count": f"{listedCount} items",
                "Avg Price 24 Hours": f"{avgPrice24hr} SOL",
                "Volume 24 Hours": f"{volume24hr} SOL",
            }
            self.send_webhook(
                event=collection_info.get("name", "name not found"),
                text=collection_info.get("description", "description not found"),
                author="Collection Data found",
                url=f'https://magiceden.io/marketplace/{collection_info.get("symbol", None)}',
                image=collection_info.get("image", None),
                target_webhook=self.collection_monitor_webhook_url,
                fields=fields,
            )
        elif old_collection_data["floorPrice"] != collection_data["floorPrice"]:
            print("collection changed", slug)
            floor_price = float(collection_data["floorPrice"] / 1000000000).__round__(2)
            listedCount = collection_data["listedCount"]
            avgPrice24hr = float(collection_data["avgPrice24hr"] / 1000000000).__round__(2) \
                if collection_data.get("avgPrice24hr", None) is not None else 1
            volume24hr = float(collection_data.get("volume24hr", None) / 1000000000).__round__(2) \
                if collection_data.get("volume24hr", None) is not None else 1

            old_floor_price = float(old_collection_data["floorPrice"] / 1000000000).__round__(2)
            old_listedCount = old_collection_data["listedCount"]
            old_avgPrice24hr = float(old_collection_data["avgPrice24hr"] / 1000000000).__round__(2) \
                if old_collection_data.get("avgPrice24hr", None) is not None else 1
            old_volume24hr = float(old_collection_data["volume24hr"] / 1000000000).__round__(2) \
                if old_collection_data.get("volume24hr", None) is not None else 1

            floor_price_changed_less_than_10_percent = (floor_price - old_floor_price) / old_floor_price < 0.1
            if floor_price_changed_less_than_10_percent is True:
                return
            # only post and save if floor price changed more than 10%
            self.file_handler.save_collection_data_to_file(slug, collection_data)

            floor_change_positive = "+" if floor_price > old_floor_price else ""
            floor_change_in_percentage = float((floor_price - old_floor_price) / old_floor_price * 100).__round__(2)
            listed_count_change_positive = "+" if listedCount > old_listedCount else ""
            listed_count_change_in_percentage = float(
                (listedCount - old_listedCount) / old_listedCount * 100).__round__(2)
            avg_price_24hr_change_positive = "+" if avgPrice24hr > old_avgPrice24hr else ""
            avg_price_24hr_change_in_percentage = float(
                (avgPrice24hr - old_avgPrice24hr) / old_avgPrice24hr * 100
            ).__round__(2)
            volume_24hr_change_positive = "+" if volume24hr > old_volume24hr else ""
            volume_24hr_change_in_percentage = float(
                (volume24hr - old_volume24hr) / old_volume24hr * 100
            ).__round__(2)

            fields = {
                "Floor Price": f'{old_floor_price} -> {floor_price} SOL '
                               f'({floor_change_positive}{floor_change_in_percentage}%)'
                if floor_price != old_floor_price else f'{floor_price} SOL',
                "Listed Count": f'{old_listedCount} -> {listedCount} items '
                                f'({listed_count_change_positive}{listed_count_change_in_percentage}%)'
                if listedCount != old_listedCount else f'{listedCount} items',
                "Avg Price 24 Hours": f'{old_avgPrice24hr} -> {avgPrice24hr} SOL '
                                      f'({avg_price_24hr_change_positive}{avg_price_24hr_change_in_percentage}%)'
                if avgPrice24hr != old_avgPrice24hr else f'{avgPrice24hr} SOL',
                "Volume 24 Hours": f'{old_volume24hr} -> {volume24hr} SOL '
                                   f'({volume_24hr_change_positive}{volume_24hr_change_in_percentage}%)'
                if volume24hr != old_volume24hr else f'{volume24hr} SOL',
                "Last Floor Change": f"<t:{old_collection_data.get('lastChange', int(time.time()))}:R>",
            }

            self.send_webhook(
                event=collection_info.get("name", "name not found"),
                text=collection_info.get("description", "description not found"),
                author="Floor Price changed",
                url=f'https://magiceden.io/marketplace/{collection_info.get("symbol", None)}',
                image=collection_info.get("image", None),
                target_webhook=self.collection_monitor_webhook_url,
                fields=fields,
            )

    def check_all_collections_in_interval(self, slug_list):
        data = []
        for slug in slug_list:
            print(datetime.datetime.now(), "check_collection_by_slug", slug)
            collection_info = self.file_handler.get_collection_info_from_file(slug)
            if collection_info is None:
                try:
                    collection_info = self.get_collection_info(slug)
                except Exception as e:
                    print("error get_collection_info:", e)
                    self.rotate_proxy()
                    continue
                self.file_handler.save_collection_info_to_file(slug, collection_info)
            try:
                collection_data = self.get_collection_data(slug)
            except Exception as e:
                print("error get_collection_data:", e)
                self.rotate_proxy()
                continue
            if collection_data is None:
                print("failed getting collection data by slug", slug)
                self.rotate_proxy()
                continue
            old_collection_data = self.file_handler.get_collection_interval_from_file(slug)

            results = collection_data.get("results", None)
            if results is None:
                continue
            collection_data = collection_data["results"]
            if old_collection_data is None:
                print("new collection found", slug)
                self.file_handler.save_collection_interval_to_file(slug, collection_data)
                try:
                    floor_price = float(collection_data["floorPrice"] / 1000000000).__round__(2)
                    listedCount = collection_data["listedCount"]
                    avgPrice24hr = float(collection_data["avgPrice24hr"] / 1000000000).__round__(2)
                    volume24hr = float(collection_data["volume24hr"] / 1000000000).__round__(2)
                except:
                    continue

                fields = {
                    "Collection Name": collection_info.get("name", "name not found"),
                    "Floor Price": f"{floor_price} SOL",
                    "Listed Count": f"{listedCount} items",
                    "Avg Price 24 Hours": f"{avgPrice24hr} SOL",
                    "Volume 24 Hours": f"{volume24hr} SOL",
                    "image": collection_info.get("image", None),
                }
                # collection_str = " ".join([f"{k}: {v}" for k, v in fields.items()])
                data.append(fields)
            elif old_collection_data["floorPrice"] != collection_data["floorPrice"]:
                print("collection changed", slug)
                self.file_handler.save_collection_interval_to_file(slug, collection_data)
                floor_price = float(collection_data["floorPrice"] / 1000000000).__round__(2)
                listedCount = collection_data["listedCount"]
                avgPrice24hr = float(collection_data["avgPrice24hr"] / 1000000000).__round__(2) \
                    if collection_data["avgPrice24hr"] is not None else 1
                volume24hr = float(collection_data["volume24hr"] / 1000000000).__round__(2) \
                    if collection_data["volume24hr"] is not None else 1

                old_floor_price = float(old_collection_data["floorPrice"] / 1000000000).__round__(2)
                old_listedCount = old_collection_data["listedCount"]
                old_avgPrice24hr = float(old_collection_data["avgPrice24hr"] / 1000000000).__round__(2) if \
                    old_collection_data["avgPrice24hr"] is not None else 1
                old_volume24hr = float(old_collection_data["volume24hr"] / 1000000000).__round__(2) if \
                    old_collection_data["volume24hr"] is not None else 1

                floor_change_positive = "+" if floor_price > old_floor_price else ""
                floor_change_in_percentage = float((floor_price - old_floor_price) / old_floor_price * 100).__round__(2)
                listed_count_change_positive = "+" if listedCount > old_listedCount else ""
                listed_count_change_in_percentage = float(
                    (listedCount - old_listedCount) / old_listedCount * 100).__round__(2)
                avg_price_24hr_change_positive = "+" if avgPrice24hr > old_avgPrice24hr else ""
                avg_price_24hr_change_in_percentage = float(
                    (avgPrice24hr - old_avgPrice24hr) / old_avgPrice24hr * 100
                ).__round__(2)
                volume_24hr_change_positive = "+" if volume24hr > old_volume24hr else ""
                volume_24hr_change_in_percentage = float(
                    (volume24hr - old_volume24hr) / old_volume24hr * 100
                ).__round__(2)

                fields = {
                    "Collection Name": collection_info.get("name", "name not found"),
                    "Floor Price": f'{old_floor_price} -> {floor_price} SOL '
                                   f'({floor_change_positive}{floor_change_in_percentage}%)'
                    if floor_price != old_floor_price else f'{floor_price} SOL',
                    "Listed Count": f'{old_listedCount} -> {listedCount} items '
                                    f'({listed_count_change_positive}{listed_count_change_in_percentage}%)'
                    if listedCount != old_listedCount else f'{listedCount} items',
                    "Avg Price 24 Hours": f'{old_avgPrice24hr} -> {avgPrice24hr} SOL '
                                          f'({avg_price_24hr_change_positive}{avg_price_24hr_change_in_percentage}%)'
                    if avgPrice24hr != old_avgPrice24hr else f'{avgPrice24hr} SOL',
                    "Volume 24 Hours": f'{old_volume24hr} -> {volume24hr} SOL '
                                       f'({volume_24hr_change_positive}{volume_24hr_change_in_percentage}%)',
                    "image": collection_info.get("image", None),
                }

                # collection_str = " ".join([f"{k}: {v}" for k, v in fields.items()])
                data.append(fields)
        i = 1
        for x in range(0, len(data), 5):
            todo = data[x:x + 5]
            new_todo = {}
            image_url = None
            for t in todo:
                collection_name = t.get("Collection Name", "not found")
                if t.get("image") is not None and image_url is None:
                    image_url = t.get("image")
                t.pop("image")
                t.pop("Collection Name")
                new_data_str = "\n".join([f"{k}: {v}" for k, v in t.items()])
                new_todo[collection_name] = new_data_str
                i += 1
            self.send_webhook(
                event="Floor Price Ticker (15 min interval)",
                author="Collection Monitor",
                # text=todo_str,
                text=None,
                url=f'https://magiceden.io/collections?type=popular',
                image=image_url,
                target_webhook=self.collection_interval_monitor_webhook_url,
                # self.collection_monitor_webhook_url,
                fields=new_todo,
            )

    def get_collection_info_for_command(self, slug):
        try:
            collection_info = self.get_collection_info(slug)
            collection_data = self.get_collection_data(slug)
            collection_data = collection_data["results"]
            # print(collection_info)
            # print(collection_data)

            floor_price = float(collection_data["floorPrice"] / 1000000000).__round__(2)
            listedCount = collection_data["listedCount"]
            avgPrice24hr = float(collection_data["avgPrice24hr"] / 1000000000).__round__(2)
            volume24hr = float(collection_data["volume24hr"] / 1000000000).__round__(2)

            embed = Embed(
                title=collection_info.get("name", "name not found"),
                url=f'https://magiceden.io/marketplace/{slug}',
                description=collection_info.get("description", "description not found"),
                color=0xF0258B,
            )
            embed.set_thumbnail(
                url=collection_info.get("image", None)
            )
            embed.add_field(
                name="Floor Price",
                value=f'{floor_price} SOL',
                inline=False,
            )
            embed.add_field(
                name="Listed Count",
                value=listedCount,
                inline=False,
            )
            embed.add_field(
                name="Avg Price 24 Hours",
                value=f'{avgPrice24hr} SOL',
                inline=False,
            )
            embed.add_field(
                name="Volume 24 Hours",
                value=f'{volume24hr} SOL',
                inline=False,
            )
            # embed.add_field(
            #     name=f"Last Floor Change",
            #     value=f"<t:{collection_data.get('lastChange', int(time.time()))}:R>",
            #     inline=False,
            # )
            embed.set_author(
                name="Magiceden",
                icon_url="https://www.magiceden.io/img/favicon.png"
            )
            embed.set_footer(
                text="MetaMint",
                icon_url=self.logo_url
            )
        except Exception as e:
            print("error getting collection info for command:", e, e.__class__.__name__)
            return None
        else:
            return embed

    def send_webhook(self, event, text, author, url, image, target_webhook, fields):
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

        response = requests.post(target_webhook, json=data)
        print(response.status_code, response.reason, response.elapsed.total_seconds(),
              response.url, response.text, event)
        if response.status_code == 429:
            print("magiceden webhook rate limit 429")
            retry_after = response.json()["retry_after"]
            time.sleep((retry_after // 1000) + 1)
            self.send_webhook(event, text, author, url, image, target_webhook, fields)

    def scrape_new_listings_form_csv(self, collection_name):
        headers = {
            'authority': 'api-mainnet.magiceden.io',
            'cache-control': 'max-age=0'
        }

        url = f'https://api-mainnet.magiceden.io/rpc/getListedNFTsByQuery?q=%7B%22%24match%22%3A%7B%22collectionSymbol%22%3A%22{collection_name}%22%7D%2C%22%24sort%22%3A%7B%22createdAt%22%3A-1%7D%2C%22%24skip%22%3A0%2C%22%24limit%22%3A10%7D'
        print(url)
        response = self.session.request(
            method="GET",
            url=url,
            headers=headers,
            proxy=self.proxy,
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def compare_new_listings_with_csv(self, new_data_response):
        minttoken_list = self.file_handler.read_ranking_from_csv()
        found_minttoken_list = self.file_handler.get_ranking_from_file()
        for line in new_data_response["results"]:
            if minttoken_list.get(line["mintAddress"], None) is not None and line["mintAddress"] not in \
                    found_minttoken_list["mint_addresses"]:
                self.file_handler.append_ranking(line["mintAddress"])
                displayed_rank = minttoken_list[line["mintAddress"]]
                # new item found from mint token list
                # todo webhook senden
                self.send_webhook(
                    event=line["title"],
                    text=line["content"],
                    url=f"https://magiceden.io/item-details/{line['mintAddress']}",
                    author="ME Special Item found",
                    image=line.get("img", None),
                    target_webhook=self.collection_monitor_webhook_url,
                    fields={
                        "Rank": displayed_rank,
                        "Price": f'{str(line["price"])} SOL',
                    }
                )
            # else:
            #     print("nothing changed")
