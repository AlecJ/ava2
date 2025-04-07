from flask import Blueprint, jsonify, request

from app.models.session import Session, PhaseNumber
from app.models.game_state import GameState
from app.models.unit import Unit
from app.services.session import validate_player
from app.services.game import (purchase_unit, mobilize_units, move_units,
                               load_transport_with_units, unload_transport,
                               get_battles, end_turn)


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
    session, game_state = fetch_session_and_game_state(session_id)
    if not session or not game_state:
        return jsonify({'status': 'Session ID not found.'}), 404

    if session.phase_num != PhaseNumber.PURCHASE_UNITS:
        return jsonify({'status': 'User cannot purchase units outside of the purchase units phase.'}), 400

    # Must be the player's turn
    player_id = request.args.get('pid')
    player = session.get_player_by_id(player_id)

    if not validate_player(session, player):
        return jsonify({'status': 'Cannot perform actions outside of your turn.'}), 400

    # Process the request
    data = request.get_json()
    unit_type_to_purchase = data.get('unitType')

    if not purchase_unit(game_state, player, unit_type_to_purchase):
        return jsonify({'status': 'Purchase failed. Player does not have sufficient funds.'}), 400

    session.update()

    response = {
        'status': 'Unit purchase action handled successfully.',
        'session_id': session.session_id,
        'session': session.to_dict(sanitize_players=True),
    }
    return jsonify(response), 200


@game_route.route('/<string:session_id>/moveunits', methods=['POST'])
def handle_move_units(session_id):
    # Fetch the session and game state by session ID
    session, game_state = fetch_session_and_game_state(session_id)
    if not session or not game_state:
        return jsonify({'status': 'Session ID not found.'}), 404

    if session.phase_num not in [PhaseNumber.COMBAT_MOVE, PhaseNumber.NON_COMBAT_MOVE]:
        return jsonify({'status': 'User cannot move units outside of combat and non-combat movement phases.'}), 400

    # Must be the player's turn
    player_id = request.args.get('pid')
    player = session.get_player_by_id(player_id)

    if not validate_player(session, player):
        return jsonify({'status': 'Cannot perform actions outside of your turn.'}), 400

    # Process the request
    data = request.get_json()
    territory_a = data.get('territoryA')
    territory_b = data.get('territoryB')
    units_to_move = data.get('units')

    result, message = move_units(session, game_state, player,
                                 territory_a, territory_b, units_to_move)

    if not result:
        message = message or 'Invalid troop movement.'
        return jsonify({'status': message}), 400

    game_state.update()

    response = {
        'status': 'Unit movement action handled successfully.',
        'session_id': game_state.session_id,
        'game_state': game_state.to_dict(),
    }
    return jsonify(response), 200


@game_route.route('/<string:session_id>/loadtransport', methods=['POST'])
def handle_load_transport(session_id):
    # Fetch the session and game state by session ID
    session, game_state = fetch_session_and_game_state(session_id)
    if not session or not game_state:
        return jsonify({'status': 'Session ID not found.'}), 404

    if session.phase_num not in [PhaseNumber.COMBAT_MOVE, PhaseNumber.NON_COMBAT_MOVE]:
        return jsonify({'status': 'User cannot load transports outside of combat and non-combat movement phases.'}), 400

    # Must be the player's turn
    player_id = request.args.get('pid')
    player = session.get_player_by_id(player_id)

    if not validate_player(session, player):
        return jsonify({'status': 'Cannot perform actions outside of your turn.'}), 400

    # Process the request
    data = request.get_json()
    territory_name = data.get('territoryName')
    transport = data.get('transport')
    units_to_load = data.get('units')

    # cast json units to class objects
    transport = Unit.from_dict(transport)

    result, message = load_transport_with_units(game_state, player,
                                                territory_name, transport, units_to_load)

    if not result:
        message = message or 'Invalid transport loading.'
        return jsonify({'status': message}), 400

    game_state.update()

    response = {
        'status': 'Transport loading action handled successfully.',
        'session_id': game_state.session_id,
        'game_state': game_state.to_dict(),
    }
    return jsonify(response), 200


@game_route.route('/<string:session_id>/unloadtransport', methods=['POST'])
def handle_unload_transport(session_id):
    # Fetch the session and game state by session ID
    session, game_state = fetch_session_and_game_state(session_id)
    if not session or not game_state:
        return jsonify({'status': 'Session ID not found.'}), 404

    if session.phase_num not in [PhaseNumber.COMBAT_MOVE, PhaseNumber.NON_COMBAT_MOVE]:
        return jsonify({'status': 'User cannot load transports outside of combat and non-combat movement phases.'}), 400

    # Must be the player's turn
    player_id = request.args.get('pid')
    player = session.get_player_by_id(player_id)

    if not validate_player(session, player):
        return jsonify({'status': 'Cannot perform actions outside of your turn.'}), 400

    # Process the request
    data = request.get_json()
    sea_territory_name = data.get('seaTerritory')
    selected_territory_name = data.get('selectedTerritory')
    transport = data.get('transport')

    # cast json unit to class objects
    transport = Unit.from_dict(transport)

    result, message = unload_transport(game_state, player,
                                       sea_territory_name, selected_territory_name, transport)

    if not result:
        message = message or 'Invalid transport unloading.'
        return jsonify({'status': message}), 400

    game_state.update()

    response = {
        'status': 'Transport loading action handled successfully.',
        'session_id': game_state.session_id,
        'game_state': game_state.to_dict(),
    }
    return jsonify(response), 200


