from random import randint

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


def purchase_unit(game_state, player, unit_type_to_purchase):
    """
    Validate player has funds. Add unit to waiting pool (placed at end of round)
    and remove IPCs from player.

    :return bool: if the purchase was successful.
    """
    new_unit_data = UNIT_DATA[unit_type_to_purchase]

    # special rule, do not allow player to purchase an industrial complex
    # if they have no where to place it
    if unit_type_to_purchase == "INDUSTRIAL-COMPLEX":
        if not player_can_purchase_industrial_complex(game_state, player):
            return False

    # player must have sufficient funds
    if player.ipcs < new_unit_data['cost']:
        return False

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
    :territory_a_name: The name of the territory to move from
    :territory_b_name: The name of the territory to move to
    :units_to_move: The list of units to move (as dict).
    :return bool: if the units were successfully moved.
    """
    territory_a = game_state.territories[territory_a_name]
    territory_b = game_state.territories[territory_b_name]

    territory_a_generic_data = TERRITORY_DATA[territory_a_name]
    territory_b_generic_data = TERRITORY_DATA[territory_b_name]

    territory_b_is_ocean = territory_b_generic_data['is_ocean']

    # territories are neighbors
    if not territory_b_name in territory_a_generic_data['neighbors']:
        return False, "Territories are not neighbors."

    # fetch units from game_state and validate they are in territory A
    units_to_move = [retrieve_unit_from_territory(
        territory_a, Unit.from_dict(unit)) for unit in units_to_move]
    if not all(units_to_move):
        return False, "All/some units are not in the territory."

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

    # If entering an enemy territory, either capture it (no enemy units) or create a battle
    is_enemy_territory = is_hostile_territory(territory_b, player.team_num)

    has_enemy_units = has_hostile_units(territory_b, player.team_num)

    moving_force_has_land_unit = any(is_land_unit(unit.unit_type)
                                     for unit in units_to_move)

    # Either capture empty enemy territories or create a battle
    if is_enemy_territory:

        if not has_enemy_units and moving_force_has_land_unit:
            territory_b.team = player.team_num

        if has_enemy_units:
            game_state.add_battle(
                player.team_num, territory_b_name, territory_a_name)

    # Adjust movement of all moving units
    for unit in units_to_move:
        unit.movement -= 1

        # Land and sea units must stop once they enter a hostile territory
        # Tanks lose movement only if there are hostile units in the territory
        if (
            is_enemy_territory
            and not is_air_unit(unit.unit_type)
            and (
                not unit.unit_type == "TANK"
                or (unit.unit_type == "TANK" and has_enemy_units)
            )
        ):
            unit.movement = 0  # will be subtracted to 0 later

    # remove units from territory A
    territory_a.units = [
        unit for unit in territory_a.units if unit not in units_to_move]

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

    :param game_state: The current game state.
    :param player: The player making the move.
    :param territory_name: The sea territory where the transports are loading.
    :param transport: The transport unit to load the units onto.
    :param units_to_load: The list of units to load (as dict).
    :return: Bool, if the units were successfully loaded.
    """
    # get sea territory
    sea_territory = game_state.territories[territory_name]
    sea_territory_generic_data = TERRITORY_DATA[territory_name]

    if not sea_territory_generic_data["is_ocean"]:
        return False, "Selected territory is not an ocean."

    # load transport from game_state, also ensures it exists in territory
    transport = retrieve_unit_from_territory(sea_territory, transport)
    if not transport:
        return False, "Transport not found in territory."

    # transport is owned by player
    if transport.team != player.team_num:
        return False, "Transport is not owned by player."

    # unit validation
    for unit in units_to_load:
        unit_territory_name = unit["territory"]
        unit_territory = game_state.territories[unit_territory_name]

        # fetch unit from game_state
        unit = Unit.from_dict(unit)
        unit = retrieve_unit_from_territory(unit_territory, unit)
        if not unit:
            return False, "Unit not found in territory."

        # each unit is in a friendly territory
        if unit_territory.team != player.team_num:
            return False, "Unit is not in a friendly territory."

        # each unit is in a territory that neighbors the sea territory
        if unit_territory_name not in sea_territory_generic_data['neighbors']:
            return False, "Unit is not in a neighboring territory."

        # units must have movement available
        # TODO untested
        if unit.movement < 1:
            return False, "Unit does not have enough movement."

        # if transport, must be a land unit
        if transport.unit_type == "TRANSPORT" and (not is_land_unit(unit.unit_type) or unit.unit_type == "ANTI-AIRCRAFT"):
            return False, "Transport can only load land units, excluding anti-aircraft."

        # if carrier, must be an air unit
        if transport.unit_type == "AIRCRAFT-CARRIER" and not is_air_unit(unit.unit_type):
            return False, "Carrier can only load air units."

        # move unit to transport
        transport.cargo.append(unit)
        unit_territory.units.remove(unit)

    # final validation, transport can only have 2 units and 1 must be infantry if max
    if len(transport.cargo) > 2:
        return False, "Transport cannot have more than 2 units."

    # full transports (2 units), one must be infantry
    if (transport.unit_type == "TRANSPORT" and len(transport.cargo) == 2 and
            not any(unit.unit_type == "INFANTRY" for unit in transport.cargo)):
        return False, "Transport must have 1 infantry and 1 other land unit."

    return True, None


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
    if not transport:
        return False, "Transport not found in territory."

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

    # If entering an enemy territory, either capture it (no enemy units) or create a battle
    is_enemy_territory = is_hostile_territory(
        selected_territory, player.team_num)

    has_enemy_units = has_hostile_units(selected_territory, player.team_num)

    if is_enemy_territory:

        if not has_enemy_units:
            selected_territory.team = player.team_num

        # TODO do not duplicate for each unload, add to existing
        if has_enemy_units:
            game_state.add_battle(
                player.team_num, selected_territory_name, sea_territory_name)

    # units cannot move after unloading
    for unit in transport.cargo:
        unit.movement = 0

    # move units to land territory
    selected_territory.units.extend(transport.cargo)
    transport.cargo = []

    return True, None


