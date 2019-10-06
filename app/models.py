from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext import mutable
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.types import PickleType
import json
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    routes = db.relationship('Route', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class JsonEncodedDict(db.TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = db.Text

    def process_bind_param(self, value, dialect):
        if value is None:
            return '{}'
        else:
            return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return {}
        else:
            return json.loads(value)

mutable.MutableDict.associate_with(JsonEncodedDict)


class Route(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    start = Column(String(100), nullable=False)
    stop = Column(String(100), nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    route = Column(JsonEncodedDict)
    coords = Column(PickleType)
    distances = Column(PickleType)
    prev_coord = Column(PickleType)
    prev_distance = Column(PickleType)
    current = Column(PickleType)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Route %r>' % self.id


