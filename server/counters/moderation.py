from flask_restx import Namespace, Resource
from flask_restx.reqparse import RequestParser

from add import argument_parser, jwt_authorizer, database_searcher, with_session, pagination, pagination_parser
from users import User
from .entities import LinkCounter, CounterModes

link_moderation_namespace = Namespace("links", path="/links/")
link_parser: RequestParser = RequestParser()
link_parser.add_argument("mode", default=CounterModes.EXCLUDE_AUTHOR.to_string(),
                         choices=CounterModes.get_all_field_names())

link_model = link_moderation_namespace.model("LinkCounterIndex", LinkCounter.marshal_models["link-info"])


@link_moderation_namespace.route("/")
class LinkCreator(Resource):
    @with_session
    @jwt_authorizer(link_moderation_namespace, User)
    @argument_parser(link_moderation_namespace, link_parser)
    def post(self, session, user: User, mode: str):
        mode: CounterModes = CounterModes.from_string(mode)  # add None-check?
        LinkCounter.create(session, user, mode)


@link_moderation_namespace.route("/<int:link_counter_id>/")
class LinkManager(Resource):
    @with_session
    @jwt_authorizer(link_moderation_namespace, User)
    @database_searcher(link_moderation_namespace, LinkCounter)
    @argument_parser(link_moderation_namespace, link_parser)
    def put(self, user: User, mode: str, link_counter: LinkCounter):
        if link_counter.user_id != user.id:
            return "Not your link!", 403
        mode: CounterModes = CounterModes.from_string(mode)  # add None-check?
        link_counter.mode = mode

    @with_session
    @jwt_authorizer(link_moderation_namespace, User)
    @database_searcher(link_moderation_namespace, LinkCounter, use_session=True)
    def delete(self, session, user: User, link_counter: LinkCounter):
        if link_counter.user_id != user.id:
            return "Not your link!", 403
        session.delete(link_counter)


@link_moderation_namespace.route("/index/")
class LinkLister(Resource):
    @with_session
    @jwt_authorizer(link_moderation_namespace, User, use_session=False)
    @argument_parser(link_moderation_namespace, pagination_parser)
    @pagination(link_moderation_namespace, 20, link_model)
    def post(self, user: User, offset: int, limit: int):
        return user.links[offset:offset + limit]
