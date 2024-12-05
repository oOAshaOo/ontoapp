from app.models import Users
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User:
    """
    Class handling user management functions, such as registration, retrieval, and deletion.
    """

    @staticmethod
    def add_user(username: str, password: str) -> bool:
        """Register a new user in the database.

        Parameters
        ----------
            username : str The username of the new user.
            password : str The plain-text password to be hashed for the new user.

        Returns
        -------
            bool: True if the user was successfully created. False if the username already exists.
        """
        if Users.query.filter_by(username=username).first():
            return False
        else:
            password_hash = generate_password_hash(password)
            new_user = Users(username=username, password_hash=password_hash)
            db.session.add(new_user)
            db.session.commit()
            return True

    @staticmethod
    def get_user_by_username(username: str):
        """
        Retrieve a user's information by their username.

        Parameters
        ----------
            username (str): The username of the user to retrieve.

        Returns
        -------
            Users: A Users object containing user data.
        """
        user = Users.query.filter_by(username=username).first()
        return user

    @staticmethod
    def delete_user(username: str, password: str) -> bool:
        """
        Delete a user from the database after verifying their password.

        Checks if a user with the given username exists and validates the password.
        If valid, deletes the user from the database.

        Parameters
        ----------
            username (str): The username of the user to delete.
            password (str): The plain-text password to verify before deletion.

        Returns
        -------
            bool: True if the user was successfully deleted. False if the user does not exist or the password is incorrect.
        """
        user = Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            db.session.delete(user)
            db.session.commit()
            return True
        else:
            return False
