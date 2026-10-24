"""Thème visuel de l'application (couleurs, polices, styles ttk)."""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

COULEURS = {
    "fond": "#f3f5f8",
    "carte": "#ffffff",
    "texte": "#1f2933",
    "texte_discret": "#6b7785",
    "accent": "#1f6feb",
    "accent_survol": "#1858bd",
    "danger": "#c93c37",
    "danger_survol": "#a32d29",
    "ligne_paire": "#ffffff",
    "ligne_impaire": "#f1f5fb",
    "selection": "#cfe0fc",
    # Couleurs de lignes selon le statut / le rang
    "termine": "#e6f6ea",
    "abandon": "#fdeaea",
    "non_partant": "#eceff3",
    "or": "#fff3c4",
    "argent": "#e9edf2",
    "bronze": "#f6e2d0",
}


def appliquer_theme(racine: tk.Tk) -> None:
    """Configure le thème ``clam`` et les styles personnalisés."""
    style = ttk.Style(racine)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    police_defaut = tkfont.nametofont("TkDefaultFont")
    police_defaut.configure(size=10)
    tkfont.nametofont("TkTextFont").configure(size=10)
    police_gras = police_defaut.copy()
    police_gras.configure(weight="bold")
    police_titre = police_defaut.copy()
    police_titre.configure(weight="bold", size=15)
    # Les polices doivent rester référencées pour ne pas être détruites.
    racine._polices = (police_gras, police_titre)

    c = COULEURS
    racine.configure(background=c["fond"])
    style.configure(".", background=c["fond"], foreground=c["texte"])
    style.configure("TFrame", background=c["fond"])
    style.configure("TLabel", background=c["fond"], foreground=c["texte"])
    style.configure("TLabelframe", background=c["fond"], bordercolor="#d5dbe3")
    style.configure(
        "TLabelframe.Label", background=c["fond"], foreground=c["accent"], font=police_gras
    )
    style.configure("TRadiobutton", background=c["fond"])
    style.configure("TNotebook", background=c["fond"], borderwidth=0)
    style.configure("TNotebook.Tab", padding=(16, 7), font=police_gras)
    style.map(
        "TNotebook.Tab",
        background=[("selected", c["carte"]), ("!selected", "#e1e6ed")],
        foreground=[("selected", c["accent"])],
    )

    style.configure("Titre.TLabel", font=police_titre, foreground=c["accent"])
    style.configure("Discret.TLabel", foreground=c["texte_discret"])
    style.configure("Gras.TLabel", font=police_gras)
    style.configure(
        "Statut.TLabel", background="#e1e6ed", foreground=c["texte_discret"], padding=(10, 4)
    )

    style.configure("TButton", padding=(12, 6))
    style.configure(
        "Accent.TButton", background=c["accent"], foreground="white", font=police_gras
    )
    style.map(
        "Accent.TButton",
        background=[("disabled", "#a9c3ef"), ("active", c["accent_survol"])],
        foreground=[("disabled", "white")],
    )
    style.configure(
        "Danger.TButton", background=c["danger"], foreground="white", font=police_gras
    )
    style.map(
        "Danger.TButton",
        background=[("disabled", "#e5a9a7"), ("active", c["danger_survol"])],
        foreground=[("disabled", "white")],
    )

    style.configure(
        "Treeview",
        background=c["carte"],
        fieldbackground=c["carte"],
        rowheight=26,
        bordercolor="#d5dbe3",
    )
    style.map("Treeview", background=[("selected", c["selection"])],
              foreground=[("selected", c["texte"])])
    style.configure("Treeview.Heading", font=police_gras, padding=(6, 5), background="#e1e6ed")
