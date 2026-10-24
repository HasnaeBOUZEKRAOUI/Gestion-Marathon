"""Onglet « Historique » : toutes les participations d'un coureur."""

import tkinter as tk
from tkinter import ttk

from ...models import Statut
from .base_tab import BaseTab, gerer_erreurs
from .theme import COULEURS
from .widgets import Colonne, ListeEntites, TableauDonnees

_ETIQUETTES_STATUT = {
    Statut.TERMINE.value: "termine",
    Statut.ABANDON.value: "abandon",
    Statut.NON_PARTANT.value: "non_partant",
}


class HistoriqueTab(BaseTab):
    TITRE = "Historique"

    COLONNES = (
        Colonne("marathon", "Marathon", 240, extensible=True),
        Colonne("date", "Date", 100, "center"),
        Colonne("ville", "Ville", 130),
        Colonne("dossard", "Dossard", 80, "center"),
        Colonne("statut", "Statut", 110, "center"),
        Colonne("temps", "Temps", 100, "center"),
    )

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self._var_resume = tk.StringVar()
        self._construire()
        self.refresh()

    def _construire(self) -> None:
        haut = ttk.Frame(self)
        haut.pack(fill="x")
        ttk.Label(haut, text="Coureur :", style="Gras.TLabel").pack(side="left")
        self.liste_coureurs = ListeEntites(haut, largeur=48)
        self.liste_coureurs.pack(side="left", padx=8)
        self.liste_coureurs.bind("<<ComboboxSelected>>", lambda _e: self._recharger())

        resume = ttk.LabelFrame(self, text="Résumé", padding=10)
        resume.pack(fill="x", pady=(12, 0))
        ttk.Label(resume, textvariable=self._var_resume, justify="left").pack(anchor="w")

        self.tableau = TableauDonnees(
            self,
            self.COLONNES,
            etiquettes={
                "termine": COULEURS["termine"],
                "abandon": COULEURS["abandon"],
                "non_partant": COULEURS["non_partant"],
            },
        )
        self.tableau.pack(fill="both", expand=True, pady=(12, 0))

    def refresh(self) -> None:
        self.liste_coureurs.charger(
            [(c.id_coureur, f"{c.nom} {c.prenom} — {c.email}") for c in self.app.coureurs.lister()]
        )
        self._recharger()

    @gerer_erreurs
    def _recharger(self) -> None:
        id_coureur = self.liste_coureurs.identifiant()
        if id_coureur is None:
            self.tableau.charger([])
            self._var_resume.set("Aucun coureur enregistré.")
            return

        historique = self.app.participations.historique_coureur(id_coureur)
        self.tableau.charger(
            [
                (
                    h.id_participation,
                    (
                        f"{h.nom_evenement} {h.annee}",
                        h.date_course.isoformat(),
                        h.ville,
                        h.num_dossard,
                        h.statut,
                        h.temps_final,
                    ),
                    _ETIQUETTES_STATUT.get(h.statut),
                )
                for h in historique
            ]
        )
        temps = [h.temps_final for h in historique if h.temps_final]
        self._var_resume.set(
            f"Participations : {len(historique)}   |   "
            f"Courses terminées : {len(temps)}   |   "
            f"Meilleur temps personnel : {min(temps) if temps else '—'}"
        )
        self.notifier(f"{len(historique)} participation(s) pour ce coureur.")
