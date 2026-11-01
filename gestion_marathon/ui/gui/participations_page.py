"""Page « Participations » : inscriptions, dossards, statuts et temps finaux."""

import tkinter as tk
from tkinter import ttk

from ...exceptions import ValidationError
from ...models import Statut
from .base_page import BasePage, gerer_erreurs
from .theme import COULEURS
from .widgets import (
    Carte,
    Colonne,
    ListeEntites,
    TableauDonnees,
    activer,
    desactiver,
    etiquette,
    zone_boutons,
)

_ETIQUETTES_STATUT = {
    Statut.TERMINE.value: "termine",
    Statut.ABANDON.value: "abandon",
    Statut.NON_PARTANT.value: "non_partant",
}


class ParticipationsPage(BasePage):
    TITRE = "Participations"
    SOUS_TITRE = "Inscrivez les coureurs, attribuez les dossards et saisissez les résultats."
    ICONE = "✎"

    COLONNES = (
        Colonne("dossard", "Dossard", 80, "center"),
        Colonne("nom", "Nom", 160),
        Colonne("prenom", "Prénom", 160),
        Colonne("sexe", "Sexe", 55, "center"),
        Colonne("statut", "Statut", 110, "center"),
        Colonne("temps", "Temps final", 110, "center", extensible=True),
    )

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self._participants = {}  # id_participation (str) -> ParticipantLigne
        self._var_dossard = tk.StringVar()
        self._var_temps = tk.StringVar()
        self._var_selection = tk.StringVar(value="Aucun participant sélectionné.")
        self._construire()
        self.refresh()

    # --------------------------------------------------------------- construction
    def _construire(self) -> None:
        haut = ttk.Frame(self)
        haut.pack(fill="x")
        ttk.Label(haut, text="Marathon", style="Gras.TLabel").pack(side="left")
        self.liste_marathons = ListeEntites(haut, largeur=50)
        self.liste_marathons.pack(side="left", padx=10)
        self.liste_marathons.bind("<<ComboboxSelected>>", lambda _e: self._changer_marathon())

        panneaux = ttk.Frame(self)
        panneaux.pack(fill="x", pady=(12, 0))
        panneaux.columnconfigure((0, 1), weight=1)

        # --- Inscription
        inscription = Carte(panneaux, "Inscrire un coureur")
        inscription.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        i = inscription.contenu
        i.columnconfigure(1, weight=1)
        etiquette(i, "Coureur *").grid(row=0, column=0, sticky="w", pady=5)
        self.liste_coureurs = ListeEntites(i, largeur=26)
        self.liste_coureurs.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        etiquette(i, "Dossard").grid(row=1, column=0, sticky="w", pady=5)
        ligne = ttk.Frame(i, style="Carte.TFrame")
        ligne.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        ttk.Entry(ligne, textvariable=self._var_dossard, width=8).pack(side="left")
        etiquette(i, "Dossard vide = attribution automatique.", "discret").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(2, 0)
        )
        self.btn_inscrire = ttk.Button(
            i, text="Inscrire", style="Accent.TButton", command=self.inscrire
        )
        self.btn_inscrire.grid(row=3, column=0, columnspan=2, sticky="w", pady=(12, 0))

        # --- Résultat / statut du participant sélectionné
        resultat = Carte(panneaux, "Participant sélectionné")
        resultat.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        r = resultat.contenu
        r.columnconfigure(2, weight=1)
        etiquette(r, role="gras", textvariable=self._var_selection).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )
        etiquette(r, "Temps final").grid(row=1, column=0, sticky="w")
        self.champ_temps = ttk.Entry(r, textvariable=self._var_temps, width=12)
        self.champ_temps.grid(row=1, column=1, sticky="w", padx=10)
        self.btn_temps = ttk.Button(
            r, text="Enregistrer", style="Accent.TButton", command=self.enregistrer_temps
        )
        self.btn_temps.grid(row=1, column=2, sticky="w")
        etiquette(
            r, "Format HH:MM:SS (ex. 03:45:12). Un autre statut efface le temps.", "discret"
        ).grid(row=2, column=0, columnspan=3, sticky="w", pady=(4, 0))
        statuts = zone_boutons(r)
        statuts.grid(row=3, column=0, columnspan=3, sticky="w", pady=(10, 0))
        self.btn_abandon = ttk.Button(
            statuts, text="Abandon", command=lambda: self.changer_statut(Statut.ABANDON)
        )
        self.btn_non_partant = ttk.Button(
            statuts, text="Non-partant", command=lambda: self.changer_statut(Statut.NON_PARTANT)
        )
        self.btn_inscrit = ttk.Button(
            statuts, text="Inscrit", command=lambda: self.changer_statut(Statut.INSCRIT)
        )
        self.btn_desinscrire = ttk.Button(
            r, text="Désinscrire", style="Danger.TButton", command=self.desinscrire
        )
        self.btn_desinscrire.grid(row=0, column=2, sticky="e", pady=(0, 8))
        for bouton in (self.btn_abandon, self.btn_non_partant, self.btn_inscrit):
            bouton.configure(style="Compact.TButton")
            bouton.pack(side="left", padx=(0, 6))
        self._boutons_participant = (
            self.btn_temps, self.btn_abandon, self.btn_non_partant,
            self.btn_inscrit, self.btn_desinscrire, self.champ_temps,
        )

        liste = Carte(self, "Participants du marathon")
        liste.pack(fill="both", expand=True, pady=(16, 0))
        self.tableau = TableauDonnees(
            liste.contenu,
            self.COLONNES,
            on_select=self._on_select,
            etiquettes={
                "termine": COULEURS["termine"],
                "abandon": COULEURS["abandon"],
                "non_partant": COULEURS["non_partant"],
            },
        )
        self.tableau.pack(fill="both", expand=True)
        self._maj_boutons()

    # --------------------------------------------------------------------- état
    def _maj_boutons(self) -> None:
        participant = self._participant_selectionne()
        if participant is None:
            desactiver(*self._boutons_participant)
            self._var_selection.set("Aucun participant sélectionné.")
        else:
            activer(*self._boutons_participant)
            self._var_selection.set(
                f"Dossard {participant.num_dossard} — {participant.nom_complet} "
                f"({participant.statut})"
            )

    def _participant_selectionne(self):
        return self._participants.get(self.tableau.identifiant_selectionne())

    def _marathon_choisi(self) -> int:
        identifiant = self.liste_marathons.identifiant()
        if identifiant is None:
            raise ValidationError("Aucun marathon sélectionné : créez-en un d'abord.")
        return identifiant

    # ------------------------------------------------------------------ données
    def refresh(self) -> None:
        self.liste_marathons.charger(
            [(m.id_marathon, f"{m.libelle} — {m.ville}") for m in self.app.marathons.lister()]
        )
        self.liste_coureurs.charger(
            [(c.id_coureur, f"{c.nom} {c.prenom} — {c.email}") for c in self.app.coureurs.lister()]
        )
        self._recharger_tableau()

    def _recharger_tableau(self, selectionner=None) -> None:
        identifiant = self.liste_marathons.identifiant()
        participants = self.app.participations.lister_participants(identifiant) if identifiant else []
        self._participants = {str(p.id_participation): p for p in participants}
        self.tableau.charger(
            [
                (
                    p.id_participation,
                    (p.num_dossard, p.nom, p.prenom, p.sexe, p.statut, p.temps_final),
                    _ETIQUETTES_STATUT.get(p.statut),
                )
                for p in participants
            ]
        )
        if selectionner is not None:
            self.tableau.selectionner(selectionner)
        self._maj_boutons()
        self.notifier(f"{len(participants)} participant(s) dans ce marathon.")

    @gerer_erreurs
    def _changer_marathon(self) -> None:
        self._recharger_tableau()
        self._var_temps.set("")

    def _on_select(self, _identifiant) -> None:
        participant = self._participant_selectionne()
        self._var_temps.set((participant.temps_final or "") if participant else "")
        self._maj_boutons()

    # ------------------------------------------------------------------ actions
    @gerer_erreurs
    def inscrire(self) -> None:
        id_marathon = self._marathon_choisi()
        id_coureur = self.liste_coureurs.identifiant()
        if id_coureur is None:
            raise ValidationError("Sélectionnez un coureur à inscrire.")
        dossard = self._var_dossard.get().strip() or None
        participation = self.app.participations.inscrire(id_coureur, id_marathon, dossard)
        self._var_dossard.set("")
        self._recharger_tableau()
        self._selectionner_dossard(participation.num_dossard)
        self.notifier(f"Inscription enregistrée (dossard {participation.num_dossard}).")

    @gerer_erreurs
    def enregistrer_temps(self) -> None:
        participant = self._participant_selectionne()
        if participant is None:
            return
        self.app.participations.enregistrer_resultat(
            self._marathon_choisi(), participant.num_dossard, self._var_temps.get()
        )
        self._recharger_tableau(selectionner=participant.id_participation)
        self._on_select(None)
        self.notifier(f"Temps enregistré pour {participant.nom_complet}.")

    @gerer_erreurs
    def changer_statut(self, statut: Statut) -> None:
        participant = self._participant_selectionne()
        if participant is None:
            return
        if participant.temps_final and not self.confirmer(
            f"Le temps enregistré ({participant.temps_final}) sera effacé. Continuer ?"
        ):
            return
        self.app.participations.changer_statut(
            self._marathon_choisi(), participant.num_dossard, statut
        )
        self._recharger_tableau(selectionner=participant.id_participation)
        self._on_select(None)
        self.notifier(f"Statut de {participant.nom_complet} : {statut.value}.")

    @gerer_erreurs
    def desinscrire(self) -> None:
        participant = self._participant_selectionne()
        if participant is None:
            return
        if not self.confirmer(
            f"Désinscrire {participant.nom_complet} (dossard {participant.num_dossard}) ?"
        ):
            return
        self.app.participations.desinscrire(self._marathon_choisi(), participant.num_dossard)
        self._recharger_tableau()
        self.notifier(f"{participant.nom_complet} a été désinscrit.")

    def _selectionner_dossard(self, dossard: int) -> None:
        for identifiant, participant in self._participants.items():
            if participant.num_dossard == dossard:
                self.tableau.selectionner(identifiant)
                return
