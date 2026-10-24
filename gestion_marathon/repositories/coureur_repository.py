"""Dépôt des coureurs."""

from dataclasses import replace
from datetime import date
from typing import List

from ..models import Coureur
from .base_repository import BaseRepository


class CoureurRepository(BaseRepository[Coureur]):
    TABLE = "COUREURS"
    PK = "id_coureur"
    ORDRE_DEFAUT = "nom, prenom"

    def _vers_modele(self, ligne) -> Coureur:
        naissance = ligne["date_naissance"]
        return Coureur(
            id_coureur=ligne["id_coureur"],
            nom=ligne["nom"],
            prenom=ligne["prenom"],
            sexe=ligne["sexe"],
            date_naissance=date.fromisoformat(naissance) if naissance else None,
            email=ligne["email"],
        )

    def add(self, coureur: Coureur) -> Coureur:
        curseur = self._db.execute(
            "INSERT INTO COUREURS (nom, prenom, sexe, date_naissance, email) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                coureur.nom,
                coureur.prenom,
                coureur.sexe,
                coureur.date_naissance.isoformat() if coureur.date_naissance else None,
                coureur.email,
            ),
        )
        return replace(coureur, id_coureur=curseur.lastrowid)

    def update(self, coureur: Coureur) -> None:
        self._db.execute(
            "UPDATE COUREURS SET nom = ?, prenom = ?, sexe = ?, date_naissance = ?, email = ? "
            "WHERE id_coureur = ?",
            (
                coureur.nom,
                coureur.prenom,
                coureur.sexe,
                coureur.date_naissance.isoformat() if coureur.date_naissance else None,
                coureur.email,
                coureur.id_coureur,
            ),
        )

    def rechercher(self, terme: str) -> List[Coureur]:
        motif = f"%{terme}%"
        lignes = self._db.query_all(
            "SELECT * FROM COUREURS WHERE nom LIKE ? OR prenom LIKE ? OR email LIKE ? "
            f"ORDER BY {self.ORDRE_DEFAUT}",
            (motif, motif, motif),
        )
        return [self._vers_modele(ligne) for ligne in lignes]
