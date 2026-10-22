from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.participant import Participant


class PersonneBase(SQLModel):
    id: str = Field(primary_key=True)


class PersonneCreate(PersonneBase):
    pass


class PersonneLink:
    def __init__(self, relation: str, table: type[SQLModel], create: type[PersonneCreate], *, required: bool) -> None:
        self.relation = relation
        self.table = table
        self.create = create
        self.required = required


def _personne(class_name: str, relation: str, *, required: bool) -> PersonneLink:
    table = SQLModel.__class__(
        class_name,
        (PersonneBase,),
        {
            "__module__": __name__,
            "__tablename__": relation,
            "__annotations__": {"participants": list["Participant"]},
            "participants": Relationship(back_populates=relation),
        },
        table=True,
    )
    return PersonneLink(relation, table, PersonneCreate, required=required)


DRIVER = _personne("Driver", "driver", required=True)
ENTRAINEUR = _personne("Entraineur", "entraineur", required=True)
PROPRIETAIRE = _personne("Proprietaire", "proprietaire", required=True)
ELEVEUR = _personne("Eleveur", "eleveur", required=False)

PERSONNES = (DRIVER, ENTRAINEUR, PROPRIETAIRE, ELEVEUR)

Driver = DRIVER.table
Entraineur = ENTRAINEUR.table
Proprietaire = PROPRIETAIRE.table
Eleveur = ELEVEUR.table
DriverCreate = PersonneCreate
EntraineurCreate = PersonneCreate
ProprietaireCreate = PersonneCreate
EleveurCreate = PersonneCreate
