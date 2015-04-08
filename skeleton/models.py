import datetime

from .model_lib import base
from . import db, crypt


class User(base):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    _password = db.Column(db.String)

    __table_args__ = (
        db.UniqueConstraint('email', name='user_email_unique'),
        db.UniqueConstraint('username', name='user_username_unique'),
    )

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
