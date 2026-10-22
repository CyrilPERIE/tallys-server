from pmu.endpoints import get_participants
from service.utils.deps import get_session
from service.course import get_active_courses_identifiers
from service.participant import create_participant
import logging
from scraper.pipelines.utils.pipeline_decorator import log_scraper

logger = logging.getLogger(__name__)

@log_scraper
def scrap_participants() -> None:
    """
    Récupération des participants pour les courses actives.
    """
    logger.info("scrap_participants")
    with get_session() as session:
        course_identifiers = get_active_courses_identifiers(session)
    logger.info(f"{len(course_identifiers)} courses to scrap")
    for course_identifier in course_identifiers:
        logger.info(f"scraping course {course_identifier}")
        res = get_participants(course_identifier)
        logger.info(f"scraping {len(res['participants'])} participants for {course_identifier}")
        participants = res['participants']
        for participant in participants:
            logger.info(f"scraping participant {participant['numPmu']} for {course_identifier}")
            with get_session() as session:
                create_participant(participant, str(course_identifier), session)