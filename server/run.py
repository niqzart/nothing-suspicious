from flask import send_from_directory
from flask_restx import Api
from flask_jwt_extended import JWTManager

from add import with_session
from counters import link_moderation_namespace, rolling_namespace
from users import users_namespace, TokenBlockList
from setup import app, db_meta


@app.route("/")
def serve():
    return send_from_directory(app.static_folder, "index.html")


api = Api(app, doc="/doc/", perfix="/api/", version="0.2.0")
api.add_namespace(users_namespace)
api.add_namespace(link_moderation_namespace)
api.add_namespace(rolling_namespace)

jwt: JWTManager = JWTManager(app)

db_meta.create_all()


@jwt.token_in_blocklist_loader
@with_session
def check_if_token_revoked(_, jwt_payload, session):
    return TokenBlockList.find_by_jti(session, jwt_payload["jti"]) is not None


if __name__ == "__main__":
    app.run(debug=True)
