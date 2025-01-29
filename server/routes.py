from server import app, db
from server.models import Video_Request
from flask import jsonify, request, Response
from werkzeug.exceptions import InternalServerError, HTTPException, BadRequest

from server.auxillary.decorators import *
from server.auxillary.utils import *

from sqlalchemy import select, insert, delete
from sqlalchemy.exc import SQLAlchemyError

from traceback import format_exc
from uuid import uuid4
from time import time
from datetime import datetime

### Exception Handler for the entire Flask app ###
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

### Endpoints ###
@app.route("/videos", methods=["POST"])
@validate_video
def processVideo() -> Response:
    ### Block to persist video temporarily to disk ###
    try:
        filename : str = f"{g.VIDEO_FILE.split('.')[0] or int(time())}_{uuid4().hex}.{g.FTYPE}"
        absFilepath : os.PathLike = os.path.join(app.static_folder, filename)
        g.VIDEO_FILE.save(absFilepath)
        epoch : datetime = datetime.now()
    except:
        raise InternalServerError("Failed to save video file. This may be an issue with video encoding")

    ### Block to extract video metadata ###
    videoLength : float = getVideoLength(absFilepath)
    if videoLength == 0:
        videoLength = getVideoLength_WithMoviePy(absFilepath)
    if not videoLength or videoLength == 0:
        raise InternalServerError("Video encoding error, please change the encoding to a more mainstream encoder")
    
    additionalResponseKwargs : dict = {}
    try:
        context_tag = request.form.get("ctx_tag")
        if context_tag and len(context_tag.split()) > 1:
            context_tag = context_tag[0]
            additionalResponseKwargs["tag_info" : "Only 1 context tag is allowed. From the provided tags, only {ctx_tag} was selected.".format(ctx_tag=context_tag)]
        
        context_text : str = request.form.get("ctx_text")
        if context_text and len(context_text) > 128:
            context_text = context_text[:128]
            symbolsList : list[str] = [" ", ".", "!", "?"]
            for idx in range(127, 0, -1):
                if context_text[idx] in symbolsList:
                    context_text = context_text[:idx]
        
        db.session.execute(insert(Video_Request).values(filename=filename.split(".")[0],
                                                        filetype=g.FTYPE,
                                                        video_length=videoLength,
                                                        context_tag=context_tag,
                                                        context_text=context_text,
                                                        in_disk=True,
                                                        time_added=epoch,
                                                        time_removed=None))
        db.session.commit()
        
    except SQLAlchemyError:
        raise InternalServerError("There was some issue with our database service. Please try again later")
    except (ValueError, TypeError):
        raise BadRequest("Invalid data sent via ctx_tags or ctx_text")

    return jsonify({"filename" : filename,
                    "epoch" : epoch.strftime("%H:%M:%S, %d/%m/%y"),
                    "message" : "Video saved succesfully"}), 201

    
