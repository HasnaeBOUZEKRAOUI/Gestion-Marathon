"""Dépôt des participations (inscriptions + résultats)."""

from dataclasses import replace
from datetime import date
from typing import Dict, List, Optional

from ..models import HistoriqueLigne, ParticipantLigne, Participation, Statut
from .base_repository import BaseRepository

_SELECT_PARTICIPANT = """
    SELECT p.id_participation, p.num_dossard, p.statut, p.temps_final,
           c.id_coureur, c.nom, c.prenom, c.sexe
    FROM PARTICIPATIONS p
    JOIN COUREURS c ON c.id_coureur = p.id_coureur
"""


class ParticipationRepository(BaseRepository[Participation]):
    TABLE = "PARTICIPATIONS"
    PK = "id_participation"
    ORDRE_DEFAUT = "id_marathon, num_dossard"

    # ----------------------------------------------------------------- conversions
    def _vers_modele(self, ligne) -> Participation:
        return Participation(
            id_participation=ligne["id_participation"],
            id_coureur=ligne["id_coureur"],
            id_marathon=ligne["id_marathon"],
            num_dossard=ligne["num_dossard"],
            temps_final=ligne["temps_final"],
            statut=Statut(ligne["statut"]),
        )

    @staticmethod
    def _vers_participant(ligne) -> ParticipantLigne:
        return ParticipantLigne(
            id_participation=ligne["id_participation"],
            num_dossard=ligne["num_dossard"],
            id_coureur=ligne["id_coureur"],
            nom=ligne["nom"],
            prenom=ligne["prenom"],
            sexe=ligne["sexe"],
            statut=ligne["statut"],
            temps_final=ligne["temps_final"],
        )

    # ------------------------------------------------------------------- écriture
    def add(self, participation: Participation) -> Participation:
        curseur = self._db.execute(
            "INSERT INTO PARTICIPATIONS (id_coureur, id_marathon, num_dossard, temps_final, statut) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                participation.id_coureur,
                participation.id_marathon,
                participation.num_dossard,
                participation.temps_final,
                participation.statut.value,
            ),
        )
        return replace(participation, id_participation=curseur.lastrowid)

    def update(self, participation: Participation) -> None:
        self._db.execute(
            "UPDATE PARTICIPATIONS SET num_dossard = ?, temps_final = ?, statut = ? "
            "WHERE id_participation = ?",
            (
                participation.num_dossard,
                participation.temps_final,
                participation.statut.value,
                participation.id_participation,
            ),
        )

    # -------------------------------------------------------------------- lecture
    def get_by_dossard(self, id_marathon: int, num_dossard: int) -> Optional[Participation]:
        ligne = self._db.query_one(
            "SELECT * FROM PARTICIPATIONS WHERE id_marathon = ? AND num_dossard = ?",
            (id_marathon, num_dossard),
        )
        return self._vers_modele(ligne) if ligne else None

    def prochain_dossard(self, id_marathon: int) -> int:
        ligne = self._db.query_one(
            "SELECT COALESCE(MAX(num_dossard), 0) + 1 AS suivant "
            "FROM PARTICIPATIONS WHERE id_marathon = ?",
            (id_marathon,),
        )
        return ligne["suivant"]

    def lister_participants(self, id_marathon: int) -> List[ParticipantLigne]:
        lignes = self._db.query_all(
            _SELECT_PARTICIPANT + " WHERE p.id_marathon = ? ORDER BY p.num_dossard",
            (id_marathon,),
        )
        return [self._vers_participant(ligne) for ligne in lignes]

    def lister_classement(
        self, id_marathon: int, sexe: Optional[str] = None
    ) -> List[ParticipantLigne]:
        """Coureurs ayant terminé, du plus rapide au plus lent."""
        requete = _SELECT_PARTICIPANT + " WHERE p.id_marathon = ? AND p.statut = ?"
        params: list = [id_marathon, Statut.TERMINE.value]
        if sexe:
            requete += " AND c.sexe = ?"
            params.append(sexe)
        requete += " ORDER BY p.temps_final ASC, c.nom, c.prenom"
        return [self._vers_participant(ligne) for ligne in self._db.query_all(requete, params)]

    def lister_historique(self, id_coureur: int) -> List[HistoriqueLigne]:
        lignes = self._db.query_all(
            "SELECT p.id_participation, p.num_dossard, p.statut, p.temps_final, "
            "       m.nom_evenement, m.annee, m.date_course, m.ville "
            "FROM PARTICIPATIONS p "
            "JOIN MARATHONS m ON m.id_marathon = p.id_marathon "
            "WHERE p.id_coureur = ? ORDER BY m.date_course DESC",
            (id_coureur,),
        )
        return [
            HistoriqueLigne(
                id_participation=l["id_participation"],
                nom_evenement=l["nom_evenement"],
                annee=l["annee"],
                date_course=date.fromisoformat(l["date_course"]),
                ville=l["ville"],
                num_dossard=l["num_dossard"],
                statut=l["statut"],
                temps_final=l["temps_final"],
            )
            for l in lignes
        ]

    def compter_par_statut(self, id_marathon: int) -> Dict[str, int]:
        lignes = self._db.query_all(
            "SELECT statut, COUNT(*) AS n FROM PARTICIPATIONS "
            "WHERE id_marathon = ? GROUP BY statut",
            (id_marathon,),
        )
        compteurs = {s.value: 0 for s in Statut}
        compteurs.update({l["statut"]: l["n"] for l in lignes})
        return compteurs

    def temps_finaux(self, id_marathon: int) -> List[str]:
        lignes = self._db.query_all(
            "SELECT temps_final FROM PARTICIPATIONS "
            "WHERE id_marathon = ? AND statut = ? ORDER BY temps_final",
            (id_marathon, Statut.TERMINE.value),
        )
        return [l["temps_final"] for l in lignes]
