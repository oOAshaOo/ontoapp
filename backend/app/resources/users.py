from flask_restx import Namespace, Resource, fields
from flask import request
from .users_service import *
from .auth_service import *


namespace_user = Namespace("user", description="User operations")

user_model = namespace_user.model(
    "User",
    {
        "username": fields.String(required=True, description="A username"),
        "password": fields.String(required=True, description="A password"),
    },
)

user_response_model = namespace_user.model(
    "UserResponse",
    {
        "username": fields.String(description="A username"),
        "created_at": fields.String(description="Account creation date"),
        "last_login": fields.String(description="Last login date"),
    },
)

password_model = namespace_user.model(
    "Password",
    {
        "password": fields.String(required=True, description="A password"),
    },
)


@namespace_user.route("/add")
class SignUpUser(Resource):
    @namespace_user.expect(user_model, validate=True)
    @namespace_user.response(201, "User successfully added")
    @namespace_user.response(409, "User already exists")
    @namespace_user.response(400, "BAD REQUEST")
    def post(self):
        """
        Register a new user.

        This method accepts a username and password to create a new user
        account. If the username already exists, an appropriate error message
        is returned.
        """
        data = request.get_json()
        username = data["username"]
        password = data["password"]
        if User.add_user(username=username, password=password):
            return f"{username} successfully added.", 201
        else:
            return f"{username} already exists", 409


@namespace_user.route("/get")
class GetUser(Resource):
    @namespace_user.doc(security="jasonWebToken")
    @namespace_user.response(200, "Success.", user_response_model)
    @namespace_user.response(403, "Access Denied")
    @Auth.token_required
    def get(self, current_user):
        """
        Retrieve information for the currently authenticated user.

        This method returns the user details for the authenticated user.
        """
        if current_user:
            user = User.get_user_by_username(username=current_user)
            if user:
                return user.to_dict(), 200


@namespace_user.route("/delete")
class DeleteUser(Resource):
    @namespace_user.doc(security="jasonWebToken")
    @namespace_user.expect(password_model, validate=True)
    @namespace_user.response(200, "User successfully deleted")
    @namespace_user.response(401, "Wrong password")
    @namespace_user.response(403, "Access Denied")
    @namespace_user.response(400, "BAD REQUEST")
    @Auth.token_required
    def delete(self, current_user):
        """
        Delete the currently authenticated user.

        This method requires the user to provide their password for
        verification before deleting their account.
        """
        data = request.get_json()
        password = data["password"]
        if User.delete_user(current_user, password):
            return f"{current_user} successfully deleted", 200
        else:
            return "Wrong password", 401
