from uuid import uuid4
from app.models.order_of_play import order_of_play


"""

A Player is:
    Player ID
    Session ID
    Country
    IPCs
    MOBILIZATION_UNITS

"""


class Player:
    def __init__(self, player_id=None, session_id=None, country=None, ipcs=0, mobilization_units=[]):
        self.player_id = player_id or str(uuid4())
        self.session_id = str(session_id)
        self.country = country
        self.ipcs = ipcs
        self.mobilization_units = mobilization_units

        if country is None or session_id is None:
            raise ValueError(
                "Cannot instatiate Player Class: Invalid data: missing required values.")

        # logging, or error handling?
        # session cannot be null, neither name nor country

    def __repr__(self):
        return (
            f"<Player(player_id={self.player_id}, "
            f"session_id={self.session_id}, "
            f"country={self.country}),"
            f"apcs={self.ipcs}>"
        )

    def to_dict(self):
        """
        Converts the Player object to a dictionary for JSON serialization.
        """
        return {
            'player_id': self.player_id,
            'session_id': self.session_id,
            'country': self.country,
            'ipcs': self.ipcs,
            'mobilization_units': self.mobilization_units,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Creates a Player object from a dictionary.
        """
        try:
            return cls(
                player_id=data['player_id'],
                session_id=data['session_id'],
                country=data['country'],
                ipcs=data['ipcs'],
                mobilization_units=data.get('mobilization_units', []),
            )
        except KeyError as e:
            raise ValueError(f"Invalid data: missing key {e}")

    @property
    def team_num(self):
        """
        Just sort of came up enough that this should be a function.
        Index of country in order_of_play.
        """
        return order_of_play.index(self.country)
