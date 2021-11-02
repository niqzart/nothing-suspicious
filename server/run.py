from flask import send_from_directory
from flask_restx import Api

from setup import app, db_meta


@app.route("/")
def serve():
    return send_from_directory(app.static_folder, "index.html")


api = Api(app, doc="/doc/")

db_meta.create_all()

if __name__ == "__main__":
    app.run(debug=True)
