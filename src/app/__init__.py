from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.routes import session_route
from app.routes import game_route

from app.extensions import mongo


def create_app(config_override=None):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    # Apply test config if provided
    if config_override:
        app.config.update(config_override)

    # Initialize extensions
    mongo.init_app(app)

    # Register blueprints
    app.register_blueprint(session_route, url_prefix='/session')
    app.register_blueprint(game_route, url_prefix='/game')

    return app
