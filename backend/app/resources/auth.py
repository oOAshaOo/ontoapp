from flask_restx import Namespace, Resource, fields
from flask import request
from .auth_service import Auth
import jwt
import os


namespace_auth = Namespace("auth", description="Authentication operations")

login_model = namespace_auth.model(
    "User",
    {
        "username": fields.String(required=True, description="A username"),
        "password": fields.String(required=True, description="A password"),
    },
)

tokens_response_model = namespace_auth.model(
    "Tokens",
    {
        "access_token": fields.String(required=True, description="A access token"),
        "refresh_token": fields.String(required=True, description="A refresh token"),
    },
)

refresh_tokens_model = namespace_auth.model(
    "RefreshTokens",
    {
        "refresh_token": fields.String(required=True, description="A refresh token"),
    },
)


@namespace_auth.route("/login")
class Login(Resource):
    @namespace_auth.expect(login_model, validate=True)
    @namespace_auth.response(200, "Success", tokens_response_model)
    @namespace_auth.response(404, "User does not exist or wrong password")
    @namespace_auth.response(400, "BAD REQUEST")
    def post(self):
        """
        Authenticate a user and return access and refresh tokens.

        This method validates the user's credentials and, if successful,
        generates and returns an access token and a refresh token.
        """
        data = request.get_json()
        username = data["username"]
        password = data["password"]
        if Auth.login_user(username=username, password=password):
            return {
                "access_token": Auth.create_tokens(
                    username=username, token_type="access"
                ),
                "refresh_token": Auth.create_tokens(
                    username=username, token_type="refresh"
                ),
            }, 200
        else:
            return "User does not exist or wrong password", 404


@namespace_auth.route("/logout")
class Logout(Resource):
    @namespace_auth.doc(security="jasonWebToken")
    @namespace_auth.response(204, "Success")
    @namespace_auth.response(403, "Access Denied")
    @Auth.token_required
    def post(self, current_user):
        """
        Log out a user and invalidate their tokens.

        This method logs out the current user by invalidating their access
        and refresh tokens, making them unusable.
        """
        Auth.logout_user(username=current_user)
        return "Success", 204


@namespace_auth.route("/refresh")
class Refresh(Resource):
    @namespace_auth.expect(refresh_tokens_model, validate=True)
    @namespace_auth.response(200, "Success", tokens_response_model)
    @namespace_auth.response(403, "Access Denied")
    @namespace_auth.response(400, "BAD REQUEST")
    def post(self):
        """
        Refresh the access token using a valid refresh token.

        This method checks the provided refresh token and, if valid,
        generates and returns a new access token along with a new refresh token.
        """
        data = request.get_json()
        token = data["refresh_token"]
        try:
            token_data = jwt.decode(
                token, os.getenv("SECRET_KEY"), algorithms=["HS256"]
            )
            current_user = token_data["sub"]
            if Auth.check_access_token(
                token=token, username=current_user, token_data=token_data
            ):
                return {
                    "access_token": Auth.create_tokens(
                        username=current_user, token_type="access"
                    ),
                    "refresh_token": Auth.create_tokens(
                        username=current_user, token_type="refresh"
                    ),
                }, 200
            else:
                return "Invalid refresh token. Please log in again", 403
        except jwt.ExpiredSignatureError:
            return "Refresh token expired. Please log in again", 403
        except jwt.InvalidTokenError:
            return "Invalid refresh token. Please log in again", 403
