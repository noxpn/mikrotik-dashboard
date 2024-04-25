from datetime import datetime
from mkdashboard import db


class User(db.Model):
    hash = db.Column(db.String(256), primary_key=True, nullable=False)
    email = db.Column(db.String(512), nullable=False)
    pwd = db.Column(db.String(512), nullable=False)
    admin = db.Column(db.Boolean, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Record %r>' % self.hash


class RouterBoard(db.Model):
    hash = db.Column(db.String(256), nullable=False, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    ip = db.Column(db.String(16), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    login = db.Column(db.String(128), nullable=False)
    enc_pwd = db.Column(db.String(512), nullable=False)
    owner = db.Column(db.String(128), nullable=False)
    isp = db.Column(db.String(128), nullable=False)
    loc = db.Column(db.String(256), nullable=False)
    enabled = db.Column(db.Boolean, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Record %r>' % self.hash
