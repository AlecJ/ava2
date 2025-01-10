from uuid import uuid4
from enum import Enum

from app.models.player import Player

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
valid_countries = ['USA', 'USSR', 'UK', 'Germany', 'Japan']


class SessionStatus(Enum):
    TEAM_SELECT = 'team_select'
    ACTIVE = 'active'
    COMPLETE = 'complete'


class Session:
    def __init__(self, session_id=uuid4(), players=[], status=SessionStatus.TEAM_SELECT, current_turn=0):
        self.session_id = str(session_id)
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

    def to_dict(self):
        """
        Converts the Session object to a dictionary for JSON serialization.
        """
        return {
            'session_id': self.session_id,
            'players': [player.to_dict() for player in self.players],
            'status': self.status.name,
            'current_turn': self.current_turn
        }

    @classmethod
    def from_dict(cls, data):
        """
        Creates a Session object from a dictionary.

        This should only be used on existing data, not for creating new sessions.

        If a session is missing values, this will raise an error.
        """
        try:
            return cls(session_id=data['session_id'],
                       players=data['players'],
                       status=SessionStatus(data['status']),
                       current_turn=data['current_turn']
                       )
        except KeyError as e:
            # TODO log error
            raise ValueError(
                f"Failed to cast Session json to class. Missing required key: {e}")

    def join_game(self, name=None, country=None):
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

        # player must have a name TODO add validation
        if name is None:
            raise ValueError("Name is required.")

        # return result
        new_player = Player(session_id=self.session_id,
                            name=name, country=country)
        self.players.append(new_player)

        return new_player

    def next_turn(self):
        self.current_turn = (self.current_turn + 1) % len(self.players)
        pass

    def complete_turn(self):
        pass
