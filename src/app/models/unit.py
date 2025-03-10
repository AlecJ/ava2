from enum import Enum

"""
A Unit is:
Unit Type
Team ID
Territory
Remaining Movement
"""

unit_type_to_movement = {
    'INFANTRY': 2
}


class UnitType(Enum):
    INFANTRY = 'INFANTRY'


class Unit:
    def __init__(self, team, unit_type, territory, movement=None):
        self.team = team
        self.unit_type = unit_type
        self.territory = territory
        self.movement = movement or unit_type_to_movement[unit_type]

        if team is None or unit_type is None or territory is None:
            raise ValueError(
                "Cannot instatiate Unit Class: Invalid data: missing required values.")

    def __str__(self):
        return f"Unit: {self.unit_type} Team: {self.team} Territory: {self.territory}"

    def __repr__(self):
        return (
            f"<Unit(type={self.unit_type}, team={self.team}, territory={self.territory}>"
        )

    def to_dict(self):
        """
        Converts the Unit object to a dictionary for JSON serialization.
        """
        return {
            'team': self.team,
            'unit_type': self.unit_type,
            'territory': self.territory,
            'movement': self.movement,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Creates a Unit object from a dictionary.

        If a unit is missing values, this will raise an error.
        """
        try:
            return cls(
                team=data['team'],
                unit_type=data['unit_type'],
                territory=data['territory'],
                movement=data['movement']
            )
        except KeyError as e:
            # TODO log error
            raise ValueError(
                f"Failed to cast Unit json to class: {e}")
