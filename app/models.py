from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.types import PickleType
from sqlalchemy.dialects.postgresql import JSON
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

    def my_routes(self):
        own = Route.query.filter_by(user_id=self.id)
        return own.order_by(Route.date_created.desc())


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Route(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    start = Column(String(100), nullable=False)
    stop = Column(String(100), nullable=False)
    date_created = Column(DateTime, default=datetime.now)
    date_finished = Column(DateTime, default=datetime.now)
    route = Column(JSON)
    coords = Column(PickleType)
    distances = Column(PickleType)
    prev_coord = Column(PickleType)
    prev_distance = Column(Integer)
    current = Column(PickleType)
    done = Column(Boolean)
    status = Column(String(30), default="Not started")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Route %r>' % self.id


