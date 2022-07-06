import os
import json


def get_advisory():
    with open(os.path.dirname(os.path.abspath(__file__)) + "/data/" + "Advisory.json", "r") as file:
        data = json.load(file)
        return data[0]
