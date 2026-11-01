"""Widgets réutilisables : cartes, tuiles de statistiques, tableau, liste d'entités."""

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Callable, Optional, Sequence, Tuple

from .theme import COULEURS

_STYLES_ETIQUETTE = {
    "normal": "Carte.TLabel",
    "gras": "CarteGras.TLabel",
    "discret": "CarteDiscret.TLabel",
    "titre": "CarteTitre.TLabel",
    "kpi": "Kpi.TLabel",
}


def etiquette(parent, texte: str = "", role: str = "normal", **options) -> ttk.Label:
    """Étiquette à fond blanc, à utiliser à l'intérieur d'une ``Carte``."""
    return ttk.Label(parent, text=texte, style=_STYLES_ETIQUETTE[role], **options)


class Carte(tk.Frame):
    """Bloc blanc à fine bordure, avec un titre facultatif.

    Le contenu se place dans ``carte.contenu`` (et non dans la carte elle-même).
    """

    def __init__(self, parent, titre: str = "", rembourrage: int = 18):
        super().__init__(parent, background=COULEURS["bordure"], padx=1, pady=1)
        self.corps = ttk.Frame(self, style="Carte.TFrame", padding=rembourrage)
        self.corps.pack(fill="both", expand=True)
        if titre:
            etiquette(self.corps, titre, "titre").pack(anchor="w", pady=(0, 12))
        self.contenu = ttk.Frame(self.corps, style="Carte.TFrame")
        self.contenu.pack(fill="both", expand=True)


class TuileStat(Carte):
    """Petite carte affichant un chiffre clé, avec un liseré de couleur."""

    def __init__(self, parent, libelle: str, couleur: Optional[str] = None):
        super().__init__(parent, rembourrage=16)
        tk.Frame(self, height=3, background=couleur or COULEURS["accent"]).pack(
            side="top", fill="x", before=self.corps
        )
        self._valeur = tk.StringVar(value="—")
        self._detail = tk.StringVar()
        etiquette(self.contenu, libelle, "discret").pack(anchor="w")
        etiquette(self.contenu, role="kpi", textvariable=self._valeur).pack(anchor="w", pady=(2, 0))
        etiquette(self.contenu, role="discret", textvariable=self._detail, wraplength=150,
                  justify="left").pack(anchor="w")

    def definir(self, valeur, detail: str = "") -> None:
        self._valeur.set(str(valeur))
        self._detail.set(detail)


@dataclass(frozen=True)
class Colonne:
    """Description d'une colonne de tableau."""

    cle: str
    titre: str
    largeur: int = 100
    ancre: str = "w"  # "w" (gauche), "center", "e" (droite)
    extensible: bool = False


