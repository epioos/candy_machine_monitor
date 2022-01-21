import json
import os.path


def create_file():
    if os.path.isfile("to_monitor.json"):
        return
    with open("to_monitor.json", "w") as file:
        file.write(json.dumps({"list": []}))


def read_from_file():
    create_file()
    with open("to_monitor.json", "r") as file:
        return json.loads(file.read())["list"]


def add_to_file(cm_id):
    data = read_from_file()
    if cm_id in data:
        return
    data.append(cm_id)
    with open("to_monitor.json", "w") as file:
        file.write(json.dumps({"list": data}))


def remove_from_file(cm_id):
    data = read_from_file()
    if cm_id not in data:
        return
    data.remove(cm_id)
    with open("to_monitor.json", "w") as file:
        file.write(json.dumps({"list": data}))

# add_to_file("123kdfgdhjkdfhklj43435")
# add_to_file("892q5hnc34obv836o78h28cf23")
# one = read_from_file()
# print("ONE", one)
# remove_from_file("123kdfgdhjkdfhklj43435")
# remove_from_file("2987e3465chn")
# two = read_from_file()
# print("TWO", two)
