from server import app, supabaseClient

from flask import Response, jsonify, g
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound

import pandas as pd
# import pickle         Fuck this lil nigga

from server.FraudDetect import AnomalyDetection
from server.auxillary import validate_CSV, enforce_JSON, require_token

from datetime import datetime
from uuid import uuid4
import os



@app.route("/parse-csv", methods=["POST"])
# @require_token
@validate_CSV
def storeCSV():
    try:
        tempDf = pd.read_csv(g.CSV_FILE, dtype=app.config["CSV_COL_DTYPES"])
    except:
        raise BadRequest("CSV file could not be parsed properly. Ensure proper file format, size, encoding, and properly formatted columns.")
    
    epoch = datetime.now()
    filename = f"{g.CSV_FILE.name or 'csv_file'}_{epoch.strftime('%H%M%S%d%m%y')}_{uuid4().hex}.csv"
    tempPath = os.path.join(app.static_folder, filename)

    try:
        tempDf.to_csv(tempPath)
    except:
        raise InternalServerError("There seems to be an issue on our side when saving CSV files. Please try again later :(")
    
    supabaseClient.storage.from_("Data/0d5432a1-459a-4bb6-b301-9a8c5fbfe0c0").upload(path = filename,
                                                                                     file=tempPath,
                                                                                     file_options={'Content-Type': 'text/csv'})
    try:
        supabaseClient.from_("analysis").insert({
            "score": None,
            "file_name": filename,
            "user_id": "0d5432a1-459a-4bb6-b301-9a8c5fbfe0c0",
            "category": None
        }).execute()

        newRecord = int(supabaseClient.from_("users").select("records").execute().data[0]['records']) + 1
        
        supabaseClient.from_("users").update({
            "records": newRecord
        }).eq("user_id", "0d5432a1-459a-4bb6-b301-9a8c5fbfe0c0").execute()
    except:
        # supabaseClient.storage.from_("Data/0d5432a1-459a-4bb6-b301-9a8c5fbfe0c0").remove([filename])
        os.remove(tempPath)
        raise InternalServerError("There seems to be an issue our Supabase integration, please try again later :(")
    
    os.remove(tempPath)

    return jsonify({"user" : "0d5432a1-459a-4bb6-b301-9a8c5fbfe0c0",
                    "epoch" : datetime.strftime(epoch, "%H:%M:%S, %d/%m/%y"),
                    "sb_filename" : filename}), 201

@app.route("/analyze/<string:filename>", methods=["GET"])
# @require_token
def analyze(filename : str):
    if not filename:
        raise BadRequest("Empty filename passed")
        
    try:
        response = supabaseClient.storage.from_("Data/0d5432a1-459a-4bb6-b301-9a8c5fbfe0c0").download(filename+".csv")
    except:
        raise NotFound("The given filename could not be located in your bucket")
    


    # ML logic here
    res : dict = {}
    model = AnomalyDetection()
    model.run(pd.read_csv("server/output.csv"))

    return jsonify(res), 200

