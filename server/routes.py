from server import app, supabaseClient

from flask import Response, jsonify, g
from werkzeug.exceptions import BadRequest, InternalServerError

import pandas as pd

from auxillary import validate_CSV, enforce_JSON, require_token

from datetime import datetime
from uuid import uuid4

@app.route("/parse-csv", methods=["POST"])
@require_token
@validate_CSV
def storeCSV():
    try:
        pd.read_csv(g.CSV_FILE, dtype=app.config["CSV_COL_DTYPES"])
    except:
        raise BadRequest("CSV file could not be parsed properly. Ensure proper file format, size, encoding, and properly formatted columns.")
    
    epoch = datetime.now()
    filename = f"{g.CSV_FILE}_{epoch.strftime('%H%M%S%d%m%y')}_{uuid4.hex}.csv"

    response = supabaseClient.storage.from_(g.tkn["sub"]).upload(filename)
    if response.get("error"):
        raise InternalServerError(f"Error uploading file: {response['error']}")
    
    analysis_response = supabaseClient.from_("analysis").insert({
        "score": None,
        "file_name": filename,
        "user_id": g.tkn["sub"],
        "category": None
    }).execute()

    if analysis_response.get("error"):
        raise InternalServerError(f"Error inserting into 'analysis': {analysis_response['error']}")

    # Update the 'records' column in the 'users' table
    update_response = supabaseClient.from_("users").update({
        "records": supabaseClient.raw("records + 1")
    }).eq("uuid", g.tkn["sub"]).execute()

    if update_response.get("error"):
        raise InternalServerError(f"Error updating 'users': {update_response['error']}")

    return jsonify({"user" : g.tkn["sub"],
                    "epoch" : datetime.strftime(epoch, "%H:%M:%S, %d/%m/%y"),
                    "sb_filename" : filename}), 201

@app.route("/analyze/<str:filename>", methods=["POST"])
@require_token
def analyze(filename : str):
    if not filename:
        raise BadRequest("Empty filename passed")
    response = supabaseClient.storage.from_(g.tkn["sub"]).download(filename+".csv")

    if response.get("error"):
        raise InternalServerError(f"File could not be retrieved: {response['error']['message']}")

    file_content = response.get("data")

    # ML logic here
    res : dict = {}

    return jsonify(res), 200

