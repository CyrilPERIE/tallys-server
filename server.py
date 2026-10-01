import sys
from api.routes import metrics
from api.routes import scrap
from fastapi import FastAPI
from utils.logger import setup_logging
import uvicorn
from scraper.orchestrator import every_day, every_five_minutes, update_metrics
from fastapi_utilities import repeat_every, repeat_at

active_scraper = True
not_dev_mode = True

app = FastAPI()

app.include_router(metrics.router)
app.include_router(scrap.router)

@app.on_event('startup')
def startup_event():
    setup_logging()
    if active_scraper and not_dev_mode:
        every_day()
    if not_dev_mode:
        update_metrics()

@app.on_event('startup')
@repeat_every(seconds=60 * 5)
def every_five_minutes_event():
    if active_scraper and not_dev_mode:
        every_five_minutes()
    if not_dev_mode:
        update_metrics()

## Tous les jours à 4h
@app.on_event('startup')
@repeat_at(cron='0 4 * * *')
def every_day_event():
    if active_scraper and not_dev_mode:
        every_day()
    if not_dev_mode:
        update_metrics()

'''TODO: Création d'un middleware pour éviter le DDOS.
'''
'''TODO: Permettre le multi-threading pour la gestion asyncronne des requêtes et des pipelines.
'''
@app.get("/health")
async def read_root():
    return {"message": "ok"}


if __name__ == "__main__":
    args = sys.argv[1:]
    if "no-scraper" in args:
        active_scraper = False
    if "dev" in sys.argv[1:]:
        not_dev_mode = False
    uvicorn.run(app, host="0.0.0.0", port=8080)
