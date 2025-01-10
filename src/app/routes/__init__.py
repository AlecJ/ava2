from flask import Blueprint, jsonify
from uuid import uuid4

from app.extensions import mongo
from app.services.session import get_session_by_session_id, create_session, join_session


session_route = Blueprint('session_route', __name__)


@session_route.route('/<string:session_id>', methods=['GET'])
def handle_get_session(session_id):
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
def handle_create_session():
    session = create_session()

    return jsonify({'status': 'Session created.', 'session_id': session.session_id, 'session': session}), 201


@session_route.route('/join/<string:session_id>', methods=['POST'])
def handle_join_session(session_id, name, country):
    # verify session is valid
    session = get_session_by_session_id(session_id)

    if not session:
        return jsonify({'status': 'Session ID not found.'}), 404

    # attempt to add player to the session
    result = join_session(session_id, name, country)

    if result:
        return jsonify({'status': 'Player joined.'}), 200

    # TODO add reason for error (name or country)
    return jsonify({'status': 'Error joining session.'}), 400


@session_route.route('/delete/<string:session_id>', methods=['DELETE'])
def handle_delete_session(session_id):
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
