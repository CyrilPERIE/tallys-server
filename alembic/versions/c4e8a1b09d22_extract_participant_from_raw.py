"""Extract participant fields from raw.

Revision ID: c4e8a1b09d22
Revises: db9647e0e07e
Create Date: 2026-10-23 10:00:00.000000

"""
from dataclasses import dataclass
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4e8a1b09d22"
down_revision: Union[str, Sequence[str], None] = "db9647e0e07e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PERSONNES = ("driver", "entraineur", "proprietaire", "eleveur")


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    type_: sa.types.TypeEngine
    expression: str
    nullable: bool = False
    references: str | None = None


def _column(name: str, type_: sa.types.TypeEngine, expression: str, *, nullable: bool = False, references: str | None = None) -> ColumnSpec:
    return ColumnSpec(name, type_, expression, nullable, references)


COLUMNS = [
    _column("num_pmu", sa.Integer(), "(raw::jsonb ->> 'numPmu')::integer"),
    _column("age_cheval", sa.Integer(), "COALESCE((raw::jsonb ->> 'age')::integer, 0)"),
    _column("statut", sa.String(), "COALESCE(raw::jsonb ->> 'statut', '')"),
    _column("oeilleres", sa.String(), "COALESCE(raw::jsonb ->> 'oeilleres', '')"),
    _column("driver_change", sa.Boolean(), "COALESCE((raw::jsonb ->> 'driverChange')::boolean, false)"),
    _column("robe_code_cheval", sa.String(), "NULLIF(raw::jsonb -> 'robe' ->> 'code', '')", nullable=True),
    _column("robe_libelle_court_cheval", sa.String(), "COALESCE(raw::jsonb -> 'robe' ->> 'libelleCourt', '')"),
    _column("robe_libelle_long_cheval", sa.String(), "COALESCE(raw::jsonb -> 'robe' ->> 'libelleLong', '')"),
    _column("indicateur_inedit", sa.Boolean(), "COALESCE((raw::jsonb ->> 'indicateurInedit')::boolean, false)"),
    _column("musique_cheval", sa.String(), "COALESCE(raw::jsonb ->> 'musique', '')"),
    _column("nombre_courses_cheval", sa.Integer(), "COALESCE((raw::jsonb ->> 'nombreCourses')::integer, 0)"),
    _column("nombre_victoires_cheval", sa.Integer(), "COALESCE((raw::jsonb ->> 'nombreVictoires')::integer, 0)"),
    _column("nombre_places_cheval", sa.Integer(), "COALESCE((raw::jsonb ->> 'nombrePlaces')::integer, 0)"),
    _column("nombre_places_second_cheval", sa.Integer(), "COALESCE((raw::jsonb ->> 'nombrePlacesSecond')::integer, 0)"),
    _column("nombre_places_troisieme_cheval", sa.Integer(), "COALESCE((raw::jsonb ->> 'nombrePlacesTroisieme')::integer, 0)"),
    _column("allure", sa.String(), "COALESCE(raw::jsonb ->> 'allure', '')"),
    _column("avis_entraineur", sa.String(), "NULLIF(raw::jsonb ->> 'avisEntraineur', '')", nullable=True),
    _column("ordre_arrivee", sa.Integer(), "(raw::jsonb ->> 'ordreArrivee')::integer", nullable=True),
    _column("jument_pleine", sa.Boolean(), "COALESCE((raw::jsonb ->> 'jumentPleine')::boolean, false)"),
    _column("engagement", sa.Boolean(), "COALESCE((raw::jsonb ->> 'engagement')::boolean, false)"),
    _column("supplement", sa.Integer(), "COALESCE((raw::jsonb ->> 'supplement')::numeric::integer, 0)"),
    _column("handicap_distance", sa.Integer(), "(raw::jsonb ->> 'handicapDistance')::integer", nullable=True),
    _column("poids_condition_monte_change", sa.Boolean(), "COALESCE((raw::jsonb ->> 'poidsConditionMonteChange')::boolean, false)"),
    _column("temps_obtenu", sa.Float(), "(raw::jsonb ->> 'tempsObtenu')::double precision", nullable=True),
    _column("reduction_kilometrique", sa.Float(), "(raw::jsonb ->> 'reductionKilometrique')::double precision", nullable=True),
    _column("gains_carriere", sa.Float(), "COALESCE((raw::jsonb -> 'gainsParticipant' ->> 'gainsCarriere')::double precision, 0)"),
    _column("gains_victoires", sa.Float(), "COALESCE((raw::jsonb -> 'gainsParticipant' ->> 'gainsVictoires')::double precision, 0)"),
    _column("gains_place", sa.Float(), "COALESCE((raw::jsonb -> 'gainsParticipant' ->> 'gainsPlace')::double precision, 0)"),
    _column("gains_annee_en_cours", sa.Float(), "COALESCE((raw::jsonb -> 'gainsParticipant' ->> 'gainsAnneeEnCours')::double precision, 0)"),
    _column("gains_annee_precedente", sa.Float(), "COALESCE((raw::jsonb -> 'gainsParticipant' ->> 'gainsAnneePrecedente')::double precision, 0)"),
    _column("proprietaire_id", sa.String(), "NULLIF(btrim(raw::jsonb ->> 'proprietaire'), '')", references="proprietaire"),
    _column("entraineur_id", sa.String(), "NULLIF(btrim(raw::jsonb ->> 'entraineur'), '')", references="entraineur"),
    _column("driver_id", sa.String(), "NULLIF(btrim(raw::jsonb ->> 'driver'), '')", references="driver"),
    _column("cheval_id", sa.String(), "NULLIF(btrim(raw::jsonb ->> 'nom'), '')", references="cheval"),
    _column("eleveur_id", sa.String(), "NULLIF(btrim(raw::jsonb ->> 'eleveur'), '')", nullable=True, references="eleveur"),
]


