from functools import wraps
from typing import Type, Optional

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace
from inflection import underscore

from .tables import Identifiable
from .utils import get_or_pop


class UserRole(Identifiable):
    error_code: int = 403

    @classmethod
    def find_by_id(cls, session, entity_id: int) -> Optional[Identifiable]:
        raise NotImplementedError


def jwt_authorizer(ns: Namespace, role: Type[UserRole], check_only: bool = False, use_session: bool = True):
    """
    - Authorizes user by JWT-token.
    - If token is missing or is not processable, falls back on flask-jwt-extended error handlers.
    - If user doesn't exist or doesn't have the role required, sends the corresponding response.
    - All error responses are added to the documentation automatically.
    - Can pass user and session objects to the decorated function.
    :param ns: the namespace
    :param role: role to expect
    :param check_only: (default: False) if True, user object won't be passed to the decorated function
    :param use_session: (default: True) whether or not to pass the session to the decorated function
    """

    auth_errors: list[tuple[str, str]] = [("401 ", "JWTError"), ("422 ", "InvalidJWT")]
    result_field_name: str = underscore(role.__name__)

    def authorizer_wrapper(function):
        @ns.response(f"{role.error_code} ", role.not_found_text)  # noqa # strings do work there! # add model
        @ns.response(*auth_errors[0])
        @ns.response(*auth_errors[1])
        @jwt_required()
        @wraps(function)
        def authorizer_inner(*args, **kwargs):
            session = get_or_pop(kwargs, "session", use_session)  # add None-checks with 400-response
            if (entity := role.find_by_id(session, get_jwt_identity())) is None:
                return role.not_found_text, role.error_code
            if not check_only:
                kwargs[result_field_name] = entity
            return function(*args, **kwargs)

        return authorizer_inner

    return authorizer_wrapper
