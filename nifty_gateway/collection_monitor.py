import json
import os
from discord_webhook import DiscordWebhook, DiscordEmbed
import requests

from nifty_filehandler import NiftyFileHandler


class NiftyCollection:
    def __init__(self, contract_address):
        self.contract_address = contract_address
        self.logo_url_mm = "https://cdn.discordapp.com/attachments/907443660717719612/928263386603589682/Q0bOuU6.png"
        self.logo_url_ng = "https://i.imgur.com/RKT8t7K.png"


        self.webhook_url = "https://discord.com/api/webhooks/933135796884623420/c7qWgRRfDTqteyTaxs2YRKZwqtumi0ZDNTsz5PgnKtqNoTZaI9QiMGbn8GhlMdASnDQL"
        self.filehandler = NiftyFileHandler()

    def get_info_on_request(self):
        headers = {
            'authority': 'niftygateway.com',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
            'sec-ch-ua-platform': '"Windows"',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        }

        response = requests.get(f'https://api.niftygateway.com/market/summary-stats/?contractAddress={self.contract_address}&niftyType=1', headers=headers)
        #print(response.status_code, response.reason, response.json())
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def compare_changes(self, name, picture, listings_type):
        old_data = self.filehandler.get_collection_from_file(self.contract_address)
        new_data = self.get_info_on_request()
        if old_data is None:
            self.filehandler.save_collection_to_file(self.contract_address, new_data)
            self.send_webhook(new_data,name, picture, listings_type)
        elif old_data["floor_price_in_cents"] != new_data["floor_price_in_cents"]:
            self.send_webhook(new_data,name, picture, listings_type)
            self.filehandler.save_collection_to_file(self.contract_address, new_data)

    def get_picture_name_listingstype(self):
        import requests

        headers = {
            'authority': 'api.niftygateway.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'accept': 'application/json, text/plain, */*',
            'origin': 'https://niftygateway.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://niftygateway.com/'
        }

        params = (
            ('page', '{"current":1,"size":20}'),
            ('filter', '{"contractAddress":"'+ self.contract_address + '"}'),
            ('sort', '{}'),
        )

        response = requests.get('https://api.niftygateway.com/marketplace/nifty-types/', headers=headers, params=params)
        useful_data = response.json()["data"]["results"][0]
        name = useful_data["niftyTitle"]
        image = useful_data["niftyDisplayImage"]
        listings_type = useful_data["listingType"]
        return name, image, listings_type

    def send_webhook(self, data_to_send, name,image , listings_type):
        floor_price = int(data_to_send["floor_price_in_cents"]/100)
        volume_30 = int(data_to_send["volume_last_30_days_in_cents"]/100)
        last_sale = int(data_to_send["last_sale_amount_in_cents"]/100)
        average_listing = int(data_to_send["average_listing_price_in_cents"]/100)

        webhook = DiscordWebhook(self.webhook_url, username="NiftyGateway", avatar_url=self.logo_url_mm)

        embed = DiscordEmbed(title=name, color='83eaca', url=f"https://niftygateway.com/marketplace/collectible/{self.contract_address}")
        embed.set_author(name='Collection Monitor', icon_url=self.logo_url_ng)
        embed.set_thumbnail(url=image)
        embed.add_embed_field(name='Floor Price', value=f"${floor_price}")
        embed.add_embed_field(name='Volume last 30 Days', value=f"${volume_30}")
        embed.add_embed_field(name='Last Sale', value=f"${last_sale}")
        embed.add_embed_field(name='Average listing Price', value=f"${average_listing}")
        embed.add_embed_field(name='Listing Type', value=str(listings_type))
        embed.add_embed_field(name='Listings', value=str(data_to_send["number_of_listings"]))
        embed.set_footer(text='MetaMint', icon_url=self.logo_url_mm)
        embed.set_timestamp()
        webhook.add_embed(embed)
        webhook.execute()

def main():
    nifty_fh = NiftyFileHandler()
    collection_list = nifty_fh.read_file()
    for collection in collection_list:
        nc = NiftyCollection(collection)
        nc.get_info_on_request()
        name, picture, listings_type = nc.get_picture_name_listingstype()
        nc.compare_changes(name, picture, listings_type)


if __name__ == '__main__':
    main()




