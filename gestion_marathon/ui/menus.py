"""Menus de l'application (un menu = une classe)."""

from typing import Callable, List, Tuple

from ..app import Application
from ..exceptions import MarathonError
from ..models import Statut
from . import console as ui

Option = Tuple[str, Callable[[], None]]


class Menu:
    """Menu générique : affiche des options numérotées et exécute l'action choisie."""

    TITRE = ""

    def __init__(self, app: Application):
        self.app = app

    def options(self) -> List[Option]:
        raise NotImplementedError

    def run(self) -> None:
        while True:
            options = self.options()
            ui.titre(self.TITRE)
            for numero, (libelle, _) in enumerate(options, start=1):
                print(f"  {numero}. {libelle}")
            print("  0. Retour / Quitter")
            choix = input("\n  Votre choix : ").strip()
            if choix == "0":
                return
            if not choix.isdigit() or not 1 <= int(choix) <= len(options):
                ui.erreur("Choix invalide.")
                continue
            try:
                options[int(choix) - 1][1]()
            except MarathonError as exc:
                ui.erreur(str(exc))

    # ------------------------------------------------------- aides de sélection
    def choisir_coureur(self) -> int:
        self._tableau_coureurs(self.app.coureurs.lister())
        return ui.saisir_entier("ID du coureur")

    def choisir_marathon(self) -> int:
        self._tableau_marathons()
        return ui.saisir_entier("ID du marathon")

    @staticmethod
    def _tableau_coureurs(coureurs) -> None:
        ui.afficher_tableau(
            ["ID", "Nom", "Prénom", "Sexe", "Naissance", "Âge", "Email"],
            [
                (c.id_coureur, c.nom, c.prenom, c.sexe, c.date_naissance, c.age(), c.email)
                for c in coureurs
            ],
        )

    def _tableau_marathons(self) -> None:
        ui.afficher_tableau(
            ["ID", "Événement", "Année", "Date", "Ville"],
            [
                (m.id_marathon, m.nom_evenement, m.annee, m.date_course, m.ville)
                for m in self.app.marathons.lister()
            ],
        )

    @staticmethod
    def _tableau_participants(participants, avec_rang: bool = False) -> None:
        entetes = ["Dossard", "Coureur", "Sexe", "Statut", "Temps"]
        if avec_rang:
            entetes.insert(0, "Rang")
        lignes = []
        for p in participants:
            ligne = [p.num_dossard, p.nom_complet, p.sexe, p.statut, p.temps_final]
            if avec_rang:
                ligne.insert(0, p.rang)
            lignes.append(ligne)
        ui.afficher_tableau(entetes, lignes)


# ================================================================== COUREURS
class MenuCoureurs(Menu):
    TITRE = "GESTION DES COUREURS"

    def options(self) -> List[Option]:
        return [
            ("Lister les coureurs", self.lister),
            ("Rechercher un coureur", self.rechercher),
            ("Ajouter un coureur", self.ajouter),
            ("Modifier un coureur", self.modifier),
            ("Supprimer un coureur", self.supprimer),
        ]

    def lister(self) -> None:
        self._tableau_coureurs(self.app.coureurs.lister())

    def rechercher(self) -> None:
        terme = ui.saisir_texte("Nom, prénom ou email à rechercher")
        self._tableau_coureurs(self.app.coureurs.rechercher(terme))

    def ajouter(self) -> None:
        coureur = self.app.coureurs.creer(
            nom=ui.saisir_texte("Nom"),
            prenom=ui.saisir_texte("Prénom"),
            sexe=ui.saisir_texte("Sexe (M/F)"),
            date_naissance=ui.saisir_date("Date de naissance", obligatoire=False),
            email=ui.saisir_texte("Email"),
        )
        ui.succes(f"Coureur ajouté : {coureur.nom_complet} (ID {coureur.id_coureur}).")

    def modifier(self) -> None:
        actuel = self.app.coureurs.obtenir(self.choisir_coureur())
        ui.info("Appuyez sur Entrée pour conserver la valeur entre crochets.")
        coureur = self.app.coureurs.modifier(
            actuel.id_coureur,
            nom=ui.saisir_texte("Nom", actuel.nom),
            prenom=ui.saisir_texte("Prénom", actuel.prenom),
            sexe=ui.saisir_texte("Sexe (M/F)", actuel.sexe),
            date_naissance=ui.saisir_date(
                "Date de naissance", actuel.date_naissance, obligatoire=False
            ),
            email=ui.saisir_texte("Email", actuel.email),
        )
        ui.succes(f"Coureur modifié : {coureur.nom_complet}.")

    def supprimer(self) -> None:
        coureur = self.app.coureurs.obtenir(self.choisir_coureur())
        if ui.confirmer(f"Supprimer {coureur.nom_complet} ?"):
            self.app.coureurs.supprimer(coureur.id_coureur)
            ui.succes("Coureur supprimé.")


