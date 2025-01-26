# Oh Allah forgive me for having everything in a single file
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from server.auxillary import generic_error_handler

loaded = load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
print(os.path.join(os.path.dirname(__file__), ".env"))
if not loaded:
    raise FileNotFoundError()

app = Flask("AI Service",
            static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), os.environ["APP_STATIC_FOLDER"]))

CONFIG = {
    "SECRET_KEY" : os.environ["SECRET_KEY"],
    "MAX_CSV_SIZE" : int(os.environ["MAX_CSV_SIZE"]),
    "CSV_COL_DTYPES" : {
        'Date': 'object',
        'Payment Type': 'object',
        'Transaction Name': 'object',
        'Category': 'object',
        'Amount (INR)': 'int64',
    },
    "SB_API_KEY" : os.environ["SUPABASE_KEY"],
    "MAX_ACTIVE_KEYS" : int(os.environ["MAX_ACTIVE_KEYS"]),
    "JWT_KEYS" : os.environ["JWT_KEYS"].split(",")
}


CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "authorization"],
        "expose_headers": ["Authorization", "authorization"]
    }
})

app.config.from_mapping(CONFIG)
app.register_error_handler(Exception, generic_error_handler)

### Supabase setup ###
from supabase import Client
supabaseClient : Client = Client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

from server import routes