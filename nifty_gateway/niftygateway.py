import datetime
import json
import os
import time

import requests


class FileHandler:
    def __init__(self):
        self.file_path = os.path.dirname(os.path.realpath(__file__))
        self.verified_folder_path = os.path.join(self.file_path, "verified")
        self.curated_folder_path = os.path.join(self.file_path, "curated")
        self.create_folders()

    def create_folders(self):
        if not os.path.exists(self.verified_folder_path):
            os.makedirs(self.verified_folder_path)
        if not os.path.exists(self.curated_folder_path):
            os.makedirs(self.curated_folder_path)

    def save_verified_release_to_file(self, release_id, release_data):
        release_file_path = os.path.join(self.verified_folder_path, release_id + ".json")
        with open(release_file_path, "w") as release_file:
            release_file.write(json.dumps(release_data, indent=4))

    def get_verified_release_from_file(self, release_id):
        release_file_path = os.path.join(self.verified_folder_path, release_id + ".json")
        if not os.path.isfile(release_file_path):
            return None
        with open(release_file_path, "r") as release_file:
            return json.loads(release_file.read())

    def save_curated_release_to_file(self, release_id, release_data):
        release_file_path = os.path.join(self.curated_folder_path, release_id + ".json")
        with open(release_file_path, "w") as release_file:
            release_file.write(json.dumps(release_data, indent=4))

    def get_curated_release_from_file(self, release_id):
        release_file_path = os.path.join(self.curated_folder_path, release_id + ".json")
        if not os.path.isfile(release_file_path):
            return None
        with open(release_file_path, "r") as release_file:
            return json.loads(release_file.read())


