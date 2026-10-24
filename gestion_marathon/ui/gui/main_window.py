"""Fenêtre principale : menu, onglets et barre d'état."""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import List

from ... import __version__
from ...app import Application
from ...demo import charger_demo
from .base_tab import BaseTab
from .classement_tab import ClassementTab
from .coureurs_tab import CoureursTab
from .historique_tab import HistoriqueTab
from .marathons_tab import MarathonsTab
from .participations_tab import ParticipationsTab
from .theme import appliquer_theme

TITRE_APPLICATION = "Gestion de Marathon"


class MainWindow(tk.Tk):
    """Fenêtre racine ; reçoit l'``Application`` (services métier) en paramètre."""

    ONGLETS = (CoureursTab, MarathonsTab, ParticipationsTab, ClassementTab, HistoriqueTab)

    def __init__(self, app: Application):
        super().__init__()
        self.app = app
        self.title(TITRE_APPLICATION)
        self.geometry("1050x720")
        self.minsize(900, 620)
        appliquer_theme(self)

        self._var_statut = tk.StringVar(value="Prêt.")
        self._onglets: List[BaseTab] = []
        self._construire_menu()
        self._construire_interface()
        self.bind("<F5>", lambda _e: self.actualiser())

    # --------------------------------------------------------------- construction
    def _construire_menu(self) -> None:
        barre = tk.Menu(self)
        fichier = tk.Menu(barre, tearoff=False)
        fichier.add_command(label="Charger des données de démonstration",
                            command=self.charger_demo)
        fichier.add_command(label="Actualiser   (F5)", command=self.actualiser)
        fichier.add_separator()
        fichier.add_command(label="Quitter", command=self.destroy)
        barre.add_cascade(label="Fichier", menu=fichier)

        aide = tk.Menu(barre, tearoff=False)
        aide.add_command(label="À propos", command=self._a_propos)
        barre.add_cascade(label="Aide", menu=aide)
        self.configure(menu=barre)

    def _construire_interface(self) -> None:
        entete = ttk.Frame(self, padding=(16, 12, 16, 0))
        entete.pack(fill="x")
        ttk.Label(entete, text=TITRE_APPLICATION, style="Titre.TLabel").pack(side="left")
        ttk.Label(entete, text=f"Base : {self.app.db.chemin}", style="Discret.TLabel").pack(
            side="right"
        )

        ttk.Label(self, textvariable=self._var_statut, style="Statut.TLabel", anchor="w").pack(
            side="bottom", fill="x"
        )

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=12)
        for classe in self.ONGLETS:
            onglet = classe(self.notebook, self.app)
            self.notebook.add(onglet, text=classe.TITRE)
            self._onglets.append(onglet)
        self.notebook.bind("<<NotebookTabChanged>>", self._onglet_change)

    # ------------------------------------------------------------------ actions
    def afficher_statut(self, message: str) -> None:
        self._var_statut.set(message)

    def actualiser(self) -> None:
        """Recharge tous les onglets depuis la base."""
        for onglet in self._onglets:
            onglet.refresh()
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

    def _onglet_change(self, _event=None) -> None:
        # Un onglet peut afficher des données modifiées dans un autre : on le rafraîchit.
        self.nametowidget(self.notebook.select()).refresh()

    def _a_propos(self) -> None:
        messagebox.showinfo(
            "À propos",
            f"{TITRE_APPLICATION} v{__version__}\n\n"
            "Python orienté objet · SQLite3 · Tkinter",
            parent=self,
        )


def lancer(app: Application) -> None:
    """Crée la fenêtre principale et démarre la boucle d'événements."""
    MainWindow(app).mainloop()
