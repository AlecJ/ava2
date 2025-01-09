from flask import Blueprint, jsonify
from uuid import uuid4

from app.extensions import mongo
from services.session import get_session_by_session_id, create_session, join_session


session_route = Blueprint('session_route', __name__)


@session_route.route('/<string:session_id>', methods=['GET'])
def get_session(session_id):
    # get session from db
    # returned as .... json? class?
    result = get_session_by_session_id(session_id)

    if not result:
        return jsonify({'status': 'ID not found.'}), 404

    response = {
        'status': 'Session found.',
        'session_id': result.session_id,
        'data': result.to_dict(),
    }

    return jsonify(response), 200


@session_route.route('/create', methods=['POST'])
def create_session():
    session = create_session()

    return jsonify({'status': 'Session created.', 'session_id': session.session_id, 'session': session}), 201


@session_route.route('/join/<string:session_id>', methods=['POST'])
def join_session(session_id, country):
    # verify id is valid
    session =

    # call join_session
    player = join_session(session_id, country)

    # return response
    return jsonify({'status': 'Player joined.', 'player_id': player.player_id, 'country': player.country}), 200


@session_route.route('/delete/<string:session_id>', methods=['DELETE'])
def delete_session(session_id):
    # get session from db
    result = mongo.db.session.find_one({'session_id': session_id})

    if not result:
        return jsonify({'status': 'ID not found.'}), 404

    mongo.db.session.delete_one({'session_id': session_id})

    response = {
        'status': 'Session deleted.',
        'session_id': result['session_id'],
    }

    return jsonify(response), 200
