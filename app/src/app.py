from flask import Flask
# from flask_pymongo import PyMongo

from routes import *
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
# mongo = PyMongo(app)

app.register_blueprint(example_route)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
