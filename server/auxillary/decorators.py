from functools import wraps
from flask import request, current_app, g
from werkzeug.exceptions import BadRequest

import sys

def validate_video(endpoint):
    @wraps(endpoint)
    def decorated(*args, **kwargs):
        VIDEO_FILE = request.files.get("video_file")
        if not VIDEO_FILE:
            raise BadRequest(f"Endpoint {request.root_path} requires a video file to be sent")
        
        if VIDEO_FILE.filename[-4:].lower() not in current_app.config["SUPPORTED_VIDEO_FORMATS"]:
            raise BadRequest(f"File must be in these formats only: {','.join(current_app.config['SUPPORTED_VIDEO_FORMATS'])}")
        
        if sys.getsizeof(VIDEO_FILE) > current_app.config["MAX_CSV_SIZE"]:
            raise BadRequest(f"Given file {VIDEO_FILE.name or ''} needs to be less than {current_app.config['MAX_VIDEO_SIZE']} bytes in size")
        
        g.VIDEO_FILE = VIDEO_FILE
        return endpoint(*args, **kwargs)
    return decorated