### Project classes ###
from server import app, supabaseClient

### Flask and Werkzeug dependencies ###
from flask import Response, jsonify, g
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound

### Data transformation and CSV-assosciated functions ###
import pandas as pd

### Models ###
from server.FraudDetect import AnomalyDetection
from server.summary import Summary

### Custom decorators ###
from server.auxillary import validate_CSV, enforce_JSON, require_token

### Standard library ###
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
        tempDf.to_csv(tempPath, index=False)
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
    
    if filename[-4:] != ".csv":
        raise BadRequest("Analysis requires filepath param to be a .csv file")
        
    try:
        response : bytes = supabaseClient.storage.from_("Data/0d5432a1-459a-4bb6-b301-9a8c5fbfe0c0").download(filename)
        idx = response.index(b'Date')
        response = response[idx:]
        idx = response.index(b'--')
        response = response[:idx]
    except ValueError as e:
        raise InternalServerError()
    except Exception as e:
        raise NotFound(f"The given filename could not be located in your bucket: {str(e)}")
    
    tempFilepath = os.path.join(app.static_folder, f"temp_0d5432a1-459a-4bb6-b301-9a8c5fbfe0c0_{filename}")
    with open(tempFilepath, "wb") as tempFile:
        tempFile.write(response)
        df = pd.read_csv(tempFilepath)
        print(df.dtypes)


    # ML logic here
    try:
        anomalyDetector = AnomalyDetection()
        anomalyDetector.run(df)

        summarizer = Summary()
        summarizer.start(df)
        summarizer.runner()
    except:
        raise InternalServerError("An error occured with our ML service :(")
    finally:
        # os.remove(tempFilepath)
        ...

    return jsonify([]), 200

