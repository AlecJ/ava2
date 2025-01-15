from flask import Blueprint, jsonify, request
from uuid import uuid4

from app.extensions import mongo
from app.services.session import get_session_by_session_id, create_session, join_session


session_route = Blueprint('session_route', __name__)


@session_route.route('/<string:session_id>', methods=['GET'])
def handle_get_session(session_id):
    # returned as json row from db
    session = get_session_by_session_id(session_id)

    if not session:
        return jsonify({'status': 'ID not found.'}), 404

    player_id = request.args.get('pid')
    if player_id:
        players = session['players']

    # remove player data from session (IDs are private)
    del session['players']

    response = {
        'status': 'Session found.',
        'session_id': session['session_id'],
        'session': session,
    }

    # if player ID is included in the request, send back player data
    if player_id:
        for player in players:
            if player['player_id'] == player_id:
                response['player'] = player
                break

    return jsonify(response), 200


@session_route.route('/create', methods=['POST'])
def handle_create_session():
    session = create_session()

    session = session.to_dict()

    # remove player data from session (IDs are private)
    del session['players']

    response = {'status': 'Session created.',
                'session_id': session['session_id'], 'session': session}

    return jsonify(response), 201


@session_route.route('/join/<string:session_id>', methods=['POST'])
def handle_join_session(session_id):
    # get country from data
    data = request.get_json()
    country_name = data.get('countryName')

    # verify session is valid
    session = get_session_by_session_id(session_id)

    if not session:
        return jsonify({'status': 'Session ID not found.'}), 404

    # attempt to add player to the session
    player = join_session(session_id, country_name)

    if not player:
        return jsonify({'status': 'Error joining session.'}), 400

    response = {'status': 'Player joined.',
                'session_id': session_id, 'player': player.to_dict()}

    return jsonify(response), 200


@session_route.route('/delete/<string:session_id>', methods=['DELETE'])
def handle_delete_session(session_id):
    result = mongo.db.session.find_one({'session_id': session_id})

    if not result:
        return jsonify({'status': 'ID not found.'}), 404

    mongo.db.session.delete_one({'session_id': session_id})

    response = {
        'status': 'Session deleted.',
        'session_id': result['session_id'],
    }

    return jsonify(response), 200
