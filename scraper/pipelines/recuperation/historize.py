import datetime
from pmu.types.types import ProgrammeIdentifier
from pmu.constants import MIN_DATE
from pmu.dates import date_to_programme_date
from scraper.pipelines.recuperation.scrap_past_programmes import scrap_past_programmes
from scraper.pipelines.utils.pipeline_decorator import log_scraper

LOWEST_DATE = ProgrammeIdentifier(MIN_DATE)
HIGHEST_DATE = ProgrammeIdentifier(date_to_programme_date(datetime.date.today()))

@log_scraper
def historize(start_date: ProgrammeIdentifier = LOWEST_DATE, end_date: ProgrammeIdentifier = HIGHEST_DATE) -> None:
    '''
    Démarre une collecte qui peut avoir des dates antérieures à aujourd'hui.
    La collecte peut être limitée à une période spécifique en fournissant les dates de début et de fin.
    Les programmes collectés sont stockés en base de données en isScraped=False, ainsi au prochain passage des scrapers, les données seront récupérées (courses, participants, rapports...).
    '''
    if start_date < LOWEST_DATE:
        start_date = LOWEST_DATE
    if end_date > HIGHEST_DATE:
        end_date = HIGHEST_DATE
    if start_date > end_date:
        raise ValueError("start_date must be before end_date")
    programmes: list[ProgrammeIdentifier] = []
    while start_date <= end_date:
        programmes.append(start_date)
        start_date = start_date.increment()
    for programme in programmes:
        scrap_past_programmes(programme)
    '''
    TODO: Voir si il faut intégrer les scrapers des autres pipelines (courses, participants, rapports...).
    '''