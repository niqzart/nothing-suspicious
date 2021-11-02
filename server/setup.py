from datetime import timedelta
from os import getenv

from flask import Flask
from flask_cors import CORS
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

app: Flask = Flask(__name__, static_folder="../client/build", static_url_path="")
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=72)
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access"]

for secret_name in ["SECRET_KEY", "JWT_SECRET_KEY"]:
    app.config[secret_name] = getenv(secret_name, "hope it's local")

cors = CORS(app)

engine = create_engine("sqlite:///db.sqlite3", pool_recycle=280)  # , echo=True)
db_meta = MetaData(bind=engine)
Base = declarative_base(metadata=db_meta)
Session = sessionmaker(bind=engine)
