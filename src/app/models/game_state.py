# from uuid import uuid4
# from enum import Enum
from collections import Counter
from app.models.territory_data import TERRITORY_DATA

from app.models.unit import Unit

"""
This is the game_state object. It tracks the state of the game world including the territories, units, and players.

A game_state is a:

Session ID
List of Units

A Unit is:
Unit Type
Team ID
Territory
Remaining Movement

"""


class GameState:
    def __init__(self, session_id, units=[]):
        self.session_id = session_id
        self.units = units

        if not self.units:
            self.units = self.initialize_units()

    def __str__(self):
        return f"Session {self.session_id}"

    def __repr__(self):
        return (
            f"<Session(session_id={self.session_id}, "
        )

    def to_dict(self):
        """
        Converts the Session object to a dictionary for JSON serialization.
        """
        return {
            'session_id': self.session_id,
            'units': [unit.to_dict() for unit in self.units]
        }

    @classmethod
    def from_dict(cls, data):
        """
        Creates a Session object from a dictionary.

        This should only be used on existing data, not for creating new sessions.

        If a session is missing values, this will raise an error.
        """
        try:
            return cls(
                session_id=data['session_id'],
                units=[Unit.from_dict(unit) for unit in data['units']]
            )
        except KeyError as e:
            # TODO log error
            raise ValueError(
                f"Failed to cast GameState json to class: {e}")

    def initialize_units(self):
        """
        Initializes the units for game start.
        """
        result = []

        for territory_name, territory in TERRITORY_DATA.items():
            for unit in territory['units']:
                result.append(Unit(
                    unit_type=unit['type'],
                    team=unit['team'],
                    territory=territory_name
                ))

        return result

    def validate_unit_movement(self, player_team, territory_a, territory_b, units_to_move):
        """
        Validates that the unit can move to the new territory.
        """
        total_unit_count = Counter(self.units)
        # [{'movement': 2, 'team': 0, 'territory': 'Western United States', 'unit_type': 'INFANTRY', 'selected': True}]
        # cast dict units to class units
        moving_unit_count = Counter(units_to_move)

        # for unit in self.units:
        #     # territory
        #     # team
        #     # type
        #     # movement
        #     if unit.territory == territory_a and unit.team == player_team and unit.unit_type in units_to_move.keys() and units_to_move[unit.unit_type] > 0:
        #         units_to_move[unit.unit_type] -= 1

        # # make sure there were enough of each unit type in the territory
        # for unit_count in units_to_move.values():
        #     if unit_count > 0:
        #         return False

        if not all(total_unit_count[unit] >= moving_unit_count[unit] for unit in moving_unit_count):
            # not enough units of that type in the territory
            return False

        # make sure territories are neighbors
        territory_a_data = TERRITORY_DATA[territory_a]

        return territory_b in territory_a_data['neighbors']

    def move_units(self, player_team, territory_a, territory_b, units_to_move):
        """
        Moves the units from territory A to territory B.
        """
        moving_unit_count = Counter(units_to_move)

        for unit in self.units:
            if moving_unit_count[unit] > 0:
                moving_unit_count[unit] -= 1
                unit.territory = territory_b
                unit.movement -= 1

        return True
