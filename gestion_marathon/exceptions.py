"""Exceptions métier de l'application.

Toutes héritent de ``MarathonError`` : l'interface n'a donc qu'une seule
famille d'erreurs à intercepter pour informer l'utilisateur.
"""


class MarathonError(Exception):
    """Erreur de base de l'application."""


class ValidationError(MarathonError):
    """Une donnée saisie est invalide."""


class NotFoundError(MarathonError):
    """L'élément demandé n'existe pas."""


class DuplicateError(MarathonError):
    """Une contrainte d'unicité est violée (email, dossard, inscription...)."""


class RelationError(MarathonError):
    """Une contrainte de référence est violée (ex. suppression d'un élément lié)."""