def sort_battles(game_state):
    """
    Sort battles by sea first, and then land.
    Order is important because they are resolved in order.

    :param game_state: The current game state.
    :return: Bool, if the sorting was successful.
    """
    game_state.battles = sorted(
        game_state.battles,
        key=lambda x: not TERRITORY_DATA[x['location']]['is_ocean']
    )

    return True


def combat_opening_fire(game_state, territory_name):
    """
    In the first round of combat, some special units can fire before
    the main combat begins.

    Anti-aircraft guns can fire at air units as if the air units
    are passing over the territory.

    Battleships can attack land units during an amphibious assault
    if there was no sea battle in the sea territory.

    (Ocean combat) submarines get to attack before the main combat
    begins.

    Any units destroyed in opening fire do not get to fire back.
    """
    # Anti aircraft guns
    # Battleship bombardment
    # Submarine attack
    pass


def combat_attack(game_state, territory_name):
    """
    Main combat attack intiated by the attacker.

    Each combat must have at least one attack and combat is resolved
    only when a side loses all of its units, or the attacker retreats.
    """
    battle, message = validate_combat_attack_and_retrieve_battle(
        game_state, territory_name)

    if not battle:
        return False, message

    # if this is the first round of combat, perform opening fire
    if battle.get('turn') == 0:
        combat_opening_fire(game_state, territory_name)

    # get the attacking and defending units
    territory = game_state.territories[territory_name]

    attacker_team_num = battle.get('attacker')
    defending_team_numbers = get_hostile_team_nums_for_player(
        attacker_team_num)

    attacking_units = [
        unit for unit in territory.units if unit.team == attacker_team_num]
    defending_units = [
        unit for unit in territory.units if unit.team in defending_team_numbers]

    # roll for attack and defense
    battle['attacker_rolls'] = [combat_roll(unit, is_attacker=True)
                                for unit in attacking_units]
    battle['defender_rolls'] = [combat_roll(unit, is_attacker=False)
                                for unit in defending_units]

    battle['is_resolving_turn'] = True

    return True, None


def validate_combat_attack_and_retrieve_battle(game_state, territory_name):
    """
    Validation for combat attack:
    - if there are any unresolved sea battles, they must be resolved first
    - if any battles are resolving causalties, they cannot attack (mid combat turn)
    - player cannot have two battles ongoing at the same time
    """
    has_unresolved_sea_combat = any(TERRITORY_DATA[battle.get('location')]['is_ocean']
                                    and battle.get('result') is None
                                    for battle in game_state.battles)

    if has_unresolved_sea_combat and not TERRITORY_DATA[territory_name]['is_ocean']:
        return False, "There are unresolved sea battles. Resolve them first."

    # Find the battle for the given territory
    battle = next((battle for battle in game_state.battles if battle.get(
        'location') == territory_name), None)

    if not battle:
        return False, "No battle found for the given territory."

    # if the player must select casualties, they cannot attack
    if any(battle.get('is_resolving_turn') for battle in game_state.battles):
        return False, "Cannot attack. Battle has casualties to resolve."

    # Player cannot have two battles ongoing at the same time
    ongoing_battles = [
        battle for battle in game_state.battles if battle.get('turn') > 0 and battle.get('result') is None]

    if ongoing_battles and battle.get('turn') == 0:
        return False, f"Battles must be resolved one at a time. See: {ongoing_battles[0]['location']}"

    return battle, None


