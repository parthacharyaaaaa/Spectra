### Project classes ###
from server import app, supabaseClient

### Flask and Werkzeug dependencies ###
from flask import Response, jsonify, g, request
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound

### Data transformation and CSV-assosciated functions ###
import pandas as pd

### Models ###
from server.FraudDetect import AnomalyDetection
from server.summary import Summary
from server.SpendingPattern import ClusterAnalysis

### Custom decorators ###
from server.auxillary import validate_CSV, enforce_JSON, require_token, private

### Standard library ###
from datetime import datetime
from uuid import uuid4
import os



@app.route("/parse-csv", methods=["POST"])
@require_token
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
    
    supabaseClient.storage.from_(f"Data/{request.headers.get("uuid")}").upload(path = filename,
                                                                                     file=tempPath,
                                                                                     file_options={'Content-Type': 'text/csv'})
    try:
        supabaseClient.from_("analysis").insert({
            "score": None,
            "file_name": filename,
            "user_id": request.headers.get("uuid"),
            "category": None
        }).execute()

        newRecord = int(supabaseClient.from_("users").select("records").execute().data[0]['records']) + 1
        
        supabaseClient.from_("users").update({
            "records": newRecord
        }).eq("user_id", request.headers.get("uuid")).execute()
    except:
        os.remove(tempPath)
        raise InternalServerError("There seems to be an issue our Supabase integration, please try again later :(")
    
    os.remove(tempPath)

    return jsonify({"user" : request.headers.get("uuid"),
                    "epoch" : datetime.strftime(epoch, "%H:%M:%S, %d/%m/%y"),
                    "sb_filename" : filename}), 201
@app.route("/analyze/<string:filename>", methods=["GET"])
@require_token
def analyze(filename : str):
    if not filename:
        raise BadRequest("Empty filename passed")
    
    if filename[-4:] != ".csv":
        raise BadRequest("Analysis requires filepath param to be a .csv file")
        
    try:
        response : bytes = supabaseClient.storage.from_(f"Data/{request.headers.get('uuid')}").download(filename)
        idx = response.index(b'Date')
        response = response[idx:]
        idx = response.index(b'--')
        response = response[:idx]
    except ValueError as e:
        raise InternalServerError()
    except Exception as e:
        raise NotFound(f"The given filename could not be located in your bucket: {str(e)}")
    
    tempFilepath = os.path.join(app.static_folder, f"{request.headers.get('uuid')}_/{filename}")
    with open(tempFilepath, "wb") as tempFile:
        tempFile.write(response)
        df = pd.read_csv(tempFilepath)


    # ML logic here
    try:
        identifier = uuid4().hex
        basepath = os.path.join(app.config["GRAPHS_DIR"], f"temp_{request.headers.get('uuid')}_{filename[:-4]}")
        paths : dict ={}

        anomalyDetector = AnomalyDetection(basepath, identifier)
        anomalyDetector.run(df)

        summarizer = Summary()
        summarizer.start(df, basepath=basepath, uuid=identifier)
        summarizer.save_all_graphs()

        clusterAnalyzer = ClusterAnalysis(df, basepath, identifier)
        clusterAnalyzer.run()

        paths.update(anomalyDetector.paths)
        paths.update(summarizer.paths)
        paths.update(clusterAnalyzer.paths)

        for k, v in paths.items():
            print("Bucket:",k,"Other:",v)
            supabaseClient.storage.from_(f"Plots/{request.headers.get('uuid')}").upload(path=k+".png",
                                                                                              file=v,
                                                                                              file_options={"content-type" : "image/png"})
    except Exception as e:
        print(e)
        raise InternalServerError("An error occured with our ML service :(")
    finally:
        os.remove(tempFilepath)
        for graphPath in paths.values():
            os.remove(graphPath)

    return jsonify([f"Plots/{request.headers.get('uuid')}_/{bucketPath}" for bucketPath in paths.keys()]), 200

# @app.route("/keys/rotate", methods=["POST"])
# # @private
# # @enforce_JSON
# def rotateKey():
#     if not ("new_key" in g.REQUEST_JSON and
#             "old_key" in g.REQUEST_JSON):
#         raise BadRequest(f"{request.path} expects 'new_key' and 'old_key' in JSON body")
#     try:
#         newKey = str(g.REQUEST_JSON["new_key"]).strip()
#     except:
#         raise BadRequest("Invalid key")
#     if not (16 < len(newKey) < 128):
#         raise BadRequest("JWT Signing key must be between 16 and 128 characters long")
    
#     app.config["JWT_KEYS"].append(g.REQUEST_JSON("new_key"))
#     currentKeyCount = len(app.config["JWT_KEYS"])
#     if currentKeyCount > app.config["MAX_ACTIVE_KEYS"]:
#         app.config["JWT_KEYS"] = app.config["JWT_KEYS"][currentKeyCount-app.config["MAX_ACTIVE_KEYS"]:]

#     return jsonify("Keys updated"), 200