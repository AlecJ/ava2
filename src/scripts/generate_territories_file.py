import json
import os

if __name__ == '__main__':
    with open('triangles.json', 'r') as f:
        names = json.load(f)

    result = {}

    for name in names:
        is_ocean_tile = name[:5] == 'ocean'
        result[name] = {
            'team': 0,
            'is_capital': False,
            'is_ocean': is_ocean_tile,
            'power': 0,
            'neighbors': []
        }

    sorted_result = {key: result[key] for key in sorted(result)}

    with open('territories.json', 'w') as output:
        json.dump(sorted_result, output)
