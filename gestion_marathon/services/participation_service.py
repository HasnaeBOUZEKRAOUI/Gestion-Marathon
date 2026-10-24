"""Règles de gestion des inscriptions, dossards, statuts et résultats."""

from dataclasses import replace
from typing import List, Optional

from ..exceptions import NotFoundError, ValidationError
from ..models import (
    HistoriqueLigne,
    ParticipantLigne,
    Participation,
    StatistiquesMarathon,
    Statut,
)
from ..repositories import ParticipationRepository
from ..utils.time_utils import normaliser_temps, temps_moyen
from ..utils.validators import valider_sexe
from .coureur_service import CoureurService
from .marathon_service import MarathonService


class ParticipationService:
    def __init__(
        self,
        repo: ParticipationRepository,
        coureurs: CoureurService,
        marathons: MarathonService,
    ):
        self._repo = repo
        self._coureurs = coureurs
        self._marathons = marathons

    # -------------------------------------------------------------- inscriptions
    def inscrire(
        self, id_coureur: int, id_marathon: int, num_dossard: Optional[int] = None
    ) -> Participation:
        """Inscrit un coureur ; le dossard est attribué automatiquement si absent."""
        self._coureurs.obtenir(id_coureur)
        self._marathons.obtenir(id_marathon)
        if num_dossard is None:
            num_dossard = self._repo.prochain_dossard(id_marathon)
        else:
            num_dossard = self._valider_dossard(num_dossard)
        return self._repo.add(
            Participation(
                id_coureur=id_coureur, id_marathon=id_marathon, num_dossard=num_dossard
            )
        )

    def desinscrire(self, id_marathon: int, num_dossard: int) -> None:
        participation = self.trouver_par_dossard(id_marathon, num_dossard)
        if participation.statut == Statut.TERMINE:
            raise ValidationError(
                "Impossible de supprimer une participation dont le résultat est enregistré."
            )
        self._repo.delete(participation.id_participation)

    def trouver_par_dossard(self, id_marathon: int, num_dossard: int) -> Participation:
        self._marathons.obtenir(id_marathon)
        participation = self._repo.get_by_dossard(id_marathon, num_dossard)
        if participation is None:
            raise NotFoundError(
                f"Aucun participant avec le dossard {num_dossard} dans ce marathon."
            )
        return participation

    # -------------------------------------------------------- statuts et résultats
    def enregistrer_resultat(self, id_marathon: int, num_dossard: int, temps) -> Participation:
        """Enregistre le temps final : le statut passe à « Terminé »."""
        participation = self.trouver_par_dossard(id_marathon, num_dossard)
        if participation.statut in (Statut.ABANDON, Statut.NON_PARTANT):
            raise ValidationError(
                f"Ce coureur est « {participation.statut.value} » : "
                "repassez-le au statut « Inscrit » avant d'enregistrer un temps."
            )
        modifiee = replace(
            participation, temps_final=normaliser_temps(temps), statut=Statut.TERMINE
        )
        self._repo.update(modifiee)
        return modifiee

    def changer_statut(
        self, id_marathon: int, num_dossard: int, statut: Statut
    ) -> Participation:
        """Passe en Inscrit / Abandon / Non-partant (efface un éventuel temps)."""
        if statut == Statut.TERMINE:
            raise ValidationError(
                "Pour passer au statut « Terminé », enregistrez un temps final."
            )
        participation = self.trouver_par_dossard(id_marathon, num_dossard)
        modifiee = replace(participation, statut=statut, temps_final=None)
        self._repo.update(modifiee)
        return modifiee

    # ------------------------------------------------------------------ consultation
    def lister_participants(self, id_marathon: int) -> List[ParticipantLigne]:
        self._marathons.obtenir(id_marathon)
        return self._repo.lister_participants(id_marathon)

    def classement(self, id_marathon: int, sexe: Optional[str] = None) -> List[ParticipantLigne]:
        """Classement des coureurs ayant terminé ; les ex-æquo partagent le même rang."""
        self._marathons.obtenir(id_marathon)
        sexe = valider_sexe(sexe) if sexe else None
        classement: List[ParticipantLigne] = []
        rang, temps_precedent = 0, None
        for position, ligne in enumerate(self._repo.lister_classement(id_marathon, sexe), 1):
            if ligne.temps_final != temps_precedent:
                rang, temps_precedent = position, ligne.temps_final
            classement.append(replace(ligne, rang=rang))
        return classement

    def historique_coureur(self, id_coureur: int) -> List[HistoriqueLigne]:
        self._coureurs.obtenir(id_coureur)
        return self._repo.lister_historique(id_coureur)

    def statistiques(self, id_marathon: int) -> StatistiquesMarathon:
        self._marathons.obtenir(id_marathon)
        compteurs = self._repo.compter_par_statut(id_marathon)
        temps = self._repo.temps_finaux(id_marathon)
        termines = compteurs[Statut.TERMINE.value]
        abandons = compteurs[Statut.ABANDON.value]
        partis = termines + abandons
        return StatistiquesMarathon(
            total_inscrits=sum(compteurs.values()),
            en_attente=compteurs[Statut.INSCRIT.value],
            termines=termines,
            abandons=abandons,
            non_partants=compteurs[Statut.NON_PARTANT.value],
            meilleur_temps=temps[0] if temps else None,
            temps_moyen=temps_moyen(temps),
            taux_arrivee=round(100 * termines / partis, 1) if partis else None,
        )

    # --------------------------------------------------------------------- interne
    @staticmethod
    def _valider_dossard(valeur) -> int:
        try:
            dossard = int(valeur)
        except (TypeError, ValueError):
            raise ValidationError("Le dossard doit être un nombre entier.") from None
        if dossard <= 0:
            raise ValidationError("Le dossard doit être un entier positif.")
        return dossard
