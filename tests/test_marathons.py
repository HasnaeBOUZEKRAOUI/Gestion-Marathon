from datetime import date

from gestion_marathon.exceptions import (
    DuplicateError,
    NotFoundError,
    RelationError,
    ValidationError,
)
from tests.base import BaseTestCase


class TestMarathonService(BaseTestCase):
    def test_creation(self):
        m = self.marathon()
        self.assertEqual(m.date_course, date(2025, 10, 26))
        self.assertEqual(m.libelle, "Marathon Test 2025")
        self.assertEqual(self.app.marathons.obtenir(m.id_marathon), m)

    def test_annee_coherente_avec_la_date(self):
        with self.assertRaises(ValidationError):
            self.app.marathons.creer("M", 2024, "2025-10-26", "Rabat")

    def test_annee_non_numerique(self):
        with self.assertRaises(ValidationError):
            self.app.marathons.creer("M", "abcd", "2025-10-26", "Rabat")

    def test_edition_unique(self):
        self.marathon()
        with self.assertRaises(DuplicateError):
            self.marathon()
        # même événement, autre année : autorisé
        self.marathon(annee=2026, date="2026-10-25")

    def test_modification(self):
        m = self.marathon()
        modifie = self.app.marathons.modifier(m.id_marathon, ville="Rabat")
        self.assertEqual(modifie.ville, "Rabat")
        self.assertEqual(modifie.nom_evenement, m.nom_evenement)

    def test_modification_changement_annee_et_date(self):
        m = self.marathon()
        modifie = self.app.marathons.modifier(m.id_marathon, annee=2027, date_course="2027-03-01")
        self.assertEqual((modifie.annee, modifie.date_course), (2027, date(2027, 3, 1)))

    def test_liste_triee_par_date_decroissante(self):
        self.marathon(annee=2024, date="2024-10-27")
        self.marathon(annee=2026, date="2026-10-25")
        self.marathon(annee=2025, date="2025-10-26")
        annees = [m.annee for m in self.app.marathons.lister()]
        self.assertEqual(annees, [2026, 2025, 2024])

    def test_suppression(self):
        m = self.marathon()
        self.app.marathons.supprimer(m.id_marathon)
        with self.assertRaises(NotFoundError):
            self.app.marathons.obtenir(m.id_marathon)

    def test_suppression_refusee_si_participation(self):
        m, c = self.marathon(), self.coureur()
        self.app.participations.inscrire(c.id_coureur, m.id_marathon)
        with self.assertRaises(RelationError):
            self.app.marathons.supprimer(m.id_marathon)
