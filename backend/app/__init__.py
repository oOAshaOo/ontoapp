from flask import Flask
from .extensions import db, api, cors
from .resources import *
from dotenv import load_dotenv
import os


def create_app():
    """
    Create and configure a Flask application.

    This function sets up a Flask application with a database connection and API authorization.
    It loads environment variables for database credentials, configures the SQLAlchemy database URI,
    sets up API authorization headers, and initializes necessary extensions. Additionally, it registers
    various API namespaces for routing.

    Returns
     -------
        Flask: A configured Flask application instance.
    """
    app = Flask(__name__)
    load_dotenv("../.env")
    db_username = os.getenv("MARIADB_USER")
    db_password = os.getenv("MARIADB_PASSWORD")

    # database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{db_username}:{db_password}@db/ontoapp_database"
    )

    # authorization configuaration
    api.authorizations = {
        "jasonWebToken": {"type": "apiKey", "in": "header", "name": "jasonWebToken"}
    }

    # initialize extensions
    db.init_app(app)
    api.init_app(app)
    cors.init_app(app, resources={r"*": {"origins": "*"}})

    # register namespace
    api.add_namespace(namespace_user)
    api.add_namespace(namespace_auth)
    api.add_namespace(namespace_taxonomie)

    return app