# ================================================================= MARATHONS
class MenuMarathons(Menu):
    TITRE = "GESTION DES MARATHONS"

    def options(self) -> List[Option]:
        return [
            ("Lister les marathons", self._tableau_marathons),
            ("Créer une édition", self.ajouter),
            ("Modifier une édition", self.modifier),
            ("Supprimer une édition", self.supprimer),
        ]

    def ajouter(self) -> None:
        marathon = self.app.marathons.creer(
            nom_evenement=ui.saisir_texte("Nom de l'événement"),
            annee=ui.saisir_entier("Année"),
            date_course=ui.saisir_date("Date de la course"),
            ville=ui.saisir_texte("Ville"),
        )
        ui.succes(f"Édition créée : {marathon.libelle} (ID {marathon.id_marathon}).")

    def modifier(self) -> None:
        actuel = self.app.marathons.obtenir(self.choisir_marathon())
        ui.info("Appuyez sur Entrée pour conserver la valeur entre crochets.")
        marathon = self.app.marathons.modifier(
            actuel.id_marathon,
            nom_evenement=ui.saisir_texte("Nom de l'événement", actuel.nom_evenement),
            annee=ui.saisir_entier("Année", actuel.annee),
            date_course=ui.saisir_date("Date de la course", actuel.date_course),
            ville=ui.saisir_texte("Ville", actuel.ville),
        )
        ui.succes(f"Édition modifiée : {marathon.libelle}.")

    def supprimer(self) -> None:
        marathon = self.app.marathons.obtenir(self.choisir_marathon())
        if ui.confirmer(f"Supprimer « {marathon.libelle} » ?"):
            self.app.marathons.supprimer(marathon.id_marathon)
            ui.succes("Édition supprimée.")


# ============================================================== INSCRIPTIONS
class MenuInscriptions(Menu):
    TITRE = "INSCRIPTIONS ET DOSSARDS"

    def options(self) -> List[Option]:
        return [
            ("Inscrire un coureur à un marathon", self.inscrire),
            ("Voir les participants d'un marathon", self.participants),
            ("Marquer un abandon / non-partant / remettre « Inscrit »", self.changer_statut),
            ("Désinscrire un participant", self.desinscrire),
        ]

    def inscrire(self) -> None:
        id_marathon = self.choisir_marathon()
        id_coureur = self.choisir_coureur()
        dossard = ui.saisir_entier("Numéro de dossard (Entrée = automatique)", obligatoire=False)
        participation = self.app.participations.inscrire(id_coureur, id_marathon, dossard)
        ui.succes(f"Inscription enregistrée avec le dossard n°{participation.num_dossard}.")

    def participants(self) -> None:
        id_marathon = self.choisir_marathon()
        self._tableau_participants(self.app.participations.lister_participants(id_marathon))

    def changer_statut(self) -> None:
        id_marathon = self.choisir_marathon()
        self._tableau_participants(self.app.participations.lister_participants(id_marathon))
        dossard = ui.saisir_entier("Numéro de dossard")
        print("  1. Abandon\n  2. Non-partant\n  3. Inscrit (annule un résultat/statut)")
        choix = ui.saisir_entier("Nouveau statut")
        statuts = {1: Statut.ABANDON, 2: Statut.NON_PARTANT, 3: Statut.INSCRIT}
        if choix not in statuts:
            ui.erreur("Choix invalide.")
            return
        participation = self.app.participations.changer_statut(
            id_marathon, dossard, statuts[choix]
        )
        ui.succes(f"Statut du dossard {dossard} : {participation.statut.value}.")

    def desinscrire(self) -> None:
        id_marathon = self.choisir_marathon()
        self._tableau_participants(self.app.participations.lister_participants(id_marathon))
        dossard = ui.saisir_entier("Numéro de dossard à désinscrire")
        if ui.confirmer(f"Désinscrire le dossard {dossard} ?"):
            self.app.participations.desinscrire(id_marathon, dossard)
            ui.succes("Participant désinscrit.")


