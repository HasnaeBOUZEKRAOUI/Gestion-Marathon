"""Thème visuel moderne : palette, polices et styles ttk.

Principe : un fond de page gris très clair, des « cartes » blanches pour regrouper
les contenus, une barre latérale sombre et une couleur d'accent bleue.
"""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
from typing import Dict

COULEURS = {
    # Pages et cartes
    "fond": "#f3f4f6",
    "carte": "#ffffff",
    "bordure": "#e5e7eb",
    "bordure_champ": "#d1d5db",
    "texte": "#111827",
    "texte_discret": "#6b7280",
    # Accent et danger
    "accent": "#2563eb",
    "accent_survol": "#1d4ed8",
    "accent_desactive": "#93b4f5",
    "danger": "#dc2626",
    "danger_survol": "#b91c1c",
    "danger_desactive": "#f1a5a5",
    # Barre latérale
    "sb_fond": "#0f172a",
    "sb_survol": "#1e293b",
    "sb_actif": "#1e293b",
    "sb_texte": "#94a3b8",
    "sb_texte_actif": "#ffffff",
    "sb_discret": "#64748b",
    # Tableaux
    "entete_tableau": "#f9fafb",
    "ligne_paire": "#ffffff",
    "ligne_impaire": "#f8fafc",
    "selection": "#dbeafe",
    # Lignes colorées (statuts, podium)
    "termine": "#dcfce7",
    "abandon": "#fee2e2",
    "non_partant": "#f1f5f9",
    "or": "#fef3c7",
    "argent": "#e5e7eb",
    "bronze": "#fde4cf",
    # Couleurs des tuiles de statistiques
    "violet": "#7c3aed",
    "orange": "#f59e0b",
    "vert": "#10b981",
    "rouge": "#ef4444",
    "gris": "#64748b",
}


