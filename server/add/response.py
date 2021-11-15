from functools import wraps

from flask import jsonify
from flask_jwt_extended import set_access_cookies, create_access_token


def add_auth_cookies(function):
    @wraps(function)
    def add_auth_cookies_inner(*args, **kwargs):
        result = function(*args, **kwargs)
        if len(result) == 2:
            response, user = result
            code = 200
        elif len(result) == 3:
            response, code, user = result
        else:
            return "Invalid return from decorated function", 500
        response = jsonify(response)
        response.status_code = code
        if user is not None:
            set_access_cookies(response, create_access_token(identity=user.id))
        return response

    return add_auth_cookies_inner
