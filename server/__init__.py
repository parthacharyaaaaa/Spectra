# Oh Allah forgive me for having everything in a single file
import os
from flask import Flask
from dotenv import load_dotenv
from auxillary import generic_error_handler

loaded = load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
if not loaded:
    raise FileNotFoundError()

app = Flask("AI Service")

CONFIG = {
    "SECRET_KEY" : os.environ["SECRET_KEY"]
    
}

app.config.from_mapping(CONFIG)
app.register_error_handler(Exception, generic_error_handler)