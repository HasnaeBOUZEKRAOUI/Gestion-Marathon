"""Règles de gestion des coureurs."""

from datetime import date
from typing import List, Optional

from ..exceptions import NotFoundError, ValidationError
from ..models import Coureur
from ..repositories import CoureurRepository
from ..utils.validators import (
    parser_date_optionnelle,
    valider_email,
    valider_sexe,
    valider_texte,
)


class CoureurService:
    ANNEE_NAISSANCE_MIN = 1900

    def __init__(self, repo: CoureurRepository):
        self._repo = repo

    # ----------------------------------------------------------------- validation
    def _normaliser(self, nom, prenom, sexe, date_naissance, email) -> dict:
        naissance = parser_date_optionnelle(date_naissance, "date de naissance")
        if naissance is not None:
            if naissance > date.today():
                raise ValidationError("La date de naissance ne peut pas être dans le futur.")
            if naissance.year < self.ANNEE_NAISSANCE_MIN:
                raise ValidationError(
                    f"La date de naissance doit être postérieure à {self.ANNEE_NAISSANCE_MIN}."
                )
        return {
            "nom": valider_texte(nom, "nom").upper(),
            "prenom": valider_texte(prenom, "prénom").title(),
            "sexe": valider_sexe(sexe),
            "date_naissance": naissance,
            "email": valider_email(email),
        }

    # ----------------------------------------------------------------------- CRUD
    def creer(self, nom, prenom, sexe, email, date_naissance=None) -> Coureur:
        donnees = self._normaliser(nom, prenom, sexe, date_naissance, email)
        return self._repo.add(Coureur(**donnees))

    def obtenir(self, id_coureur: int) -> Coureur:
        coureur = self._repo.get_by_id(id_coureur)
        if coureur is None:
            raise NotFoundError(f"Aucun coureur avec l'identifiant {id_coureur}.")
        return coureur

    def lister(self) -> List[Coureur]:
        return self._repo.get_all()

    def rechercher(self, terme: str) -> List[Coureur]:
        terme = (terme or "").strip()
        return self._repo.rechercher(terme) if terme else self._repo.get_all()

    def modifier(
        self,
        id_coureur: int,
        nom: Optional[str] = None,
        prenom: Optional[str] = None,
        sexe: Optional[str] = None,
        email: Optional[str] = None,
        date_naissance=None,
    ) -> Coureur:
        """Met à jour uniquement les champs fournis (non None)."""
        actuel = self.obtenir(id_coureur)
        donnees = self._normaliser(
            nom if nom is not None else actuel.nom,
            prenom if prenom is not None else actuel.prenom,
            sexe if sexe is not None else actuel.sexe,
            date_naissance if date_naissance is not None else actuel.date_naissance,
            email if email is not None else actuel.email,
        )
        modifie = Coureur(id_coureur=id_coureur, **donnees)
        self._repo.update(modifie)
        return modifie

    def supprimer(self, id_coureur: int) -> None:
        self.obtenir(id_coureur)  # lève NotFoundError si absent
        self._repo.delete(id_coureur)  # RelationError si des participations existent
