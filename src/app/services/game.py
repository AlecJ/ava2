from app.models.territory_data import TERRITORY_DATA
from app.models.unit_data import UNIT_DATA
from app.models.session import Session, PhaseNumber


"""
purchase_unit

validate_unit_movement

move_units

add_territory_power_to_player_ipcs

end_turn

"""


def purchase_unit(game_state, unit_type_to_purchase):
    """
    Validate player has funds. Add unit to waiting pool (placed at end of round)
    and remove IPCs from player.
    """
    # get player

    # add unit to player

    # remove IPCs


def validate_unit_movement(game_state, territory_a_name, territory_b_name, units_to_move):
    """
    Validates that the unit can move to the new territory.
    """
    territory_a = game_state.territories[territory_a_name]

    # ensure all moving units are in territory A
    units_in_territory_a_ids = {unit.unit_id for unit in territory_a.units}
    moving_unit_ids = {unit.unit_id for unit in units_to_move}
    if not set(units_in_territory_a_ids).issubset(moving_unit_ids):
        return False

    # ensure all units_have movement remaining
    if not all([unit.movement > 0 for unit in territory_a.units if unit.unit_id in moving_unit_ids]):
        return False

    # make sure territories are neighbors
    territory_a_data = TERRITORY_DATA[territory_a_name]

    return territory_b_name in territory_a_data['neighbors']


def move_units(game_state, territory_a_name, territory_b_name, units_to_move):
    """
    Moves the units from territory A to territory B.
    """
    territory_a = game_state.territories[territory_a_name]
    territory_b = game_state.territories[territory_b_name]

    moving_unit_ids = [unit.unit_id for unit in units_to_move]

    units_to_move = [
        unit for unit in territory_a.units if unit.unit_id in moving_unit_ids]

    # decrement moving units' remaining movement
    for unit in units_to_move:
        unit.movement -= 1

    territory_a.units = [
        unit for unit in territory_a.units if unit.unit_id not in moving_unit_ids]
    territory_b.units.extend(units_to_move)

    return


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
    """
    for territory_name, territory in game_state.territories.items():
        # if turn_num % 5 == 0:
        add_territory_power_to_player_ipcs(session, territory_name, territory)

        for unit in territory.units:
            unit.movement = UNIT_DATA[unit.unit_type]['movement']

    session.turn_num += 1
    session.phase_num = PhaseNumber.PURCHASE_UNITS

    return
