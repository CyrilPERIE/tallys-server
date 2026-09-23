from models.metrics import MetricCategory, Metrics
from models.scraper_log import ScraperLog
from scraper.pipelines.recuperation.update_metrics import update_metrics
from service.database import get_database_size
from service.metrics import get_metrics, get_metrics_by_category, update_scraper_metrics
from service.scraper_log import get_scraper_logs
from service.utils.deps import get_session
from fastapi import APIRouter

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/recuperation")
def metrics_recuperation() -> dict[str, list[Metrics] | list[ScraperLog] | str]:
    with get_session() as session:
        metrics = get_metrics_by_category(session, MetricCategory.RECUPERATION)
        scraper_logs = get_scraper_logs(session)
        database_size = get_database_size(session)
        return {
            "metrics": metrics,
            "scraper_logs": scraper_logs,
            "database_size": database_size
        }

@router.get("/exploration")
def metrics_recuperation() -> dict[str, list[Metrics] | list[ScraperLog] | str]:
    with get_session() as session:
        metrics = get_metrics_by_category(session, MetricCategory.EXPLORATION)
    return {
        "metrics": metrics
    }

@router.get("/")
def metrics() -> dict[str, list[Metrics] | list[ScraperLog] | str]:
    with get_session() as session:
        metrics = get_metrics(session)
        return metrics

@router.get("/update")
def update() -> None:
    update_metrics()
    return {"message": "Metrics updated"}
