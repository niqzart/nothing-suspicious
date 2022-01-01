from datetime import timedelta
from os import getenv

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

app: Flask = Flask(__name__, static_folder="../client/build", static_url_path="")
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=72)
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access"]

for secret_name in ["SECRET_KEY", "JWT_SECRET_KEY"]:
    app.config[secret_name] = getenv(secret_name, "hope it's local")

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
for setting_name in ["MAIL_USERNAME", "MAIL_PASSWORD"]:
    app.config[setting_name] = getenv(setting_name)
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]

mail = Mail(app)

# with app.app_context():
#     from flask_mail import Message
#     mail.send(Message("Hello", ["qwert45hi@yandex.ru"], body="Hey, how are you?", html="<h1>I'm beautiful</h1><br>"))
#     exit()

cors = CORS(app)

engine = create_engine("sqlite:///db.sqlite3", pool_recycle=280)  # , echo=True)
db_meta = MetaData(bind=engine)
Base = declarative_base(metadata=db_meta)
Session = sessionmaker(bind=engine)
