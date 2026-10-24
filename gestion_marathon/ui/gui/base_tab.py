"""Classe de base des onglets et gestion centralisée des erreurs."""

import functools
import logging
from tkinter import messagebox, ttk

from ...app import Application
from ...exceptions import MarathonError

logger = logging.getLogger(__name__)


def gerer_erreurs(methode):
    """Décorateur : affiche une boîte de dialogue au lieu de propager l'erreur.

    - ``MarathonError`` (saisie invalide, doublon...) : avertissement lisible.
    - toute autre exception : erreur inattendue, journalisée.
    """

    @functools.wraps(methode)
    def enveloppe(self, *args, **kwargs):
        try:
            return methode(self, *args, **kwargs)
        except MarathonError as exc:
            messagebox.showwarning("Action impossible", str(exc), parent=self)
        except Exception as exc:  # noqa: BLE001 - dernier filet de sécurité de l'UI
            logger.exception("Erreur inattendue dans %s", methode.__qualname__)
            messagebox.showerror("Erreur inattendue", f"{type(exc).__name__} : {exc}", parent=self)
        return None

    return enveloppe


class BaseTab(ttk.Frame):
    """Onglet de l'application : reçoit l'``Application`` et sait se rafraîchir."""

    TITRE = ""

    def __init__(self, parent, app: Application):
        super().__init__(parent, padding=12)
        self.app = app

    def refresh(self) -> None:
        """Recharge les données affichées depuis la base."""
        raise NotImplementedError

    def notifier(self, message: str) -> None:
        """Affiche un message dans la barre d'état de la fenêtre principale."""
        afficher = getattr(self.winfo_toplevel(), "afficher_statut", None)
        if afficher:
            afficher(message)

    def confirmer(self, message: str, titre: str = "Confirmation") -> bool:
        return messagebox.askyesno(titre, message, parent=self, icon="warning")
