"""Objets de lecture (résultats de jointures, statistiques)."""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class ParticipantLigne:
    """Un participant d'un marathon (jointure Participation + Coureur)."""

    id_participation: int
    num_dossard: int
    id_coureur: int
    nom: str
    prenom: str
    sexe: str
    statut: str
    temps_final: Optional[str] = None
    rang: Optional[int] = None  # renseigné uniquement pour un classement

    @property
    def nom_complet(self) -> str:
        return f"{self.prenom} {self.nom}"


@dataclass(frozen=True)
class HistoriqueLigne:
    """Une participation d'un coureur (jointure Participation + Marathon)."""

    id_participation: int
    nom_evenement: str
    annee: int
    date_course: date
    ville: str
    num_dossard: int
    statut: str
    temps_final: Optional[str] = None


@dataclass(frozen=True)
class StatistiquesMarathon:
    total_inscrits: int
    en_attente: int
    termines: int
    abandons: int
    non_partants: int
    meilleur_temps: Optional[str]
    temps_moyen: Optional[str]
    taux_arrivee: Optional[float]  # terminés / (terminés + abandons), en %
