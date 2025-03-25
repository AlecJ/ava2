from app.models.session import Session, SessionStatus
from app.models.player import Player
from app.models.game_state import GameState
from app.services.game import end_turn


valid_countries = ['United States', 'United Kingdom',
                   'Soviet Union', 'Germany', 'Japan']


def join_session(session_id, country):
    """
    Join a game session.

    User must provide a valid and available country name.

    Player object is returned, if valid.
    """
    session = Session.get_session_by_session_id(
        session_id, convert_to_class=True)

    # raises ValueError if invalid, caught in route
    validate_country_selection(session, country)

    # add new player
    new_player = Player(session_id=session.session_id,
                        country=country)
    session.players.append(new_player)

    # if game is full, start the game
    if len(session.players) == 5:
        session.status = SessionStatus.ACTIVE
        session.sort_players_by_player_order()

        game_state = GameState.create_game_state(session.session_id)

        # initializes some data for the first turn
        end_turn(session, game_state)
        session.turn_num = 0
        game_state.update()

    return session, new_player


def validate_country_selection(session, country=None):
    """
    Validate the country selection for a player joining a session.
    Raises ValueError if the country is invalid or already taken, or game is full.

    :param session: The current game session.
    :param country: The country name selected by the player.
    :return: None
    """
    # ensure country is valid
    if country not in valid_countries:
        raise ValueError(f"Country {country} is not a valid country.")

    taken_countries = [player.country for player in session.players]

    if country in taken_countries:
        raise ValueError(f"Country {country} is already taken.")

    # ensure game is not full
    if len(session.players) > 4:
        raise ValueError("Game is full.")

    return


def activate_game(session):
    """
    Set game to active and sort players by player order.
    """
