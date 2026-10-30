from models.rapport import Rapport, RapportCreate
from sqlmodel import Session, select
from pmu.types.enum import BetType
from pmu.types.types import CourseIdentifier
from service.utils.crud import upsert

def create_rapport(rapport_create: RapportCreate, session: Session) -> Rapport:
    return upsert(Rapport, rapport_create, session)

def get_rapport_by_course_and_bet_type(course: CourseIdentifier, bet_type: BetType, session: Session) -> Rapport | None:
    return session.exec(select(Rapport).where(Rapport.id == f"{str(course)}-{bet_type.value}")).first()