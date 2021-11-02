from flask import send_from_directory
from flask_restx import Api
from flask_jwt_extended import JWTManager

from users import users_namespace, User
from setup import app, db_meta


@app.route("/")
def serve():
    return send_from_directory(app.static_folder, "index.html")


api = Api(app, doc="/doc/", perfix="/api/")
api.add_namespace(users_namespace)

jwt: JWTManager = JWTManager(app)

db_meta.create_all()

if __name__ == "__main__":
    app.run(debug=True)
