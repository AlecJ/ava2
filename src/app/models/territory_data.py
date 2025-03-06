import json
import os


def load_territory_data():
    with open(os.path.join(os.path.dirname(__file__), "./territories.json")) as f:
        return json.load(f)


TERRITORY_DATA = load_territory_data()
