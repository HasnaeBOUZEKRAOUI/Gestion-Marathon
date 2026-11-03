"""Barre de navigation verticale (menu latéral)."""

import tkinter as tk
from typing import Callable, Dict, List, Sequence, Tuple

from .theme import COULEURS

C = COULEURS


class ItemNavigation(tk.Frame):
    """Une entrée du menu : liseré d'état, icône et texte, avec effet de survol."""

    def __init__(self, parent, icone: str, texte: str, commande: Callable[[], None], polices):
        super().__init__(parent, background=C["sb_fond"], cursor="hand2")
        self._actif = False
        self._polices = polices
        self.indicateur = tk.Frame(self, width=4, background=C["sb_fond"])
        self.indicateur.pack(side="left", fill="y")
        self.lbl_icone = tk.Label(self, text=icone, width=3, font=polices["icone"],
                                  background=C["sb_fond"], foreground=C["sb_texte"])
        self.lbl_texte = tk.Label(self, text=texte, anchor="w", font=polices["nav"],
                                  background=C["sb_fond"], foreground=C["sb_texte"])
        self.lbl_icone.pack(side="left", pady=11)
        self.lbl_texte.pack(side="left", fill="x", expand=True)

        self._elements = (self, self.indicateur, self.lbl_icone, self.lbl_texte)
        for widget in (self, self.lbl_icone, self.lbl_texte):
            widget.bind("<Button-1>", lambda _e: commande())
            widget.bind("<Enter>", lambda _e: self._peindre(survol=True))
            widget.bind("<Leave>", self._sortie)

    def definir_actif(self, actif: bool) -> None:
        self._actif = actif
        self.lbl_texte.configure(font=self._polices["nav_gras" if actif else "nav"])
        self._peindre()

    def _sortie(self, _event) -> None:
        # Quitter le cadre pour entrer dans l'un de ses enfants n'est pas une vraie sortie.
        try:
            sous_le_curseur = self.winfo_containing(*self.winfo_pointerxy())
        except KeyError:
            sous_le_curseur = None
        if sous_le_curseur not in self._elements:
            self._peindre()

    def _peindre(self, survol: bool = False) -> None:
        if self._actif:
            fond, texte = C["sb_actif"], C["sb_texte_actif"]
        elif survol:
            fond, texte = C["sb_survol"], C["sb_texte_actif"]
        else:
            fond, texte = C["sb_fond"], C["sb_texte"]
        self.configure(background=fond)
        self.indicateur.configure(background=C["accent"] if self._actif else fond)
        for etiquette in (self.lbl_icone, self.lbl_texte):
            etiquette.configure(background=fond, foreground=texte)


class BarreLaterale(tk.Frame):
    """Menu vertical : marque, pages, actions secondaires et numéro de version."""

    LARGEUR = 240

    def __init__(
        self,
        parent,
        polices: Dict,
        pages: Sequence[Tuple[str, str]],
        actions: Sequence[Tuple[str, str, Callable[[], None]]],
        version: str,
        on_page: Callable[[int], None],
    ):
        super().__init__(parent, background=C["sb_fond"], width=self.LARGEUR)
        self.pack_propagate(False)
        self._items: List[ItemNavigation] = []

        # Marque
        marque = tk.Frame(self, background=C["sb_fond"])
        marque.pack(fill="x", padx=22, pady=(26, 22))
        tk.Label(marque, text="Runtrack", font=polices["marque"], anchor="w",
                 background=C["sb_fond"], foreground=C["sb_texte_actif"]).pack(fill="x")
        tk.Label(marque, text="Gestion des courses", font=polices["petit"], anchor="w",
                 background=C["sb_fond"], foreground=C["sb_discret"]).pack(fill="x")

        self._section("NAVIGATION", polices)
        for index, (icone, titre) in enumerate(pages):
            item = ItemNavigation(self, icone, titre, lambda i=index: on_page(i), polices)
            item.pack(fill="x")
            self._items.append(item)

        tk.Frame(self, background=C["sb_fond"]).pack(fill="both", expand=True)  # espaceur

        self._section("ACTIONS", polices)
        for icone, texte, commande in actions:
            ItemNavigation(self, icone, texte, commande, polices).pack(fill="x")
        tk.Label(self, text=f"Version {version}", font=polices["petit"],
                 background=C["sb_fond"], foreground=C["sb_discret"]).pack(pady=(14, 16))

    def _section(self, titre: str, polices) -> None:
        tk.Label(self, text=titre, font=polices["section"], anchor="w",
                 background=C["sb_fond"], foreground=C["sb_discret"]).pack(
            fill="x", padx=26, pady=(4, 6)
        )

    def activer(self, index: int) -> None:
        for position, item in enumerate(self._items):
            item.definir_actif(position == index)
