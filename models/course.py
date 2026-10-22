from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from models.base import StoredRaw

if TYPE_CHECKING:
    from models.combinaison import Combinaison
    from models.participant import Participant
    from models.rapport import Rapport
    from models.reunion import Reunion


class CourseBase(StoredRaw):
    id: str = Field(max_length=16, primary_key=True)
    is_over: bool = Field(default=False)


class CourseCreate(CourseBase):
    reunion_id: str


class Course(CourseBase, table=True):
    reunion_id: str = Field(foreign_key="reunion.id")
    reunion: "Reunion" = Relationship(back_populates="courses")
    participants: list["Participant"] = Relationship(back_populates="course")
    rapports: list["Rapport"] = Relationship(back_populates="course")
    combinaisons: list["Combinaison"] = Relationship(back_populates="course")
