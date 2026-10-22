from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from models.base import StoredRaw

if TYPE_CHECKING:
    from models.reunion import Reunion


class ProgrammeBase(StoredRaw):
    id: str = Field(max_length=14, primary_key=True)
    is_scraped: bool = Field(default=False)


class ProgrammeCreate(ProgrammeBase):
    pass


class Programme(ProgrammeBase, table=True):
    reunions: list["Reunion"] = Relationship(back_populates="programme")
