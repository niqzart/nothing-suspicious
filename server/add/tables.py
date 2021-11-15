from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from json import loads as json_loads
from typing import Type, Dict, Union, Optional, Callable, get_type_hints

from flask_restx import Namespace
from flask_restx.fields import (Raw as RawField, Boolean as BooleanField,
                                Integer as IntegerField, String as StringField)
from inflection import underscore
from sqlalchemy import Column, Sequence
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.types import Boolean, Integer, String, JSON, DateTime

from .utils import get_or_pop


class DateTimeField(StringField):
    def format(self, value: datetime) -> str:
        return value.isoformat()


class JSONLoadableField(RawField):
    def format(self, value: str) -> list:
        return json_loads(value)


type_to_field: Dict[type, Type[RawField]] = {
    bool: BooleanField,
    int: IntegerField,
    str: StringField,
    JSON: JSONLoadableField,
    datetime: DateTimeField,
}

column_to_field: Dict[Type[TypeEngine], Type[RawField]] = {
    Integer: IntegerField,
    String: StringField,
    Boolean: BooleanField,
    JSON: JSONLoadableField,
    DateTime: DateTimeField,
}


@dataclass()
class LambdaFieldDef:
    """
    A field to be used in create_marshal_model, which can't be described as a :class:`Column`.
    - model_name — global name of the model to connect the field to.
    - field_type — field's return type (:class:`bool`, :class:`int`, :class:`str` or :class:`datetime`).
    - attribute — the attribute to pass to the field's keyword argument ``attribute``.
      can be a :class:`Callable` that uses models pre-marshalled version.
    """

    model_name: str
    field_type: type
    attribute: Union[str, Callable]
    name: Optional[str] = None

    def to_field(self) -> Union[Type[RawField], RawField]:
        field_type: Type[RawField] = RawField
        for supported_type in type_to_field:
            if issubclass(self.field_type, supported_type):
                field_type = type_to_field[supported_type]
                break
        return field_type(attribute=self.attribute)


def create_marshal_model(model_name: str, *fields: str, inherit: Optional[str] = None, use_defaults: bool = False):
    """
    - Adds a marshal model to a database object, marked as :class:`Marshalable`.
    - Automatically adds all :class:`LambdaFieldDef`-marked class fields to the model.
    - Sorts modules keys by alphabet and puts ``id`` field on top if present.
    :param model_name: the **global** name for the new model or model to be overwritten.
    :param fields: filed names of columns to be added to the model.
    :param inherit: model name to inherit fields from.
    :param use_defaults: whether or not to describe columns' defaults in the model.
    """

    def create_marshal_model_wrapper(cls):
        def create_field(column: Column, column_type: Type[TypeEngine]):
            field_type: Type[RawField] = column_to_field[column_type]

            if not use_defaults or column.default is None or column.nullable or isinstance(column.default, Sequence):
                return field_type(attribute=column.name)
            else:
                return field_type(attribute=column.name, default=column.default.arg)

        model_dict = {} if inherit is None else cls.marshal_models[inherit].copy()

        model_dict.update({
            column.name.replace("_", "-"): create_field(column, supported_type)
            for column in cls.__table__.columns
            if column.name in fields
            for supported_type in column_to_field.keys()
            if isinstance(column.type, supported_type)
        })

        model_dict.update({
            field_name.replace("_", "-") if field.name is None else field.name: field.to_field()
            for field_name, field_type in get_type_hints(cls).items()
            if isinstance(field_type, type) and issubclass(field_type, LambdaFieldDef)
            if (field := getattr(cls, field_name)).model_name == model_name
        })

        cls.marshal_models[model_name] = OrderedDict(sorted(model_dict.items()))
        if "id" in cls.marshal_models[model_name].keys():
            cls.marshal_models[model_name].move_to_end("id", last=False)

        return cls

    return create_marshal_model_wrapper


class Marshalable:
    """ Marker-class for classes that can be decorated with ``create_marshal_model`` """
    marshal_models: Dict[str, OrderedDict[str, Type[RawField]]] = {}


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
        @ns.response("404 ", identifiable.not_found_text)  # noqa # strings do work there! # add model
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
