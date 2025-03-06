from app.extensions import mongo
from app.models.game_state import GameState


"""
create_game_state

get_game_state_by_session_id

move_units

end_turn
"""


def create_game_state(session_id):
    """
    Create a session.
    """
    game_state = GameState(session_id)
    mongo.db.game_state.insert_one(game_state.to_dict())
    return game_state


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
