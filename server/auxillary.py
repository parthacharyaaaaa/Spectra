from flask import request, g, current_app
from werkzeug.exceptions import BadRequest, Unauthorized
import jwt

RESPONSE_METADATA : dict = {
    "authorization" : ""
}

def generic_error_handler(e : Exception):
    response = {"message" : getattr(e, "description", "An error occured")}
    if getattr(e, "kwargs"):
        response.update({k : v for k,v in e["kwargs"]})
    
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
            
                