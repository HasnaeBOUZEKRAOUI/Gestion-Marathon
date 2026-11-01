"""Page « Historique » : toutes les participations d'un coureur."""

from tkinter import ttk

from ...models import Statut
from .base_page import BasePage, gerer_erreurs
from .theme import COULEURS
from .widgets import Carte, Colonne, ListeEntites, TableauDonnees, TuileStat

_ETIQUETTES_STATUT = {
    Statut.TERMINE.value: "termine",
    Statut.ABANDON.value: "abandon",
    Statut.NON_PARTANT.value: "non_partant",
}


class HistoriquePage(BasePage):
    TITRE = "Historique"
    SOUS_TITRE = "Le parcours sportif d'un coureur, édition après édition."
    ICONE = "↺"

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
        self._construire()
        self.refresh()

    def _construire(self) -> None:
        haut = ttk.Frame(self)
        haut.pack(fill="x")
        ttk.Label(haut, text="Coureur", style="Gras.TLabel").pack(side="left")
        self.liste_coureurs = ListeEntites(haut, largeur=50)
        self.liste_coureurs.pack(side="left", padx=10)
        self.liste_coureurs.bind("<<ComboboxSelected>>", lambda _e: self._recharger())

        rang = ttk.Frame(self)
        rang.pack(fill="x", pady=(14, 0))
        rang.columnconfigure((0, 1, 2), weight=1, uniform="tuile")
        modeles = (
            ("participations", "Participations", COULEURS["accent"]),
            ("terminees", "Courses terminées", COULEURS["vert"]),
            ("record", "Meilleur temps personnel", COULEURS["violet"]),
        )
        self.tuiles = {}
        for colonne, (cle, libelle, couleur) in enumerate(modeles):
            tuile = TuileStat(rang, libelle, couleur)
            tuile.grid(row=0, column=colonne, sticky="nsew",
                       padx=(0 if colonne == 0 else 6, 0 if colonne == 2 else 6))
            self.tuiles[cle] = tuile

        liste = Carte(self, "Courses du coureur")
        liste.pack(fill="both", expand=True, pady=(16, 0))
        self.tableau = TableauDonnees(
            liste.contenu,
            self.COLONNES,
            etiquettes={
                "termine": COULEURS["termine"],
                "abandon": COULEURS["abandon"],
                "non_partant": COULEURS["non_partant"],
            },
        )
        self.tableau.pack(fill="both", expand=True)

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
            for tuile in self.tuiles.values():
                tuile.definir("—")
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
        self.tuiles["participations"].definir(len(historique))
        self.tuiles["terminees"].definir(len(temps))
        self.tuiles["record"].definir(min(temps) if temps else "—")
        self.notifier(f"{len(historique)} participation(s) pour ce coureur.")
