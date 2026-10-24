from gestion_marathon.exceptions import (
    DuplicateError,
    NotFoundError,
    RelationError,
    ValidationError,
)
from gestion_marathon.models import Statut
from tests.base import BaseTestCase


class TestParticipationService(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.m = self.marathon()
        self.c1 = self.coureur("Alaoui", "Sara", "F")
        self.c2 = self.coureur("Tazi", "Omar", "M")
        self.c3 = self.coureur("Idrissi", "Nadia", "F")

    def inscrire(self, coureur, dossard=None):
        return self.app.participations.inscrire(coureur.id_coureur, self.m.id_marathon, dossard)

    # ----------------------------------------------------------------- inscription
    def test_dossards_automatiques_consecutifs(self):
        self.assertEqual(self.inscrire(self.c1).num_dossard, 1)
        self.assertEqual(self.inscrire(self.c2).num_dossard, 2)

    def test_dossard_explicite(self):
        self.assertEqual(self.inscrire(self.c1, "100").num_dossard, 100)
        self.assertEqual(self.inscrire(self.c2).num_dossard, 101)

    def test_dossard_invalide(self):
        for valeur in ("abc", "0", "-3"):
            with self.assertRaises(ValidationError):
                self.inscrire(self.c1, valeur)

    def test_dossard_deja_attribue(self):
        self.inscrire(self.c1, 7)
        with self.assertRaises(DuplicateError):
            self.inscrire(self.c2, 7)

    def test_double_inscription_refusee(self):
        self.inscrire(self.c1)
        with self.assertRaises(DuplicateError):
            self.inscrire(self.c1)

    def test_coureur_ou_marathon_inconnu(self):
        with self.assertRaises(NotFoundError):
            self.app.participations.inscrire(999, self.m.id_marathon)
        with self.assertRaises(NotFoundError):
            self.app.participations.inscrire(self.c1.id_coureur, 999)

    # ------------------------------------------------------------ statuts / temps
    def test_resultat_passe_en_termine(self):
        p = self.inscrire(self.c1)
        p = self.app.participations.enregistrer_resultat(self.m.id_marathon, p.num_dossard, "3:45:12")
        self.assertEqual(p.statut, Statut.TERMINE)
        self.assertEqual(p.temps_final, "03:45:12")

    def test_temps_invalide(self):
        p = self.inscrire(self.c1)
        for temps in ("", "abc", "03:61:00", "25:00:00", "00:00:00"):
            with self.assertRaises(ValidationError):
                self.app.participations.enregistrer_resultat(
                    self.m.id_marathon, p.num_dossard, temps
                )

    def test_abandon_efface_le_temps(self):
        p = self.inscrire(self.c1)
        self.app.participations.enregistrer_resultat(self.m.id_marathon, p.num_dossard, "04:00:00")
        p = self.app.participations.changer_statut(
            self.m.id_marathon, p.num_dossard, Statut.ABANDON
        )
        self.assertIsNone(p.temps_final)
        self.assertEqual(p.statut, Statut.ABANDON)

    def test_pas_de_temps_pour_un_abandon(self):
        p = self.inscrire(self.c1)
        self.app.participations.changer_statut(self.m.id_marathon, p.num_dossard, Statut.ABANDON)
        with self.assertRaises(ValidationError):
            self.app.participations.enregistrer_resultat(
                self.m.id_marathon, p.num_dossard, "04:00:00"
            )

    def test_statut_termine_exige_un_temps(self):
        p = self.inscrire(self.c1)
        with self.assertRaises(ValidationError):
            self.app.participations.changer_statut(
                self.m.id_marathon, p.num_dossard, Statut.TERMINE
            )

    def test_desinscription(self):
        p = self.inscrire(self.c1)
        self.app.participations.desinscrire(self.m.id_marathon, p.num_dossard)
        self.assertEqual(self.app.participations.lister_participants(self.m.id_marathon), [])

    def test_desinscription_refusee_si_resultat(self):
        p = self.inscrire(self.c1)
        self.app.participations.enregistrer_resultat(self.m.id_marathon, p.num_dossard, "04:00:00")
        with self.assertRaises(ValidationError):
            self.app.participations.desinscrire(self.m.id_marathon, p.num_dossard)

    # -------------------------------------------------------- classement / stats
    def _courir(self, coureur, temps):
        p = self.inscrire(coureur)
        self.app.participations.enregistrer_resultat(self.m.id_marathon, p.num_dossard, temps)

    def test_classement_trie_avec_ex_aequo(self):
        self._courir(self.c1, "03:30:00")
        self._courir(self.c2, "03:10:00")
        self._courir(self.c3, "03:30:00")
        classement = self.app.participations.classement(self.m.id_marathon)
        self.assertEqual([p.rang for p in classement], [1, 2, 2])
        self.assertEqual(classement[0].nom, "TAZI")

    def test_classement_par_sexe(self):
        self._courir(self.c1, "03:30:00")
        self._courir(self.c2, "03:10:00")
        femmes = self.app.participations.classement(self.m.id_marathon, "F")
        self.assertEqual([p.nom for p in femmes], ["ALAOUI"])
        self.assertEqual(femmes[0].rang, 1)

    def test_classement_exclut_abandons_et_inscrits(self):
        self._courir(self.c1, "03:30:00")
        p = self.inscrire(self.c2)
        self.app.participations.changer_statut(self.m.id_marathon, p.num_dossard, Statut.ABANDON)
        self.inscrire(self.c3)
        self.assertEqual(len(self.app.participations.classement(self.m.id_marathon)), 1)

    def test_statistiques(self):
        self._courir(self.c1, "03:00:00")
        self._courir(self.c2, "04:00:00")
        p = self.inscrire(self.c3)
        self.app.participations.changer_statut(self.m.id_marathon, p.num_dossard, Statut.ABANDON)
        s = self.app.participations.statistiques(self.m.id_marathon)
        self.assertEqual((s.total_inscrits, s.termines, s.abandons), (3, 2, 1))
        self.assertEqual(s.meilleur_temps, "03:00:00")
        self.assertEqual(s.temps_moyen, "03:30:00")
        self.assertEqual(s.taux_arrivee, 66.7)

    def test_historique_du_coureur(self):
        autre = self.app.marathons.creer("Marathon Test", 2026, "2026-11-01", "Casablanca")
        self._courir(self.c1, "03:30:00")
        self.app.participations.inscrire(self.c1.id_coureur, autre.id_marathon)
        historique = self.app.participations.historique_coureur(self.c1.id_coureur)
        self.assertEqual([h.annee for h in historique], [2026, 2025])  # plus récent d'abord

    # ----------------------------------------------------------------- intégrité
    def test_suppression_refusee_si_participation_liee(self):
        self.inscrire(self.c1)
        with self.assertRaises(RelationError):
            self.app.coureurs.supprimer(self.c1.id_coureur)
        with self.assertRaises(RelationError):
            self.app.marathons.supprimer(self.m.id_marathon)
