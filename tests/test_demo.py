from gestion_marathon.demo import charger_demo
from tests.base import BaseTestCase


class TestDemo(BaseTestCase):
    def test_chargement_unique(self):
        self.assertTrue(charger_demo(self.app))
        self.assertFalse(charger_demo(self.app))  # base déjà remplie : rien ne change
        self.assertEqual(len(self.app.coureurs.lister()), 10)
        self.assertEqual(len(self.app.marathons.lister()), 2)

    def test_classement_de_la_demo(self):
        charger_demo(self.app)
        edition_2025 = next(m for m in self.app.marathons.lister() if m.annee == 2025)
        classement = self.app.participations.classement(edition_2025.id_marathon)
        self.assertEqual(len(classement), 6)
        self.assertEqual(classement[0].temps_final, "02:58:09")
        self.assertEqual([p.rang for p in classement][1:3], [2, 2])  # ex-æquo
