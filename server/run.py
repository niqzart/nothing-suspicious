from flask import send_from_directory
from flask_restx import Api

from setup import app


@app.route("/")
def serve():
    return send_from_directory(app.static_folder, "index.html")


api = Api(app, doc="/doc/")

if __name__ == "__main__":
    app.run()
