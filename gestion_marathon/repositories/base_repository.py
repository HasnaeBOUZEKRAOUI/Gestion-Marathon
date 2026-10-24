"""Classe de base commune aux dépôts."""

import sqlite3
from typing import Generic, List, Optional, TypeVar

from ..database import Database

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Opérations génériques : lecture par identifiant, liste, suppression, comptage.

    Les sous-classes définissent ``TABLE``, ``PK``, ``ORDRE_DEFAUT`` et
    ``_vers_modele`` (conversion ligne SQL -> objet métier).
    """

    TABLE: str = ""
    PK: str = ""
    ORDRE_DEFAUT: str = ""

    def __init__(self, db: Database):
        self._db = db

    def _vers_modele(self, ligne: sqlite3.Row) -> T:
        raise NotImplementedError

    def get_by_id(self, identifiant: int) -> Optional[T]:
        ligne = self._db.query_one(
            f"SELECT * FROM {self.TABLE} WHERE {self.PK} = ?", (identifiant,)
        )
        return self._vers_modele(ligne) if ligne else None

    def get_all(self) -> List[T]:
        lignes = self._db.query_all(f"SELECT * FROM {self.TABLE} ORDER BY {self.ORDRE_DEFAUT}")
        return [self._vers_modele(ligne) for ligne in lignes]

    def delete(self, identifiant: int) -> bool:
        curseur = self._db.execute(
            f"DELETE FROM {self.TABLE} WHERE {self.PK} = ?", (identifiant,)
        )
        return curseur.rowcount > 0

    def count(self) -> int:
        return self._db.query_one(f"SELECT COUNT(*) AS n FROM {self.TABLE}")["n"]
