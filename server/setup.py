from flask import Flask
from flask_cors import CORS

app: Flask = Flask(__name__, static_folder="../client/build", static_url_path="")
app.config["PROPAGATE_EXCEPTIONS"] = True

cors = CORS(app)
