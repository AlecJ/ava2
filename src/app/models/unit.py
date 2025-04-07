from uuid import uuid4

from app.models.unit_data import UNIT_DATA


"""

A Unit is:
    Unit ID
    Team ID
    Unit Type
    Remaining Movement
    Cargo

"""


class Unit:
    def __init__(self, unit_id=None, team=None, unit_type=None, movement=None, cargo=None):
        self.unit_id = unit_id or str(uuid4())
        self.team = team
        self.unit_type = unit_type
        # 0 movement is valid
        self.movement = movement or UNIT_DATA[unit_type]['movement']
        self.cargo = cargo if cargo is not None else []

        # todo -- does this do anything
        if team is None or unit_type is None:
            raise ValueError(
                "Cannot instatiate Unit Class: Invalid data: missing required values.")

    def __repr__(self):
        return (
            f"<Unit(id={self.unit_id}, type={self.unit_type}, team={self.team}>"
        )

    def __eq__(self, other):
        """
        Checks if two units are the same based on their type, team, territory, and movement.
        """
        return (self.unit_id == other.unit_id and
                self.unit_type == other.unit_type and
                self.team == other.team and
                self.movement == other.movement)

    def __hash__(self):
        """
        This is necessary to enable Counters for checking if a list of units is a subset of another list.

        See GameState.move_units for more details.
        """
        return hash((self.unit_type, self.team, self.movement))

    def to_dict(self):
        """
        Converts the Unit object to a dictionary for JSON serialization.
        """
        # if len(self.cargo) > 0:
        #     breakpoint()

        # print(self.cargo)
        # print(len(self.cargo))

        return {
            'unit_id': self.unit_id,
            'team': self.team,
            'unit_type': self.unit_type,
            'movement': self.movement,
            'cargo': [unit.to_dict() for unit in self.cargo],
        }

    @classmethod
    def from_dict(cls, data):
        """
        Creates a Unit object from a dictionary.

        If a unit is missing values, this will raise an error.
        """
        try:
            return cls(
                unit_id=data['unit_id'],
                team=data['team'],
                unit_type=data['unit_type'],
                movement=data['movement'],
                cargo=[Unit.from_dict(unit) for unit in data.get('cargo', [])],
            )
        except KeyError as e:
            # TODO log error
            raise ValueError(
                f"Failed to cast Unit json to class: {e}")
