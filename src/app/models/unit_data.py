import json
import os


def load_unit_data():
    with open(os.path.join(os.path.dirname(__file__), "./units.json")) as f:
        return json.load(f)


UNIT_DATA = load_unit_data()
