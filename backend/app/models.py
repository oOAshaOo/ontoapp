from .extensions import db


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    access_token_hash = db.Column(db.String(255), nullable=True)
    refresh_token_hash = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.now())
    last_login = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.now())

    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat(),
        }


class Taxonomie(db.Model):
    __tablename__ = "taxonomie"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    domain = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.now())
    last_update = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.now())

    def __init__(self, user_id, domain, description, data):
        self.user_id = user_id
        self.domain = domain
        self.description = description
        self.data = data

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "domain": self.domain,
            "description": self.description,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "last_update": self.last_update.isoformat(),
        }
