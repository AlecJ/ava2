class Config:
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'your_secret_key'
    DATABASE_URI = 'mongodb://localhost:27017/your_database_name'


class ProductionConfig(Config):
    SECRET_KEY = 'your_secret_key'
    DATABASE_URI = 'mongodb://localhost:27017/your_database_name'
