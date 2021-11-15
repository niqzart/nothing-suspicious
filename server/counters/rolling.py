from flask import redirect
from flask_restx import Namespace, Resource

from add import jwt_authorizer, database_searcher, with_session
from users import User
from .entities import LinkCounter, CounterMode

rolling_namespace: Namespace = Namespace("rolling", path="/images/")


@rolling_namespace.route("/<int:link_counter_id>/")
class Roller(Resource):
    @with_session
    @jwt_authorizer(rolling_namespace, User, optional=True)
    @database_searcher(rolling_namespace, LinkCounter)
    def get(self, link_counter: LinkCounter, user: User = None):
        if link_counter.mode == CounterMode.COUNT_ALL.value:
            count = True
        elif link_counter.mode == CounterMode.EXCLUDE_AUTHOR.value:
            count = user is None or user.id != link_counter.user_id
        else:  # link_counter.mode == CounterMode.EXCLUDE_USERS.value:
            count = user is None

        if count:
            link_counter.counter += 1

        return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
