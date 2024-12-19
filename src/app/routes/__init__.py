from flask import Blueprint, jsonify

from app.extensions import mongo


example_route = Blueprint('example_route', __name__)


@example_route.route('/')
def hello_world():
    response = {
        'message': 'Hello, World!'
    }
    return jsonify(response), 200


@example_route.route('/add', methods=['POST'])
def add_document():
    data = {'status': 'added'}
    mongo.db.session.insert_one(data)
    return jsonify({'message': 'Document added successfully!'}), 201
