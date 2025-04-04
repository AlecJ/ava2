from app.models.territory_data import TERRITORY_DATA
from app.models.unit_data import UNIT_DATA
from app.models.session import Session, PhaseNumber
from app.models.unit import Unit


"""
purchase_unit

move_units

add_territory_power_to_player_ipcs

end_turn

"""


def purchase_unit(player, unit_type_to_purchase):
    """
    Validate player has funds. Add unit to waiting pool (placed at end of round)
    and remove IPCs from player.

    :return bool: if the purchase was successful.
    """
    new_unit_data = UNIT_DATA[unit_type_to_purchase]

    # ensure player has sufficient funds
    if player.ipcs < new_unit_data['cost']:
        return False

    # remove IPCs
    player.ipcs -= new_unit_data['cost']

    # add unit to player
    player.mobilization_units.append(unit_type_to_purchase)

    return True


def move_units(session, game_state, player, territory_a_name, territory_b_name, units_to_move):
    """
    Validates and moves units from one territory to another.

    Validation:
    - selected territory is a neighbor to the current territory
    - all moving units have movement available and are in the current territory
    - a land unit can not enter an ocean territory (loading on ships is separate behavior)
    - a sea unit cannot enter a land territory
    - a unit cannot move from a hostile territory (unless it started there???)
    - player has units to place
    - territory has industrial complex and is owned by the player
    - sea units must be in ocean with a neighboring industrial complex
    - new industrial complex must be in a controlled territory without an existing one
    - anti-aircraft units can only move in non-combat phase

    Additonal Rules:
    - land and sea units must stop once they enter a hostile territory

    :session: The current game session.
    :game_state: The current game state.
    :player: The player making the move.
    :territory_a_name: The name of the territory to move
    :territory_b_name: The name of the territory to move to
    :units_to_move: The list of units to move.
    :return bool: if the units were successfully moved.
    """
    territory_a = game_state.territories[territory_a_name]
    territory_b = game_state.territories[territory_b_name]

    territory_a_generic_data = TERRITORY_DATA[territory_a_name]
    territory_b_generic_data = TERRITORY_DATA[territory_b_name]

    territory_b_is_ocean = territory_b_generic_data['is_ocean']
    territory_b_is_controlled_by_player = player.team_num == territory_b.team

    # territories are neighbors
    if not territory_b_name in territory_a_generic_data['neighbors']:
        return False, "Territories are not neighbors."

    # all moving units are in territory A
    territory_a_unit_ids = {unit.unit_id for unit in territory_a.units}
    moving_unit_ids = {unit.unit_id for unit in units_to_move}

    if not set(moving_unit_ids).issubset(territory_a_unit_ids):
        return False, "Units are not in the selected territory."

    for unit in units_to_move:
        if unit.movement < 1:
            return False, "Unit does not have enough movement."
        if is_land_unit(unit.unit_type) and territory_b_is_ocean:
            return False, "Land units cannot enter ocean territories."
        if is_sea_unit(unit.unit_type) and not territory_b_is_ocean:
            return False, "Sea units cannot enter land territories."
        if unit.unit_type == "ANTI-AIRCRAFT" and session.phase_num != PhaseNumber.NON_COMBAT_MOVE:
            return False, "Anti-aircraft units can only move in non-combat phase."
        if not is_air_unit(unit.unit_type) and is_hostile_territory(territory_b, player.team_num) and session.phase_num == PhaseNumber.NON_COMBAT_MOVE:
            return False, "Land and sea units cannot move into hostile territories in the non-combat phase."

        """Validation Passed"""

        if not is_air_unit(unit.unit_type) and is_hostile_territory(territory_b, player.team_num):
            unit.movement = 1  # will be subtracted to 0 later

    for unit in units_to_move:
        unit.movement -= 1

    # remove units from territory A
    territory_a.units = [
        unit for unit in territory_a.units if unit.unit_id not in moving_unit_ids]

    # add units to territory B
    territory_b.units.extend(units_to_move)

    return True, None