def combat_roll(unit, is_attacker=True):
    """
    Roll for a unit's attack or defense.

    A roll is a HIT if it is less than or equal to the unit's attack or defense value.

    :param unit: The unit to roll for.
    :param is_attacker: True if the unit is attacking, False if defending.
    :return: Dict, with the roll and bool if the roll was successful.
    """
    unit_type_data = UNIT_DATA[unit.unit_type]

    roll_to_hit = unit_type_data['attack'] if is_attacker else unit_type_data['defense']

    roll = randint(1, 6)

    return {'unit_id': unit.unit_id, 'roll': roll, 'result': roll <= roll_to_hit}


def combat_select_casualties(game_state, territory_name, casualty_units):
    """
    This is where units are actually removed and the battle is concluded.
    Remove the attacker's selected casualties, and auto-remove the defenders
    casualties.

    This also handles resolving combat.

    If either force is wiped out, the combat is automatically ended.

    :param game_state: The current game state.
    :param territory_name: The name of the territory.
    :param casualty_units: The list of units to remove.
    :return: Bool, if the casualties were successfully selected.
    """
    territory = game_state.territories[territory_name]

    battle = next((battle for battle in game_state.battles if battle.get(
        'is_resolving_turn')), None)

    if not battle or battle.get('location') != territory_name:
        return False, "Territory is not the current battle."

    attacker_team_num = battle.get('attacker')

    defending_team_numbers = get_hostile_team_nums_for_player(
        attacker_team_num)

    # Convert request units to game_state units
    attacker_casualties = [retrieve_unit_from_territory(
        territory, unit) for unit in casualty_units]

    if not all(attacker_casualties):
        return False, "Some units are not in the territory."

    # Special rule, Battleships take two hits to destroy
    first_hit_battleships = []

    for unit in attacker_casualties:
        if unit.unit_type == "BATTLESHIP":

            # A battleship is sent twice by the frontend to represent two hits,
            # or once to represent one hit.
            if unit.unit_id not in battle['hit_battleships']:
                first_hit_battleships.append(unit.unit_id)
                battle['hit_battleships'].append(unit.unit_id)

            # if the battleship has been hit, remove it from the list of living battleships
            elif unit.unit_id in first_hit_battleships:
                first_hit_battleships.remove(unit.unit_id)

    attacker_casualties = [
        unit for unit in attacker_casualties if unit.unit_id not in first_hit_battleships]

    # Auto select defender casualties
    defender_casualty_count = sum(roll['result']
                                  for roll in battle['attacker_rolls'])

    defender_casualties = combat_auto_select_defender_casualties(
        territory, battle, defending_team_numbers, defender_casualty_count)

    # Remove casualties from game
    territory.units = [
        unit for unit in territory.units if unit not in attacker_casualties + defender_casualties]

    attacking_units = [
        unit for unit in territory.units if unit.team == attacker_team_num]

    defending_units = [
        unit for unit in territory.units if unit.team in defending_team_numbers]

    # Make sure the user selected a unit for each casualty, or all remaining units
    # Either the casualties equals the number of defender hits or there
    # are no attacker units left

    attacker_casualty_count = sum(roll['result']
                                  for roll in battle['defender_rolls'])

    # Verify the attacker has selected the correct number of casualties
    if attacking_units and len(attacker_casualties) + len(first_hit_battleships) != attacker_casualty_count:
        return False, "Number of selected units does not match the number of casualties."

    # If either side has lost all units, resolve combat

    # if there are no attacking units, the defender wins (includes draws)
    if not attacking_units:
        battle['result'] = 'defender'

    # if there are attacking units and no defending units, attacker wins (territory flips)
    elif attacking_units and not defending_units:
        battle['result'] = 'attacker'

        # territories cannot be captured by air units
        if any(not is_air_unit(unit.unit_type) for unit in attacking_units):
            territory.team = attacker_team_num

    battle['attacker_rolls'] = []
    battle['defender_rolls'] = []
    battle['is_resolving_turn'] = False
    battle['turn'] += 1

    return True, None


