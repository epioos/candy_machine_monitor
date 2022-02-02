import json
import os
import random
import ssl
import time
from threading import Thread

from discord_webhook import DiscordWebhook, DiscordEmbed

from ProxyManager import get_random_proxy
from http_client import Client
from bs4 import BeautifulSoup
import cloudscraper
import helheim

from storage import webhooks, skip_webhook


class OpenSeaFloor:
    def __init__(self):
        self.client = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'mobile': False,
                'platform': 'windows'
            },
            requestPostHook=self.injection,
            captcha={
                'provider': 'vanaheim'
            }
        )
        current_path = os.path.dirname(os.path.realpath(__file__))
        bifrost_file = os.path.join(current_path, "bifrost-0.0.4.1-windows.x86_64.dll")
        # helheim.bifrost(self.client, bifrost_file)

        self.client.adapters['https://'].ssl_context.check_hostname = False
        self.client.adapters['https://'].ssl_context.verify_mode = ssl.CERT_NONE

        helheim.wokou(self.client, "chrome")

    def injection(self, session, response):
        if helheim.isChallenge(session, response):
            # solve(session, response, max_tries=5)
            return helheim.solve(session, response)
        else:
            return response

    def rotate_proxy(self):
        try:
            new_proxy = get_random_proxy()
            self.client.proxies = new_proxy
        except:
            self.client.proxies = None
        print("rotated proxy", self.client.proxies)
        try:
            self.client.cookies.clear()
        except:
            pass

    def scrape_floor(self, collection_name):
        try:
            headers = {
                'authority': 'opensea.io',
                'pragma': 'no-cache',
                'cache-control': 'no-cache',
                'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
                'sec-ch-ua-mobile': '?0',
                'upgrade-insecure-requests': '1',
                # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,da;q=0.6,ja;q=0.5,und;q=0.4,ru;q=0.3',
                'dnt': '1',
            }

            response = self.client.request(
                method="GET",
                url=f"https://opensea.io/collection/{collection_name}?collectionSlug={collection_name}",
                headers=headers
            )
            print("scraping floor", collection_name, response.status_code, response.reason,
                  response.elapsed.total_seconds())
            if response.status_code != 200:
                print(response.text)
                # self.client.rotate_proxy(new_proxy=get_random_proxy()["http"])
                self.rotate_proxy()
                time.sleep(30)
                return self.scrape_floor(collection_name)
            # print(response.text)
            soup = BeautifulSoup(response.text, "html.parser")
            all_divs = soup.find_all("div")
            # print(len(all_divs), "results")
            founds_floor = []
            founds_volume = []
            for x in all_divs:
                if "volume" in str(x.text):
                    founds_volume.append(x)
                if "floor" in str(x.text):
                    founds_floor.append(x)
            z = founds_volume[len(founds_volume) - 2]
            a = founds_floor[len(founds_floor) - 2]
            spans_volume = z.find_all("span")
            span_volume = spans_volume[1]
            y = span_volume.find("div")
            ballaballa = y.text
            if "<" in ballaballa:
                ballaballa = 0.01
            # print(a)
            spans_floor = a.find_all("span")
            span_floor = spans_floor[1]
            b = span_floor.find("div")
            # print("hahahahahahaahah",b.text)
            # print("floor found", collection_name, b.text)
            bla = b.text
            if "<" in bla:
                bla = 0.01
            return {"floor": float(bla), "volume": float(ballaballa)}
        except Exception as e:
            print("error getting floor", e.__class__.__name__, e)
            return None

    def save_floor(self, collection_name, floor_data):
        if not os.path.exists("./floor/"):
            os.mkdir("./floor")
        with open(f"./floor/{collection_name}.json", "w") as file:
            file.write(json.dumps(floor_data, indent=4))

    def get_floor(self, collection_name):
        try:
            with open(f"./floor/{collection_name}.json", "r") as file:
                f_content = file.read()
                file.close()
            return json.loads(f_content)
        except:
            return None

    def post_floor_webhook(self, collection_name, old_floor, floor_data, notification="Floor price / Volume changed"):
        if skip_webhook is True:
            return
        for wb in webhooks:
            print("WB", wb)
            floor_webhook = wb["floor_webhook"]
            if floor_webhook is None:
                print("FLOOR WEBHOOK NONE?")
                continue
            username = wb["username"]
            footer_icon = wb["footer_icon"]
            footer_text = wb["footer_text"]
            avatar_url = wb["avatar_url"]
            webhook = DiscordWebhook(
                url=floor_webhook,
                proxies=get_random_proxy(),
                username=username,
                avatar_url=avatar_url
            )
            #r_num = lambda: random.randint(0, 255)
            #r_color = '0x%02X%02X%02X' % (r_num(), r_num(), r_num())
            _old_floor = old_floor.get("floor", "not found")
            _old_volume = old_floor.get("volume", "not found")
            embed = DiscordEmbed(
                title=f"{collection_name.title()}",
                description=f"`{_old_floor} ETH -> {floor_data['floor']} ETH`\n"
                            f"`{_old_volume} ETH -> {floor_data['volume']} ETH`",
                color='00FFA3',
                url=f"https://opensea.io/collection/{collection_name}"
            )
            embed.set_author(name=notification)
            embed.set_footer(
                text=footer_text,
                icon_url=footer_icon
            )
            embed.set_timestamp()
            # embed.add_embed_field(name='Field 2', value='dolor sit')
            webhook.add_embed(embed)
            # webhook.set_content(f"||@everyone||")
            r = 429
            while r == 429:
                try:
                    response = webhook.execute()
                    r = response.status_code
                    if r not in range(200, 300):
                        time.sleep(response.json()["retry_after"] // 1000)
                        raise Exception("not successfully sent")
                except Exception as e:
                    print("webhook error", e.__class__.__name__, e)
                    # time.sleep(5)

    def start_floor_checker(self, collection_name):
        while 1:
            # try:
            new_floor = self.scrape_floor(collection_name)
            if new_floor is None:
                continue
            print("found floor", collection_name, new_floor)
            old_floor = self.get_floor(collection_name)
            if old_floor is None:
                print("new floor found", collection_name, new_floor)
                self.save_floor(collection_name, new_floor)
                self.post_floor_webhook(collection_name, old_floor, new_floor)
            else:
                if new_floor is not None and old_floor is not None and new_floor != old_floor:
                    print("floor changed", collection_name, new_floor)
                    self.save_floor(collection_name, new_floor)
                    self.post_floor_webhook(collection_name, old_floor, new_floor)
            # except Exception as e:
            #     print("error checking floor", e.__class__.__name__, e, collection_name)
            time.sleep(30)


def start_checker(collection_name):
    open_sea_floor = OpenSeaFloor()
    open_sea_floor.start_floor_checker(collection_name)
