from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from models.base import StoredRaw

if TYPE_CHECKING:
    from models.course import Course


class CombinaisonBase(StoredRaw):
    id: str = Field(max_length=32, primary_key=True)


class CombinaisonCreate(CombinaisonBase):
    course_id: str


class Combinaison(CombinaisonBase, table=True):
    course_id: str = Field(foreign_key="course.id")
    course: "Course" = Relationship(back_populates="combinaisons")
