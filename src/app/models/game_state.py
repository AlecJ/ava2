# from uuid import uuid4
# from enum import Enum


from app.extensions import mongo
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

    @classmethod
    def create(cls, session_id):
        """
        Create a session.
        """
        game_state = cls(session_id=session_id)
        mongo.db.game_state.insert_one(game_state.to_dict())
        return game_state

    @classmethod
    def get_game_state_by_session_id(cls, session_id, convert_to_class=True):
        """
        Get a session by session ID.
        """
        result = mongo.db.game_state.find_one({'session_id': session_id})

        # remove mongo ObjectID
        del result['_id']

        if not result:
            return None

        if convert_to_class:
            return GameState.from_dict(result)

        return result

    def update(self):
        """
        Update a game state.

        Returns None.
        """
        mongo.db.game_state.update_one(
            {'session_id': self.session_id},
            {'$set': self.to_dict()}
        )

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
