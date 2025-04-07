from app.extensions import mongo
from app.models.territory_data import TERRITORY_DATA
from app.models.unit import Unit
from app.models.territory import Territory

"""
This is the game_state object. It tracks the state of the game world including the territories, units, and players.

A game_state is a:
    Session ID
    List of Territory

A Territory is:
    Team ID
    List of Unit
    has_factory (bool)


"""


class GameState:
    def __init__(self, session_id, territories=None):
        self.session_id = session_id
        self.territories = territories if territories is not None else {}

        if not self.territories:
            self.territories = self.initialize_territories()

    def __repr__(self):
        return (
            f"<Session(session_id={self.session_id}, "
        )

    def to_dict(self):
        """
        Converts the Session object to a dictionary for JSON serialization.
        """

        result = {'session_id': self.session_id, 'territories': {}}

        for territory_name, territory in self.territories.items():
            result['territories'][territory_name] = territory.to_dict()

        return result

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
                territories={territory_name: Territory.from_dict(territory)
                             for territory_name, territory in data['territories'].items()}
            )
        except KeyError as e:
            # TODO log error
            raise ValueError(
                f"Failed to cast GameState json to class: {e}")

    @classmethod
    def create_game_state(cls, session_id):
        """
        Create a Game State and tie it to this session via session id.
        """
        game_state = cls(session_id=session_id)
        mongo.db.game_state.insert_one(game_state.to_dict())
        return game_state

    @staticmethod
    def get_game_state_by_session_id(session_id, convert_to_class=True):
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

    def backup_game_state(self):
        """
        Backup the game state to a separate collection to allow players to undo.
        """
        mongo.db.game_state_backup.delete_many(
            {'session_id': self.session_id})

        mongo.db.game_state_backup.insert_one(self.to_dict())

    def restore_game_state(self):
        """
        Restore the game state from a backup.
        """
        backup = mongo.db.game_state_backup.find_one(
            {'session_id': self.session_id})

        if not backup:
            # TODO log error
            return None

        mongo.db.game_state.delete_one({'session_id': self.session_id})

        mongo.db.game_state.insert_one(backup)

        return GameState.from_dict(backup)

    @staticmethod
    def initialize_units(territory_data):
        """
        Helper method for initializing units for a territory.
        """
        result = []

        for unit in territory_data['starting_units']:
            for _ in range(unit['count']):
                result.append(Unit(
                    unit_type=unit['type'],
                    team=territory_data['team'],
                ))

        return result

    def initialize_territories(self):
        """
        Initializes the territories for game start.
        """
        result = {}

        for territory_name, territory_data in TERRITORY_DATA.items():
            # skip neutral territories
            if territory_data['team'] == -1:
                continue

            units = self.initialize_units(territory_data)

            # if territory_name == 'ocean_tile_37':
            #     breakpoint()
            # TODO -- remove this

            result[territory_name] = Territory(
                team=territory_data['team'],
                units=units,
                has_factory=territory_data.get('has_factory', False),
            )

        return result
