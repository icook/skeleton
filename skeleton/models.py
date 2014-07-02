from .model_lib import base
from . import db


class Address(base):
    address = db.Column(db.String, primary_key=True)
    currency = db.Column(db.String(4))

    request_id = db.Column(db.Integer, db.ForeignKey('payment_request.id'))
    request = db.relationship('PaymentRequest', foreign_keys=[request_id])