# ================================================================= RÉSULTATS
class MenuResultats(Menu):
    TITRE = "RÉSULTATS ET CLASSEMENTS"

    def options(self) -> List[Option]:
        return [
            ("Enregistrer un temps final", self.enregistrer),
            ("Classement général", lambda: self.classement(None)),
            ("Classement hommes", lambda: self.classement("M")),
            ("Classement femmes", lambda: self.classement("F")),
            ("Statistiques d'un marathon", self.statistiques),
        ]

    def enregistrer(self) -> None:
        id_marathon = self.choisir_marathon()
        self._tableau_participants(self.app.participations.lister_participants(id_marathon))
        dossard = ui.saisir_entier("Numéro de dossard")
        temps = ui.saisir_texte("Temps final (HH:MM:SS)")
        participation = self.app.participations.enregistrer_resultat(id_marathon, dossard, temps)
        ui.succes(f"Résultat enregistré : dossard {dossard} → {participation.temps_final}.")

    def classement(self, sexe) -> None:
        id_marathon = self.choisir_marathon()
        self._tableau_participants(
            self.app.participations.classement(id_marathon, sexe), avec_rang=True
        )

    def statistiques(self) -> None:
        id_marathon = self.choisir_marathon()
        s = self.app.participations.statistiques(id_marathon)
        marathon = self.app.marathons.obtenir(id_marathon)
        ui.titre(f"Statistiques – {marathon.libelle}")
        ui.info(f"Inscrits au total   : {s.total_inscrits}")
        ui.info(f"En attente          : {s.en_attente}")
        ui.info(f"Arrivés (Terminé)   : {s.termines}")
        ui.info(f"Abandons            : {s.abandons}")
        ui.info(f"Non-partants        : {s.non_partants}")
        ui.info(f"Meilleur temps      : {s.meilleur_temps or '—'}")
        ui.info(f"Temps moyen         : {s.temps_moyen or '—'}")
        taux = f"{s.taux_arrivee} %" if s.taux_arrivee is not None else "—"
        ui.info(f"Taux d'arrivée      : {taux}  (arrivés / partis)")


# ================================================================= HISTORIQUE
class MenuHistorique(Menu):
    TITRE = "HISTORIQUE D'UN COUREUR"

    def options(self) -> List[Option]:
        return [("Consulter l'historique d'un coureur", self.historique)]

    def historique(self) -> None:
        coureur = self.app.coureurs.obtenir(self.choisir_coureur())
        lignes = self.app.participations.historique_coureur(coureur.id_coureur)
        ui.titre(f"Historique de {coureur.nom_complet}")
        ui.afficher_tableau(
            ["Événement", "Année", "Date", "Ville", "Dossard", "Statut", "Temps"],
            [
                (l.nom_evenement, l.annee, l.date_course, l.ville,
                 l.num_dossard, l.statut, l.temps_final)
                for l in lignes
            ],
        )


# ============================================================ MENU PRINCIPAL
class MenuPrincipal(Menu):
    TITRE = "GESTION DE MARATHONS"

    def options(self) -> List[Option]:
        return [
            ("Coureurs", MenuCoureurs(self.app).run),
            ("Marathons", MenuMarathons(self.app).run),
            ("Inscriptions et dossards", MenuInscriptions(self.app).run),
            ("Résultats et classements", MenuResultats(self.app).run),
            ("Historique d'un coureur", MenuHistorique(self.app).run),
        ]
