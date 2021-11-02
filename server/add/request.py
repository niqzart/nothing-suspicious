from functools import wraps

from flask_restx import Namespace
from flask_restx.reqparse import RequestParser


def argument_parser(namespace: Namespace, parser: RequestParser):
    def argument_parser_wrapper(function):
        @namespace.expect(parser)
        @wraps(function)
        def argument_parser_inner(*args, **kwargs):
            kwargs.update(parser.parse_args())
            return function(*args, **kwargs)

        return argument_parser_inner

    return argument_parser_wrapper
