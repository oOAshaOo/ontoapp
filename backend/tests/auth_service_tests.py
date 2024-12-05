import unittest
from flask import Flask
from app.extensions import db
from app.models import Users
from app.resources.auth_service import Auth
from unittest.mock import patch
import jwt
from werkzeug.security import generate_password_hash, check_password_hash


class AuthServiceTestCase(unittest.TestCase):
    def setUp(self):
        """Set up a test app and initialize the database."""
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.init_app(self.app)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        user = Users(
            username="testuser", password_hash=generate_password_hash("testpassword")
        )
        db.session.add(user)
        db.session.commit()
        self.patcher_secret_key = patch.dict("os.environ", {"SECRET_KEY": "secret"})
        self.patcher_access_expiry = patch.dict(
            "os.environ", {"ACCESS_TOKEN_EXPIRATION_MINUTES": "30"}
        )
        self.patcher_refresh_expiry = patch.dict(
            "os.environ", {"REFRESH_TOKEN_EXPIRATION_MINUTES": "30"}
        )
        self.patcher_secret_key.start()
        self.patcher_access_expiry.start()
        self.patcher_refresh_expiry.start()

    def tearDown(self):
        """Roll back any session changes and remove all tables."""
        db.session.remove()
        db.drop_all()
        self.context.pop()
        self.patcher_secret_key.stop()
        self.patcher_access_expiry.stop()
        self.patcher_refresh_expiry.stop()

    def test_login_user_success(self):
        """Test logging in with valid credentials."""
        result = Auth.login_user("testuser", "testpassword")
        self.assertTrue(result)

    def test_login_user_failure(self):
        """Test logging in with invalid credentials."""
        result = Auth.login_user("testuser", "wrongpassword")
        self.assertFalse(result)

    def test_create_access_token(self):
        """Test creating an access token."""
        token = Auth.create_tokens("testuser", "access")
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 0)

    def test_create_refresh_token(self):
        """Test creating a refresh token."""
        token = Auth.create_tokens("testuser", "refresh")
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 0)

    def test_check_access_token_success(self):
        """Test verifying a valid access token."""
        token = Auth.create_tokens("testuser", "refresh")
        token_data = jwt.decode(token, "secret", algorithms=["HS256"])
        result = Auth.check_access_token(token, "testuser", token_data)
        self.assertTrue(result)

    def test_check_access_token_failure(self):
        """Test verifying an invalid access token."""
        result = Auth.check_access_token("invalid_token", "testuser", {})
        self.assertFalse(result)

    def test_logout_user(self):
        """Test logging out a user."""
        Auth.logout_user("testuser")
        user = Users.query.filter_by(username="testuser").first()
        if user:
            self.assertTrue(check_password_hash(user.access_token_hash, ""))
            self.assertTrue(check_password_hash(user.refresh_token_hash, ""))


if __name__ == "__main__":
    unittest.main()
