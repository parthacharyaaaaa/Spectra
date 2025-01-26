from server import app, supabaseClient

from flask import Response, jsonify, g
from werkzeug.exceptions import BadRequest

import pandas as pd

from auxillary import validate_CSV, enforce_JSON, require_token

from datetime import datetime

@app.route("/parse-csv", methods=["POST"])
@require_token
@validate_CSV
def storeCSV():
    try:
        pd.read_csv(g.CSV_FILE, dtype=app.config["CSV_COL_DTYPES"])
    except:
        raise BadRequest("CSV file could not be parsed properly. Ensure proper file format, size, encoding, and properly formatted columns.")
    
    supabaseClient.storage().from_(g.tkn["sub"]).upload(g.CSV_FILE)
    return jsonify({"user" : g.tkn["sub"],
                    "epoch" : datetime.strftime(datetime.now(), "%H:%M:%S, %d/%m/%y"),
                    "filename" : g.CSV_FILE.name}), 200