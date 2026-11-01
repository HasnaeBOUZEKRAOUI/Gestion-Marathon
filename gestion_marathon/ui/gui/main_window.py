"""Fenêtre principale : barre latérale verticale, en-tête de page et zone de contenu."""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import List

from ... import __version__
from ...app import Application
from ...demo import charger_demo
from .base_page import BasePage
from .classement_page import ClassementPage
from .coureurs_page import CoureursPage
from .dashboard_page import TableauBordPage
from .historique_page import HistoriquePage
from .marathons_page import MarathonsPage
from .participations_page import ParticipationsPage
from .sidebar import BarreLaterale
from .theme import COULEURS, appliquer_theme

TITRE_APPLICATION = "Gestion de Marathon"


class MainWindow(tk.Tk):
    """Fenêtre racine ; reçoit l'``Application`` (services métier) en paramètre.

    Disposition : barre latérale (navigation) à gauche ; à droite, un en-tête
    (titre + sous-titre de la page), la page courante et une barre d'état.
    """

    PAGES = (
        TableauBordPage,
        CoureursPage,
        MarathonsPage,
        ParticipationsPage,
        ClassementPage,
        HistoriquePage,
    )

    def __init__(self, app: Application):
        super().__init__()
        self.app = app
        self.title(f"{TITRE_APPLICATION} — v{__version__}")
        self.geometry("1240x800")
        self.minsize(1100, 700)
        self._polices = appliquer_theme(self)

        self._var_titre = tk.StringVar()
        self._var_sous_titre = tk.StringVar()
        self._var_statut = tk.StringVar(value="Prêt.")
        self._pages: List[BasePage] = []
        self._index = 0

        self._construire()
        self.bind("<F5>", lambda _e: self.actualiser())
        for position in range(len(self.PAGES)):  # Ctrl+1 ... Ctrl+6
            self.bind(f"<Control-Key-{position + 1}>", lambda _e, i=position: self.afficher(i))
        self.afficher(0)

    # --------------------------------------------------------------- construction
    def _construire(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.barre = BarreLaterale(
            self,
            self._polices,
            pages=[(page.ICONE, page.TITRE) for page in self.PAGES],
            actions=[
                ("↻", "Actualiser (F5)", self.actualiser),
                ("✚", "Données de démo", self.charger_demo),
                ("ⓘ", "À propos", self._a_propos),
            ],
            version=__version__,
            on_page=self.afficher,
        )
        self.barre.grid(row=0, column=0, sticky="ns")

        contenu = tk.Frame(self, background=COULEURS["fond"])
        contenu.grid(row=0, column=1, sticky="nsew")

        entete = ttk.Frame(contenu)
        entete.pack(fill="x", padx=32, pady=(26, 16))
        ttk.Label(entete, textvariable=self._var_titre, style="Titre.TLabel").pack(anchor="w")
        ttk.Label(entete, textvariable=self._var_sous_titre, style="Discret.TLabel").pack(
            anchor="w", pady=(2, 0)
        )

        ttk.Label(contenu, textvariable=self._var_statut, style="Statut.TLabel").pack(
            side="bottom", fill="x", padx=32, pady=(4, 10)
        )

        zone_pages = tk.Frame(contenu, background=COULEURS["fond"])
        zone_pages.pack(fill="both", expand=True, padx=32)
        zone_pages.rowconfigure(0, weight=1)
        zone_pages.columnconfigure(0, weight=1)
        for classe in self.PAGES:
            page = classe(zone_pages, self.app)
            page.grid(row=0, column=0, sticky="nsew")
            self._pages.append(page)

    # --------------------------------------------------------------- navigation
    def afficher(self, index: int) -> None:
        """Affiche la page ``index`` (rafraîchie, car d'autres pages ont pu changer les données)."""
        page = self._pages[index]
        self._index = index
        page.tkraise()
        self.barre.activer(index)
        self._var_titre.set(page.TITRE)
        self._var_sous_titre.set(page.SOUS_TITRE)
        page.refresh()

    # ------------------------------------------------------------------ actions
    def afficher_statut(self, message: str) -> None:
        self._var_statut.set(message)

    def actualiser(self) -> None:
        """Recharge toutes les pages depuis la base."""
        for page in self._pages:
            page.refresh()
        self.afficher_statut("Données actualisées.")

    def charger_demo(self) -> None:
        if charger_demo(self.app):
            self.actualiser()
            self.afficher_statut("Données de démonstration chargées.")
        else:
            messagebox.showinfo(
                "Données de démonstration",
                "La base contient déjà des données : rien n'a été modifié.",
                parent=self,
            )

    def _a_propos(self) -> None:
        messagebox.showinfo(
            "À propos",
            f"{TITRE_APPLICATION} — version {__version__}\n\n"
            "Python orienté objet · SQLite3 · Tkinter",
            parent=self,
        )


def lancer(app: Application) -> None:
    """Crée la fenêtre principale et démarre la boucle d'événements."""
    MainWindow(app).mainloop()