def upgrade() -> None:
    op.alter_column(
        "participant",
        "id",
        existing_type=sa.String(length=20),
        type_=sa.String(length=32),
        existing_nullable=False,
    )

    op.create_table(
        "cheval",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("nom", sa.String(), nullable=False),
        sa.Column("sexe", sa.String(), nullable=False),
        sa.Column("race", sa.String(), nullable=False),
        sa.Column("nom_pere", sa.String(), nullable=False),
        sa.Column("nom_mere", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    for table in PERSONNES:
        op.create_table(
            table,
            sa.Column("id", sa.String(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    for column in COLUMNS:
        op.add_column("participant", sa.Column(column.name, column.type_, nullable=True))

    op.execute(
        sa.text(
            """
            INSERT INTO cheval (id, nom, sexe, race, nom_pere, nom_mere, created_at, updated_at)
            SELECT DISTINCT ON (nom)
                nom,
                nom,
                COALESCE(sexe, ''),
                COALESCE(race, ''),
                COALESCE(nom_pere, ''),
                COALESCE(nom_mere, ''),
                NOW(),
                NOW()
            FROM (
                SELECT
                    btrim(raw::jsonb ->> 'nom') AS nom,
                    btrim(raw::jsonb ->> 'sexe') AS sexe,
                    btrim(raw::jsonb ->> 'race') AS race,
                    btrim(raw::jsonb ->> 'nomPere') AS nom_pere,
                    btrim(raw::jsonb ->> 'nomMere') AS nom_mere,
                    updated_at,
                    id
                FROM participant
                WHERE raw IS NOT NULL
                  AND NULLIF(btrim(raw::jsonb ->> 'nom'), '') IS NOT NULL
            ) AS src
            ORDER BY nom, updated_at DESC, id DESC
            """
        )
    )
    for table in PERSONNES:
        op.execute(
            sa.text(
                f"""
                INSERT INTO {table} (id)
                SELECT DISTINCT btrim(raw::jsonb ->> '{table}')
                FROM participant
                WHERE raw IS NOT NULL
                  AND NULLIF(btrim(raw::jsonb ->> '{table}'), '') IS NOT NULL
                """
            )
        )

    assignments = ",\n".join(f"{column.name} = {column.expression}" for column in COLUMNS)
    op.execute(sa.text(f"UPDATE participant SET {assignments} WHERE raw IS NOT NULL"))

    for column in COLUMNS:
        if not column.nullable:
            op.alter_column("participant", column.name, nullable=False)
        if column.references:
            op.create_index(f"ix_participant_{column.name}", "participant", [column.name])
            op.create_foreign_key(
                f"fk_participant_{column.name}",
                "participant",
                column.references,
                [column.name],
                ["id"],
            )


def downgrade() -> None:
    for column in COLUMNS:
        if column.references:
            op.drop_constraint(f"fk_participant_{column.name}", "participant", type_="foreignkey")
            op.drop_index(f"ix_participant_{column.name}", table_name="participant")
    for column in reversed(COLUMNS):
        op.drop_column("participant", column.name)
    for table in (*reversed(PERSONNES), "cheval"):
        op.drop_table(table)
    op.alter_column(
        "participant",
        "id",
        existing_type=sa.String(length=32),
        type_=sa.String(length=20),
        existing_nullable=False,
    )
