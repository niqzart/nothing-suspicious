from __future__ import annotations

from functools import wraps
from inflection import underscore
from typing import Type, Optional

from flask_restx import Namespace

from .utils import get_or_pop


class Identifiable:
    not_found_text: str = "Entity not found"

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def find_by_id(cls, session, entity_id: int) -> Optional[Identifiable]:
        raise NotImplementedError


def database_searcher(ns: Namespace, identifiable: Type[Identifiable], *, result_field_name: Optional[str] = None,
                      check_only: bool = False, use_session: bool = False):
    if result_field_name is None:
        result_field_name = underscore(identifiable.__name__)

    def database_searcher_wrapper(function):
        @ns.response("404 ", identifiable.not_found_text) # noqa # strings do work there! # add model
        @wraps(function)
        def database_searcher_inner(*args, **kwargs):
            session = get_or_pop(kwargs, "session", use_session)  # add None-checks with 400-response
            entity_id: int = get_or_pop(kwargs, result_field_name + "_id", check_only)
            if (entity := identifiable.find_by_id(session, entity_id)) is None:
                return identifiable.not_found_text, 404
            if not check_only:
                kwargs[result_field_name] = entity
            return function(*args, **kwargs)

        return database_searcher_inner

    return database_searcher_wrapper
