def generic_error_handler(e : Exception):
    response = {"message" : getattr(e, "description", "An error occured")}
    if getattr(e, "_additionalInfo"):
        response["additional info"] = e._additionalInfo
    
    return response, getattr(e, "code", 500)