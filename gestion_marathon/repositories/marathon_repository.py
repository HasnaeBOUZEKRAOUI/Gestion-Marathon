"""Dépôt des marathons."""

from dataclasses import replace
from datetime import date

from ..models import Marathon
from .base_repository import BaseRepository


class MarathonRepository(BaseRepository[Marathon]):
    TABLE = "MARATHONS"
    PK = "id_marathon"
    ORDRE_DEFAUT = "date_course DESC"

    def _vers_modele(self, ligne) -> Marathon:
        return Marathon(
            id_marathon=ligne["id_marathon"],
            nom_evenement=ligne["nom_evenement"],
            annee=ligne["annee"],
            date_course=date.fromisoformat(ligne["date_course"]),
            ville=ligne["ville"],
        )

    def add(self, marathon: Marathon) -> Marathon:
        curseur = self._db.execute(
            "INSERT INTO MARATHONS (nom_evenement, annee, date_course, ville) "
            "VALUES (?, ?, ?, ?)",
            (
                marathon.nom_evenement,
                marathon.annee,
                marathon.date_course.isoformat(),
                marathon.ville,
            ),
        )
        return replace(marathon, id_marathon=curseur.lastrowid)

    def update(self, marathon: Marathon) -> None:
        self._db.execute(
            "UPDATE MARATHONS SET nom_evenement = ?, annee = ?, date_course = ?, ville = ? "
            "WHERE id_marathon = ?",
            (
                marathon.nom_evenement,
                marathon.annee,
                marathon.date_course.isoformat(),
                marathon.ville,
                marathon.id_marathon,
            ),
        )
