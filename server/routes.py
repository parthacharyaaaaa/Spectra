from server import app, db
from flask import jsonify, request
from werkzeug.exceptions import InternalServerError, HTTPException

from server.auxillary.decorators import *
from server.auxillary.utils import *

from sqlalchemy import select, insert, delete
from sqlalchemy.exc import SQLAlchemyError

from traceback import format_exc

@app.errorhandler(HTTPException)
@app.errorhandler(SQLAlchemyError)
@app.errorhandler(Exception)
def generic_error_handler(e : Exception):
    print(e)
    print(format_exc())
    response = {"message" : getattr(e, "description", "An error occured")}
    if getattr(e, "kwargs", None):
        response.update({k : v for k,v in e.kwargs.items()})
    
    return response, getattr(e, "code", 500)