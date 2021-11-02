from flask_restx import Namespace, Resource
from flask_restx.reqparse import RequestParser

from add import argument_parser, with_session, add_auth_cookies
from .database import User

users_namespace: Namespace = Namespace("users", path="/")


@users_namespace.route("/sign-up/")
class SignUp(Resource):
    parser: RequestParser = RequestParser()
    parser.add_argument("email", required=True)
    parser.add_argument("password", required=True)

    @with_session
    @argument_parser(users_namespace, parser)
    @add_auth_cookies
    def post(self, session, email: str, password: str):
        return (user := User.create(session, email, password)) is not None, user


@users_namespace.route("/sign-in/")
class SignIn(Resource):
    parser: RequestParser = RequestParser()
    parser.add_argument("email", required=True)
    parser.add_argument("password", required=True)

    @with_session
    @argument_parser(users_namespace, parser)
    @add_auth_cookies
    def post(self, session, email: str, password: str):
        if (user := User.find_by_email(session, email)) is None:
            return "user does not exist", 404, user
        if User.verify_hash(password, user.password):
            return "success", user
        return "wrong password", user
