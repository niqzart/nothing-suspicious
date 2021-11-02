from flask_restx import Namespace, Resource
from flask_restx.reqparse import RequestParser

from add import argument_parser, with_session
from .database import User

users_namespace: Namespace = Namespace("users", path="/")


@users_namespace.route("/sign-up/")
class SignUp(Resource):
    parser: RequestParser = RequestParser
    parser.add_argument("email", type=str, required=True)
    parser.add_argument("password", type=str, required=True)

    @with_session
    @argument_parser(users_namespace, parser)
    def post(self, session, email: str, password: str) -> bool:
        return User.create(session, email, password) is not None


@users_namespace.route("/sign-in/")
class SignIn(Resource):
    parser: RequestParser = RequestParser
    parser.add_argument("email", type=str, required=True)
    parser.add_argument("password", type=str, required=True)

    @with_session
    @argument_parser(users_namespace, parser)
    def post(self, session, email: str, password: str):
        if (user := User.find_by_email(session, email)) is None:
            return "User does not exist", 404
        return User.verify_hash(password, user.password)
