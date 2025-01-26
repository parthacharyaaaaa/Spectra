from flask import request, g
from werkzeug.exceptions import BadRequest

def generic_error_handler(e : Exception):
    response = {"message" : getattr(e, "description", "An error occured")}
    if getattr(e, "_additionalInfo"):
        response["additional info"] = e._additionalInfo
    
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

