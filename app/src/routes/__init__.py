from flask import Blueprint, jsonify

example_route = Blueprint('example_route', __name__)


@example_route.route('/')
def hello_world():
    response = {
        'message': 'Hello, World!'
    }
    return jsonify(response), 200
