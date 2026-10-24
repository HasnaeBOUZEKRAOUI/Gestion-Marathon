"""Racine de composition : assemble base, dépôts et services."""

from pathlib import Path
from typing import Union

from .config import CHEMIN_BD_PAR_DEFAUT
from .database import Database
from .repositories import CoureurRepository, MarathonRepository, ParticipationRepository
from .services import CoureurService, MarathonService, ParticipationService


class Application:
    """Point d'entrée unique pour utiliser les services métier.

    Exemple :
        app = Application("marathon.db")
        coureur = app.coureurs.creer("Alaoui", "Sara", "F", "sara@mail.com")
    """

    def __init__(self, chemin_bd: Union[str, Path] = CHEMIN_BD_PAR_DEFAUT):
        self.db = Database(chemin_bd)
        self.coureurs = CoureurService(CoureurRepository(self.db))
        self.marathons = MarathonService(MarathonRepository(self.db))
        self.participations = ParticipationService(
            ParticipationRepository(self.db), self.coureurs, self.marathons
        )

    def close(self) -> None:
        self.db.close()

    def __enter__(self) -> "Application":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()
