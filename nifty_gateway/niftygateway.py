import requests

class NiftiyGateway:
    def __init__(self):
        self.verified_api_url = "https://api.niftygateway.com/drops/open/?dropType=verified&size=6&current=1"
        self.curated_api_url = "https://api.niftygateway.com/drops/open/?dropType=curated&size=6&current=1"
        self.project_name = None
        self.opening_time_utc = None
        self.closing_time_utc = None
        self.collection_url_slug = None
        self.collection_url = None
        self.description = None

    def do_api_request(self, target_url):
        r = requests.get(target_url)
        if r.status_code == 200:
            return r.json()
        else:
            print(f"request failed with: {r.status_code} {r.reason}")

    def verified_monitor(self):
        json_response = self.do_api_request(self.verified_api_url)
        for project in json_response:
            self.project_name = project.get("name", None)
            self.opening_time_utc = project.get("OpeningDateTimeInUTC", None)
            self.closing_time_utc = project.get("ClosingDateTimeInUTC", None)
            for exhibition in project["Exhibitions"]:
                self.collection_url_slug = exhibition.get("storeURL", None)
                if self.collection_url_slug is not None:
                    self.collection_url = f"https://niftygateway.com/collections/{self.collection_url_slug}"
                self.description = exhibition["storeDescription"]