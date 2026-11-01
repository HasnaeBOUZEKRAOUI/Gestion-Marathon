"""Page « Classement » : résultats triés d'un marathon et statistiques."""

import tkinter as tk
from tkinter import ttk

from .base_page import BasePage, gerer_erreurs
from .theme import COULEURS
from .widgets import Carte, Colonne, ListeEntites, TableauDonnees, TuileStat


class ClassementPage(BasePage):
    TITRE = "Classement"
    SOUS_TITRE = "Résultats officiels, podium et statistiques de la course."
    ICONE = "★"

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
        self._construire()
        self.refresh()

    def _construire(self) -> None:
        haut = ttk.Frame(self)
        haut.pack(fill="x")
        ttk.Label(haut, text="Marathon", style="Gras.TLabel").pack(side="left")
        self.liste_marathons = ListeEntites(haut, largeur=50)
        self.liste_marathons.pack(side="left", padx=10)
        self.liste_marathons.bind("<<ComboboxSelected>>", lambda _e: self._recharger())

        ttk.Label(haut, text="Catégorie", style="Gras.TLabel").pack(side="left", padx=(24, 8))
        for libelle, valeur in (("Tous", ""), ("Hommes", "M"), ("Femmes", "F")):
            ttk.Radiobutton(
                haut, text=libelle, value=valeur, variable=self._var_sexe,
                command=self._recharger,
            ).pack(side="left", padx=5)

        # Tuiles de statistiques
        rang = ttk.Frame(self)
        rang.pack(fill="x", pady=(14, 0))
        rang.columnconfigure(tuple(range(5)), weight=1, uniform="tuile")
        modeles = (
            ("inscrits", "Inscrits", COULEURS["accent"]),
            ("termines", "Terminés", COULEURS["vert"]),
            ("abandons", "Abandons", COULEURS["rouge"]),
            ("meilleur", "Meilleur temps", COULEURS["violet"]),
            ("moyen", "Temps moyen", COULEURS["orange"]),
        )
        self.tuiles = {}
        for colonne, (cle, libelle, couleur) in enumerate(modeles):
            tuile = TuileStat(rang, libelle, couleur)
            tuile.grid(row=0, column=colonne, sticky="nsew",
                       padx=(0 if colonne == 0 else 6, 0 if colonne == 4 else 6))
            self.tuiles[cle] = tuile

        liste = Carte(self, "Classement général")
        liste.pack(fill="both", expand=True, pady=(16, 0))
        self.tableau = TableauDonnees(
            liste.contenu,
            self.COLONNES,
            etiquettes={
                "or": COULEURS["or"],
                "argent": COULEURS["argent"],
                "bronze": COULEURS["bronze"],
            },
        )
        self.tableau.pack(fill="both", expand=True)

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
            for tuile in self.tuiles.values():
                tuile.definir("—")
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
        taux = f"{s.taux_arrivee} % d'arrivée" if s.taux_arrivee is not None else ""
        self.tuiles["inscrits"].definir(
            s.total_inscrits, f"dont {s.non_partants} non-partant(s), {s.en_attente} en attente"
        )
        self.tuiles["termines"].definir(s.termines, taux)
        self.tuiles["abandons"].definir(s.abandons)
        self.tuiles["meilleur"].definir(s.meilleur_temps or "—")
        self.tuiles["moyen"].definir(s.temps_moyen or "—")
        self.notifier(f"{len(classement)} classé(s).")
