from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from models.base import Timestamped

if TYPE_CHECKING:
    from models.participant import Participant


class ChevalBase(Timestamped):
    id: str = Field(primary_key=True)
    nom: str = Field()
    sexe: str = Field()
    race: str = Field()
    nom_pere: str = Field()
    nom_mere: str = Field()


class ChevalCreate(ChevalBase):
    pass


class Cheval(ChevalBase, table=True):
    participants: list["Participant"] = Relationship(back_populates="cheval")
