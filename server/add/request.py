from __future__ import annotations

from enum import IntEnum
from functools import wraps
from typing import Optional

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


class TypeEnum(IntEnum):
    @classmethod
    def from_string(cls, string: str) -> Optional[TypeEnum]:
        return cls.__members__.get(string.upper().replace("-", "_"), None)

    @classmethod
    def get_all_field_names(cls) -> list[str]:
        return [member.lower().replace("_", "-") for member in cls.__members__]

    @classmethod
    def form_whens(cls) -> list[str]:  # TODO name shouldn't be db-related
        return list(cls.__members__.items())

    def to_string(self) -> str:
        return self.name.lower().replace("_", "-")
