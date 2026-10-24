"""Onglet « Classement » : résultats triés d'un marathon et statistiques."""

import tkinter as tk
from tkinter import ttk

from .base_tab import BaseTab, gerer_erreurs
from .theme import COULEURS
from .widgets import Colonne, ListeEntites, TableauDonnees


class ClassementTab(BaseTab):
    TITRE = "Classement"

    COLONNES = (
        Colonne("rang", "Rang", 70, "center"),
        Colonne("dossard", "Dossard", 80, "center"),
        Colonne("nom", "Coureur", 260, extensible=True),
        Colonne("sexe", "Sexe", 60, "center"),
        Colonne("temps", "Temps", 120, "center"),
    )

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self._var_sexe = tk.StringVar(value="")
        self._var_stats = tk.StringVar()
        self._construire()
        self.refresh()

    def _construire(self) -> None:
        haut = ttk.Frame(self)
        haut.pack(fill="x")
        ttk.Label(haut, text="Marathon :", style="Gras.TLabel").pack(side="left")
        self.liste_marathons = ListeEntites(haut, largeur=48)
        self.liste_marathons.pack(side="left", padx=8)
        self.liste_marathons.bind("<<ComboboxSelected>>", lambda _e: self._recharger())

        ttk.Label(haut, text="Catégorie :", style="Gras.TLabel").pack(side="left", padx=(20, 6))
        for libelle, valeur in (("Tous", ""), ("Hommes", "M"), ("Femmes", "F")):
            ttk.Radiobutton(
                haut, text=libelle, value=valeur, variable=self._var_sexe,
                command=self._recharger,
            ).pack(side="left", padx=4)

        stats = ttk.LabelFrame(self, text="Statistiques de la course", padding=10)
        stats.pack(fill="x", pady=(12, 0))
        ttk.Label(stats, textvariable=self._var_stats, justify="left").pack(anchor="w")

        self.tableau = TableauDonnees(
            self,
            self.COLONNES,
            etiquettes={
                "or": COULEURS["or"],
                "argent": COULEURS["argent"],
                "bronze": COULEURS["bronze"],
            },
        )
        self.tableau.pack(fill="both", expand=True, pady=(12, 0))

    def refresh(self) -> None:
        marathons = self.app.marathons.lister()  # triés du plus récent au plus ancien
        premiere_fois = self.liste_marathons.identifiant() is None
        self.liste_marathons.charger(
            [(m.id_marathon, f"{m.libelle} — {m.ville}") for m in marathons]
        )
        if premiere_fois:
            # Par défaut : la dernière édition qui a déjà des résultats.
            for m in marathons:
                if self.app.participations.statistiques(m.id_marathon).termines:
                    self.liste_marathons.selectionner(m.id_marathon)
                    break
        self._recharger()

    @gerer_erreurs
    def _recharger(self) -> None:
        id_marathon = self.liste_marathons.identifiant()
        if id_marathon is None:
            self.tableau.charger([])
            self._var_stats.set("Aucun marathon enregistré.")
            return

        classement = self.app.participations.classement(id_marathon, self._var_sexe.get() or None)
        podium = {1: "or", 2: "argent", 3: "bronze"}
        self.tableau.charger(
            [
                (
                    p.id_participation,
                    (p.rang, p.num_dossard, p.nom_complet, p.sexe, p.temps_final),
                    podium.get(p.rang),
                )
                for p in classement
            ]
        )

        s = self.app.participations.statistiques(id_marathon)
        taux = f"{s.taux_arrivee} %" if s.taux_arrivee is not None else "—"
        self._var_stats.set(
            f"Inscrits : {s.total_inscrits}   |   Terminés : {s.termines}   |   "
            f"Abandons : {s.abandons}   |   Non-partants : {s.non_partants}   |   "
            f"En attente : {s.en_attente}\n"
            f"Meilleur temps : {s.meilleur_temps or '—'}   |   "
            f"Temps moyen : {s.temps_moyen or '—'}   |   Taux d'arrivée : {taux}"
        )
        self.notifier(f"{len(classement)} classé(s).")
