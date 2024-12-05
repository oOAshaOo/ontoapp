import datetime
import jwt
from flask import request
from app.models import Users
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
import os
from functools import wraps


class Auth:
    """
    Class handling user authentication, including token creation, validation,
    and user login/logout functionalities.
    """

    @staticmethod
    def create_tokens(username: str, token_type: str) -> str:
        """
        Generate an access or refresh token for the user.

        The token is created with an expiration time based on the type
        (either "access" or "refresh") and encoded with a secret key.

        Parameters
        ----------
            username (str): The username for whom the token is created.
            token_type (str): The type of token to create, either "access" or "refresh".

        Returns
        -------
            str: The generated JSON Web Token (JWT).
        """

        if token_type == "access":
            minutes = os.getenv("ACCESS_TOKEN_EXPIRATION_MINUTES")
        else:
            minutes = os.getenv("REFRESH_TOKEN_EXPIRATION_MINUTES")
        payload = {}
        if minutes:
            payload = {
                "exp": datetime.datetime.utcnow()
                + datetime.timedelta(minutes=int(minutes)),
                "sub": username,
                "type": token_type,
            }
        token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")
        Auth.write_token_hash_to_db(
            token=token, username=username, token_type=token_type
        )
        return token

    @staticmethod
    def write_token_hash_to_db(token: str, username: str, token_type: str) -> None:
        """
        Hash and store a token in the database for the specified user.

        Parameters
        ----------
            token (str): The token to hash and store.
            username (str): The username associated with the token.
            token_type (str): The type of token, either "access" or "refresh".

        Returns
        -------
            None
        """
        user = Users.query.filter_by(username=username).first()
        if user:
            if token_type == "access":
                user.access_token_hash = generate_password_hash(token)
            else:
                user.refresh_token_hash = generate_password_hash(token)
            db.session.commit()

    @staticmethod
    def check_access_token(token: str, username: str, token_data) -> bool:
        """
        Verify the validity of a user's access token.

        Checks the database for the hashed token and verifies its type.

        Parameters
        ----------
            token (str): The token to check.
            username (str): The username associated with the token.
            token_data: Decoded token data, including type information.

        Returns
        -------
            bool: True if the token is valid. False otherwise.
        """
        user = Users.query.filter_by(username=username).first()
        if user and user.refresh_token_hash:
            if (
                check_password_hash(user.refresh_token_hash, token)
                and token_data["type"] == "refresh"
            ):
                return True
            else:
                return False
        return False

    @staticmethod
    def token_required(f):
        """
        Decorator function that ensures a valid access token is provided.

        Checks the provided token's validity and type before allowing access to the
        decorated route.

        Parameters
        ----------
            f: The function to decorate.

        Returns
        -------
            The decorated function or a response indicating the token issue.
        """

        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get("jasonWebToken")
            if token:
                try:
                    token_data = jwt.decode(
                        token, os.getenv("SECRET_KEY"), algorithms=["HS256"]
                    )
                    current_user = token_data["sub"]
                    user = Users.query.filter_by(username=current_user).first()
                    if user:
                        if token_data["type"] != "access" or not check_password_hash(
                            user.access_token_hash, token
                        ):
                            return (
                                "Invalid access token",
                                403,
                            )

                except jwt.ExpiredSignatureError:
                    return "Access token expired. Please use refresh token", 403
                except jwt.InvalidTokenError:
                    return "Invalid access token. Please use refresh token", 403
            else:
                return "Access token required", 403
            return f(*args, current_user, **kwargs)

        return decorated

    @staticmethod
    def login_user(username: str, password: str) -> bool:
        """
        Log in a user by validating their credentials.

        Checks the password for the given username and updates the last login timestamp.

        Parameters
        ----------
            username (str): The username of the user logging in.
            password (str): The plain-text password for validation.

        Returns
        -------
            bool: True if login is successful. False if credentials are invalid.
        """
        user = Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            user.last_login = datetime.datetime.utcnow()
            db.session.commit()
            return True
        else:
            return False

    @staticmethod
    def logout_user(username: str) -> None:
        """
        Log out a user by invalidating their access and refresh tokens.

        Parameters
        ----------
            username (str): The username of the user logging out.

        Returns
        -------
            None
        """
        Auth.write_token_hash_to_db(token="", username=username, token_type="access")
        Auth.write_token_hash_to_db(token="", username=username, token_type="refresh")
