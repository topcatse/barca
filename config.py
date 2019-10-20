import os
basedir = os.path.abspath(os.path.dirname(__file__))

print(os.environ.get('DATABASE_URL'))

class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
    API_KEY_GOOGLEMAPS = os.environ.get('API_KEY_GOOGLEMAPS')
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True

