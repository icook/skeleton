import datetime

from flask.ext.security import UserMixin, RoleMixin
from .model_lib import base
from . import db, crypt


roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(base, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    _password = db.Column(db.String)
    confirmed_at = db.Column(db.DateTime)
    active = db.Column(db.Boolean)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, val):
        self._password = crypt.encode(val)

    def check_password(self, password):
        return crypt.check(self._password, password)

    # Authentication
    # ========================================================================
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class EmailConfirm(base):
    recover_hash = db.Column(db.String)
    type = db.Column(db.Enum("email", "password", "activation",
                             name="confirm_type"), nullable=False)
    recover_gen = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', foreign_keys=[user_id])
