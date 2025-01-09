from uuid import uuid4
from enum import Enum

"""
A Session is a:

Session ID
List of Players
Status
Current Turn

A Player is:
Player ID
Country

Country is one of:
USA
USSR
UK
Germany
Japan

"""


class SessionStatus(Enum):
    STARTING = 'starting'
    ACTIVE = 'active'
    COMPLETE = 'complete'


valid_countries = ['USA', 'USSR', 'UK', 'Germany', 'Japan']


class Session:
    def __init__(self, session_id=uuid4(), players=[], status=SessionStatus.STARTING, current_turn=0):
        self.session_id = str(session_id)
        # list of uuid representing their player_id, same they will use for joining the game
        self.players = players
        self.status = status
        self.current_turn = current_turn

        # if the game is being created for first time, assign a uuid for the session

    def __str__(self):
        return f"Session {self.session_id} (Status: {self.status.name}, Current Turn: {self.current_turn})"

    def __repr__(self):
        return (
            f"<Session(session_id={self.session_id}, "
            f"players={len(self.players)}, "
            f"status={self.status.name}, "
            f"current_turn={self.current_turn})>"
        )

    @classmethod
    def from_dict(cls, data):
        """
        Creates a Session object from a dictionary.
        """
        return cls(session_id=data.get('session_id'), players=data.get('players', []))

    def join_game(self, country=None):
        """
        Adds a player to the game. The user provides a country
        """
        # ensure country is valid
        if country not in valid_countries:
            raise ValueError(f"Country {country} is not a valid country.")

        taken_countries = [player['country'] for player in self.players]

        if country in taken_countries:
            raise ValueError(f"Country {country} is already taken.")

        # ensure game is not full
        if self.players.length > 4:
            raise ValueError("Game is full.")

        new_player = {
            'id': str(uuid4()),
            'country': country
        }
        self.players.append(new_player)

        return new_player

    def next_turn(self):
        self.current_turn = (self.current_turn + 1) % len(self.players)
        pass

    def complete_turn(self):
        pass
