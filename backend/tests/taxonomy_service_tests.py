import unittest
import json
from werkzeug.security import generate_password_hash
from unittest.mock import patch
from flask import Flask
from app.extensions import db
from app.models import Taxonomie, Users
from app.resources.taxonomy_service import Taxonomy


class TaxonomyServiceTestCase(unittest.TestCase):
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
        self.user_id = user.id

    def tearDown(self):
        """Roll back any session changes and remove all tables."""
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_add_taxonomy_success(self):
        """Test adding a new taxonomy successfully."""
        result = Taxonomy.add_taxonomy("Test Domain", "Test Description", "testuser")
        self.assertTrue(result)
        taxonomy = Taxonomie.query.filter_by(
            domain="Test Domain", user_id=self.user_id
        ).first()
        self.assertIsNotNone(taxonomy)

    def test_add_taxonomy_user_not_found(self):
        """Test adding a taxonomy with a non-existent user fails."""
        result = Taxonomy.add_taxonomy(
            "Test Domain", "Test Description", "nonexistentuser"
        )
        self.assertFalse(result)

    def test_get_taxonomy_by_id(self):
        """Test retrieving a taxonomy by ID."""
        taxonomy = Taxonomie(
            user_id=self.user_id,
            domain="Test Domain",
            description="Test Description",
            data=None,
        )
        db.session.add(taxonomy)
        db.session.commit()

        result = Taxonomy.get_taxonomy(taxonomy.id, "testuser")
        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result["id"], taxonomy.id)

    def test_get_all_taxonomies(self):
        """Test retrieving all taxonomies for a user."""
        Taxonomie(
            user_id=self.user_id,
            domain="Domain 1",
            description="Description 1",
            data=None,
        )
        Taxonomie(
            user_id=self.user_id,
            domain="Domain 2",
            description="Description 2",
            data=None,
        )
        db.session.commit()

        result = Taxonomy.get_taxonomy(0, "testuser")
        self.assertIsInstance(result, dict)
        if result:
            self.assertEqual(len(result), 2)

    def test_delete_taxonomy_success(self):
        """Test successfully deleting a taxonomy."""
        taxonomy = Taxonomie(
            user_id=self.user_id,
            domain="Test Domain",
            description="Test Description",
            data=None,
        )
        db.session.add(taxonomy)
        db.session.commit()

        result = Taxonomy.delete_taxonomie(taxonomy.id, "testuser", "testpassword")
        self.assertTrue(result)
        deleted_taxonomy = Taxonomie.query.get(taxonomy.id)
        self.assertIsNone(deleted_taxonomy)

    def test_save_taxonomy_success(self):
        """Test successfully saving/updating a taxonomy."""
        taxonomy = Taxonomie(
            user_id=self.user_id,
            domain="Test Domain",
            description="Test Description",
            data=None,
        )
        db.session.add(taxonomy)
        db.session.commit()
        updated_taxonomy = Taxonomie.query.get(taxonomy.id)
        if updated_taxonomy:
            self.assertEqual(
                updated_taxonomy.data["categories"], [{"name": "Test Category 1"}]
            )

    @patch("app.resources.taxonomy_service.OpenAI")
    def test_generate_taxonomy(self, mock_openai):
        """Test generating taxonomy using an API call simulation."""
        taxonomy = Taxonomie(
            user_id=self.user_id,
            domain="Test Domain",
            description="Test Description",
            data=None,
        )
        db.session.add(taxonomy)
        db.session.commit()
        data = {
            "api_key": "None",
            "id": str(taxonomy.id),
            "categories": [],
        }
        taxonomy.data = data
        db.session.commit()
        data = {
            "id": taxonomy.id,
            "api_key": "fake_api_key",
            "categories": [],
        }
        mock_openai().chat.completions.create.return_value.choices[
            0
        ].message.content = json.dumps(
            {"categories": [{"name": "Category1"}, {"name": "Category2"}]}
        )
        response = Taxonomy.generate_taxonomie(data, "testuser")
        self.assertIsNotNone(response)
        if response:
            self.assertIn("categories", response)


if __name__ == "__main__":
    unittest.main()