class NiftiyGateway:
    def __init__(self):
        self.verified_api_url = "https://api.niftygateway.com/drops/open/?dropType=verified&size=6&current=1"
        self.curated_api_url = "https://api.niftygateway.com/drops/open/?dropType=curated&size=6&current=1"

        self.logo_url = "https://cdn.discordapp.com/attachments/907443660717719612/928263386603589682/Q0bOuU6.png"

        self.webhook_url = "https://discord.com/api/webhooks/943907674234449940/1gkTICojW9r_2prLQhmlKBoDCp9J7XBQMQo7nFXYXTUmxGtQJjMw3ZBLVdrY3fcN0Eic"

        self.file_handler = FileHandler()

    def do_api_request(self, target_url):
        r = requests.get(target_url)
        if r.status_code == 200:
            return r.json()
        else:
            print(f"request failed with: {r.status_code} {r.reason}")

    def get_api_data(self, target_url):
        json_response = self.do_api_request(target_url)
        projects = []
        drops = json_response.get("listOfDrops", None)
        print(target_url)
        if drops is None:
            return
        print(len(drops), "drops found")
        for project in drops:
            project_id = project.get("id", None)
            project_name = project.get("name", None)
            release_data = {
                "project_id": project_id,
                "project_name": project_name,
                "exhibitions": []
            }
            for exhibition in project["Exhibitions"]:
                exhibition_id = exhibition.get("id", None)
                collection_url_slug = exhibition.get("storeURL", None)
                opening_time_utc = project.get("OpeningDateTimeInUTC", None)
                closing_time_utc = project.get("ClosingDateTimeInUTC", None)
                if collection_url_slug is not None:
                    collection_url = f"https://niftygateway.com/collections/{collection_url_slug}"
                else:
                    collection_url = None
                description = exhibition.get("storeDescription", None)
                image = exhibition.get("project_icon", None)
                name = exhibition.get("storeName", None)
                ex = {
                    "exhibition_id": exhibition_id,
                    "name": name,
                    "opening_time_utc": opening_time_utc,
                    "closing_time_utc": closing_time_utc,
                    "collection_url": collection_url,
                    "description": description,
                    "image": image,
                }
                release_data["exhibitions"].append(ex)
            projects.append(release_data)
        return projects

    def check_exhibitions(self, old_exhibitions, new_exhibitions, project_name):
        old_exhibitions_id_list = [x["exhibition_id"] for x in old_exhibitions]
        _old_exhibitions = {}
        for old_ex in old_exhibitions:
            exhibition_id = old_ex["exhibition_id"]
            _old_exhibitions[str(exhibition_id)] = old_ex
        for exhibition in new_exhibitions:
            exhibition_id = exhibition["exhibition_id"]
            print("checking exhibition", exhibition_id)
            wb_exhibition = exhibition.copy()
            del wb_exhibition["image"]
            del wb_exhibition["collection_url"]
            del wb_exhibition["exhibition_id"]
            if wb_exhibition.get("description", None) is not None:
                wb_exhibition["description"] = wb_exhibition["description"][:500]
            if exhibition_id not in old_exhibitions_id_list:
                print("new exhibition found")
                self.send_webhook(
                    project_name,
                    "New exhibition found",
                    author=f"Nifty Gateway Monitor",
                    url=exhibition["collection_url"],
                    image=exhibition["image"],
                    target_webhook=self.webhook_url,
                    fields=wb_exhibition
                )
            elif _old_exhibitions[str(exhibition_id)]["opening_time_utc"] != exhibition["opening_time_utc"]:
                print("opening time changed")
                self.send_webhook(
                    project_name,
                    "Opening time changed",
                    author=f"Nifty Gateway Monitor",
                    url=exhibition["collection_url"],
                    image=exhibition["image"],
                    target_webhook=self.webhook_url,
                    fields=wb_exhibition
                )
            elif _old_exhibitions[str(exhibition_id)]["closing_time_utc"] != exhibition["closing_time_utc"]:
                print("closing time changed")
                self.send_webhook(
                    project_name,
                    "Closing time changed",
                    author=f"Nifty Gateway Monitor",
                    url=exhibition["collection_url"],
                    image=exhibition["image"],
                    target_webhook=self.webhook_url,
                    fields=wb_exhibition
                )

    def process_release_data(self, release_data_list, verified=True):
        for release in release_data_list:
            project_id = str(release["project_id"])
            print("processing", project_id)
            if verified:
                old_release = self.file_handler.get_verified_release_from_file(project_id)
            else:
                old_release = self.file_handler.get_curated_release_from_file(project_id)
            print("old_release", old_release)
            if old_release is None:
                # new project found
                print("new project")
                for exhibition in release["exhibitions"]:
                    print("ex", exhibition)
                    wb_exhibition = exhibition.copy()
                    del wb_exhibition["image"]
                    del wb_exhibition["collection_url"]
                    del wb_exhibition["exhibition_id"]
                    if wb_exhibition.get("description", None) is not None:
                        wb_exhibition["description"] = wb_exhibition["description"][:500]
                    print("new exhibition")
                    self.send_webhook(
                        release["project_name"],
                        "New project found",
                        author=f"Nifty Gateway Monitor",
                        url=exhibition.get("collection_url", None),
                        image=exhibition.get("image", None),
                        target_webhook=self.webhook_url,
                        fields=wb_exhibition
                    )
                    pass
                if verified:
                    self.file_handler.save_verified_release_to_file(project_id, release)
                else:
                    self.file_handler.save_curated_release_to_file(project_id, release)
            elif release["exhibitions"] != old_release["exhibitions"]:
                # exhibitions changed
                self.check_exhibitions(release["exhibitions"], old_release["exhibitions"], release["project_name"])
                if verified:
                    self.file_handler.save_verified_release_to_file(project_id, release)
                else:
                    self.file_handler.save_curated_release_to_file(project_id, release)

    def send_webhook(self, event, text, author, url, image, target_webhook, fields):
        print("Sending webhook", event, text, author, url, image, target_webhook, fields)
        time_now = datetime.datetime.now()
        data = {
            "content": None,
            "username": "NiftyGateway",
            "avatar_url": self.logo_url,
            "embeds": [
                {
                    "title": None if event is None else event,
                    "description": None if text is None else text,
                    "url": None if url is None else url,
                    "color": 0x00F2CC,
                    "fields": [],
                    "timestamp": f"{time_now}",
                    "author": {
                        "name": None if author is None else author,
                        #     "url": "https://www.reddit.com/r/cats/",
                        "icon_url": "https://i.imgur.com/RKT8t7K.png"
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
              response.url, response.text, text, event, fields)
        print(json.dumps(data))
        if response.status_code == 429:
            print("magiceden webhook rate limit 429")
            retry_after = response.json()["retry_after"]
            time.sleep((retry_after // 1000) + 1)
            self.send_webhook(event, text, author, url, image, target_webhook, fields)


def main():
    ng = NiftiyGateway()
    while 1:
        try:
            verified_release_data = ng.get_api_data(ng.verified_api_url)
            ng.process_release_data(verified_release_data, verified=True)
            curated_release_data = ng.get_api_data(ng.curated_api_url)
            ng.process_release_data(curated_release_data, verified=False)
            time.sleep(15)
        except Exception as e:
            print("error - ", e)


if __name__ == '__main__':
    main()
