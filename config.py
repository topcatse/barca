import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
    API_KEY_GOOGLEMAPS = os.environ.get('API_KEY_GOOGLEMAPS')
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
