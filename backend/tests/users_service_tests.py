import unittest
from flask import Flask
from app.extensions import db
from app.resources.users_service import User
from app.models import Users


class UserServiceTestCase(unittest.TestCase):
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

    def tearDown(self):
        """Roll back any session changes and remove all tables."""
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_add_user_success(self):
        """Test adding a new user successfully."""
        result = User.add_user("testuser", "password123")
        self.assertTrue(result)
        user = User.get_user_by_username("testuser")
        self.assertIsNotNone(user)
        if user:
            self.assertEqual(user.username, "testuser")

    def test_add_user_duplicate(self):
        """Test adding a user with a duplicate username fails."""
        User.add_user("testuser", "password123")
        result = User.add_user("testuser", "newpassword")
        self.assertFalse(result)

    def test_get_user_by_username(self):
        """Test retrieving a user by username."""
        User.add_user("testuser", "password123")
        user = User.get_user_by_username("testuser")
        self.assertIsNotNone(user)
        if user:
            self.assertEqual(user.username, "testuser")

    def test_delete_user_success(self):
        """Test successfully deleting a user."""
        User.add_user("testuser", "password123")
        result = User.delete_user("testuser", "password123")
        self.assertTrue(result)
        user = User.get_user_by_username("testuser")
        self.assertIsNone(user)

    def test_delete_user_failure(self):
        """Test deleting a user with an incorrect password fails."""
        User.add_user("testuser", "password123")
        result = User.delete_user("testuser", "wrongpassword")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
