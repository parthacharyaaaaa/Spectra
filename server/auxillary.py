from flask import request, g, current_app
from werkzeug.exceptions import BadRequest, Unauthorized
import jwt
import sys
from traceback import format_exc

RESPONSE_METADATA : dict = {
    "authorization" : ""
}

def generic_error_handler(e : Exception):
    print(e)
    print(format_exc())
    response = {"message" : getattr(e, "description", "An error occured")}
    if getattr(e, "kwargs", None):
        response.update({k : v for k,v in e.kwargs.items()})
    
    return response, getattr(e, "code", 500)

def enforce_JSON(endpoint):
    def decorated(*args, **kwargs):
        if request.mimetype.split("/")[-1].lower() != "json":
            raise BadRequest(f"Requests to {request.root_path} must be in JSON format")
        
        g.REQUEST_JSON = request.get_json(silent=True, force=True)
        if not g.REQUEST_JSON:
            raise BadRequest(f"Failed to parse JSON: Request is not JSON formatted")
        
        return endpoint(*args, **kwargs)
    return decorated

def require_token(endpoint):
    def decorated(*args, **kwargs):
        global RESPONSE_METADATA
        encodedToken : str = request.headers.get("Authorization", request.headers.get("authorization", None))
        if not encodedToken:
            exc = Unauthorized("Endpoint {} requires authentication to be accessed")
            exc.__setattr__("kwargs", {"additional" : "Please login to access this endpoint. If you don't have an account, please sign up",
                                       "auth" : RESPONSE_METADATA["authorization"]})
            raise exc
        
        isValid : bool = False
        for key in current_app.config["JWT_KEYS"]:
            try:
                tkn : dict | None = jwt.decode(encodedToken,
                                               key=key,
                                               verify=True,
                                               leeway=current_app.config["JWT_LEEWAY"])
                g.tkn = tkn
                isValid = True
                break
            except jwt.PyJWTError:
                continue
        
        if not isValid:
            exc = Unauthorized("Invalid JWT")
            exc.__setattr__("kwargs", {"additional" : "If you had logged in, please log in again in case your token has expired",
                                    "auth" : RESPONSE_METADATA["authorization"]})
            raise exc
        
        return endpoint(*args, **kwargs)
    return decorated

def validate_CSV(endpoint):
    def decorated(*args, **kwargs):
        CSV_FILE = request.files.get("csv_file")
        if not CSV_FILE:
            raise BadRequest(f"Endpoint {request.root_path} requires a csv file to be sent")
        
        if CSV_FILE.filename[-4:].lower() != ".csv":
            raise BadRequest("File must be in csv format")
        
        if sys.getsizeof(CSV_FILE) > current_app.config["MAX_CSV_SIZE"]:
            raise BadRequest(f"Given file {CSV_FILE.name} needs to be less than {current_app.config['MAX_CSV_SIZE']} bytes in size")
        
        g.CSV_FILE = CSV_FILE
        return endpoint(*args, **kwargs)
    return decorated