class TableauDonnees(ttk.Frame):
    """Treeview avec barres de défilement, lignes alternées et rappel de sélection.

    Chaque ligne est un tuple ``(identifiant, valeurs[, etiquette])`` ; l'étiquette
    optionnelle colore la ligne (voir ``etiquettes``) et remplace la rayure alternée.
    """

    def __init__(
        self,
        parent,
        colonnes: Sequence[Colonne],
        hauteur: int = 10,
        on_select: Optional[Callable[[Optional[str]], None]] = None,
        etiquettes: Optional[dict] = None,
    ):
        super().__init__(parent, style="Carte.TFrame")
        self._on_select = on_select

        self.arbre = ttk.Treeview(
            self,
            columns=[c.cle for c in colonnes],
            show="headings",
            selectmode="browse",
            height=hauteur,
        )
        for colonne in colonnes:
            self.arbre.heading(colonne.cle, text=colonne.titre, anchor=colonne.ancre)
            self.arbre.column(
                colonne.cle,
                width=colonne.largeur,
                minwidth=40,
                anchor=colonne.ancre,
                stretch=colonne.extensible,
            )

        self.arbre.tag_configure("paire", background=COULEURS["ligne_paire"])
        self.arbre.tag_configure("impaire", background=COULEURS["ligne_impaire"])
        for nom, couleur in (etiquettes or {}).items():
            self.arbre.tag_configure(nom, background=couleur)

        barre_v = ttk.Scrollbar(self, orient="vertical", command=self.arbre.yview)
        self.arbre.configure(yscrollcommand=barre_v.set)
        self.arbre.grid(row=0, column=0, sticky="nsew")
        barre_v.grid(row=0, column=1, sticky="ns")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.arbre.bind("<<TreeviewSelect>>", self._selection_changee)

    # ------------------------------------------------------------------ données
    def charger(self, lignes: Sequence[tuple]) -> None:
        """Remplace le contenu du tableau (la sélection est perdue)."""
        self.arbre.delete(*self.arbre.get_children())
        for position, ligne in enumerate(lignes):
            identifiant, valeurs, *reste = ligne
            # Une étiquette de couleur (statut, podium) remplace la rayure alternée.
            if reste and reste[0]:
                etiquettes = [reste[0]]
            else:
                etiquettes = ["impaire" if position % 2 else "paire"]
            valeurs = tuple("" if v is None else v for v in valeurs)
            self.arbre.insert("", "end", iid=str(identifiant), values=valeurs, tags=etiquettes)

    def effectif(self) -> int:
        return len(self.arbre.get_children())

    # ---------------------------------------------------------------- sélection
    def identifiant_selectionne(self) -> Optional[str]:
        selection = self.arbre.selection()
        return selection[0] if selection else None

    def selectionner(self, identifiant) -> None:
        iid = str(identifiant)
        if self.arbre.exists(iid):
            self.arbre.selection_set(iid)
            self.arbre.focus(iid)
            self.arbre.see(iid)

    def deselectionner(self) -> None:
        self.arbre.selection_remove(*self.arbre.selection())

    def _selection_changee(self, _event=None) -> None:
        if self._on_select:
            self._on_select(self.identifiant_selectionne())


class ListeEntites(ttk.Combobox):
    """Liste déroulante en lecture seule associant un libellé à un identifiant."""

    def __init__(self, parent, largeur: int = 38, **options):
        super().__init__(parent, state="readonly", width=largeur, **options)
        self._identifiants: list = []

    def charger(self, elements: Sequence[Tuple[int, str]]) -> None:
        """Recharge la liste en conservant, si possible, l'élément sélectionné."""
        precedent = self.identifiant()
        self._identifiants = [identifiant for identifiant, _ in elements]
        self["values"] = [libelle for _, libelle in elements]
        if precedent in self._identifiants:
            self.current(self._identifiants.index(precedent))
        elif self._identifiants:
            self.current(0)
        else:
            self.set("")

    def identifiant(self) -> Optional[int]:
        position = self.current()
        if 0 <= position < len(self._identifiants):
            return self._identifiants[position]
        return None

    def selectionner(self, identifiant: int) -> None:
        if identifiant in self._identifiants:
            self.current(self._identifiants.index(identifiant))


def placer_champ(parent, ligne: int, colonne: int, libelle: str, widget, etendu: int = 1) -> None:
    """Place un libellé (fond blanc) et son champ côte à côte dans une grille."""
    etiquette(parent, libelle).grid(row=ligne, column=colonne, sticky="w", padx=(0, 8), pady=5)
    widget.grid(row=ligne, column=colonne + 1, columnspan=etendu, sticky="ew",
                padx=(0, 20), pady=5)


def zone_boutons(parent) -> ttk.Frame:
    """Barre horizontale (fond blanc) destinée à accueillir des boutons."""
    return ttk.Frame(parent, style="Carte.TFrame")


def desactiver(*widgets: tk.Widget) -> None:
    for widget in widgets:
        widget.state(["disabled"])


def activer(*widgets: tk.Widget) -> None:
    for widget in widgets:
        widget.state(["!disabled"])
