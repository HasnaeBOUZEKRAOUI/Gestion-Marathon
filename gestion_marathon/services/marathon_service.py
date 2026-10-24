"""Règles de gestion des éditions de marathon."""

from typing import List, Optional

from ..exceptions import NotFoundError, ValidationError
from ..models import Marathon
from ..repositories import MarathonRepository
from ..utils.validators import parser_date, valider_texte


class MarathonService:
    def __init__(self, repo: MarathonRepository):
        self._repo = repo

    @staticmethod
    def _normaliser(nom_evenement, annee, date_course, ville) -> dict:
        try:
            annee = int(annee)
        except (TypeError, ValueError):
            raise ValidationError("L'année doit être un nombre entier.") from None
        date_obj = parser_date(date_course, "date de la course")
        if date_obj.year != annee:
            raise ValidationError(
                f"L'année ({annee}) ne correspond pas à la date de la course ({date_obj.year})."
            )
        return {
            "nom_evenement": valider_texte(nom_evenement, "nom de l'événement", 100),
            "annee": annee,
            "date_course": date_obj,
            "ville": valider_texte(ville, "ville"),
        }

    def creer(self, nom_evenement, annee, date_course, ville) -> Marathon:
        donnees = self._normaliser(nom_evenement, annee, date_course, ville)
        return self._repo.add(Marathon(**donnees))

    def obtenir(self, id_marathon: int) -> Marathon:
        marathon = self._repo.get_by_id(id_marathon)
        if marathon is None:
            raise NotFoundError(f"Aucun marathon avec l'identifiant {id_marathon}.")
        return marathon

    def lister(self) -> List[Marathon]:
        return self._repo.get_all()

    def modifier(
        self,
        id_marathon: int,
        nom_evenement: Optional[str] = None,
        annee: Optional[int] = None,
        date_course=None,
        ville: Optional[str] = None,
    ) -> Marathon:
        actuel = self.obtenir(id_marathon)
        donnees = self._normaliser(
            nom_evenement if nom_evenement is not None else actuel.nom_evenement,
            annee if annee is not None else actuel.annee,
            date_course if date_course is not None else actuel.date_course,
            ville if ville is not None else actuel.ville,
        )
        modifie = Marathon(id_marathon=id_marathon, **donnees)
        self._repo.update(modifie)
        return modifie

    def supprimer(self, id_marathon: int) -> None:
        self.obtenir(id_marathon)
        self._repo.delete(id_marathon)  # RelationError si des participations existent
