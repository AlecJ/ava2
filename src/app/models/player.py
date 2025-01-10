from uuid import uuid4


class Player:
    def __init__(self, player_id=uuid4(), session_id=None, name=None, country=None):
        self.player_id = str(player_id)
        self.session_id = session_id
        self.name = name
        self.country = country

        if name is None or country is None or session_id is None:
            raise ValueError(
                "Cannot instatiate Player Class: Invalid data: missing required values.")

        # logging, or error handling?
        # session cannot be null, neither name nor country

    def __str__(self):
        return f"Player {self.player_id} (Name: {self.name}, Country: {self.country})"

    def __repr__(self):
        return (
            f"<Player(player_id={self.player_id}, "
            f"session_id={self.session_id}, "
            f"name={self.name}, "
            f"country={self.country})>"
        )

    def to_dict(self):
        """
        Converts the Player object to a dictionary for JSON serialization.
        """
        return {
            'player_id': self.player_id,
            'session_id': self.session_id,
            'name': self.name,
            'country': self.country
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
                name=data['name'],
                country=data['country']
            )
        except KeyError as e:
            raise ValueError(f"Invalid data: missing key {e}")
