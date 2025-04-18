from flask import Blueprint, jsonify, request

from app.services.session import join_session
from app.models.session import Session
from app.models.game_state import GameState


session_route = Blueprint('session_route', __name__)


@session_route.route('/<string:session_id>', methods=['GET'])
def handle_get_session(session_id):
    """
    Get session by session ID.
    """
    session = Session.get_session_by_session_id(
        session_id, convert_to_class=True)

    if not session:
        return jsonify({'status': 'Session not found.'}), 404

    response = {
        'status': 'Session found.',
        'session_id': session.session_id,
        'session': session.to_dict(sanitize_players=True),
    }

    # add player data if a valid player ID is provided
    player_id = request.args.get('pid')
    if not player_id:
        return jsonify(response), 200

    player = session.get_player_by_id(player_id)

    if player:
        response['player'] = player.to_dict()

    return jsonify(response), 200


@session_route.route('/create', methods=['POST'])
def handle_create_session():
    """
    Create a new session.
    """
    session = Session.create_session()

    session = session.to_dict()

    response = {'status': 'Session created.',
                'session_id': session['session_id'],
                'session': session}

    return jsonify(response), 201


@session_route.route('/join/<string:session_id>', methods=['POST'])
def handle_join_session(session_id):
    """
    Join a session and handles player selection.

    If the game reaches 5 players, the game will start."""
    # get country from data
    data = request.get_json()
    country_name = data.get('countryName')

    # verify session is valid
    session = Session.get_session_by_session_id(
        session_id, convert_to_class=True)

    if not session:
        return jsonify({'status': 'Session ID not found.'}), 404

    # attempt to add player to the session
    try:
        session, player = join_session(session_id, country_name)
    except ValueError as e:
        return jsonify({'status': str(e)}), 400

    if not player:
        return jsonify({'status': 'Error joining session.'}), 400

    session.update()

    response = {'status': 'Player joined.',
                'session_id': session_id,
                'session': session.to_dict(sanitize_players=True),
                'player': player.to_dict()}

    return jsonify(response), 201


# @session_route.route('/delete/<string:session_id>', methods=['DELETE'])
# def handle_delete_session(session_id):
#     result = mongo.db.session.find_one({'session_id': session_id})

#     if not result:
#         return jsonify({'status': 'ID not found.'}), 404

#     mongo.db.session.delete_one({'session_id': session_id})

#     response = {
#         'status': 'Session deleted.',
#         'session_id': result['session_id'],
#     }

#     return jsonify(response), 200
