from flask import Flask
from flask_cors import CORS
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

app: Flask = Flask(__name__, static_folder="../client/build", static_url_path="")
app.config["PROPAGATE_EXCEPTIONS"] = True

cors = CORS(app)

engine = create_engine("sqlite:///db.sqlite3", pool_recycle=280)  # , echo=True)
db_meta = MetaData(bind=engine)
Base = declarative_base(metadata=db_meta)
Session = sessionmaker(bind=engine)
