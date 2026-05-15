from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100), nullable=True)

    def get_reset_token(self, expires_sec=1800):
        from flask import current_app
        from itsdangerous import URLSafeTimedSerializer as Serializer

        s = Serializer(current_app.config["SECRET_KEY"], expires_in=expires_sec)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        from flask import current_app
        from itsdangerous import URLSafeTimedSerializer as Serializer

        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except Exception:
            return None
        return User.query.get(data["user_id"])


class StateProvince(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)


class UserTracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    state_province_id = db.Column(db.Integer, db.ForeignKey("state_province.id"))
    user = db.relationship("User", back_populates="tracked_states")
    state_province = db.relationship("StateProvince", back_populates="users")


User.tracked_states = db.relationship("UserTracking", back_populates="user")
StateProvince.users = db.relationship("UserTracking", back_populates="state_province")