def combat_auto_select_defender_casualties(territory, battle, defending_team_numbers, defender_casualty_count):
    """
    Defender does not choose which units to lose. Instead, they will be
    selected from the least to most valuable.

    Prioritize battleship first hits and then lowest to most valuable units.

    :param territory: The territory the battle is in.
    :param defender_casualty_count: The number of casualties to select.
    :return: List of units to remove.
    """
    units_to_remove = []

    defending_units = [
        unit for unit in territory.units if unit.team in defending_team_numbers]

    # sort units by value
    unit_priority = {"SUBMARINE": 1, "TRANSPORT": 2}

    defending_units.sort(
        key=lambda unit: (UNIT_DATA[unit.unit_type]['cost'],
                          unit_priority.get(unit.unit_type, 0)))

    # for each battleship in the list, check if it has been hit
    # if it hasn't been hit, add it to the list of hit battleships
    # and reduce casualty count by one
    for unit in defending_units:
        if unit.unit_type == "BATTLESHIP" and unit.unit_id not in battle['hit_battleships']:
            battle['hit_battleships'].append(unit.unit_id)
            defender_casualty_count -= 1

    # now start selecting units as casualties
    for unit in defending_units:
        if defender_casualty_count <= 0:
            break

        # remove unit from territory
        units_to_remove.append(unit)
        defender_casualty_count -= 1

    return units_to_remove


def combat_retreat(game_state, territory_name):
    """
    End combat and retreat the attacker to the territory they attacked from.

    For a retreat to be possible, the battle must be on its second round.
    There should also only be one battle that is unresolved and ongoing.

    Amphibious assault retreats make the units reload onto the transports
    they came from.

    :param game_state: The current game state.
    :param territory_name: The name of the territory.
    :return: Bool, if the retreat was successful.
    """
    # breakpoint()

    battle_territory = game_state.territories[territory_name]
    battle_territory_generic_data = TERRITORY_DATA[territory_name]

    # fetch ongoing battle
    battle = next((battle for battle in game_state.battles if battle.get(
        'turn') > 0 and not battle.get('result') and not battle.get('is_resolving_turn')), None)

    if not battle or battle.get('location') != territory_name:
        return False, "Territory is not the current battle."

    retreat_territory_name = battle.get('attack_from')
    retreat_territory = game_state.territories[retreat_territory_name]
    retreat_territory_generic_data = TERRITORY_DATA[retreat_territory_name]

    # get retreating units
    attacker_team_num = battle.get('attacker')
    retreating_units = [
        unit for unit in battle_territory.units if unit.team == attacker_team_num]

    # if we are retreating from land to ocean
    if not battle_territory_generic_data['is_ocean'] and retreat_territory_generic_data['is_ocean']:

        # This means the attacker is retreating during an amphibious assault

        # Load units onto transports
        load_retreating_units_onto_transports(
            game_state, battle_territory, retreat_territory, attacker_team_num)

    # else just move the units
    else:
        battle_territory.units = [
            unit for unit in battle_territory.units if unit not in retreating_units]

        retreat_territory.units.extend(retreating_units)

    # finally mark the battle as a loss for the attacker
    battle['result'] = 'defender'

    return True, None


def load_retreating_units_onto_transports(game_state, battle_territory, sea_territory, attacker_team_num):
    """
    Load all units onto transports in the sea territory.

    This happens when an attacker retreats during an amphibious assault.

    There must be a transport for each unit retreating, otherwise they would have been
    destroyed before the retreat.

    Excess units are destroyed (although this shouldn't happen.)

    :param game_state: The current game state.
    :param battle_territory: The territory the battle is in.
    :param sea_territory: The sea territory the units are retreating to.
    :param attacker_team_num: The team number of the attacker.
    :return: Bool, if the units were successfully loaded.
    """
    # get the retreating units
    retreating_units = [
        unit for unit in battle_territory.units if unit.team == attacker_team_num]

    # sort the retreating units by infantry first
    retreating_units.sort(
        key=lambda unit: (unit.unit_type != "INFANTRY", UNIT_DATA[unit.unit_type]['cost']))

    # get the transports in the sea territory
    transports = [unit for unit in sea_territory.units if unit.unit_type ==
                  "TRANSPORT" and unit.team == attacker_team_num]

    # for each transport, load one infantry
    for transport in transports:
        if not retreating_units:
            break

        # find the infantry unit
        infantry_unit = next(
            (unit for unit in retreating_units if unit.unit_type == "INFANTRY"), None)

        if infantry_unit:
            transport.cargo.append(infantry_unit)
            battle_territory.units.remove(infantry_unit)
            retreating_units.remove(infantry_unit)

    # now iterate again...
    # for each transport, load one remaining unit
    for transport in transports:
        if not retreating_units:
            break

        land_unit = next((unit for unit in retreating_units), None)

        if land_unit:
            transport.cargo.append(land_unit)
            battle_territory.units.remove(land_unit)
            retreating_units.remove(land_unit)

    # TODO this should never happen, log it if it does
    # if there are any remaining units, they are destroyed
    if retreating_units:
        for unit in retreating_units:
            battle_territory.units.remove(unit)

    return True


