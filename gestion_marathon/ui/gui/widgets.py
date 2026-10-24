"""Widgets réutilisables : tableau de données, liste déroulante d'entités."""

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Callable, Optional, Sequence, Tuple

from .theme import COULEURS


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

    Chaque ligne est un tuple ``(identifiant, valeurs[, etiquette])`` ;
    l'étiquette optionnelle sert à colorer la ligne (voir ``etiquettes``).
    """

    def __init__(
        self,
        parent,
        colonnes: Sequence[Colonne],
        hauteur: int = 10,
        on_select: Optional[Callable[[Optional[str]], None]] = None,
        etiquettes: Optional[dict] = None,
    ):
        super().__init__(parent)
        self._on_select = on_select

        self.arbre = ttk.Treeview(
            self,
            columns=[c.cle for c in colonnes],
            show="headings",
            selectmode="browse",
            height=hauteur,
        )
        for colonne in colonnes:
            self.arbre.heading(colonne.cle, text=colonne.titre)
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
        barre_h = ttk.Scrollbar(self, orient="horizontal", command=self.arbre.xview)
        self.arbre.configure(yscrollcommand=barre_v.set, xscrollcommand=barre_h.set)
        self.arbre.grid(row=0, column=0, sticky="nsew")
        barre_v.grid(row=0, column=1, sticky="ns")
        barre_h.grid(row=1, column=0, sticky="ew")
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
    """Place un libellé et son champ côte à côte dans une grille."""
    ttk.Label(parent, text=libelle).grid(
        row=ligne, column=colonne, sticky="w", padx=(0, 6), pady=4
    )
    widget.grid(row=ligne, column=colonne + 1, columnspan=etendu, sticky="ew", padx=(0, 16), pady=4)


def zone_boutons(parent) -> ttk.Frame:
    """Barre horizontale destinée à accueillir des boutons."""
    return ttk.Frame(parent)


def desactiver(*widgets: tk.Widget) -> None:
    for widget in widgets:
        widget.state(["disabled"])


def activer(*widgets: tk.Widget) -> None:
    for widget in widgets:
        widget.state(["!disabled"])
