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

def update_count_combinaisons(session: Session) -> MetricsBase:
    count = session.exec(select(func.count(Combinaison.id))).one()
    metric = Metrics(type=MetricType.COUNT, value={"value": count}, name="Nombre de combinaisons récupérées", category=MetricCategory.RECUPERATION)
    return create_metric(metric, session)

def update_count_courses(session: Session) -> MetricsBase:
    count = session.exec(select(func.count(Course.id))).one()
    metric = Metrics(type=MetricType.COUNT, value={"value": count}, name="Nombre de courses récupérées", category=MetricCategory.RECUPERATION)
    return create_metric(metric, session)

def update_count_courses_incoming(session: Session) -> MetricsBase:
    count = session.exec(select(func.count(Course.id)).where(Course.is_over == False)).one()
    metric = Metrics(type=MetricType.COUNT, value={"value": count}, name="Nombre de courses en cours de récupération", category=MetricCategory.RECUPERATION)
    return create_metric(metric, session)

def update_count_courses_over(session: Session) -> MetricsBase:
    count = session.exec(select(func.count(Course.id)).where(Course.is_over == True)).one()
    metric = Metrics(type=MetricType.COUNT, value={"value": count}, name="Nombre de courses terminées", category=MetricCategory.RECUPERATION)
    return create_metric(metric, session)

def update_count_participants(session: Session) -> MetricsBase:
    count = session.exec(select(func.count(Participant.id))).one()
    metric = Metrics(type=MetricType.COUNT, value={"value": count}, name="Nombre de participants récupérés", category=MetricCategory.RECUPERATION)
    return create_metric(metric, session)

def update_count_programmes(session: Session) -> MetricsBase:
    count = session.exec(select(func.count(Programme.id))).one()
    metric = Metrics(type=MetricType.COUNT, value={"value": count}, name="Nombre de programmes récupérés", category=MetricCategory.RECUPERATION)
    return create_metric(metric, session)

def update_count_reunions(session: Session) -> MetricsBase:
    count = session.exec(select(func.count(Reunion.id))).one()
    metric = Metrics(type=MetricType.COUNT, value={"value": count}, name="Nombre de réunions récupérées", category=MetricCategory.RECUPERATION)
    return create_metric(metric, session)

def update_count_mean_courses_by_programme(session: Session) -> MetricsBase:
    courses_by_programme = (
        select(
            Reunion.programme_id,
            func.count(Course.id).label("course_count")
        )
        .join(Course, Course.reunion_id == Reunion.id)
        .group_by(Reunion.programme_id)
        .subquery()
    )
    count = session.exec(
        select(func.avg(courses_by_programme.c.course_count))
    ).one()
    metric = Metrics(type=MetricType.COUNT, value={"value": float(count) if count is not None else 0}, name="Nombre moyen de courses par programme", category=MetricCategory.RECUPERATION)
    return create_metric(metric, session)

def update_count_mean_participants_by_course(session: Session) -> MetricsBase:
    participants_by_course = (
        select(
            Course.id,
            func.count(Participant.id).label("participant_count")
        )
        .join(Participant, Participant.course_id == Course.id)
        .group_by(Course.id)
    )
    count = session.exec(
        select(func.avg(participants_by_course.c.participant_count))
    ).one()
    metric = Metrics(type=MetricType.COUNT, value={"value": float(count) if count is not None else 0}, name="Nombre moyen de participants par course", category=MetricCategory.RECUPERATION)
    return create_metric(metric, session)

def update_count_mean_reunions_by_programme(session: Session) -> int:
    reunions_by_programme = (
        select(
            Programme.id,
            func.count(Reunion.id).label("reunion_count")
        )
        .join(Reunion, Reunion.programme_id == Programme.id)
        .group_by(Programme.id)
        .subquery()
    )
    count = session.exec(
        select(func.avg(reunions_by_programme.c.reunion_count))
    ).one()
    metric = Metrics(type=MetricType.COUNT, value={"value": float(count) if count is not None else 0}, name="Nombre moyen de réunions par programme", category=MetricCategory.RECUPERATION)
    return create_metric(metric, session)

def update_lowest_year_programme(session: Session) -> MetricsBase:
    programmes_ids = session.exec(select(Programme.id)).all()
    programmes_years = [int(programmes_id[4:]) for programmes_id in programmes_ids]
    lowest = min(programmes_years)
    metric = Metrics(type=MetricType.COUNT, value={"value": lowest}, name="Année la plus ancienne des programmes", category=MetricCategory.RECUPERATION)
    return create_metric(metric, session)

def update_scraper_metrics(session: Session) -> MetricsBase:
    scraper_logs_unique = session.exec(select(ScraperLog.scraper).distinct()).all()
    metrics_values = {}
    for scraper in scraper_logs_unique:
        count = session.exec(select(func.count(ScraperLog.id)).where(ScraperLog.scraper == scraper)).one()
        successes = session.exec(select(func.count(ScraperLog.id)).where(ScraperLog.scraper == scraper, ScraperLog.status == ScraperStatus.COMPLETED)).one()
        failures = session.exec(select(func.count(ScraperLog.id)).where(ScraperLog.scraper == scraper, ScraperLog.status == ScraperStatus.FAILED)).one()
        pending = session.exec(select(func.count(ScraperLog.id)).where(ScraperLog.scraper == scraper, ScraperLog.status == ScraperStatus.RUNNING)).one()
        metrics_values[scraper] = {
            "count": count,
            "successes": successes,
            "failures": failures,
            "pending": pending
        }
    metric = Metrics(type=MetricType.TABLE, value=metrics_values, name="Nombre de logs de scraper", category=MetricCategory.RECUPERATION)
    return create_metric(metric, session)

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
    metric = Metrics(
        type=MetricType.TABLE,
        value={"value": [{"name": name, "count": count} for name, count in rows]},
        name="Nombre de courses par spécialité",
        category=MetricCategory.EXPLORATION,
    )
    return create_metric(metric, session)

def update_count_courses_by_hippodrome(session: Session) -> MetricsBase:
    code = Reunion.raw["hippodrome"]["code"].as_string()
    libelle_long = Reunion.raw["hippodrome"]["libelleLong"].as_string()
    course_count = func.count(Course.id)
    rows = session.exec(
        select(code, libelle_long, course_count)
        .join(Course, Course.reunion_id == Reunion.id)
        .where(code.is_not(None))
        .group_by(code, libelle_long)
        .order_by(course_count.desc())
    ).all()
    metric = Metrics(
        type=MetricType.TABLE,
        value={"value": [{"code": code, "libelleLong": libelle, "count": count} for code, libelle, count in rows]},
        name="Nombre de courses par hippodrome",
        category=MetricCategory.EXPLORATION,
    )
    return create_metric(metric, session)

def update_count_courses_by_country(session: Session) -> MetricsBase:
    code = Reunion.raw["pays"]["code"].as_string()
    libelle = Reunion.raw["pays"]["libelle"].as_string()
    course_count = func.count(Course.id)
    rows = session.exec(
        select(code, libelle, course_count)
        .join(Course, Course.reunion_id == Reunion.id)
        .where(code.is_not(None))
        .group_by(code, libelle)
        .order_by(course_count.desc())
    ).all()
    metric = Metrics(
        type=MetricType.TABLE,
        value={"value": [{"code": code, "libelle": libelle, "count": count} for code, libelle, count in rows]},
        name="Nombre de courses par pays",
        category=MetricCategory.EXPLORATION,
    )
    return create_metric(metric, session)

def update_matrix_spearman(session: Session) -> MetricsBase:
    return;