def remove_resolved_battles(game_state):
    """
    Validate all battles have been resolved. If they have, remove them from the game state.

    :param game_state: The current game state.
    :return: Bool, if the battles were successfully removed.
    """
    if any(battle.get('result') is None for battle in game_state.battles):
        return False, "Not all battles have been resolved."

    game_state.battles = []

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

        # if land unit, the selected territory must be land and have an industrial complex
        if is_land_unit(unit_type):
            can_place_in_land = not is_ocean and is_controlled_by_player and has_factory

            if not can_place_in_land:
                return False

        # if sea unit, it must be be sea and have an adjacent controlled industrial complex
        if is_sea_unit(unit_type):
            can_place_in_sea = is_ocean and has_adjacent_industrial_complex

            if not can_place_in_sea:
                return False

        # if air unit, it can be placed in a sea territory with a carrier or a land territory
        if is_air_unit(unit_type):
            can_place_in_sea = is_ocean and has_adjacent_industrial_complex and can_mobilize_air_unit_in_sea(
                selected_territory_data, units_to_mobilize)
            can_place_in_land = not is_ocean and is_controlled_by_player and has_factory

            if not (can_place_in_sea or can_place_in_land):
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

        if units_to_remove:
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


def can_mobilize_air_unit_in_sea(territory, units_to_mobilize):
    """
    Air units can be mobilized in a sea territory if there is an aircraft carrier with room.
    This also includes carriers in the mobilization forces.

    Count the total cargo available in the territory and the mobilization forces and
    check if there is room for all air units.

    :territory: The territory (class) to check.
    :units_to_mobilize: The list of units to mobilize.
    :return bool: True if there is room for air units.
    """
    current_cargo_space_available_in_territory = sum(
        [2 - len(unit.cargo) for unit in territory.units if unit.unit_type == "AIRCRAFT-CARRIER"])

    count_of_carriers_in_mobilization_forces = 2 * len(
        [unit for unit in units_to_mobilize if unit['unit_type'] == "AIRCRAFT-CARRIER"])

    count_of_air_units_in_mobilization_forces = len(
        [unit for unit in units_to_mobilize if is_air_unit(unit['unit_type'])])

    return count_of_air_units_in_mobilization_forces <= current_cargo_space_available_in_territory + count_of_carriers_in_mobilization_forces


def attempt_to_load_air_unit_on_carrier(territory, air_unit):
    """
    Check if there are any aircraft carriers in the territory and load the unit onto it.

    :territory: The territory (class) to check.
    :unit: The unit (class) to find.
    :return bool: True if the unit was loaded onto a carrier, False otherwise.
    """
    for unit in territory.units:
        if unit.unit_type == "AIRCRAFT-CARRIER":
            print(f"cargo: {unit.cargo}")
            if len(unit.cargo) >= 2:
                print(f"Carrier is full, cannot load {air_unit.unit_type}")
                return False

            print(
                f"Loading {air_unit.unit_type} onto {unit.unit_type}")
            unit.cargo.append(air_unit)
            return True

    print(f"No available carrier for {air_unit.unit_type} in {territory}")
    return False


def is_hostile_territory(territory, player_team_num):
    """
    Check if a territory is controlled by a hostile player. This stops movement
    for land and sea units except for tanks.

    :territory: The territory to check.
    :player_team_num: The team number of the player.
    :return bool: True if the territory is hostile, False otherwise.
    """
    hostile_team_numbers = get_hostile_team_nums_for_player(player_team_num)

    return territory.team in hostile_team_numbers


def has_hostile_units(territory, player_team_num):
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


def get_hostile_team_nums_for_player(player_team_num):
    """
    Get the team numbers of the hostile players for a given player.

    :player_team_num: The team number of the player.
    :return list: A list of team numbers for the hostile players.
    """
    return [0, 2, 4] if player_team_num in [1, 3] else [1, 3]
