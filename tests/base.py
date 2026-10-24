"""Classe de base des tests : une application neuve sur base en mémoire."""

import unittest

from gestion_marathon.app import Application


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Application(":memory:")
        self.addCleanup(self.app.close)

    # Fabriques de données
    def coureur(self, nom="Alaoui", prenom="sara", sexe="F", email=None, naissance="1992-03-14"):
        email = email or f"{prenom}.{nom}@example.com".lower()
        return self.app.coureurs.creer(nom, prenom, sexe, email, naissance)

    def marathon(self, nom="Marathon Test", annee=2025, date="2025-10-26", ville="Casablanca"):
        return self.app.marathons.creer(nom, annee, date, ville)
