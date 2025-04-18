import os
from flask import Flask, send_from_directory
from flask_cors import CORS

from app.config import Config
from app.routes import session_route
from app.routes import game_route

from app.extensions import mongo


def create_app(config_override=None):
    static_folder = os.getenv("STATIC_PATH", "static")

    app = Flask(__name__, static_folder=static_folder)
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

    # Serve the Vue app
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_vue_app(path):
        if app.static_folder and path:
            file_path = os.path.join(app.static_folder, path)
            if os.path.exists(file_path):
                return send_from_directory(app.static_folder, path)

        return send_from_directory(app.static_folder, "index.html")

    return app
