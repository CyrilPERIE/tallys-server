from models.combinaison import Combinaison
from models.course import Course
from models.programme import Programme
from models.reunion import Reunion
from models.participant import Participant
from models.scraper_log import ScraperLog, ScraperStatus
from service.utils.crud import upsert
from sqlmodel import Session, select
from sqlalchemy import func
from models.metrics import MetricCategory, MetricType, Metrics, MetricsBase


def get_metrics(session: Session) -> list[Metrics]:
    return session.exec(select(Metrics)).all()

def get_metrics_by_category(session: Session, category: MetricCategory) -> list[Metrics]:
    return session.exec(select(Metrics).where(Metrics.category == category)).all()

def create_metric(metric: Metrics, session: Session) -> Metrics:
    return upsert(Metrics, metric, session)

def _save(session: Session, name: str, value: dict, category: MetricCategory, metric_type: MetricType = MetricType.COUNT) -> Metrics:
    return create_metric(Metrics(type=metric_type, value=value, name=name, category=category), session)

def _save_count(session: Session, column, name: str, *filters) -> Metrics:
    query = select(func.count(column))
    for clause in filters:
        query = query.where(clause)
    return _save(session, name, {"value": session.exec(query).one()}, MetricCategory.RECUPERATION)

def _save_average(session: Session, grouped, column: str, name: str) -> Metrics:
    count = session.exec(select(func.avg(grouped.c[column]))).one()
    return _save(
        session,
        name,
        {"value": float(count) if count is not None else 0},
        MetricCategory.RECUPERATION,
    )

def update_count_combinaisons(session: Session) -> MetricsBase:
    return _save_count(session, Combinaison.id, "Nombre de combinaisons récupérées")

def update_count_courses(session: Session) -> MetricsBase:
    return _save_count(session, Course.id, "Nombre de courses récupérées")

def update_count_courses_incoming(session: Session) -> MetricsBase:
    return _save_count(session, Course.id, "Nombre de courses en cours de récupération", Course.is_over == False)

def update_count_courses_over(session: Session) -> MetricsBase:
    return _save_count(session, Course.id, "Nombre de courses terminées", Course.is_over == True)

def update_count_participants(session: Session) -> MetricsBase:
    return _save_count(session, Participant.id, "Nombre de participants récupérés")

def update_count_programmes(session: Session) -> MetricsBase:
    return _save_count(session, Programme.id, "Nombre de programmes récupérés")

def update_count_reunions(session: Session) -> MetricsBase:
    return _save_count(session, Reunion.id, "Nombre de réunions récupérées")

def update_count_mean_courses_by_programme(session: Session) -> MetricsBase:
    grouped = (
        select(Reunion.programme_id, func.count(Course.id).label("total"))
        .join(Course, Course.reunion_id == Reunion.id)
        .group_by(Reunion.programme_id)
        .subquery()
    )
    return _save_average(session, grouped, "total", "Nombre moyen de courses par programme")

def update_count_mean_participants_by_course(session: Session) -> MetricsBase:
    grouped = (
        select(Course.id, func.count(Participant.id).label("total"))
        .join(Participant, Participant.course_id == Course.id)
        .group_by(Course.id)
        .subquery()
    )
    return _save_average(session, grouped, "total", "Nombre moyen de participants par course")

def update_count_mean_reunions_by_programme(session: Session) -> MetricsBase:
    grouped = (
        select(Programme.id, func.count(Reunion.id).label("total"))
        .join(Reunion, Reunion.programme_id == Programme.id)
        .group_by(Programme.id)
        .subquery()
    )
    return _save_average(session, grouped, "total", "Nombre moyen de réunions par programme")

def update_lowest_year_programme(session: Session) -> MetricsBase:
    programmes_ids = session.exec(select(Programme.id)).all()
    lowest = min(int(programme_id[4:]) for programme_id in programmes_ids)
    return _save(session, "Année la plus ancienne des programmes", {"value": lowest}, MetricCategory.RECUPERATION)

def update_scraper_metrics(session: Session) -> MetricsBase:
    rows = session.exec(
        select(ScraperLog.scraper, ScraperLog.status, func.count(ScraperLog.id))
        .group_by(ScraperLog.scraper, ScraperLog.status)
    ).all()
    values: dict[str, dict[str, int]] = {}
    status_keys = {
        ScraperStatus.COMPLETED: "successes",
        ScraperStatus.FAILED: "failures",
        ScraperStatus.RUNNING: "pending",
    }
    for scraper, status, count in rows:
        bucket = values.setdefault(scraper, {"count": 0, "successes": 0, "failures": 0, "pending": 0})
        bucket["count"] += count
        key = status_keys.get(status)
        if key:
            bucket[key] = count
    return _save(session, "Nombre de logs de scraper", values, MetricCategory.RECUPERATION, MetricType.TABLE)

def _courses_by(session: Session, code, label, name: str, value_key: str) -> Metrics:
    course_count = func.count(Course.id)
    rows = session.exec(
        select(code, label, course_count)
        .join(Course, Course.reunion_id == Reunion.id)
        .where(code.is_not(None))
        .group_by(code, label)
        .order_by(course_count.desc())
    ).all()
    payload = [{"key": key, "name": libelle, "value": count} for key, libelle, count in rows]
    return _save(session, name, {value_key: payload}, MetricCategory.EXPLORATION, MetricType.TABLE)

def update_count_courses_by_specialite(session: Session) -> MetricsBase:
    specialite = func.json_array_elements_text(Reunion.raw["specialites"]).column_valued("specialite")
    course_count = func.count(Course.id)
    rows = session.exec(
        select(specialite, course_count)
        .select_from(Reunion)
        .join(Course, Course.reunion_id == Reunion.id)
        .group_by(specialite)
        .order_by(course_count.desc())
    ).all()
    payload = [{"key": name, "name": name, "value": count} for name, count in rows]
    return _save(session, "Nombre de courses par spécialité", {"values": payload}, MetricCategory.EXPLORATION, MetricType.TABLE)

def update_count_courses_by_hippodrome(session: Session) -> MetricsBase:
    return _courses_by(
        session,
        Reunion.raw["hippodrome"]["code"].as_string(),
        Reunion.raw["hippodrome"]["libelleLong"].as_string(),
        "Nombre de courses par hippodrome",
        "values",
    )

def update_count_courses_by_country(session: Session) -> MetricsBase:
    return _courses_by(
        session,
        Reunion.raw["pays"]["code"].as_string(),
        Reunion.raw["pays"]["libelle"].as_string(),
        "Nombre de courses par pays",
        "value",
    )

def update_matrix_spearman(session: Session) -> MetricsBase:
    return
