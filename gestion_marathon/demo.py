"""Jeu de données de démonstration."""

from .app import Application
from .models import Statut

_COUREURS = [
    ("Alaoui", "Sara", "F", "sara.alaoui@example.com", "1992-03-14"),
    ("Benjelloun", "Youssef", "M", "youssef.benjelloun@example.com", "1988-07-02"),
    ("El Fassi", "Imane", "F", "imane.elfassi@example.com", "1995-11-23"),
    ("Tazi", "Omar", "M", "omar.tazi@example.com", "1985-01-30"),
    ("Bennani", "Khadija", "F", "khadija.bennani@example.com", "1990-05-19"),
    ("Chraibi", "Mehdi", "M", "mehdi.chraibi@example.com", "1993-09-08"),
    ("Dupont", "Claire", "F", "claire.dupont@example.com", "1987-12-12"),
    ("Martin", "Lucas", "M", "lucas.martin@example.com", "1991-04-27"),
    ("Idrissi", "Nadia", "F", "nadia.idrissi@example.com", None),
    ("Lahlou", "Anas", "M", "anas.lahlou@example.com", "1998-06-16"),
]

# (nom, annee, date, ville)
_MARATHONS = [
    ("Marathon de Casablanca", 2025, "2025-10-26", "Casablanca"),
    ("Marathon de Casablanca", 2026, "2026-11-01", "Casablanca"),
]

# Édition 2025 : indices des coureurs -> (statut/temps)
_RESULTATS_2025 = {
    0: "03:45:12",
    1: "03:12:40",
    2: "04:05:33",
    3: "03:12:40",  # ex-æquo avec Youssef
    4: "ABANDON",
    5: "02:58:09",
    6: "04:31:55",
    7: "NON_PARTANT",
}


def charger_demo(app: Application) -> bool:
    """Remplit la base avec des données d'exemple.

    Retourne False (sans rien modifier) si la base contient déjà des coureurs.
    """
    if app.coureurs.lister():
        return False

    coureurs = [
        app.coureurs.creer(nom, prenom, sexe, email, naissance)
        for nom, prenom, sexe, email, naissance in _COUREURS
    ]
    marathons = [app.marathons.creer(*donnees) for donnees in _MARATHONS]
    edition_2025, edition_2026 = marathons

    # Édition 2025 : 8 inscrits avec résultats
    for indice, resultat in _RESULTATS_2025.items():
        participation = app.participations.inscrire(
            coureurs[indice].id_coureur, edition_2025.id_marathon
        )
        dossard = participation.num_dossard
        if resultat == "ABANDON":
            app.participations.changer_statut(
                edition_2025.id_marathon, dossard, Statut.ABANDON
            )
        elif resultat == "NON_PARTANT":
            app.participations.changer_statut(
                edition_2025.id_marathon, dossard, Statut.NON_PARTANT
            )
        else:
            app.participations.enregistrer_resultat(
                edition_2025.id_marathon, dossard, resultat
            )

    # Édition 2026 : inscriptions ouvertes (pas encore de résultats)
    for coureur in coureurs[:6] + coureurs[8:]:
        app.participations.inscrire(coureur.id_coureur, edition_2026.id_marathon)
    return True

