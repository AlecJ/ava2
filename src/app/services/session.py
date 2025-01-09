from uuid import uuid4
from app.extensions import mongo
from models.session import Session


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


def join_session():
    """
    Join a session.
    """
    pass
