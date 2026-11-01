"""Page « Tableau de bord » : chiffres clés, prochaine course et podium."""

import tkinter as tk
from datetime import date
from tkinter import ttk

from .base_page import BasePage, gerer_erreurs
from .theme import COULEURS
from .widgets import Carte, TuileStat, etiquette


def _rang_lisible(rang: int) -> str:
    return "1er" if rang == 1 else f"{rang}e"


def _echeance(jours: int) -> str:
    if jours == 0:
        return "C'est aujourd'hui !"
    if jours == 1:
        return "Demain"
    return f"Dans {jours} jours"


class TableauBordPage(BasePage):
    TITRE = "Tableau de bord"
    SOUS_TITRE = "Vue d'ensemble de vos courses."
    ICONE = "⌂"

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self._vars = {
            nom: tk.StringVar()
            for nom in ("p_nom", "p_detail", "p_echeance", "p_inscrits",
                        "d_nom", "d_detail", "d_stats")
        }
        self._podium = [
            {cle: tk.StringVar() for cle in ("rang", "nom", "temps")} for _ in range(3)
        ]
        self._construire()
        self.refresh()

    # --------------------------------------------------------------- construction
    def _construire(self) -> None:
        rang = ttk.Frame(self)
        rang.pack(fill="x")
        rang.columnconfigure((0, 1, 2, 3), weight=1, uniform="tuile")
        modeles = (
            ("coureurs", "Coureurs", COULEURS["accent"]),
            ("marathons", "Marathons", COULEURS["violet"]),
            ("participations", "Participations", COULEURS["orange"]),
            ("termines", "Courses terminées", COULEURS["vert"]),
        )
        self.tuiles = {}
        for colonne, (cle, libelle, couleur) in enumerate(modeles):
            tuile = TuileStat(rang, libelle, couleur)
            tuile.grid(row=0, column=colonne, sticky="nsew",
                       padx=(0 if colonne == 0 else 7, 0 if colonne == 3 else 7))
            self.tuiles[cle] = tuile

        bas = ttk.Frame(self)
        bas.pack(fill="x", pady=(16, 0))
        bas.columnconfigure((0, 1), weight=1, uniform="carte")

        # --- Prochaine course
        prochaine = Carte(bas, "Prochaine course")
        prochaine.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        p = prochaine.contenu
        etiquette(p, role="gras", textvariable=self._vars["p_nom"]).pack(anchor="w")
        etiquette(p, role="discret", textvariable=self._vars["p_detail"]).pack(anchor="w", pady=2)
        etiquette(p, role="titre", textvariable=self._vars["p_echeance"]).pack(
            anchor="w", pady=(14, 2)
        )
        etiquette(p, textvariable=self._vars["p_inscrits"]).pack(anchor="w")

        # --- Dernière course avec résultats + podium
        derniere = Carte(bas, "Dernière course avec résultats")
        derniere.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        d = derniere.contenu
        etiquette(d, role="gras", textvariable=self._vars["d_nom"]).pack(anchor="w")
        etiquette(d, role="discret", textvariable=self._vars["d_detail"]).pack(anchor="w", pady=2)
        etiquette(d, textvariable=self._vars["d_stats"]).pack(anchor="w", pady=(2, 12))

        grille = ttk.Frame(d, style="Carte.TFrame")
        grille.pack(fill="x")
        grille.columnconfigure(1, weight=1)
        for ligne, variables in enumerate(self._podium):
            etiquette(grille, role="gras", textvariable=variables["rang"], width=5).grid(
                row=ligne, column=0, sticky="w", pady=4
            )
            etiquette(grille, textvariable=variables["nom"]).grid(row=ligne, column=1, sticky="w")
            etiquette(grille, role="gras", textvariable=variables["temps"]).grid(
                row=ligne, column=2, sticky="e"
            )

    # ------------------------------------------------------------------ données
    @gerer_erreurs
    def refresh(self) -> None:
        service = self.app.participations
        marathons = self.app.marathons.lister()  # du plus récent au plus ancien
        stats = {m.id_marathon: service.statistiques(m.id_marathon) for m in marathons}

        self.tuiles["coureurs"].definir(len(self.app.coureurs.lister()))
        self.tuiles["marathons"].definir(len(marathons))
        self.tuiles["participations"].definir(sum(s.total_inscrits for s in stats.values()))
        self.tuiles["termines"].definir(sum(s.termines for s in stats.values()))

        self._afficher_prochaine(marathons, stats)
        self._afficher_derniere(marathons, stats)
        self.notifier("Tableau de bord actualisé.")

    def _afficher_prochaine(self, marathons, stats) -> None:
        v = self._vars
        a_venir = [m for m in marathons if m.date_course >= date.today()]
        if not a_venir:
            v["p_nom"].set("Aucune course à venir.")
            v["p_detail"].set("Ajoutez une édition dans la page « Marathons ».")
            v["p_echeance"].set("")
            v["p_inscrits"].set("")
            return
        m = min(a_venir, key=lambda x: x.date_course)
        v["p_nom"].set(m.libelle)
        v["p_detail"].set(f"{m.date_course.isoformat()} · {m.ville}")
        v["p_echeance"].set(_echeance((m.date_course - date.today()).days))
        v["p_inscrits"].set(f"{stats[m.id_marathon].total_inscrits} coureur(s) inscrit(s)")

    def _afficher_derniere(self, marathons, stats) -> None:
        v = self._vars
        derniere = next((m for m in marathons if stats[m.id_marathon].termines), None)
        if derniere is None:
            v["d_nom"].set("Aucun résultat enregistré.")
            v["d_detail"].set("Saisissez des temps dans la page « Participations ».")
            v["d_stats"].set("")
            for variables in self._podium:
                for variable in variables.values():
                    variable.set("")
            return
        s = stats[derniere.id_marathon]
        v["d_nom"].set(derniere.libelle)
        v["d_detail"].set(f"{derniere.date_course.isoformat()} · {derniere.ville}")
        v["d_stats"].set(
            f"{s.termines} arrivée(s) · {s.abandons} abandon(s) · "
            f"temps moyen {s.temps_moyen or '—'}"
        )
        podium = self.app.participations.classement(derniere.id_marathon)[:3]
        for position, variables in enumerate(self._podium):
            if position < len(podium):
                p = podium[position]
                variables["rang"].set(_rang_lisible(p.rang))
                variables["nom"].set(p.nom_complet)
                variables["temps"].set(p.temps_final)
            else:
                for variable in variables.values():
                    variable.set("")
