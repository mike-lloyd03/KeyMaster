from flask import current_app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import sha256
from time import time
import jwt

from app import app, db, login


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        ).decode("utf-8")

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])[
                "reset_password"
            ]
        except:
            return
        return User.query.get(id)


class Key(db.Model):
    """The keys table tracks individual keys."""

    __tablename__ = "keys"

    name = db.Column(db.String, primary_key=True)
    description = db.Column(db.String)
    status = db.Column(db.String, default="Active")

    def __repr__(self):
        return f"<Key {self.name}>"

    # All this crap needs to get fixed
    def add(self):
        db.session.add(self)
        self.commit()

    def update(self):
        self.commit()

    def delete(self):
        pass

    def commit(self):
        db.session.commit()


class Assignment(db.Model):
    """The assignments table tracks when keys are checked out and in to users."""

    __tablename__ = "assignments"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String, db.ForeignKey("users.username"))
    key = db.Column(db.String, db.ForeignKey("keys.name"))
    date_out = db.Column(db.Date)
    date_in = db.Column(db.Date, nullable=True)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        pass


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
