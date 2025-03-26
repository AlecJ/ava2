from uuid import uuid4
from enum import Enum

from app.extensions import mongo
from app.models.player import Player

"""
This is the session object. It tracks the state of a game session
including the players and current turn.

A Session is:
    Session ID
    List of Player
    SessionStatus
    Current Turn

A Player is:
    Player ID
    Session ID
    Country (string)
    APCs


"""

order_of_play = ['Soviet Union', 'Germany',
                 'United Kingdom', 'Japan', 'United States']


class SessionStatus(Enum):
    TEAM_SELECT = 'TEAM_SELECT'
    ACTIVE = 'ACTIVE'
    COMPLETE = 'COMPLETE'


class PhaseNumber(Enum):
    PURCHASE_UNITS = 0
    COMBAT_MOVE = 1
    COMBAT = 2
    NON_COMBAT_MOVE = 3
    MOBILIZE = 4


class Session:
    def __init__(self, session_id=uuid4(), players=[], status=SessionStatus.TEAM_SELECT, turn_num=0, phase_num=PhaseNumber.PURCHASE_UNITS):
        self.session_id = str(session_id)
        self.players = players
        self.status = status
        self.turn_num = turn_num
        self.phase_num = phase_num

        # if the game is being created for first time, assign a uuid for the session

    @property
    def chosen_countries(self):
        return [player.country for player in self.players]

    def __str__(self):
        return f"Session {self.session_id} (Status: {self.status.name}, Turn: {self.turn_num})"

    def __repr__(self):
        return (
            f"<Session(session_id={self.session_id}, "
            f"players={len(self.players)}, "
            f"status={self.status.name}, "
            f"turn={self.turn_num})>"
        )

    def to_dict(self, sanitize_players=False):
        """
        Converts the Session object to a dictionary for JSON serialization.
        """
        result = {
            'session_id': self.session_id,
            'players': [player.to_dict() for player in self.players],
            'status': self.status.name,
            'turn_num': self.turn_num,
            'phase_num': self.phase_num.name,
        }

        if sanitize_players:
            result['players'] = [{'country': player.country,
                                  'ipcs': player.ipcs} for player in self.players]

        return result

    @classmethod
    def from_dict(cls, data):
        """
        Creates a Session object from a dictionary.

        This should only be used on existing data, not for creating new sessions.

        If a session is missing values, this will raise an error.
        """
        try:
            return cls(session_id=data['session_id'],
                       players=[Player.from_dict(player)
                                for player in data['players']],
                       status=SessionStatus[data['status']],
                       turn_num=data['turn_num'],
                       phase_num=PhaseNumber[data['phase_num']],
                       )
        except KeyError as e:
            # TODO log error
            raise ValueError(
                f"Failed to cast Session json to class. Missing required key: {e}")

    @staticmethod
    def get_session_by_session_id(session_id, convert_to_class=True):
        """
        Get a session by session ID.
        """
        result = mongo.db.session.find_one({'session_id': session_id})

        # remove mongo ObjectID
        del result['_id']

        if not result:
            return None

        if convert_to_class:
            return Session.from_dict(result)

        return result

    @staticmethod
    def create_session():
        """
        Create a session.
        """
        session = Session()
        mongo.db.session.insert_one(session.to_dict())
        return session

    def update(self):
        """
        Update a session.

        Returns None.
        """
        mongo.db.session.update_one(
            # Filter to find the session by its unique identifier
            {'session_id': self.session_id},
            {'$set': self.to_dict()}  # Update the session with the new data
        )

    def get_player_by_id(self, player_id):
        """
        Get the team of a player by their player ID.
        """
        for player in self.players:
            if player.player_id == player_id:
                return player

        raise ValueError(f"Player with ID {player_id} not found.")

    def get_player_by_team_num(self, team_num):
        """
        Get the player by their team number.
        """
        country = order_of_play[team_num]
        for player in self.players:
            if player.country == country:
                return player

    def sort_players_by_player_order(self):
        """
        Sort the player list to match the order of play.

        This is a void function that alters the data in place.
        """
        result = []

        for country in order_of_play:
            for player in self.players:
                if player.country == country:
                    result.append(player)
                    break

        self.players = result

    def increment_phase(self):
        self.phase_num = (self.phase_num + 1) % 5
