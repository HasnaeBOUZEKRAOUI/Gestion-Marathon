"""Modèle Coureur."""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Coureur:
    nom: str
    prenom: str
    sexe: str
    email: str
    date_naissance: Optional[date] = None
    id_coureur: Optional[int] = None

    @property
    def nom_complet(self) -> str:
        return f"{self.prenom} {self.nom}"

    def age(self, date_reference: Optional[date] = None) -> Optional[int]:
        """Âge en années à la date donnée (aujourd'hui par défaut)."""
        if self.date_naissance is None:
            return None
        ref = date_reference or date.today()
        anniversaire_passe = (ref.month, ref.day) >= (
            self.date_naissance.month,
            self.date_naissance.day,
        )
        return ref.year - self.date_naissance.year - (0 if anniversaire_passe else 1)
