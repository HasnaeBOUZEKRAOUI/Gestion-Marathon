"""Modèle Participation (inscription d'un coureur à un marathon + résultat)."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Statut(str, Enum):
    INSCRIT = "Inscrit"
    TERMINE = "Terminé"
    ABANDON = "Abandon"
    NON_PARTANT = "Non-partant"

    @classmethod
    def depuis_texte(cls, valeur: str) -> "Statut":
        return cls(valeur)


@dataclass
class Participation:
    id_coureur: int
    id_marathon: int
    num_dossard: int
    temps_final: Optional[str] = None  # format HH:MM:SS
    statut: Statut = Statut.INSCRIT
    id_participation: Optional[int] = None
