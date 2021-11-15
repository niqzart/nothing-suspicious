from functools import wraps

from flask import jsonify
from flask_jwt_extended import set_access_cookies, create_access_token
from flask_restx import Namespace, Model, marshal
from flask_restx.fields import Nested, List as ListField, Boolean as BoolField
from flask_restx.reqparse import RequestParser


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


pagination_parser: RequestParser = RequestParser()
pagination_parser.add_argument("counter", type=int, required=False, help="The page number for pagination")
pagination_parser.add_argument("offset", type=int, required=False, help="The starting entity index")


def pagination(ns: Namespace, page_size: int, model: Model, *,
               envelope: str = "results", skip_none: bool = True):
    list_marshal_model = ns.model("List" + model.name, {envelope: ListField(Nested(model)), "has-next": BoolField})

    def pagination_wrapper(function):
        @ns.response(200, "Success", list_marshal_model)
        @wraps(function)
        def pagination_inner(*args, **kwargs):
            offset: int = kwargs.pop("offset", None)
            counter: int = kwargs.pop("counter", None)
            if offset is None:
                if counter is None:
                    return "Neither counter nor offset are provided", 400
                offset = counter * page_size

            kwargs["offset"] = offset
            kwargs["limit"] = page_size + 1
            result_list = function(*args, **kwargs)

            if has_next := len(result_list) > page_size:
                result_list.pop()

            return {"results": marshal(result_list, model, skip_none=skip_none), "has-next": has_next}

        return pagination_inner

    return pagination_wrapper
