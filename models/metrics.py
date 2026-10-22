from enum import Enum as PyEnum
from sqlmodel import Field, SQLModel
from sqlalchemy import JSON, Column, Enum

from models.base import Timestamped

'''
TODO: Améliorer le modèle en ajoutant des colonnes
- order: pour ordonner les metrics plus facilement côté frontend
- category ? - enum: Scraper, Paris, PMU, IA... - Pour filtrer plus facilement côté frontend
'''

class MetricType(str, PyEnum):
    COUNT = "count"
    TABLE = "table"

class MetricCategory(str, PyEnum):
    RECUPERATION = "recuperation"
    EXPLORATION = "exploration"
    
class MetricsBase(Timestamped):
    name: str = Field(primary_key=True, unique=True)
    value: dict = Field(default={}, sa_column=Column(JSON))
    category: MetricCategory = Field(sa_column=Column(Enum(MetricCategory)))
    type: MetricType = Field(default=MetricType.COUNT, sa_column=Column(Enum(MetricType)))

class MetricsCreate(MetricsBase):
    name: str
    value: float
    type: MetricType = Field(default=MetricType.COUNT)
    
class Metrics(MetricsBase, table=True):
    __tablename__ = "metrics"