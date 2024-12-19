import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')
    MONGO_URI = os.environ.get(
        'MONGO_URI', 'mongodb://localhost:27017/ava')
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass
