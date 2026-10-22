from datetime import datetime

from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


class Timestamped(SQLModel):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class StoredRaw(Timestamped):
    raw: dict = Field(sa_type=JSON, nullable=True)