def load_transport_with_units(game_state, player, territory_name, transport, units_to_load):
    """
    Moves selected units from a neighboring territory onto a transport ship.

    Validation:
    - transport is owned by player
    - neighboring territory is friendly
    - units are in neighboring territory
    - units are owned by player
    - transports does not end with more than 2 units
    - transport can have 1 infantry and 1 other land unit
    - carriers can have 2 air units (fighters or bombers)
    """
    # get sea territory
    sea_territory = game_state.territories[territory_name]
    sea_territory_generic_data = TERRITORY_DATA[territory_name]
    if not sea_territory_generic_data["is_ocean"]:
        return False

    # load transport from game_state, also ensures it exists in territory
    transport = retrieve_unit_from_territory(sea_territory, transport)

    # transport is owned by player
    if transport.team != player.team_num:
        return False

    # unit validation
    for unit in units_to_load:
        unit_territory_name = unit["territory"]
        unit_territory = game_state.territories[unit_territory_name]

        # fetch unit from game_state
        unit = Unit.from_dict(unit)
        unit = retrieve_unit_from_territory(unit_territory, unit)

        # each unit is in a friendly territory
        if unit_territory.team != player.team_num:
            return False

        # each unit is in a territory that neighbors the sea territory
        if unit_territory_name not in sea_territory_generic_data['neighbors']:
            return False

        # units must have movement available
        # TODO untested
        if unit.movement < 1:
            return False

        # if transport, must be a land unit
        if transport.unit_type == "TRANSPORT" and not is_land_unit(unit.unit_type):
            return False

        # if carrier, must be an air unit
        if transport.unit_type == "AIRCRAFT-CARRIER" and not is_air_unit(unit.unit_type):
            return False

        # add unit to transport
        transport.cargo.append(unit)
        unit_territory.units.remove(unit)

    # final validation, transport can only have 2 units and 1 must be infantry if max
    if len(transport.cargo) > 2:
        return False

    # full transports (2 units), one must be infantry
    if (transport.unit_type == "TRANSPORT" and len(transport.cargo) == 2 and
            not any(unit.unit_type == "INFANTRY" for unit in transport.cargo)):
        return False

    return True


def unload_transport(game_state, player, sea_territory_name, selected_territory_name, transport):
    """
    Moves selected units from a neighboring territory onto a transport ship.

    Validation:
    - transport is in sea territory
    - territory is friendly TODO -- disable if combat should be forced?
    - transport is owned by player
    - selected territory is land

    """
    # get sea territory
    sea_territory = game_state.territories[sea_territory_name]
    sea_territory_generic_data = TERRITORY_DATA[sea_territory_name]
    if not sea_territory_generic_data["is_ocean"]:
        return False, "Sea territory is not an ocean?"

    # load transport from game_state, also ensures it exists in territory
    transport = retrieve_unit_from_territory(sea_territory, transport)

    # transport is owned by player
    if transport.team != player.team_num:
        return False, "Transport is not owned by player."

    # selected territory is land
    selected_territory = game_state.territories[selected_territory_name]
    selected_territory_generic_data = TERRITORY_DATA[selected_territory_name]
    if selected_territory_generic_data["is_ocean"]:
        return False, "Selected territory is not land."

    # selected territory neighbors the sea territory
    if selected_territory_name not in sea_territory_generic_data['neighbors']:
        return False, "Selected territory is not a neighbor of the sea territory."

    """Validation Passed"""

    # units cannot move after unloading
    for unit in transport.cargo:
        unit.movement = 0

    # move units to land territory
    selected_territory.units.extend(transport.cargo)
    transport.cargo = []

    return True, None


