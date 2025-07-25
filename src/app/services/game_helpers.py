from app.models.territory_data import TERRITORY_DATA
from app.models.unit import Unit

"""
Players
"""
# region players


def get_hostile_team_nums_for_player(player_team_num):
    """
    Get the team numbers of the hostile players for a given player.

    :player_team_num: The team number of the player.
    :return list: A list of team numbers for the hostile players.
    """
    return [0, 2, 4] if player_team_num in [1, 3] else [1, 3]


def does_player_control_capital(game_state, team_num):
    """
    Check if a player controls their capital.

    :game_state: The current game state.
    :team_num: The team number of the player.
    :return bool: True if the player controls their capital, False otherwise.
    """
    capitals = {0: "Russia", 1: "Germany", 2: "United Kingdom",
                3: "Japan", 4: "Eastern United States"}

    capital_territory = game_state.territories[capitals[team_num]]

    return capital_territory.team == team_num

# endregion players


"""
Units
"""
# region units


def is_land_unit(unit_type):
    """
    Check if given unit type is in the list of land units.

    :return bool:
    """
    return unit_type in ['INFANTRY', 'ARTILLERY', 'TANK', 'ANTI-AIRCRAFT']


def is_sea_unit(unit_type):
    """
    Check if given unit type is in the list of sea units.

    :return bool:
    """
    return unit_type in ['AIRCRAFT-CARRIER', 'TRANSPORT', 'BATTLESHIP', 'DESTROYER', 'SUBMARINE']


def is_air_unit(unit_type):
    """
    Check if given unit type is in the list of sea units.

    :return bool:
    """
    return unit_type in ['FIGHTER', 'BOMBER']


def retrieve_unit_from_game_state_by_id(game_state, unit_id):
    """
    Retrieve a unit from the game state by its ID.

    This will NOT retrieve units on transports.

    :game_state: The current game state.
    :unit_id: The ID of the unit to retrieve.
    :return: The unit if found, otherwise None.
    """
    for territory in game_state.territories.values():
        for unit in territory.units:
            if unit.unit_id == unit_id:
                return unit

    return None


def reload_units_onto_transport_from_anywhere(game_state, transport_id, units_to_load_ids):
    """
    Reload units onto a transport from any territory.

    :game_state: The current game state.
    :transport_id: The ID of the transport unit.
    :units_to_load_ids: The IDs of the units to load.
    :return None:
    """
    transport = retrieve_unit_from_game_state_by_id(game_state, transport_id)

    if not transport:
        return None

    found_units_to_load = []

    for territory in game_state.territories.values():
        for unit in territory.units:
            if unit.unit_id in units_to_load_ids:
                found_units_to_load.append(unit)

        # remove the units from the territory
        territory.units = [
            unit for unit in territory.units if unit.unit_id not in units_to_load_ids
        ]

    # Add units to the transport
    transport.cargo.extend(found_units_to_load)


# endregion units

"""
Territories
"""
# region territories


def retrieve_unit_from_territory(territory, unit_to_find):
    """
    This is used to find the db unit in a territory when we are given the unit
    from the frontend. This is used for moving and loading units, and removing
    casualties during combat.

    :territory: The territory (class) to check.
    :unit: The unit (class) to find.
    :return unit: The same unit in the given territory.
    """
    # convert dict to unit if needed
    if isinstance(unit_to_find, dict):
        unit_to_find = Unit.from_dict(unit_to_find)

    for unit in territory.units:
        if unit == unit_to_find:
            return unit

    return False


def check_territory_has_adjacent_industrial_complex(game_state, player, selected_territory):
    """
    Check neighboring territories of a territory to see if there is an industrial complex
    controlled by the player.

    :return bool:
    """
    selected_territory_generic_data = TERRITORY_DATA[selected_territory]
    neighbors = selected_territory_generic_data['neighbors']

    for neighbor in neighbors:
        neighbor_data = game_state.territories[neighbor]

        if player.team_num == neighbor_data.team and neighbor_data.has_factory:
            return True

    return False


def is_hostile_territory(territory, player_team_num, is_ocean=False):
    """
    Check if a territory is controlled by a hostile player. This stops movement
    for land and sea units except for tanks.

    Ocean territories may technically be controlled by a player, but ignore this
    if there are no units in the territory.

    :territory: The territory to check.
    :player_team_num: The team number of the player.
    :return bool: True if the territory is hostile, False otherwise.
    """
    hostile_team_numbers = get_hostile_team_nums_for_player(player_team_num)

    is_empty_ocean_zone = is_ocean and len(territory.units) == 0

    return territory.team in hostile_team_numbers and not is_empty_ocean_zone


def territory_has_hostile_units(territory, player_team_num):
    """
    Check if a territory has enemy units in it. This stops movement
    for all land and sea units.

    :territory: The territory to check.
    :player_team_num: The team number of the player.
    :return bool: True if the territory is hostile, False otherwise.
    """
    hostile_team_numbers = get_hostile_team_nums_for_player(player_team_num)

    # check if territory has units controlled by the hostile team
    for unit in territory.units:
        if unit.team in hostile_team_numbers:
            return True

    return False


