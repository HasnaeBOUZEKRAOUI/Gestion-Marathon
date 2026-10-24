from datetime import date

from gestion_marathon.exceptions import (
    DuplicateError,
    NotFoundError,
    RelationError,
    ValidationError,
)
from tests.base import BaseTestCase


class TestCoureurService(BaseTestCase):
    def test_creation_normalise_les_donnees(self):
        c = self.app.coureurs.creer("  el fassi ", "jean-pierre", "m", "JP@Mail.com", "1990-05-01")
        self.assertIsNotNone(c.id_coureur)
        self.assertEqual(c.nom, "EL FASSI")
        self.assertEqual(c.prenom, "Jean-Pierre")
        self.assertEqual(c.sexe, "M")
        self.assertEqual(c.email, "jp@mail.com")
        self.assertEqual(c.date_naissance, date(1990, 5, 1))

    def test_lecture_apres_ecriture(self):
        c = self.coureur()
        relu = self.app.coureurs.obtenir(c.id_coureur)
        self.assertEqual(relu, c)

    def test_email_unique(self):
        self.coureur(email="a@b.com")
        with self.assertRaises(DuplicateError):
            self.coureur(nom="Autre", email="A@B.com")

    def test_validations(self):
        with self.assertRaises(ValidationError):
            self.app.coureurs.creer("", "Sara", "F", "a@b.com")
        with self.assertRaises(ValidationError):
            self.app.coureurs.creer("Nom", "Sara", "Z", "a@b.com")
        with self.assertRaises(ValidationError):
            self.app.coureurs.creer("Nom", "Sara", "F", "pas-un-email")
        with self.assertRaises(ValidationError):
            self.app.coureurs.creer("Nom", "Sara", "F", "a@b.com", "2999-01-01")

    def test_date_naissance_optionnelle(self):
        c = self.app.coureurs.creer("Nom", "Sara", "F", "a@b.com")
        self.assertIsNone(c.date_naissance)
        self.assertIsNone(c.age())

    def test_age(self):
        c = self.coureur(naissance="1990-06-15")
        self.assertEqual(c.age(date(2025, 6, 14)), 34)
        self.assertEqual(c.age(date(2025, 6, 15)), 35)

    def test_modification_partielle(self):
        c = self.coureur()
        m = self.app.coureurs.modifier(c.id_coureur, ville=None) if False else \
            self.app.coureurs.modifier(c.id_coureur, nom="nouveau")
        self.assertEqual(m.nom, "NOUVEAU")
        self.assertEqual(m.prenom, c.prenom)
        self.assertEqual(self.app.coureurs.obtenir(c.id_coureur).nom, "NOUVEAU")

    def test_modification_email_en_double(self):
        a = self.coureur(email="a@x.com")
        self.coureur(nom="B", email="b@x.com")
        with self.assertRaises(DuplicateError):
            self.app.coureurs.modifier(a.id_coureur, email="b@x.com")

    def test_recherche(self):
        self.coureur(nom="Alaoui", prenom="Sara")
        self.coureur(nom="Tazi", prenom="Omar", sexe="M")
        self.assertEqual(len(self.app.coureurs.rechercher("alao")), 1)
        self.assertEqual(len(self.app.coureurs.rechercher("")), 2)
        self.assertEqual(self.app.coureurs.rechercher("zzz"), [])

    def test_suppression(self):
        c = self.coureur()
        self.app.coureurs.supprimer(c.id_coureur)
        with self.assertRaises(NotFoundError):
            self.app.coureurs.obtenir(c.id_coureur)
        with self.assertRaises(NotFoundError):
            self.app.coureurs.supprimer(c.id_coureur)

    def test_suppression_refusee_si_participation(self):
        c, m = self.coureur(), self.marathon()
        self.app.participations.inscrire(c.id_coureur, m.id_marathon)
        with self.assertRaises(RelationError):
            self.app.coureurs.supprimer(c.id_coureur)
        self.assertEqual(self.app.coureurs.obtenir(c.id_coureur).id_coureur, c.id_coureur)
