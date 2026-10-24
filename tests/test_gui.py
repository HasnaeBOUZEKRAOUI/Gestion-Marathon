"""Tests de l'interface Tkinter (ignorés si Tkinter ou un écran sont indisponibles)."""

import unittest
from unittest import mock

from gestion_marathon.app import Application

try:
    import tkinter

    from gestion_marathon.ui.gui import MainWindow
    from gestion_marathon.ui.gui import base_tab

    _racine = tkinter.Tk()
    _racine.destroy()
    GUI_DISPONIBLE = True
except Exception:  # noqa: BLE001 - ImportError ou TclError (pas d'affichage)
    GUI_DISPONIBLE = False


@unittest.skipUnless(GUI_DISPONIBLE, "Tkinter ou affichage indisponible")
class TestInterface(unittest.TestCase):
    def setUp(self):
        self.app = Application(":memory:")
        self.fenetre = MainWindow(self.app)
        self.fenetre.update()
        self.coureurs, self.marathons, self.participations, self.classement, self.historique = (
            self.fenetre._onglets
        )
        # Les boîtes de dialogue bloqueraient le test : on les remplace.
        patchs = [
            mock.patch.object(base_tab.messagebox, "showwarning"),
            mock.patch.object(base_tab.messagebox, "showerror"),
            mock.patch.object(base_tab.messagebox, "askyesno", return_value=True),
        ]
        self.avertissement, self.erreur, _ = (p.start() for p in patchs)
        for p in patchs:
            self.addCleanup(p.stop)
        self.addCleanup(self.app.close)
        self.addCleanup(self._fermer)

    def _fermer(self):
        self.fenetre.destroy()

    def _remplir_coureur(self, nom="alaoui", prenom="sara", sexe="F", email="sara@mail.com"):
        v = self.coureurs._vars
        v["nom"].set(nom)
        v["prenom"].set(prenom)
        v["sexe"].set(sexe)
        v["naissance"].set("14/03/1992")
        v["email"].set(email)

    def test_cycle_complet_coureur(self):
        self._remplir_coureur()
        self.coureurs.ajouter()
        self.assertEqual(self.coureurs.tableau.effectif(), 1)
        self.assertEqual(self.app.coureurs.lister()[0].nom, "ALAOUI")

        self.coureurs._vars["prenom"].set("Sarah")
        self.coureurs.modifier()
        self.assertEqual(self.app.coureurs.lister()[0].prenom, "Sarah")

        self.coureurs.supprimer()
        self.assertEqual(self.coureurs.tableau.effectif(), 0)
        self.erreur.assert_not_called()

    def test_erreur_de_saisie_affichee_sans_planter(self):
        self._remplir_coureur(email="pas-un-email")
        self.coureurs.ajouter()
        self.avertissement.assert_called_once()
        self.assertEqual(self.app.coureurs.lister(), [])

    def test_recherche(self):
        self._remplir_coureur()
        self.coureurs.ajouter()
        self.coureurs.nouveau()
        self._remplir_coureur("tazi", "omar", "M", "omar@mail.com")
        self.coureurs.ajouter()
        self.coureurs._var_recherche.set("taz")
        self.assertEqual(self.coureurs.tableau.effectif(), 1)

    def test_parcours_complet_inscription_classement_historique(self):
        self._remplir_coureur()
        self.coureurs.ajouter()
        m = self.marathons
        m._vars["nom"].set("Marathon de Rabat")
        m._vars["date"].set("2026-04-12")
        m._vars["ville"].set("Rabat")
        m.ajouter()

        p = self.participations
        p.refresh()
        p.inscrire()
        self.assertEqual(p.tableau.effectif(), 1)
        p.tableau.selectionner(p.tableau.arbre.get_children()[0])
        self.fenetre.update()
        p._var_temps.set("3:45:12")
        p.enregistrer_temps()
        self.assertEqual(self.app.participations.classement(1)[0].temps_final, "03:45:12")

        self.classement.refresh()
        self.assertEqual(self.classement.tableau.effectif(), 1)
        self.historique.refresh()
        self.assertEqual(self.historique.tableau.effectif(), 1)
        self.erreur.assert_not_called()
        self.avertissement.assert_not_called()

    def test_demo_et_changement_d_onglet(self):
        self.fenetre.charger_demo()
        self.assertEqual(self.coureurs.tableau.effectif(), 10)
        for onglet in self.fenetre.notebook.tabs():
            self.fenetre.notebook.select(onglet)
            self.fenetre.update()
        self.assertGreater(self.classement.tableau.effectif(), 0)
        self.erreur.assert_not_called()
