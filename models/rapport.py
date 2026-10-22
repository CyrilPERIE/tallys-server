from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from models.base import StoredRaw

if TYPE_CHECKING:
    from models.course import Course


class RapportBase(StoredRaw):
    id: str = Field(max_length=100, primary_key=True)


class RapportCreate(RapportBase):
    course_id: str


class Rapport(RapportBase, table=True):
    course_id: str = Field(foreign_key="course.id")
    course: "Course" = Relationship(back_populates="rapports")
