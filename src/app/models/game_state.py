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
    def __init__(self, session_id, territories=None, battles=None, factory_production_counts=None):
        self.session_id = session_id
        self.territories = territories if territories is not None else {}
        self.battles = battles if battles is not None else []
        self.factory_production_counts = factory_production_counts if factory_production_counts is not None else {}

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

        result = {
            'session_id': self.session_id,
            'territories': {},
            'battles': self.battles,
            'factory_production_counts': self.factory_production_counts,
        }

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
                             for territory_name, territory in data['territories'].items()},
                battles=data.get('battles'),
                factory_production_counts=data.get(
                    'factory_production_counts'),
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

            result[territory_name] = Territory(
                team=territory_data['team'],
                units=units,
                has_factory=territory_data.get('has_factory', False),
            )

        return result

    def add_battle(self, attacking_player, territory_name, attacking_from, is_aa_attack=False, air_units=None, is_ocean=False):
        """
        Add a battle to the game state.
        This is used to track where attackers would retreat to.

        :param game_state: The current game state.
        :param attacking_player: The team number of the player initiating the attack.
        :param territory_name: The name of the territory being attacked.
        :param attacking_from: The name of the territory the attack is coming from.
        :return: The battle as a dict.
        """
        new_battle = {
            'location': territory_name,
            'attack_from': attacking_from,
            'attacker': attacking_player,
            'turn': 0,
            'result': None,
            'attacker_rolls': [],
            'defender_rolls': [],
            'is_resolving_turn': False,
            'hit_battleships': [],
            'is_aa_attack': is_aa_attack,
            'air_units': air_units if air_units is not None else [],
            'is_ocean': is_ocean,
            'unloaded_transports': [],
        }

        # Prevent duplicates for a single turn
        for existing_battle in self.battles:
            if existing_battle['location'] == new_battle['location']:
                # TODO if attacking from two separate spaces, need to be able to have them
                # retreat to their separate attacking territories.
                # Currently, this will PROBABLY force them all to one of them.
                return existing_battle

        # existing battle not found, adding...
        self.battles.append(new_battle)
        self.sort_battles()

        return new_battle

    def add_or_find_battle(self, attacking_player, territory_name, attacking_from, is_aa_attack=False, air_units=None, is_ocean=False):
        """
        Add a battle to the game state.
        This is used to track where attackers would retreat to.

        :param game_state: The current game state.
        :param attacking_player: The team number of the player initiating the attack.
        :param territory_name: The name of the territory being attacked.
        :param attacking_from: The name of the territory the attack is coming from.
        :return: The battle as a dict.
        """
        # Check if the battle already exists
        battle = self.get_battle(territory_name, is_ocean, is_aa_attack)

        if battle:
            return battle

        new_battle = {
            'location': territory_name,
            'attack_from': attacking_from,
            'attacker': attacking_player,
            'turn': 0,
            'result': None,
            'attacker_rolls': [],
            'defender_rolls': [],
            'is_resolving_turn': False,
            'hit_battleships': [],
            'is_aa_attack': is_aa_attack,
            'air_units': air_units if air_units is not None else [],
            'is_ocean': is_ocean,
            'unloaded_transports': [],
        }

        # Prevent duplicate battles
        if not new_battle in self.battles:
            self.battles.append(new_battle)
            self.sort_battles()

        return new_battle

    def remove_battle(self, territory_name):
        """
        Attempt to remove a battle, if it exists.

        :param game_state: The current game state.
        :param territory_name: The name of the territory to remove battle from.
        :return: None
        """
        self.battles = [
            battle for battle in self.battles
            if battle['location'] != territory_name or battle.get('is_aa_attack', False)
        ]

    def get_battle(self, territory_name, is_ocean=False, is_aa_attack=False):
        """
        Get a battle by territory name.

        :param game_state: The current game state.
        :param territory_name: The name of the territory to get the battle from.
        :param is_ocean: Bool, if the battle is in an ocean.
        :param is_aa_attack: Bool, if the battle is an AA attack.
        :return: The battle, or None if it doesn't exist.
        """
        for battle in self.battles:
            if (battle['location'] == territory_name and
                    battle.get('is_ocean', False) == is_ocean and
                    battle.get('is_aa_attack', False) == is_aa_attack):

                return battle

        return {}

    def sort_battles(self):
        """
        Sort battles by AA fire first, then sea, and then land.
        Order is important because they are resolved in order.

        :param game_state: The current game state.
        :return: Bool, if the sorting was successful.
        """
        self.battles = sorted(
            self.battles,
            key=lambda x: (not x.get('is_aa_attack', False),
                           not TERRITORY_DATA[x['location']]['is_ocean'])
        )
