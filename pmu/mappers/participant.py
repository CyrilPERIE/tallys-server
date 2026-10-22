from dataclasses import dataclass

from sqlmodel import SQLModel

from models.cheval import Cheval, ChevalCreate
from models.participant import ParticipantCreate
from models.personne import PERSONNES, PersonneLink
from pmu.types.api_types import Participant as ApiParticipant


def _text(value: str | None) -> str:
    return (value or "").strip()


@dataclass(frozen=True)
class LinkedRow:
    model: type[SQLModel]
    payload: SQLModel


@dataclass(frozen=True)
class ParticipantAggregate:
    rows: tuple[LinkedRow, ...]
    participant: ParticipantCreate


def _personne_row(link: PersonneLink, value: str | None) -> LinkedRow | None:
    name = _text(value)
    if not name and not link.required:
        return None
    return LinkedRow(link.table, link.create(id=name))


def map_participant(raw: dict, course_id: str) -> ParticipantAggregate:
    api = ApiParticipant.model_validate(raw)
    robe = api.robe
    gains = api.gainsParticipant
    robe_code = _text(robe.code) if robe else ""
    robe_court = robe.libelleCourt if robe else ""
    robe_long = robe.libelleLong if robe else ""
    nom = _text(api.nom)
    sources = {
        "driver": api.driver,
        "entraineur": api.entraineur,
        "proprietaire": api.proprietaire,
        "eleveur": raw.get("eleveur"),
    }
    personne_rows = [
        row
        for link in PERSONNES
        if (row := _personne_row(link, sources[link.relation])) is not None
    ]
    eleveur = _text(sources["eleveur"])

    return ParticipantAggregate(
        rows=(
            LinkedRow(
                Cheval,
                ChevalCreate(
                    id=nom,
                    nom=nom,
                    sexe=_text(api.sexe),
                    race=_text(api.race),
                    nom_pere=_text(api.nomPere),
                    nom_mere=_text(api.nomMere),
                ),
            ),
            *personne_rows,
        ),
        participant=ParticipantCreate(
            id=f"{course_id}/P{api.numPmu}",
            course_id=course_id,
            num_pmu=api.numPmu,
            age_cheval=api.age,
            statut=api.statut,
            oeilleres=api.oeilleres,
            driver_change=api.driverChange,
            robe_code_cheval=robe_code or None,
            robe_libelle_court_cheval=robe_court,
            robe_libelle_long_cheval=robe_long,
            indicateur_inedit=api.indicateurInedit,
            musique_cheval=api.musique or "",
            nombre_courses_cheval=api.nombreCourses,
            nombre_victoires_cheval=api.nombreVictoires,
            nombre_places_cheval=api.nombrePlaces,
            nombre_places_second_cheval=api.nombrePlacesSecond,
            nombre_places_troisieme_cheval=api.nombrePlacesTroisieme,
            allure=api.allure,
            avis_entraineur=_text(api.avisEntraineur) or None,
            ordre_arrivee=api.ordreArrivee,
            jument_pleine=api.jumentPleine,
            engagement=api.engagement,
            supplement=api.supplement,
            handicap_distance=api.handicapDistance,
            poids_condition_monte_change=api.poidsConditionMonteChange,
            temps_obtenu=api.tempsObtenu,
            reduction_kilometrique=api.reductionKilometrique,
            gains_carriere=gains.gainsCarriere,
            gains_victoires=gains.gainsVictoires,
            gains_place=gains.gainsPlace,
            gains_annee_en_cours=gains.gainsAnneeEnCours,
            gains_annee_precedente=gains.gainsAnneePrecedente,
            proprietaire_id=_text(api.proprietaire),
            entraineur_id=_text(api.entraineur),
            driver_id=_text(api.driver),
            cheval_id=nom,
            eleveur_id=eleveur or None,
            raw=raw,
        ),
    )
