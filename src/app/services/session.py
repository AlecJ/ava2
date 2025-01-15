from app.extensions import mongo
from app.models.session import Session


"""
get_session_by_session_id

create_session

join_session
"""


def get_session_by_session_id(session_id, convert_to_class=False):
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


def create_session():
    """
    Create a session.
    """
    session = Session()
    mongo.db.session.insert_one(session.to_dict())
    return session


def update_session(session):
    """
    Update a session.

    Returns None.
    """
    mongo.db.session.update_one(
        # Filter to find the session by its unique identifier
        {'session_id': session.session_id},
        {'$set': session.to_dict()}  # Update the session with the new data
    )


def join_session(session_id, country):
    """
    Join a game session.

    User must provide a valid and available country name.

    Player object is returned, if valid.
    """
    session = get_session_by_session_id(session_id, convert_to_class=True)

    try:
        # breakpoint()
        player = session.join_game(country)
    except:
        return False

    update_session(session)

    return player
