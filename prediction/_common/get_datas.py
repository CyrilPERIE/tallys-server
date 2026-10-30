from models.course import Course
from _common.config import TRAINING_YEAR, EVALUATION_YEAR
from service.course import get_courses_by_year
from service.utils.deps import get_session


def get_training_datas() -> list[Course]:
    session = get_session()
    with session:
        return get_courses_by_year(TRAINING_YEAR, session)

def get_evaluation_datas() -> list[Course]:
    session = get_session()
    with session:
        return get_courses_by_year(EVALUATION_YEAR, session)