def appliquer_theme(racine: tk.Tk) -> Dict[str, tkfont.Font]:
    """Configure ttk et retourne les polices utilisables par les widgets ``tk``."""
    style = ttk.Style(racine)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    c = COULEURS

    base = tkfont.nametofont("TkDefaultFont")
    base.configure(size=10)
    tkfont.nametofont("TkTextFont").configure(size=10)

    def derivee(**options) -> tkfont.Font:
        police = base.copy()
        police.configure(**options)
        return police

    polices = {
        "base": base,
        "gras": derivee(weight="bold"),
        "petit": derivee(size=9),
        "titre_page": derivee(weight="bold", size=20),
        "titre_carte": derivee(weight="bold", size=12),
        "kpi": derivee(weight="bold", size=19),
        "marque": derivee(weight="bold", size=17),
        "nav": derivee(size=11),
        "nav_gras": derivee(size=11, weight="bold"),
        "icone": derivee(size=14),
        "section": derivee(size=8, weight="bold"),
    }

    racine.configure(background=c["fond"])
    # Liste déroulante des combobox (widget tk classique, hors ttk)
    racine.option_add("*TCombobox*Listbox.background", c["carte"])
    racine.option_add("*TCombobox*Listbox.foreground", c["texte"])
    racine.option_add("*TCombobox*Listbox.selectBackground", c["selection"])
    racine.option_add("*TCombobox*Listbox.selectForeground", c["texte"])
    racine.option_add("*TCombobox*Listbox.relief", "flat")

    # ------------------------------------------------------------------ base
    style.configure(".", background=c["fond"], foreground=c["texte"],
                    bordercolor=c["bordure"], troughcolor=c["fond"], focuscolor=c["fond"])
    style.configure("TFrame", background=c["fond"])
    style.configure("Carte.TFrame", background=c["carte"])

    # --------------------------------------------------------------- étiquettes
    style.configure("TLabel", background=c["fond"], foreground=c["texte"])
    style.configure("Titre.TLabel", font=polices["titre_page"], foreground=c["texte"])
    style.configure("Discret.TLabel", foreground=c["texte_discret"])
    style.configure("Gras.TLabel", font=polices["gras"])
    style.configure("Statut.TLabel", foreground=c["texte_discret"], font=polices["petit"])

    style.configure("Carte.TLabel", background=c["carte"])
    style.configure("CarteGras.TLabel", background=c["carte"], font=polices["gras"])
    style.configure("CarteDiscret.TLabel", background=c["carte"], foreground=c["texte_discret"])
    style.configure("CarteTitre.TLabel", background=c["carte"], font=polices["titre_carte"])
    style.configure("Kpi.TLabel", background=c["carte"], font=polices["kpi"])

    style.configure("TRadiobutton", background=c["fond"])
    style.configure("Carte.TRadiobutton", background=c["carte"])
    style.map("TRadiobutton", background=[("active", c["fond"])])
    style.map("Carte.TRadiobutton", background=[("active", c["carte"])])

    # ------------------------------------------------------------------ boutons
    style.configure("TButton", padding=(12, 7), relief="solid", borderwidth=1,
                    background=c["carte"], bordercolor=c["bordure_champ"],
                    lightcolor=c["bordure_champ"], darkcolor=c["bordure_champ"])
    style.map("TButton",
              background=[("active", c["fond"]), ("disabled", c["fond"])],
              foreground=[("disabled", "#9ca3af")],
              bordercolor=[("disabled", c["bordure"])])
    style.configure("Compact.TButton", padding=(9, 6))
    for nom, normal, survol, desactive in (
        ("Accent", c["accent"], c["accent_survol"], c["accent_desactive"]),
        ("Danger", c["danger"], c["danger_survol"], c["danger_desactive"]),
    ):
        style.configure(f"{nom}.TButton", background=normal, foreground="white", relief="flat",
                        bordercolor=normal, lightcolor=normal, darkcolor=normal,
                        font=polices["gras"])
        style.map(f"{nom}.TButton",
                  background=[("disabled", desactive), ("active", survol)],
                  bordercolor=[("disabled", desactive), ("active", survol)],
                  lightcolor=[("disabled", desactive), ("active", survol)],
                  darkcolor=[("disabled", desactive), ("active", survol)],
                  foreground=[("disabled", "white")])

    # ------------------------------------------------------------------ champs
    champ = dict(fieldbackground="white", bordercolor=c["bordure_champ"],
                 lightcolor=c["bordure_champ"], darkcolor=c["bordure_champ"])
    focus = dict(bordercolor=[("focus", c["accent"])], lightcolor=[("focus", c["accent"])],
                 darkcolor=[("focus", c["accent"])])
    style.configure("TEntry", padding=6, **champ)
    style.map("TEntry", **focus)
    style.configure("TCombobox", padding=5, arrowcolor=c["texte_discret"],
                    background=c["carte"], **champ)
    style.map("TCombobox", fieldbackground=[("readonly", "white")],
              selectbackground=[("readonly", "white")],
              selectforeground=[("readonly", c["texte"])], **focus)

    # ---------------------------------------------------------------- tableaux
    style.configure("Treeview", background=c["carte"], fieldbackground=c["carte"],
                    rowheight=30, borderwidth=0, relief="flat")
    style.map("Treeview", background=[("selected", c["selection"])],
              foreground=[("selected", c["texte"])])
    style.configure("Treeview.Heading", background=c["entete_tableau"],
                    foreground=c["texte_discret"], font=polices["gras"], relief="flat",
                    padding=(8, 8), bordercolor=c["bordure"],
                    lightcolor=c["entete_tableau"], darkcolor=c["entete_tableau"])
    style.map("Treeview.Heading", background=[("active", c["bordure"])])

    # Barres de défilement fines, sans flèches
    for orientation, collage in (("Vertical", "ns"), ("Horizontal", "ew")):
        nom = f"{orientation}.TScrollbar"
        style.layout(nom, [(f"{orientation}.Scrollbar.trough", {
            "sticky": collage,
            "children": [(f"{orientation}.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})],
        })])
        style.configure(nom, troughcolor=c["carte"], background="#cbd5e1",
                        bordercolor=c["carte"], lightcolor="#cbd5e1", darkcolor="#cbd5e1",
                        gripcount=0, width=8, arrowsize=8)
        style.map(nom, background=[("active", "#94a3b8")])

    return polices
