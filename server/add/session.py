from functools import wraps

from setup import Session


def with_session(function):
    @wraps(function)
    def with_session_inner(*args, **kwargs):
        with Session.begin() as session:
            kwargs["session"] = session
            return function(*args, **kwargs)

    return with_session_inner


def with_auto_commit(function):
    @wraps(function)
    def with_session_inner(*args, **kwargs):
        with Session.begin() as _:
            return function(*args, **kwargs)

    return with_session_inner