@game_route.route('/<string:session_id>/battles', methods=['GET'])
def handle_get_battles(session_id):
    # Fetch the session and game state by session ID
    session, game_state = fetch_session_and_game_state(session_id)
    if not session or not game_state:
        return jsonify({'status': 'Session ID not found.'}), 404

    # Must be in combat phase
    if session.phase_num != PhaseNumber.COMBAT:
        return jsonify({'status': 'User cannot get combat territories outside of combat phase.'}), 400

    combat_territories = get_battles(game_state)

    response = {
        'status': 'Combat territories retrieved successfully.',
        'session_id': game_state.session_id,
        'combat_territories': combat_territories,
    }
    return jsonify(response), 200


@game_route.route('/<string:session_id>/undophase', methods=['POST'])
def handle_undo_phase(session_id):
    # Fetch the session and game state by session ID
    session, game_state = fetch_session_and_game_state(session_id)
    if not session or not game_state:
        return jsonify({'status': 'Session ID not found.'}), 404

    # only allowed in combat and non-combat movement phases
    if session.phase_num not in [PhaseNumber.COMBAT_MOVE, PhaseNumber.NON_COMBAT_MOVE]:
        return jsonify({'status': 'User cannot undo phase outside of combat and non-combat movement phases.'}), 400

    # Must be the player's turn
    player_id = request.args.get('pid')
    player = session.get_player_by_id(player_id)

    if not validate_player(session, player):
        return jsonify({'status': 'Cannot perform actions outside of your turn.'}), 400

    game_state = game_state.restore_game_state()

    response = {
        'status': 'Phase reset successfully.',
        'session_id': game_state.session_id,
        'game_state': game_state.to_dict(),
    }
    return jsonify(response), 200


def handle_combat(session_id):
    pass


@game_route.route('/<string:session_id>/mobilizeunits', methods=['POST'])
def handle_mobilize_units(session_id):
    # Fetch the session and game state by session ID
    session, game_state = fetch_session_and_game_state(session_id)
    if not session or not game_state:
        return jsonify({'status': 'Session ID not found.'}), 404

    if session.phase_num != PhaseNumber.MOBILIZE:
        return jsonify({'status': 'User cannot mobilize units outside of the mobilize units phase.'}), 400

    # Must be the player's turn
    player_id = request.args.get('pid')
    player = session.get_player_by_id(player_id)

    if not validate_player(session, player):
        return jsonify({'status': 'Cannot perform actions outside of your turn.'}), 400

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


@game_route.route('/<string:session_id>/endphase', methods=['POST'])
def handle_end_phase(session_id):
    session = Session.get_session_by_session_id(
        session_id, convert_to_class=True)

    # TODO Must be the player's turn
    # player_id = request.args.get('pid')
    # player = session.get_player_by_id(player_id)

    # if not validate_player(session, player):
    #     return jsonify({'status': 'Cannot perform actions outside of your turn.'}), 400

    session.increment_phase()

    session.update()

    # Backup game state for undoing movement
    if session.phase_num in [PhaseNumber.COMBAT_MOVE, PhaseNumber.NON_COMBAT_MOVE]:
        game_state = GameState.get_game_state_by_session_id(
            session_id, convert_to_class=True)
        game_state.backup_game_state()

    response = {
        'status': 'Phase ended successfully.',
        'session_id': session.session_id,
        'session': session.to_dict(sanitize_players=True),
    }
    return jsonify(response), 200


@game_route.route('/<string:session_id>/endturn', methods=['POST'])
def handle_end_turn(session_id):
    session, game_state = fetch_session_and_game_state(session_id)
    if not session or not game_state:
        return jsonify({'status': 'Session ID not found.'}), 404

    # TODO Must be the player's turn
    # player_id = request.args.get('pid')
    # player = session.get_player_by_id(player_id)

    # if not validate_player(session, player):
    #     return jsonify({'status': 'Cannot perform actions outside of your turn.'}), 400

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


def fetch_session_and_game_state(session_id):
    """
    Helper function, called by most routes.

    Fetch the session and game state by session ID.
    """
    session = Session.get_session_by_session_id(
        session_id, convert_to_class=True)

    if not session:
        return None, None

    game_state = GameState.get_game_state_by_session_id(
        session_id, convert_to_class=True)

    if not game_state:
        return None, None

    return session, game_state
