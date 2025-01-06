from flask import Blueprint, jsonify
from uuid import uuid4

from app.extensions import mongo


session_route = Blueprint('session_route', __name__)


@session_route.route('/')
def hello_world():
    response = {
        'message': 'Hello, World!'
    }
    return jsonify(response), 200


@session_route.route('/<string:session_id>', methods=['GET'])
def get_session(session_id):
    # verify id is valid

    # get session from db
    result = mongo.db.session.find_one({'session_id': session_id})

    if not result:
        return jsonify({'status': 'ID not found.'}), 404

    response = {
        'status': 'Session found.',
        'session_id': result['session_id'],
        # 'data': result,
    }

    return jsonify(response), 200


@session_route.route('/create', methods=['POST'])
def create_session():
    session_id = str(uuid4())
    session = {'session_id': session_id}
    mongo.db.session.insert_one(session)

    return jsonify({'status': 'Session created.', 'session_id': session_id}), 201


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
