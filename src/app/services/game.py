from collections import Counter

from app.models.territory_data import TERRITORY_DATA
from app.models.unit_data import UNIT_DATA


"""
validate_unit_movement

move_units

end_turn

"""


def validate_unit_movement(game_state, territory_a, territory_b, units_to_move):
    """
    Validates that the unit can move to the new territory.
    """
    total_unit_count = Counter(game_state.units)
    moving_unit_count = Counter(units_to_move)

    if not all(total_unit_count[unit] >= moving_unit_count[unit] for unit in moving_unit_count):
        # not enough units of that type in the territory
        return False

    # make sure territories are neighbors
    territory_a_data = TERRITORY_DATA[territory_a]

    return territory_b in territory_a_data['neighbors']


def move_units(game_state, territory_b, units_to_move):
    """
    Moves the units from territory A to territory B.
    """
    moving_unit_count = Counter(units_to_move)

    for unit in game_state.units:
        if moving_unit_count[unit] > 0:
            moving_unit_count[unit] -= 1
            unit.territory = territory_b
            unit.movement -= 1

    # major error if reached
    # TODO add logging

    return True


def end_turn(game_state):
    """
    Ends the current player's turn and resets unit movement.
    """
    for unit in game_state.units:
        unit.movement = UNIT_DATA[unit.unit_type].movement

    return True
