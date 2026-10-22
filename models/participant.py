from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from models.base import StoredRaw
from models.cheval import Cheval
from models.personne import Driver, Eleveur, Entraineur, Proprietaire

if TYPE_CHECKING:
    from models.course import Course


class ParticipantBase(StoredRaw):
    id: str = Field(max_length=32, primary_key=True)

    num_pmu: int = Field()
    age_cheval: int = Field()
    statut: str = Field()
    oeilleres: str = Field()
    driver_change: bool = Field()
    robe_code_cheval: str | None = Field(default=None)
    robe_libelle_court_cheval: str = Field()
    robe_libelle_long_cheval: str = Field()
    indicateur_inedit: bool = Field()
    musique_cheval: str = Field()
    nombre_courses_cheval: int = Field()
    nombre_victoires_cheval: int = Field()
    nombre_places_cheval: int = Field()
    nombre_places_second_cheval: int = Field()
    nombre_places_troisieme_cheval: int = Field()
    allure: str = Field()
    avis_entraineur: str | None = Field(default=None)
    ordre_arrivee: int | None = Field(default=None)
    jument_pleine: bool = Field()
    engagement: bool = Field()
    supplement: int = Field()
    handicap_distance: int | None = Field(default=None)
    poids_condition_monte_change: bool = Field()
    temps_obtenu: float | None = Field(default=None)
    reduction_kilometrique: float | None = Field(default=None)
    gains_carriere: float = Field()
    gains_victoires: float = Field()
    gains_place: float = Field()
    gains_annee_en_cours: float = Field()
    gains_annee_precedente: float = Field()

    proprietaire_id: str = Field(foreign_key="proprietaire.id")
    entraineur_id: str = Field(foreign_key="entraineur.id")
    driver_id: str = Field(foreign_key="driver.id")
    cheval_id: str = Field(foreign_key="cheval.id")
    eleveur_id: str | None = Field(default=None, foreign_key="eleveur.id")


class ParticipantCreate(ParticipantBase):
    course_id: str


class Participant(ParticipantBase, table=True):
    course_id: str = Field(foreign_key="course.id")
    course: "Course" = Relationship(back_populates="participants")
    proprietaire: Proprietaire = Relationship(back_populates="participants")
    entraineur: Entraineur = Relationship(back_populates="participants")
    driver: Driver = Relationship(back_populates="participants")
    cheval: Cheval = Relationship(back_populates="participants")
    eleveur: Eleveur = Relationship(back_populates="participants")
