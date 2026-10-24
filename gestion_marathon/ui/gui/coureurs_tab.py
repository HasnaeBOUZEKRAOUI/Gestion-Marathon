"""Onglet « Coureurs » : fiche (ajout / modification / suppression) et recherche."""

import tkinter as tk
from tkinter import ttk

from ...config import SEXES
from .base_tab import BaseTab, gerer_erreurs
from .widgets import Colonne, TableauDonnees, activer, desactiver, placer_champ, zone_boutons


class CoureursTab(BaseTab):
    TITRE = "Coureurs"

    COLONNES = (
        Colonne("id", "ID", 50, "center"),
        Colonne("nom", "Nom", 140),
        Colonne("prenom", "Prénom", 140),
        Colonne("sexe", "Sexe", 55, "center"),
        Colonne("naissance", "Naissance", 100, "center"),
        Colonne("age", "Âge", 55, "center"),
        Colonne("email", "Email", 260, extensible=True),
    )

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self._id_selectionne = None
        self._vars = {cle: tk.StringVar() for cle in ("nom", "prenom", "sexe", "naissance", "email")}
        self._var_recherche = tk.StringVar()
        self._construire()
        self._vars["sexe"].set(SEXES[0])
        self._var_recherche.trace_add("write", lambda *_: self.refresh())
        self.refresh()

    # --------------------------------------------------------------- construction
    def _construire(self) -> None:
        fiche = ttk.LabelFrame(self, text="Fiche coureur", padding=12)
        fiche.pack(fill="x")
        for colonne in (1, 3):
            fiche.columnconfigure(colonne, weight=1)

        placer_champ(fiche, 0, 0, "Nom *", ttk.Entry(fiche, textvariable=self._vars["nom"]))
        placer_champ(fiche, 0, 2, "Prénom *", ttk.Entry(fiche, textvariable=self._vars["prenom"]))
        placer_champ(
            fiche, 1, 0, "Sexe *",
            ttk.Combobox(fiche, textvariable=self._vars["sexe"], values=SEXES,
                         state="readonly", width=6),
        )
        placer_champ(
            fiche, 1, 2, "Naissance",
            ttk.Entry(fiche, textvariable=self._vars["naissance"]),
        )
        placer_champ(
            fiche, 2, 0, "Email *",
            ttk.Entry(fiche, textvariable=self._vars["email"]), etendu=3,
        )
        ttk.Label(
            fiche, text="Date : AAAA-MM-JJ ou JJ/MM/AAAA (facultative)", style="Discret.TLabel"
        ).grid(row=3, column=0, columnspan=4, sticky="w", pady=(2, 0))

        boutons = zone_boutons(fiche)
        boutons.grid(row=4, column=0, columnspan=4, sticky="w", pady=(10, 0))
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

        recherche = ttk.Frame(self)
        recherche.pack(fill="x", pady=(14, 6))
        ttk.Label(recherche, text="Rechercher :", style="Gras.TLabel").pack(side="left")
        ttk.Entry(recherche, textvariable=self._var_recherche, width=34).pack(
            side="left", padx=8
        )
        ttk.Label(recherche, text="(nom, prénom ou email)", style="Discret.TLabel").pack(
            side="left"
        )

        self.tableau = TableauDonnees(self, self.COLONNES, on_select=self._on_select)
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

    def _vider_formulaire(self) -> None:
        for cle, variable in self._vars.items():
            variable.set(SEXES[0] if cle == "sexe" else "")

    def _lire_formulaire(self) -> dict:
        return {cle: variable.get() for cle, variable in self._vars.items()}

    # ------------------------------------------------------------------ données
    def refresh(self) -> None:
        coureurs = self.app.coureurs.rechercher(self._var_recherche.get())
        self.tableau.charger(
            [
                (
                    c.id_coureur,
                    (
                        c.id_coureur,
                        c.nom,
                        c.prenom,
                        c.sexe,
                        c.date_naissance.isoformat() if c.date_naissance else "",
                        c.age() if c.date_naissance else "",
                        c.email,
                    ),
                )
                for c in coureurs
            ]
        )
        if self._id_selectionne is not None:
            self.tableau.selectionner(self._id_selectionne)
        self.notifier(f"{len(coureurs)} coureur(s) affiché(s).")

    @gerer_erreurs
    def _on_select(self, identifiant) -> None:
        if identifiant is None:
            return
        coureur = self.app.coureurs.obtenir(int(identifiant))
        self._id_selectionne = coureur.id_coureur
        self._vars["nom"].set(coureur.nom)
        self._vars["prenom"].set(coureur.prenom)
        self._vars["sexe"].set(coureur.sexe)
        self._vars["naissance"].set(coureur.date_naissance.isoformat() if coureur.date_naissance else "")
        self._vars["email"].set(coureur.email)
        self._maj_boutons()

    # ------------------------------------------------------------------ actions
    def nouveau(self) -> None:
        self._id_selectionne = None
        self.tableau.deselectionner()
        self._vider_formulaire()
        self._maj_boutons()

    @gerer_erreurs
    def ajouter(self) -> None:
        d = self._lire_formulaire()
        coureur = self.app.coureurs.creer(
            d["nom"], d["prenom"], d["sexe"], d["email"], d["naissance"]
        )
        self.nouveau()
        self.refresh()
        self.tableau.selectionner(coureur.id_coureur)
        self._on_select(str(coureur.id_coureur))
        self.notifier(f"Coureur ajouté : {coureur.nom_complet}.")

    @gerer_erreurs
    def modifier(self) -> None:
        if self._id_selectionne is None:
            return
        d = self._lire_formulaire()
        coureur = self.app.coureurs.modifier(
            self._id_selectionne,
            nom=d["nom"],
            prenom=d["prenom"],
            sexe=d["sexe"],
            email=d["email"],
            date_naissance=d["naissance"],  # "" efface la date
        )
        self.refresh()
        self._on_select(str(coureur.id_coureur))
        self.notifier(f"Coureur modifié : {coureur.nom_complet}.")

    @gerer_erreurs
    def supprimer(self) -> None:
        if self._id_selectionne is None:
            return
        coureur = self.app.coureurs.obtenir(self._id_selectionne)
        if not self.confirmer(f"Supprimer définitivement {coureur.nom_complet} ?"):
            return
        self.app.coureurs.supprimer(coureur.id_coureur)
        self.nouveau()
        self.refresh()
        self.notifier(f"Coureur supprimé : {coureur.nom_complet}.")