def number_of_controlled_territories_for_player(game_state, player):
    """
    Get the number of controlled territories a player has.

    :game_state: The current game state.
    :player: The player to check.
    :return int: The number of controlled territories.
    """
    count = 0

    for territory in game_state.territories.values():
        if territory.team == player.team_num:
            count += 1

    return count


def number_of_industrial_complexes_owned_by_player(game_state, player):
    """
    Get the number of industrial complexes owned by a player.

    :game_state: The current game state.
    :player: The player to check.
    :return int: The number of industrial complexes.
    """
    count = 0

    for territory in game_state.territories.values():
        if territory.team == player.team_num and territory.has_factory:
            count += 1

    return count


def player_can_purchase_industrial_complex(game_state, player):
    """
    Players can only purchase an industrial complex if they have more controlled territories
    than industrial complexes. This includes currently owned and purchased ones.

    :game_state: The current game state.
    :player: The player to check.
    :return bool: True if the player can purchase an industrial complex, False otherwise.
    """
    number_of_controlled_territories = number_of_controlled_territories_for_player(
        game_state, player)

    number_of_industrial_complexes_owned = number_of_industrial_complexes_owned_by_player(
        game_state, player)

    number_of_purchased_industrial_complexes = len(
        [unit for unit in player.mobilization_units if unit == "INDUSTRIAL-COMPLEX"])

    return number_of_controlled_territories > (number_of_industrial_complexes_owned
                                               + number_of_purchased_industrial_complexes)


# endregion territories


"""
Battles
"""
# region battles


def has_unresolved_aa_fire(game_state):
    """
    Check if there are any unresolved AA fire combats.

    :game_state: The current game state.
    :return bool: True if there are unresolved AA fire, False otherwise.
    """
    return any(battle.get('is_aa_attack') and battle.get('result') is None for battle in game_state.battles)


def get_unresolved_aa_fire_combats(game_state):
    """
    Find and return all unresolved AA fire combats.

    :game_state: The current game state.
    :return list: A list of unresolved AA fire combats.
    """
    return [battle for battle in game_state.battles if battle.get('is_aa_attack') and battle.get('result') is None]


def has_unresolved_sea_combat(game_state):
    """
    Check if there are any unresolved sea combats.

    :game_state: The current game state.
    :return bool: True if there are unresolved sea combats, False otherwise.
    """
    return any(battle.get('is_ocean') and battle.get('result') is None for battle in game_state.battles)


def surviving_battleships_from_casualties(battle, attacker_casualties):
    """
    Check if there are any surviving battleships from the casualties.
    :battle: The battle to check.
    :attacker_casualties: The casualties to check.

    """
    surviving_battleships = []

    for unit in attacker_casualties:
        if unit.unit_type == "BATTLESHIP":

            # A battleship is sent twice by the frontend to represent two hits,
            # or once to represent one hit.
            if unit.unit_id not in battle['hit_battleships']:
                surviving_battleships.append(unit.unit_id)
                battle['hit_battleships'].append(unit.unit_id)

            # if the battleship has been hit, remove it from the list of living battleships
            elif unit.unit_id in surviving_battleships:
                surviving_battleships.remove(unit.unit_id)

    return surviving_battleships


def remove_air_unit_from_all_battles(game_state, unit):
    """
    Remove a unit from all battles in the game state.

    This is done for air units that can be in several battles due to anti-aircraft fire.

    :game_state: The current game state.
    :unit: The unit to remove.
    :return None:
    """
    unit_id = unit['unit_id'] if isinstance(unit, dict) else unit.unit_id

    for battle in game_state.battles:
        battle['air_units'] = [
            air_unit for air_unit in battle['air_units'] if air_unit['unit_id'] != unit_id
        ]


def find_and_remove_unit_from_game(game_state, unit):
    """
    Find and remove a unit from the game state.
    This is done for air units that can be in several battles due to anti-aircraft fire.
    :game_state: The current game state.
    :unit: The unit to remove.
    :return None:
    """
    unit_id = unit['unit_id'] if isinstance(unit, dict) else unit.unit_id

    for territory in game_state.territories.values():
        territory.units = [
            territory_unit for territory_unit in territory.units if territory_unit.unit_id != unit_id
        ]


def find_amphibious_assault_land_battle(game_state, territory_name):
    """
    Find the amphibious assault land battle for a given ocean territory, if one exists.

    :game_state: The current game state.
    :territory_name: The name of the sea territory the amphibious assault is in.
    :return: The battle if found, otherwise None.
    """
    return next((battle for battle in game_state.battles if battle.get(
        'attack_from') == territory_name and not battle.get('is_aa_attack') and not battle.get('is_ocean') and not battle.get('result')), None)

    # endregion battles
