from flask import Blueprint, jsonify, request

from app.extensions import mongo
from app.services.game import create_game_state, get_game_state_by_session_id, update_game_state
from app.services.session import get_player_team_by_id


game_route = Blueprint('game_route', __name__)


@game_route.route('/<string:session_id>', methods=['GET'])
def handle_get_game_state(session_id):
    game_state = get_game_state_by_session_id(
        session_id, convert_to_class=False)

    if not game_state:
        return jsonify({'status': 'Session ID not found.'}), 404

    response = {
        'status': 'Game state found.',
        'session_id': game_state['session_id'],
        'game_state': game_state,
    }

    return jsonify(response), 200


@game_route.route('/<string:session_id>/moveunits', methods=['POST'])
def handle_move_units(session_id):
    game_state = get_game_state_by_session_id(
        session_id, convert_to_class=True)

    if not game_state:
        return jsonify({'status': 'Session ID not found.'}), 404

    # TODO for EVERY turn, validate player ID matches current player turn
    # validate all units are owned by the player

    player_id = request.args.get('pid')
    player_team = get_player_team_by_id(session_id, player_id)

    # validate unit movement
    data = request.get_json()
    territory_a = data.get('territoryA')
    territory_b = data.get('territoryB')
    units_to_move = data.get('units')

    game_state.validate_unit_movement(
        player_team, territory_a, territory_b, units_to_move.copy())

    # move units
    game_state.move_units(player_team, territory_a, territory_b, units_to_move)
    update_game_state(game_state)

    response = {
        'status': 'Unit movement action handled successfully.',
        'session_id': game_state.session_id,
        'game_state': game_state.to_dict(),
    }

    return jsonify(response), 200
