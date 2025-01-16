from flask import Blueprint, jsonify, request
from uuid import uuid4

from app.extensions import mongo
from app.services.session import get_session_by_session_id, create_session, join_session


session_route = Blueprint('session_route', __name__)


@session_route.route('/<string:session_id>', methods=['GET'])
def handle_get_session(session_id):
    session = get_session_by_session_id(session_id, convert_to_class=True)

    if not session:
        return jsonify({'status': 'ID not found.'}), 404

    # remove player data from session (IDs are private)
    json_session = session.to_dict()
    del json_session['players']
    json_session['players'] = session.chosen_countries

    response = {
        'status': 'Session found.',
        'session_id': session.session_id,
        'session': json_session,
    }

    # add player data if a valid player ID is provided
    player_id = request.args.get('pid')
    player = session.get_player_by_id(player_id)

    if player:
        response['player'] = player.to_dict()

    return jsonify(response), 200


@session_route.route('/create', methods=['POST'])
def handle_create_session():
    session = create_session()

    session = session.to_dict()

    response = {'status': 'Session created.',
                'session_id': session['session_id'],
                'session': session}

    return jsonify(response), 201


@session_route.route('/join/<string:session_id>', methods=['POST'])
def handle_join_session(session_id):
    # get country from data
    data = request.get_json()
    country_name = data.get('countryName')

    # verify session is valid
    session = get_session_by_session_id(session_id, convert_to_class=True)

    if not session:
        return jsonify({'status': 'Session ID not found.'}), 404

    # attempt to add player to the session
    session, player = join_session(session_id, country_name)

    if not player:
        return jsonify({'status': 'Error joining session.'}), 400

    response = {'status': 'Player joined.',
                'session_id': session_id,
                'session': session.to_dict(),
                'player': player.to_dict()}

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
