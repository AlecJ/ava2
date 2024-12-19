from flask import Flask

from app.config import Config
from app.routes import example_route

from app.extensions import mongo


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    mongo.init_app(app)

    # Register blueprints
    app.register_blueprint(example_route)

    return app
