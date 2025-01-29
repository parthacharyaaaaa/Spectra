from server import db
from sqlalchemy import PrimaryKeyConstraint, Index
from sqlalchemy.types import INTEGER, BOOLEAN, DATETIME, VARCHAR, NUMERIC

from datetime import datetime

class Video_Request(db.Model):
    __tablename__ = "video_requests"

    id = db.Column(INTEGER, nullable = False)

    # File related metadata
    filename = db.Column(VARCHAR(128), nullable = False)
    filetype = db.Column(VARCHAR(8), nullable = False)

    # Video metadata
    video_length = db.Column(NUMERIC(5, 2), nullable = False)

    # Video context for LLM
    context_tag = db.Column(VARCHAR(16), nullable = True)
    context_text = db.Column(VARCHAR(128), nullable = True)

    # Storage metadata
    in_disk = db.Column(BOOLEAN, default = True)
    time_added = db.Column(DATETIME, nullable = False)
    time_removed = db.Column(DATETIME, nullable = True)

    __table_args__ = (
        PrimaryKeyConstraint(id, name="pk_video_requests")
    )

    def __init__(self, filename: str, filetype: str, video_length: float, context_tag: str | None = None, context_text: str | None = None, in_disk: bool = True, time_added=None):
        self.filename = filename
        self.filetype = filetype
        self.video_length = video_length
        self.context_tag = context_tag
        self.context_text = context_text
        self.in_disk = in_disk
        self.time_added = time_added or datetime.now()