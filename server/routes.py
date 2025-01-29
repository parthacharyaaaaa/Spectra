from server import app, db
from server.models import Audio_Entity
from flask import jsonify, request, Response
from werkzeug.exceptions import InternalServerError, HTTPException, BadRequest, NotFound
from moviepy import CompositeVideoClip

from server.auxillary.decorators import *
from server.auxillary.utils import *
from server.auxillary.utils_llm import *

from sqlalchemy import select, insert, update
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
@app.route("/urls", methods=["POST"])
# @validate_video
@enforce_JSON
def storeVideo() -> Response:
    ### Block to persist video temporarily to disk ###
    if "url" not in g.REQUEST_JSON:
        raise BadRequest("url missing")
    try:
        url : str = g.REQUEST_JSON["url"]
        uuid = uuid4().hex
        filename : str = f"{int(time())}_{uuid}"
        absFilepath : os.PathLike = os.path.join(app.static_folder, filename)

        print(absFilepath)
        download_youtube_video_mp3(url, absFilepath)
        download_youtube_video_mp4(url, absFilepath)
        epoch : datetime = datetime.now()
    except:
        raise InternalServerError("Failed to save video file. This may be an issue with video encoding")

    ### Block to extract audio metadata ###
    audioLength : float = getAudioLength(absFilepath+".mp3")
    if audioLength == 0:
        raise InternalServerError("Video/Audio encoding error, please change the encoding to a more mainstream encoder")
    
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
        
        db.session.execute(insert(Audio_Entity).values(filename=filename,
                                                        uuid=uuid,
                                                        url=url,
                                                        audio_length=audioLength,
                                                        context_tag=context_tag,
                                                        context_text=context_text,
                                                        in_disk=True,
                                                        time_added=epoch,
                                                        time_removed=None,
                                                        in_hitlist=False))
        db.session.commit()
        
    except SQLAlchemyError:
        raise InternalServerError("There was some issue with our database service. Please try again later")
    except (ValueError, TypeError):
        raise BadRequest("Invalid data sent via ctx_tags or ctx_text")

    return jsonify({"filename" : filename,
                    "id" : uuid,
                    "epoch" : epoch.strftime("%H:%M:%S, %d/%m/%y"),
                    "message" : "Video saved succesfully"}), 201

    
@app.route("/videos/<string:video_id>/process", methods=["GET", "HEAD"])
def processVideo(video_id : str) -> Response:
    requestedAudio : Audio_Entity = db.session.execute(select(Audio_Entity).where(Audio_Entity.uuid == video_id)).scalar_one_or_none()
    if not requestedAudio:
        raise NotFound(f"Video with id {video_id} could not be found")
    
    absFilepath : os.PathLike = os.path.join(app.static_folder, requestedAudio.filename+".mp3")
    try:
        transcript = getAssemblyAITranscript(absFilepath, app.config["AAI_API_KEY"], False)
    except:
        raise InternalServerError("Failed to extract transcript from audio")
    print(len(transcript))
    print(transcript[-1].end // 1000)

    sentences = " ".join(x.text for x in transcript).split(".")[:-1]

    sentecesWithTimestamps = []
    transcriptIterator = 0
    print(sentences)
    for sentence in sentences:
        sentecesWithTimestamps.append({"text" : sentence.strip(),
                                       "start" : transcript[transcriptIterator].start / 1000,
                                       "end" : transcript[transcriptIterator+len(sentence.split())-1].end / 1000})
        transcriptIterator += len(sentence.split())-1

    mergedSentences = []
    dictIterator = 0

    while dictIterator < len(sentecesWithTimestamps):
        breakpoints : list = []
        mergedSentence = sentecesWithTimestamps[dictIterator]["text"]
        start = sentecesWithTimestamps[dictIterator]["start"]
        end = sentecesWithTimestamps[dictIterator]["end"]
        currentDuration = end - start

        while dictIterator + 1 < len(sentecesWithTimestamps) and currentDuration < 15:
            nextSegment = sentecesWithTimestamps[dictIterator + 1]
            breakpoints.append(nextSegment["start"])
            nextDuration = nextSegment["end"] - nextSegment["start"]

            if currentDuration + nextDuration <= 15:
                mergedSentence += ". " + nextSegment["text"]
                currentDuration += nextDuration
                dictIterator += 1
                end = nextSegment["end"]
            else:
                break

        mergedSentences.append({"text": mergedSentence, "start": start, "end": end, "breakpoints" : breakpoints})

        dictIterator += 1

    newDir = os.path.join(app.static_folder, f"{video_id}_{int(time())}")
    os.mkdir(newDir)
    for index, entry in enumerate(mergedSentences):
        clip : CompositeVideoClip = makeVideoSubclipWithCaptions(entry["text"].split("."), entry["start"], VideoFileClip("temps/1738156231_357729e9881d456bb9b79f9e92ecb117.mp4"), entry["breakpoints"])
        clip.write_videofile(os.path.join(newDir, video_id+f"{index}.mp4"), codec = "libx264", audio_codec = "aac")

    
    return mergedSentences, 200