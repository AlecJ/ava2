# from app.models.unit_data import UNIT_DATA
from app.models.territory_data import TERRITORY_DATA
from app.models.unit import Unit

"""

A Territory is:
    Team ID
    List of Unit
    has_factory (bool)

A Unit is:
    Unit ID
    Team ID
    Unit Type
    Remaining Movement

"""


class Territory:
    def __init__(self, team, units=None, has_factory=None):
        self.team = team
        self.units = units if units is not None else []
        self.has_factory = has_factory if has_factory is not None else False

    def __repr__(self):
        return (
            f"<Territory(team={self.team}, units={len(self.units)}, has_factory={self.has_factory}>"
        )

    def to_dict(self):
        """
        Converts the Unit object to a dictionary for JSON serialization.
        """
        return {
            'team': self.team,
            'units': [unit.to_dict() for unit in self.units],
            'has_factory': self.has_factory
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
                units=[Unit.from_dict(unit) for unit in data['units']],
                has_factory=data['has_factory'],
            )
        except KeyError as e:
            # TODO log error
            raise ValueError(
                f"Failed to cast Territory json to class: {e}")
