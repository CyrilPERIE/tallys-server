from sqlmodel import Session

from models.participant import Participant
from pmu.mappers.participant import map_participant
from service.utils.crud import upsert


def create_participant(raw: dict, course_id: str, session: Session) -> None:
    mapped = map_participant(raw, course_id)
    for row in mapped.rows:
        upsert(row.model, row.payload, session, commit=False)
    upsert(Participant, mapped.participant, session)
