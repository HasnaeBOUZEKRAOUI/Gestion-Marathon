import unittest
from datetime import date

from gestion_marathon.exceptions import ValidationError
from gestion_marathon.utils import time_utils, validators


class TestTemps(unittest.TestCase):
    def test_normalisation(self):
        self.assertEqual(time_utils.normaliser_temps("3:45:12"), "03:45:12")
        self.assertEqual(time_utils.normaliser_temps(" 02:58:09 "), "02:58:09")

    def test_temps_invalides(self):
        for valeur in ["", "abc", "3:75:00", "24:00:00", "00:00:00", "3h45", None]:
            with self.subTest(valeur=valeur):
                with self.assertRaises(ValidationError):
                    time_utils.normaliser_temps(valeur)

    def test_conversions_et_moyenne(self):
        self.assertEqual(time_utils.vers_secondes("01:00:01"), 3601)
        self.assertEqual(time_utils.depuis_secondes(3601), "01:00:01")
        self.assertEqual(time_utils.temps_moyen(["03:00:00", "04:00:00"]), "03:30:00")
        self.assertIsNone(time_utils.temps_moyen([]))


class TestValidators(unittest.TestCase):
    def test_date_formats(self):
        self.assertEqual(validators.parser_date("2025-10-26"), date(2025, 10, 26))
        self.assertEqual(validators.parser_date("26/10/2025"), date(2025, 10, 26))
        with self.assertRaises(ValidationError):
            validators.parser_date("31/02/2025")

    def test_date_optionnelle(self):
        self.assertIsNone(validators.parser_date_optionnelle(""))
        self.assertIsNone(validators.parser_date_optionnelle(None))

    def test_email_et_sexe(self):
        self.assertEqual(validators.valider_email(" Sara@Mail.COM "), "sara@mail.com")
        self.assertEqual(validators.valider_sexe("f"), "F")
        for email in ["sans-arobase", "a@b", "a@@b.com"]:
            with self.assertRaises(ValidationError):
                validators.valider_email(email)
        with self.assertRaises(ValidationError):
            validators.valider_sexe("X")

    def test_texte(self):
        self.assertEqual(validators.valider_texte("  a   b ", "champ"), "a b")
        with self.assertRaises(ValidationError):
            validators.valider_texte("   ", "champ")
        with self.assertRaises(ValidationError):
            validators.valider_texte("x" * 51, "champ")
