from flask import Blueprint, jsonify, request

from app.models.session import Session, PhaseNumber
from app.models.game_state import GameState
from app.models.unit import Unit
from app.services.session import validate_player
from app.services.game import purchase_unit, mobilize_units, validate_unit_movement, move_units, end_turn


game_route = Blueprint('game_route', __name__)


@game_route.route('/<string:session_id>', methods=['GET'])
def handle_get_game_state(session_id):
    game_state = GameState.get_game_state_by_session_id(
        session_id, convert_to_class=False)

    if not game_state:
        return jsonify({'status': 'Session ID not found.'}), 404

    response = {
        'status': 'Game state found.',
        'session_id': game_state['session_id'],
        'game_state': game_state,
    }
    return jsonify(response), 200


@game_route.route('/<string:session_id>/purchaseunit', methods=['POST'])
def handle_purchase_unit(session_id):
    session = Session.get_session_by_session_id(
        session_id, convert_to_class=True)

    if not session:
        return jsonify({'status': 'Session ID not found.'}), 404

    # ensure it is the purchase phase
    if session.phase_num != PhaseNumber.PURCHASE_UNITS:
        return jsonify({'status': 'User cannot purchase units outside of the purchase units phase.'}), 400

    # add player data if a valid player ID is provided
    player_id = request.args.get('pid')
    player = session.get_player_by_id(player_id)

    # TODO for EVERY turn, validate player ID matches current player turn
    # validate all units are owned by the player
    # validate current turn player has correct key
    if not validate_player(player):
        return jsonify({'status': 'Player ID not found.'}), 404

    data = request.get_json()
    unit_type_to_purchase = data.get('unitType')

    if not purchase_unit(player, unit_type_to_purchase):
        return jsonify({'status': 'Purchase failed. Player does not have sufficient funds.'}), 400

    session.update()

    response = {
        'status': 'Unit purchase action handled successfully.',
        'session_id': session.session_id,
        'session': session.to_dict(sanitize_players=True),
    }
    return jsonify(response), 200


@game_route.route('/<string:session_id>/mobilizeunits', methods=['POST'])
def handle_mobilize_units(session_id):
    session = Session.get_session_by_session_id(
        session_id, convert_to_class=True)

    if not session:
        return jsonify({'status': 'Session ID not found.'}), 404

    game_state = GameState.get_game_state_by_session_id(
        session_id, convert_to_class=True)

    if not game_state:
        return jsonify({'status': 'Session ID not found.'}), 404

    # ensure it is the mobilize phase
    if session.phase_num != PhaseNumber.MOBILIZE:
        return jsonify({'status': 'User cannot mobilize units outside of the mobilize units phase.'}), 400

    # add player data if a valid player ID is provided
    player_id = request.args.get('pid')
    player = session.get_player_by_id(player_id)

    # TODO for EVERY turn, validate player ID matches current player turn
    # validate all units are owned by the player
    # validate current turn player has correct key
    if not validate_player(player):
        return jsonify({'status': 'Player ID not found.'}), 404

    data = request.get_json()
    units_to_mobilize = data.get('units')
    selected_territory = data.get('selectedTerritory')

    if not mobilize_units(game_state, player, units_to_mobilize, selected_territory):
        return jsonify({'status': 'Mobilization failed. Invalid units or territory selected.'}), 400

    session.update()
    game_state.update()

    response = {
        'status': 'Unit purchase action handled successfully.',
        'session_id': session.session_id,
        'session': session.to_dict(sanitize_players=True),
        'game_state': game_state.to_dict(),
    }
    return jsonify(response), 200


@game_route.route('/<string:session_id>/moveunits', methods=['POST'])
def handle_move_units(session_id):
    game_state = GameState.get_game_state_by_session_id(
        session_id, convert_to_class=True)

    if not game_state:
        return jsonify({'status': 'Session ID not found.'}), 404

    # TODO for EVERY turn, validate player ID matches current player turn
    # validate all units are owned by the player
    # validate current turn player has correct key

    data = request.get_json()
    territory_a = data.get('territoryA')
    territory_b = data.get('territoryB')
    units_to_move = data.get('units')

    # cast units to class objects
    units_to_move = [Unit.from_dict(unit) for unit in units_to_move]

    # validate the attempted troop movement
    validate_unit_movement(game_state,
                           territory_a, territory_b, units_to_move)

    move_units(game_state, territory_a, territory_b, units_to_move)

    game_state.update()

    response = {
        'status': 'Unit movement action handled successfully.',
        'session_id': game_state.session_id,
        'game_state': game_state.to_dict(),
    }
    return jsonify(response), 200


# @game_route.route('/<string:session_id>/undo', methods=['POST'])
def handle_undo_turn(session_id):
    pass


def handle_combat(session_id):
    pass


def handle_place_new_units(session_id):
    pass


@game_route.route('/<string:session_id>/endphase', methods=['POST'])
def handle_end_phase(session_id):
    session = Session.get_session_by_session_id(
        session_id, convert_to_class=True)

    session.increment_phase()

    session.update()

    response = {
        'status': 'Turn ended successfully.',
        'session_id': session.session_id,
        'session': session.to_dict(sanitize_players=True),
    }
    return jsonify(response), 200


@game_route.route('/<string:session_id>/endturn', methods=['POST'])
def handle_end_turn(session_id):
    session = Session.get_session_by_session_id(
        session_id, convert_to_class=True)

    game_state = GameState.get_game_state_by_session_id(
        session_id, convert_to_class=True)

    if not game_state:
        return jsonify({'status': 'Session ID not found.'}), 404

    # TODO validate player has no forces waiting to mobilize

    end_turn(session, game_state)

    session.update()
    game_state.update()

    response = {
        'status': 'Turn ended successfully.',
        'session_id': game_state.session_id,
        'session': session.to_dict(sanitize_players=True),
        'game_state': game_state.to_dict(),
    }
    return jsonify(response), 200
