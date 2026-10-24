"""Modèle Marathon (une édition d'une course)."""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Marathon:
    nom_evenement: str
    annee: int
    date_course: date
    ville: str
    id_marathon: Optional[int] = None

    @property
    def libelle(self) -> str:
        return f"{self.nom_evenement} {self.annee}"
