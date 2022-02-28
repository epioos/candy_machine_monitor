import json

import os


class NiftyFileHandler:
    def __init__(self):
        self.file_path = os.path.dirname(os.path.realpath(__file__))
        self.collection_folder_path = os.path.join(self.file_path, "collection")
        self.create_folders()

    def create_folders(self):
        if not os.path.exists(self.collection_folder_path):
            os.makedirs(self.collection_folder_path)

    def save_collection_to_file(self, collection_id, release_data):
        release_file_path = os.path.join(self.collection_folder_path, collection_id + ".json")
        with open(release_file_path, "w") as collection_file:
            collection_file.write(json.dumps(release_data, indent=4))

    def get_collection_from_file(self, collection_id):
        collection_file_path = os.path.join(self.collection_folder_path, collection_id + ".json")
        if not os.path.isfile(collection_file_path):
            return None
        with open(collection_file_path, "r") as collection_file:
            return json.loads(collection_file.read())

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