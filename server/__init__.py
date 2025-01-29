from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from server.config import configObj
import os

app = Flask("server", static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), os.environ["STATIC_DIR_NAME"]))

app.config.from_object(configObj)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from server import models
from server import routes