import json

if __name__ == '__main__':
    territories = []

    with open('territories.json', 'r') as f:
        territories = json.load(f)

    for territory in territories.keys():
        territories[territory]['units'] = []

    with open('territories.json', 'w') as f:
        json.dump(territories, f, indent=4)

    print('Finished operation.')
