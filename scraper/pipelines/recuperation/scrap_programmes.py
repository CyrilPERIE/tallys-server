from datetime import date
from models.programme import ProgrammeCreate
from pmu.endpoints import get_programme
from pmu.types.types import ProgrammeIdentifier
from pmu.dates import date_to_programme_date
from service.utils.deps import get_session
from service.programme import create_programme
import logging
from scraper.pipelines.utils.pipeline_decorator import log_scraper

logger = logging.getLogger(__name__)


@log_scraper
def scrap_programmes() -> None:
    """
    Récupération des programmes disponibles.
    Un programmes est disponible lorsque les courses sont toutes planifiées et que cela ne bougera plus (sauf soucis inatendus.)
    Il est donc plus sur de les récupérer à ce moment là.
    """
    logger.info("scrap_programmes")
    programme_identifier = ProgrammeIdentifier(date_to_programme_date(date.today()))
    programmes = get_programme(programme_identifier)
    programmes_disponibles = programmes["programme"]["datesProgrammesDisponibles"]
    logger.info(f"{len(programmes_disponibles)} dates de programmes disponibles")
    if programmes_disponibles:
        for programme_date in programmes_disponibles:
            logger.info(f"scraping programme for {programme_date}")
            programme = get_programme(ProgrammeIdentifier(programme_date))
            _programme = programme.copy()
            del _programme["programme"]["reunions"]
            with get_session() as session:
                create_programme(ProgrammeCreate(id=programme_date, raw=_programme), session)
    logger.info("scrap_programmes finished !")