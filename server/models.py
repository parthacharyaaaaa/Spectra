from server import db
from sqlalchemy import PrimaryKeyConstraint, Index, UniqueConstraint
from sqlalchemy.types import INTEGER, BOOLEAN, DATETIME, VARCHAR, NUMERIC

from datetime import datetime

class Audio_Entity(db.Model):
    __tablename__ = "video_requests"

    id = db.Column(INTEGER, nullable = False)
    uuid = db.Column(VARCHAR(128), nullable = False)

    # File related metadata
    filename = db.Column(VARCHAR(128), nullable = False)

    # Video metadata
    url = db.Column(VARCHAR(2048), nullable=False)
    audio_length = db.Column(NUMERIC(5, 2), nullable = False)

    # Video context for LLM
    context_tag = db.Column(VARCHAR(16), nullable = True)
    context_text = db.Column(VARCHAR(128), nullable = True)

    # Storage metadata
    in_disk = db.Column(BOOLEAN, default = True)
    time_added = db.Column(DATETIME, nullable = False)
    time_removed = db.Column(DATETIME, nullable = True)

    __table_args__ = (
        PrimaryKeyConstraint(id, name="pk_video_requests"),
        Index("idx_video_requests_uuid", uuid),
        UniqueConstraint(uuid, name="uqx_video_requests_uuid"),
    )

    def __init__(self, filename: str, url: str, audio_length: float, context_tag: str | None = None, context_text: str | None = None, in_disk: bool = True, time_added=None):
        self.filename = filename
        self.url = url
        self.audio_length = audio_length
        self.context_tag = context_tag
        self.context_text = context_text
        self.in_disk = in_disk
        self.time_added = time_added or datetime.now()