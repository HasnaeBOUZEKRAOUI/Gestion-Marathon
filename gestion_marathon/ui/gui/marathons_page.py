"""Page « Marathons » : gestion des éditions de course."""

import tkinter as tk
from tkinter import ttk

from ...utils.validators import parser_date
from .base_page import BasePage, gerer_erreurs
from .widgets import (
    Carte,
    Colonne,
    TableauDonnees,
    activer,
    desactiver,
    etiquette,
    placer_champ,
    zone_boutons,
)


class MarathonsPage(BasePage):
    TITRE = "Marathons"
    SOUS_TITRE = "Planifiez les éditions : nom, date et ville."
    ICONE = "⚑"

    COLONNES = (
        Colonne("id", "ID", 50, "center"),
        Colonne("nom", "Événement", 260, extensible=True),
        Colonne("annee", "Année", 70, "center"),
        Colonne("date", "Date de la course", 130, "center"),
        Colonne("ville", "Ville", 170),
    )

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self._id_selectionne = None
        self._vars = {cle: tk.StringVar() for cle in ("nom", "date", "ville")}
        self._construire()
        self.refresh()

    # --------------------------------------------------------------- construction
    def _construire(self) -> None:
        fiche = Carte(self, "Édition du marathon")
        fiche.pack(fill="x")
        f = fiche.contenu
        for colonne in (1, 3):
            f.columnconfigure(colonne, weight=1)

        placer_champ(f, 0, 0, "Événement *", ttk.Entry(f, textvariable=self._vars["nom"]), etendu=3)
        placer_champ(f, 1, 0, "Date *", ttk.Entry(f, textvariable=self._vars["date"]))
        placer_champ(f, 1, 2, "Ville *", ttk.Entry(f, textvariable=self._vars["ville"]))
        etiquette(
            f,
            "Date : AAAA-MM-JJ ou JJ/MM/AAAA. L'année de l'édition est déduite de la date.",
            "discret",
        ).grid(row=2, column=0, columnspan=4, sticky="w", pady=(2, 0))

        boutons = zone_boutons(f)
        boutons.grid(row=3, column=0, columnspan=4, sticky="w", pady=(12, 0))
        self.btn_ajouter = ttk.Button(
            boutons, text="Ajouter", style="Accent.TButton", command=self.ajouter
        )
        self.btn_modifier = ttk.Button(boutons, text="Modifier", command=self.modifier)
        self.btn_supprimer = ttk.Button(
            boutons, text="Supprimer", style="Danger.TButton", command=self.supprimer
        )
        self.btn_nouveau = ttk.Button(boutons, text="Nouveau / Vider", command=self.nouveau)
        for bouton in (self.btn_ajouter, self.btn_modifier, self.btn_supprimer, self.btn_nouveau):
            bouton.pack(side="left", padx=(0, 8))

        liste = Carte(self, "Éditions enregistrées")
        liste.pack(fill="both", expand=True, pady=(16, 0))
        self.tableau = TableauDonnees(liste.contenu, self.COLONNES, on_select=self._on_select)
        self.tableau.pack(fill="both", expand=True)
        self._maj_boutons()

    # --------------------------------------------------------------------- état
    def _maj_boutons(self) -> None:
        if self._id_selectionne is None:
            desactiver(self.btn_modifier, self.btn_supprimer)
            activer(self.btn_ajouter)
        else:
            activer(self.btn_modifier, self.btn_supprimer)
            desactiver(self.btn_ajouter)

    def _lire_formulaire(self) -> dict:
        d = {cle: variable.get() for cle, variable in self._vars.items()}
        d["annee"] = parser_date(d["date"], "date de la course").year
        return d

    # ------------------------------------------------------------------ données
    def refresh(self) -> None:
        marathons = self.app.marathons.lister()
        self.tableau.charger(
            [
                (
                    m.id_marathon,
                    (m.id_marathon, m.nom_evenement, m.annee, m.date_course.isoformat(), m.ville),
                )
                for m in marathons
            ]
        )
        if self._id_selectionne is not None:
            self.tableau.selectionner(self._id_selectionne)
        self.notifier(f"{len(marathons)} édition(s) enregistrée(s).")

    @gerer_erreurs
    def _on_select(self, identifiant) -> None:
        if identifiant is None:
            return
        marathon = self.app.marathons.obtenir(int(identifiant))
        self._id_selectionne = marathon.id_marathon
        self._vars["nom"].set(marathon.nom_evenement)
        self._vars["date"].set(marathon.date_course.isoformat())
        self._vars["ville"].set(marathon.ville)
        self._maj_boutons()

    # ------------------------------------------------------------------ actions
    def nouveau(self) -> None:
        self._id_selectionne = None
        self.tableau.deselectionner()
        for variable in self._vars.values():
            variable.set("")
        self._maj_boutons()

    @gerer_erreurs
    def ajouter(self) -> None:
        d = self._lire_formulaire()
        marathon = self.app.marathons.creer(d["nom"], d["annee"], d["date"], d["ville"])
        self.nouveau()
        self.refresh()
        self.tableau.selectionner(marathon.id_marathon)
        self._on_select(str(marathon.id_marathon))
        self.notifier(f"Marathon ajouté : {marathon.libelle}.")

    @gerer_erreurs
    def modifier(self) -> None:
        if self._id_selectionne is None:
            return
        d = self._lire_formulaire()
        marathon = self.app.marathons.modifier(
            self._id_selectionne,
            nom_evenement=d["nom"],
            annee=d["annee"],
            date_course=d["date"],
            ville=d["ville"],
        )
        self.refresh()
        self._on_select(str(marathon.id_marathon))
        self.notifier(f"Marathon modifié : {marathon.libelle}.")

    @gerer_erreurs
    def supprimer(self) -> None:
        if self._id_selectionne is None:
            return
        marathon = self.app.marathons.obtenir(self._id_selectionne)
        if not self.confirmer(f"Supprimer définitivement « {marathon.libelle} » ?"):
            return
        self.app.marathons.supprimer(marathon.id_marathon)
        self.nouveau()
        self.refresh()
        self.notifier(f"Marathon supprimé : {marathon.libelle}.")
