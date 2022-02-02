import json
import os


class BinanceFileHandler:
    def __init__(self):
        self.file_location = os.path.dirname(os.path.abspath(__file__))
        self.file_name = "opensea.json"
        self.file_path = os.path.join(self.file_location, self.file_name)
        self.create_file()

    def create_file(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                f.write(json.dumps({"list": []}, indent=4))
        else:
            print("File already exists")

    def read_file(self):
        with open(self.file_path, "r") as f:
            return json.loads(f.read())["list"]

    def add_to_list(self, slug):
        data = self.read_file()
        if slug not in data:
            data.append(slug)
            with open(self.file_path, "w") as f:
                f.write(json.dumps({"list": data}, indent=4))

    def remove_from_list(self, slug):
        data = self.read_file()
        if slug in data:
            data.remove(slug)
            with open(self.file_path, "w") as f:
                f.write(json.dumps({"list": data}, indent=4))
