from typing import List

from sqlalchemy.orm import selectinload
from models.course import Course, CourseCreate
from pmu.types.types import CourseIdentifier
from utils.mapper import course_id_to_course_identifier
from sqlmodel import Session, select
from service.utils.crud import upsert

def create_course(course_create: CourseCreate, session: Session) -> Course:
    return upsert(Course, course_create, session)

def get_active_courses_identifiers(session: Session) -> List[CourseIdentifier]:
    courses = session.exec(select(Course.id).where(Course.is_over == False)).all()
    return [course_id_to_course_identifier(course_id) for course_id in courses]

def set_course_is_over(course_identifier: CourseIdentifier, session: Session) -> Course:
    course_id = str(course_identifier)
    course = session.get(Course, course_id)
    course.is_over = True
    session.merge(course)
    session.commit()
    return course

def get_courses_by_year(year: int, session: Session) -> List[Course]:
    courses = session.exec(
        select(Course).where(Course.id.like(f"____{year}/%"))
        .options(selectinload(Course.participants))

    ).all()
    return list(courses)