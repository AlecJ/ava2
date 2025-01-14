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


def join_session(session_id, name, country):
    """
    Join a session.
    """
    # get session
    session = get_session_by_session_id(session_id, convert_to_class=True)

    # add player
    try:
        session.join_game(name, country)
        return True
    except:
        return False
