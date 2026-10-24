"""Accès à la base SQLite : connexion, schéma et traduction des erreurs."""

import sqlite3
from pathlib import Path
from typing import Iterable, List, Optional, Union

from .exceptions import DuplicateError, MarathonError, RelationError
from .models.participation import Statut


def _schema_sql() -> str:
    statuts = ", ".join(f"'{s.value}'" for s in Statut)
    termine = Statut.TERMINE.value
    return f"""
    CREATE TABLE IF NOT EXISTS COUREURS (
        id_coureur     INTEGER PRIMARY KEY AUTOINCREMENT,
        nom            TEXT NOT NULL,
        prenom         TEXT NOT NULL,
        sexe           TEXT NOT NULL CHECK (sexe IN ('M', 'F')),
        date_naissance TEXT,
        email          TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS MARATHONS (
        id_marathon   INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_evenement TEXT NOT NULL,
        annee         INTEGER NOT NULL,
        date_course   TEXT NOT NULL,
        ville         TEXT NOT NULL,
        UNIQUE (nom_evenement, annee)
    );

    CREATE TABLE IF NOT EXISTS PARTICIPATIONS (
        id_participation INTEGER PRIMARY KEY AUTOINCREMENT,
        id_coureur       INTEGER NOT NULL REFERENCES COUREURS (id_coureur),
        id_marathon      INTEGER NOT NULL REFERENCES MARATHONS (id_marathon),
        num_dossard      INTEGER NOT NULL CHECK (num_dossard > 0),
        temps_final      TEXT,
        statut           TEXT NOT NULL DEFAULT 'Inscrit'
                         CHECK (statut IN ({statuts})),
        UNIQUE (id_marathon, num_dossard),
        UNIQUE (id_coureur, id_marathon),
        CHECK (
            (statut = '{termine}' AND temps_final IS NOT NULL)
            OR (statut <> '{termine}' AND temps_final IS NULL)
        )
    );

    CREATE INDEX IF NOT EXISTS idx_participations_marathon
        ON PARTICIPATIONS (id_marathon);
    CREATE INDEX IF NOT EXISTS idx_participations_coureur
        ON PARTICIPATIONS (id_coureur);
    """


class Database:
    """Encapsule une connexion SQLite unique.

    Les clés étrangères sont activées (désactivées par défaut dans SQLite) et
    les erreurs d'intégrité sont converties en exceptions métier lisibles.
    Utiliser ``":memory:"`` comme chemin pour une base temporaire (tests).
    """

    def __init__(self, chemin: Union[str, Path] = ":memory:"):
        self.chemin = str(chemin)
        self._conn = sqlite3.connect(self.chemin)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(_schema_sql())

    # ------------------------------------------------------------------ requêtes
    def execute(self, sql: str, params: Iterable = ()) -> sqlite3.Cursor:
        """Exécute une requête d'écriture et valide la transaction."""
        try:
            curseur = self._conn.execute(sql, tuple(params))
            self._conn.commit()
            return curseur
        except sqlite3.IntegrityError as exc:
            self._conn.rollback()
            raise self._traduire(exc) from exc

    def query_all(self, sql: str, params: Iterable = ()) -> List[sqlite3.Row]:
        return self._conn.execute(sql, tuple(params)).fetchall()

    def query_one(self, sql: str, params: Iterable = ()) -> Optional[sqlite3.Row]:
        return self._conn.execute(sql, tuple(params)).fetchone()

    # --------------------------------------------------------------- cycle de vie
    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()

    # ------------------------------------------------------------ gestion d'erreurs
    @staticmethod
    def _traduire(exc: sqlite3.IntegrityError) -> MarathonError:
        message = str(exc)
        if "UNIQUE" in message:
            if "email" in message:
                return DuplicateError("Cette adresse email est déjà utilisée.")
            if "num_dossard" in message:
                return DuplicateError("Ce numéro de dossard est déjà attribué dans ce marathon.")
            if "id_coureur" in message:
                return DuplicateError("Ce coureur est déjà inscrit à ce marathon.")
            if "annee" in message:
                return DuplicateError("Cette édition de marathon existe déjà.")
            return DuplicateError("Cette donnée existe déjà.")
        if "FOREIGN KEY" in message:
            return RelationError(
                "Opération impossible : des participations sont liées à cet élément."
            )
        return MarathonError(f"Contrainte de données violée : {message}")