def mobilize_units(game_state, player, units_to_mobilize, selected_territory):
    """
    Remove units from player's mobilization units array.
    Add units to the selected territory.

    Validation
    - player has units to place
    - territory has industrial complex and is owned by the player
    - sea units must be in ocean with a neighboring industrial complex
    - new industrial complex must be in a controlled territory without an existing one

    :return bool: if the units were successfully placed.
    """
    # check if territory is valid
    selected_territory_generic_data = TERRITORY_DATA[selected_territory]
    selected_territory_data = game_state.territories[selected_territory]

    is_controlled_by_player = player.team_num == selected_territory_data.team
    is_ocean = selected_territory_generic_data['is_ocean']
    has_factory = selected_territory_data.has_factory
    has_adjacent_industrial_complex = check_territory_has_adjacent_industrial_complex(
        game_state, player, selected_territory)

    # for each unit, remove from player and create one in the territory
    for unit in units_to_mobilize:
        unit_type = unit['unit_type']

        # user cannot place more units than they have available
        if unit_type not in player.mobilization_units:
            return False

        # if land unit, it must have be land and have industrial complex
        if not is_sea_unit(unit_type) and unit_type != "INDUSTRIAL-COMPLEX" and (is_ocean or not has_factory or not is_controlled_by_player):
            return False

        # if sea unit, it must be be sea and have an adjacent controlled industrial complex
        if is_sea_unit(unit_type) and unit_type != "INDUSTRIAL-COMPLEX" and (not is_ocean or not has_adjacent_industrial_complex):
            return False

        # if industrial complex, it must be a controlled land without an existing one
        if unit_type == "INDUSTRIAL-COMPLEX" and (is_ocean or has_factory or not is_controlled_by_player):
            return False

        # remove unit from players mobilization units
        player.mobilization_units.remove(unit_type)

        # industrial complex is a special building that never moves,
        # instead of creating a "unit", update the territory data
        if unit_type == "INDUSTRIAL-COMPLEX":
            selected_territory_data.has_factory = True
        else:
            # add unit to territory
            new_unit = Unit(
                unit_type=unit_type,
                team=player.team_num,
            )
            selected_territory_data.units.append(new_unit)

    return True


def add_territory_power_to_player_ipcs(session, territory_name, territory):
    """
    Adds the IPC value of the territory to the session's IPCS.

    :param session: The current game session.
    :param:
    """
    # get player associated with the territory
    player = session.get_player_by_team_num(territory.team)
    territory_power = TERRITORY_DATA[territory_name]['power']
    player.ipcs += territory_power


def end_turn(session, game_state):
    """
    Ends the current player's turn and reset their unit movement.

    If the player is the last player for the round,
    the following actions are performed:

    Increment each player's IPCS by the IPC value of their territories.

    Increment the turn timer by 1.

    Validation:
    - air units over water with no aircraft carrier are destroyed, otherwise load them automatically
    """
    for territory_name, territory in game_state.territories.items():
        territory_is_ocean = TERRITORY_DATA[territory_name]["is_ocean"]

        # if end of a full turn, add IPCs to players
        if session.turn_num % 5 == 4:
            add_territory_power_to_player_ipcs(
                session, territory_name, territory)

        # reset unit movement, remove air units from ocean
        units_to_remove = []

        for unit in territory.units:
            unit.movement = UNIT_DATA[unit.unit_type]['movement']

            # if a fighter or bomber is on the ocean with no carrier, destroy it
            if is_air_unit(unit.unit_type) and territory_is_ocean:
                attempt_to_load_air_unit_on_carrier(territory, unit)
                # unit is removed from territory regardless
                units_to_remove.append(unit)

            # if a fighter or bomber ends in a non-friendly territory, destroy it
            if is_air_unit(unit.unit_type) and territory.team != unit.team:
                units_to_remove.append(unit)

        [territory.units.remove(unit) for unit in units_to_remove]

    session.turn_num += 1
    session.phase_num = PhaseNumber.PURCHASE_UNITS

    return


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


def retrieve_unit_from_territory(territory, unit_to_find):
    """
    This is used to find the db unit in a territory when we are given the unit separately.

    :territory: The territory (class) to check.
    :unit: The unit (class) to find.
    :return unit: The same unit in the given territory.
    """
    for unit in territory.units:
        if unit == unit_to_find:
            return unit

    raise BaseException(
        "Unit could not be found in the specified territory. U ID: ${unit_to_find.unit_id}")


def attempt_to_load_air_unit_on_carrier(territory, unit_to_load):
    """
    Check if there are any aircraft carriers in the territory and load the unit onto it.

    :territory: The territory (class) to check.
    :unit: The unit (class) to find.
    :return bool: True if the unit was loaded onto a carrier, False otherwise.
    """
    for unit in territory.units:
        if unit.unit_type == "AIRCRAFT-CARRIER":
            if len(unit.cargo) < 2:
                unit.cargo.append(unit_to_load)
                return True

    return False


def is_hostile_territory(territory, player_team_num):
    """
    Check if a territory is controlled by a hostile player.

    :territory: The territory (class) to check.
    :player_team_num: The team number of the player.
    :return bool: True if the territory is hostile, False otherwise.
    """
    hostile_team_numbers = [0, 2, 4] if player_team_num in [1, 3] else [1, 3]

    return territory.team != player_team_num and territory.team in hostile_team_numbers
