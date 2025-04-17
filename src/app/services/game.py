from random import randint

from app.models.territory_data import TERRITORY_DATA
from app.models.unit_data import UNIT_DATA
from app.models.session import Session, PhaseNumber
from app.models.unit import Unit

from app.services.game_helpers import (
    get_hostile_team_nums_for_player,
    is_land_unit,
    is_sea_unit,
    is_air_unit, retrieve_unit_from_territory,
    check_territory_has_adjacent_industrial_complex,
    is_hostile_territory,
    territory_has_hostile_units,
    player_can_purchase_industrial_complex,
    has_unresolved_aa_fire,
    has_unresolved_sea_combat,
    surviving_battleships_from_casualties,
    remove_air_unit_from_all_battles,
    find_and_remove_unit_from_game,
    find_amphibious_assault_land_battle,
    reload_units_onto_transport_from_anywhere,
)


"""
The real meat-and-potatoes of the app.

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
        if unit.in_combat_this_turn and unit.unit_type == "ANTI-AIRCRAFT":
            return False, "Anti-aircraft units cannot move after firing in combat."

        """Validation Passed"""

    # If entering an enemy territory, either capture it (no enemy units) or create a battle
    is_enemy_territory = is_hostile_territory(territory_b, player.team_num)

    has_enemy_units = territory_has_hostile_units(territory_b, player.team_num)

    moving_force_has_land_unit = any(is_land_unit(unit.unit_type)
                                     for unit in units_to_move)

    moving_force_air_units = [
        unit.to_dict() for unit in units_to_move if is_air_unit(unit.unit_type)]

    defending_force_has_aa_unit = any(unit.unit_type == "ANTI-AIRCRAFT"
                                      for unit in territory_b.units)

    if is_enemy_territory:

        # Not allowed for any units during non-combat phase
        if session.phase_num != PhaseNumber.COMBAT_MOVE:
            return False, "Units cannot move into hostile territories in non-combat phase."

        if not has_enemy_units and moving_force_has_land_unit:
            territory_b.team = player.team_num

        if has_enemy_units:

            game_state.add_battle(
                player.team_num, territory_b_name, territory_a_name, is_ocean=territory_b_is_ocean)

            # If moving force has air units and defending force has
            # anti-aircraft, there is a special attack that will occur
            # before all other combat, giving the AA a chance to hit
            # air units without retaliation.
            if moving_force_air_units and defending_force_has_aa_unit:
                game_state.add_battle(
                    player.team_num, territory_b_name, territory_a_name, is_aa_attack=True, air_units=moving_force_air_units)

    # Air units and submarines can uniquely move out of a combat zone
    # if the last territory had a battle but there are no longer fighting units,
    # remove the battle
    prev_territory_has_friendly_units = any(
        unit for unit in territory_a.units if unit.team == player.team_num and unit not in units_to_move)
    prev_territory_has_enemy_units = territory_has_hostile_units(
        territory_a, player.team_num)

    if not prev_territory_has_friendly_units and prev_territory_has_enemy_units:
        game_state.remove_battle(territory_a_name)

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
            unit.movement = 0

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

    has_enemy_units = territory_has_hostile_units(
        selected_territory, player.team_num)

    if is_enemy_territory:

        if not has_enemy_units:
            selected_territory.team = player.team_num

        if has_enemy_units:
            battle = game_state.add_or_find_battle(
                player.team_num, selected_territory_name, sea_territory_name)

            # Track which transport unloaded which units in case they are destroyed
            transport_details = {
                transport.unit_id: [unit.unit_id for unit in transport.cargo]}

            battle['unloaded_transports'].append(transport_details)

    # units cannot move after unloading
    for unit in transport.cargo:
        unit.movement = 0

    # move units to land territory
    selected_territory.units.extend(transport.cargo)
    transport.cargo = []

    return True, None


def combat_opening_fire(game_state, territory_name):
    """
    In the first round of combat, some special units can fire before
    the main combat begins.

    Battleships can attack land units during an amphibious assault
    if there was no sea battle in the sea territory.

    (Ocean combat) submarines get to attack before the main combat
    begins.

    Any units destroyed in opening fire do not get to fire back.
    """
    battle, message = validate_combat_attack_and_retrieve_battle(
        game_state, territory_name)

    if not battle:
        return False, message

    # player team num
    attacker_team_num = battle.get('attacker')

    defending_team_numbers = get_hostile_team_nums_for_player(
        attacker_team_num)

    """
    Battleship bombardment
    
    Battleships can attack land units during an amphibious assault but only if they did not
    already take part in a sea battle.
    """

    # if this is land and the attack from is sea
    current_territory_is_land = not TERRITORY_DATA[territory_name]['is_ocean']

    attack_from_territory_name = battle.get('attack_from')

    attack_from_territory_is_ocean = TERRITORY_DATA[attack_from_territory_name]['is_ocean']

    # and there was no sea battle there
    sea_battle_occurred = game_state.get_battle(
        attack_from_territory_name, is_ocean=True).get('result') is not None

    # if the current battle is land, the attack is from ocean, and there was no sea battle there...
    if current_territory_is_land and attack_from_territory_is_ocean and not sea_battle_occurred:

        # get the battleships in the territory
        attack_from_territory = game_state.territories[attack_from_territory_name]

        battleships = [unit for unit in attack_from_territory.units if unit.unit_type ==
                       "BATTLESHIP" and unit.team == attacker_team_num]

        # each battleships gets an attack roll for free
        attack_rolls = [combat_roll(unit, is_attacker=True)
                        for unit in battleships]

        defender_casualty_count = sum(roll['result'] for roll in attack_rolls)

        current_territory = game_state.territories[territory_name]

        defender_casualties = combat_auto_select_defender_casualties(
            current_territory, battle, defending_team_numbers, defender_casualty_count)

        # Remove casualties from game
        current_territory.units = [
            unit for unit in current_territory.units if unit not in defender_casualties]

    """
    Submarine attack
    
    Submarines get a free attack to start, but only if the other side doesn't have destroyers.
    """
    current_territory_is_ocean = TERRITORY_DATA[territory_name]['is_ocean']

    if current_territory_is_ocean:

        current_territory = game_state.territories[territory_name]

        # get all sea units for both sides
        attacker_sea_units = [unit for unit in current_territory.units if unit.team ==
                              attacker_team_num and is_sea_unit(unit.unit_type)]
        defender_sea_units = [
            unit for unit in current_territory.units if unit.team in defending_team_numbers and is_sea_unit(unit.unit_type)]

        # get all attacker and defender subs
        attacker_subs = [unit for unit in current_territory.units if unit.unit_type ==
                         "SUBMARINE" and unit.team == attacker_team_num]
        defender_subs = [unit for unit in current_territory.units if unit.unit_type ==
                         "SUBMARINE" and unit.team in defending_team_numbers]

        # if a destroyer exists for either side, skip the opening submarine attack for the other player
        attacker_has_destroyer = any(
            unit for unit in attacker_sea_units if unit.unit_type == "DESTROYER")
        defender_has_destroyer = any(
            unit for unit in defender_sea_units if unit.unit_type == "DESTROYER")

        # subs get a free attack on sea units only
        attacker_sub_rolls = []
        defender_sub_rolls = []

        if not defender_has_destroyer:
            attacker_sub_rolls = [combat_roll(
                unit, is_attacker=True) for unit in attacker_subs]

        if not attacker_has_destroyer:
            defender_sub_rolls = [combat_roll(
                unit, is_attacker=True) for unit in defender_subs]

        # Auto select casualties
        attacker_casualty_count = sum(roll['result']
                                      for roll in defender_sub_rolls)

        attacker_casualties = combat_auto_select_defender_casualties(
            current_territory, battle, [attacker_team_num], attacker_casualty_count)

        defender_casualty_count = sum(roll['result']
                                      for roll in attacker_sub_rolls)

        defender_casualties = combat_auto_select_defender_casualties(
            current_territory, battle, defending_team_numbers, defender_casualty_count)

        # Remove casualties from game
        current_territory.units = [
            unit for unit in current_territory.units if unit not in attacker_casualties + defender_casualties]


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
        unit for unit in territory.units if unit.team in defending_team_numbers and unit.unit_type != "ANTI-AIRCRAFT"]

    # if this is an AA fire combat, only defending anti-aircraft units roll
    if battle.get('is_aa_attack'):

        # set attacking units to the air_units field on the battle
        air_units = [Unit.from_dict(unit)
                     for unit in battle['air_units']]

        # each AA gun fires once per air unit
        defending_units = [unit for unit in territory.units if unit.team in defending_team_numbers
                           and unit.unit_type == "ANTI-AIRCRAFT"] * len(air_units)

        # set movement for AA guns
        for unit in defending_units:
            unit.in_combat_this_turn = True

        # Air units do not attack back
        attacking_units = []

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
    - if there are any unresolved AA fire, they must be resolved first
    - if there are any unresolved sea battles, they must be resolved first
    - if any battles are resolving causalties, they cannot attack (mid combat turn)
    - player cannot have two battles ongoing at the same time
    """
    unresolved_aa_fire_exists = has_unresolved_aa_fire(game_state)
    unresolved_sea_combat_exists = has_unresolved_sea_combat(game_state)

    # Find the battle for the given territory
    if unresolved_aa_fire_exists:
        battle = next((battle for battle in game_state.battles if battle.get(
            'location') == territory_name and battle.get('is_aa_attack') and battle.get('result') is None), None)

        if not battle:
            return False, "No battle found for the given territory."

    elif unresolved_sea_combat_exists:
        battle = next((battle for battle in game_state.battles if battle.get(
            'location') == territory_name and battle.get('is_ocean') and battle.get('result') is None), None)

        if not battle:
            return False, "No battle found for the given territory."

    else:
        battle = next((battle for battle in game_state.battles if battle.get(
            'location') == territory_name and battle.get('result') is None), None)

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
    if battle.get('is_aa_attack'):
        attacker_casualties = [
            unit for unit in casualty_units
            if any(unit['unit_id'] == air_unit['unit_id'] for air_unit in battle['air_units'])
        ]
    else:
        attacker_casualties = [retrieve_unit_from_territory(
            territory, unit) for unit in casualty_units]

        if not all(attacker_casualties):
            return False, "Some units are not in the territory."

        # Special rule, Battleships take two hits to destroy
        surviving_battleships = surviving_battleships_from_casualties(
            battle, attacker_casualties)

        attacker_casualties = [
            unit for unit in attacker_casualties if unit.unit_id not in surviving_battleships]

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
            unit for unit in territory.units if unit.team in defending_team_numbers and unit.unit_type != "ANTI-AIRCRAFT"]

    if battle.get('is_aa_attack'):
        # remove air units from all possible battles
        [remove_air_unit_from_all_battles(game_state, destroyed_unit)
         for destroyed_unit in attacker_casualties]

        # find and remove actual unit from game
        [find_and_remove_unit_from_game(
            game_state, destroyed_unit) for destroyed_unit in attacker_casualties]

    elif battle.get('is_ocean'):

        # Check if there is an amphibious assault originating from this territory
        land_battle = next((battle for battle in game_state.battles if battle.get(
            'attack_from') == territory_name and not battle.get('is_aa_attack') and not battle.get('is_ocean') and not battle.get('result')), None)

        # Make sure any destroyed transports also remove their recently unloaded units
        casualty_unit_ids = [unit.unit_id for unit in attacker_casualties]

        for transport in land_battle.get('unloaded_transports', []):
            for transport_id, unit_ids in transport.items():

                # remove each cargo unit from the game
                if transport_id in casualty_unit_ids:
                    [find_and_remove_unit_from_game(
                        game_state, {'unit_id': cargo_unit}) for cargo_unit in unit_ids]

    # Make sure the user selected a unit for each casualty, or all remaining units
    # Either the casualties equals the number of defender hits or there
    # are no attacker units left

    attacker_casualty_count = sum(roll['result']
                                  for roll in battle['defender_rolls'])

    # Verify the attacker has selected the correct number of casualties
    if not battle.get('is_aa_attack') and attacking_units and len(attacker_casualties) + len(surviving_battleships) != attacker_casualty_count:
        return False, "Number of selected units does not match the number of casualties."

    # If either side has lost all units, resolve combat

    # Or if this is an AA fire, resolve immediately
    if battle.get('is_aa_attack'):
        battle['result'] = 'defender'

    # if there are no attacking units, the defender wins (includes draws)
    elif not attacking_units:
        battle['result'] = 'defender'

    # if there are attacking units and no defending units, attacker wins (territory flips)
    elif attacking_units and not defending_units:
        battle['result'] = 'attacker'

        # territories cannot be captured by air units
        if any(not is_air_unit(unit.unit_type) for unit in attacking_units):
            territory.team = attacker_team_num

            # also transfer any anti-aircraft units to the attacker
            for unit in territory.units:
                if unit.unit_type == "ANTI-AIRCRAFT":
                    unit.team = attacker_team_num

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
        unit for unit in territory.units if unit.team in defending_team_numbers and unit.unit_type != "ANTI-AIRCRAFT"]

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

    # if a transport is retreating from an amphibious assault, landed units need to be reloaded
    if battle_territory_generic_data['is_ocean']:

        # Check if there is an amphibious assault originating from this territory
        ampibious_assault_land_battle = find_amphibious_assault_land_battle(
            game_state, territory_name)

        # Make sure any destroyed transports also remove their recently unloaded units
        retreating_sea_unit_ids = [unit.unit_id for unit in retreating_units]

        for transport in ampibious_assault_land_battle.get('unloaded_transports', []):
            for transport_id, unit_ids in transport.items():

                # move units from territory to transport
                if transport_id in retreating_sea_unit_ids:
                    reload_units_onto_transport_from_anywhere(
                        game_state, transport_id, unit_ids)

    # if land units are retreating during an amphibious assault, they need to be reloaded onto transports
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
