from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from models.base import StoredRaw

if TYPE_CHECKING:
    from models.course import Course
    from models.programme import Programme


class ReunionBase(StoredRaw):
    id: str = Field(max_length=14, primary_key=True)


class ReunionCreate(ReunionBase):
    programme_id: str


class Reunion(ReunionBase, table=True):
    programme_id: str = Field(foreign_key="programme.id")
    programme: "Programme" = Relationship(back_populates="reunions")
    courses: list["Course"] = Relationship(back_populates="reunion")
