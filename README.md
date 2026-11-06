# Gestion de Marathon — v2.0.0

Application de bureau pour gérer des marathons : coureurs, éditions, inscriptions, dossards, statuts, temps, classements et historique.

**Python orienté objet · SQLite3 (module standard `sqlite3`) · Tkinter** — aucune dépendance externe.

## Lancer l'application

```bash
python main.py --demo          # interface graphique + données d'exemple (si la base est vide)
python main.py                 # interface graphique
python main.py --console       # interface en ligne de commande
python main.py --db autre.db   # utiliser un autre fichier de base
```

La base `marathon.db` est créée automatiquement à côté de `main.py`.
Les données de démonstration peuvent aussi être chargées depuis la barre latérale (« Données de démo »).

> Linux : si Tkinter manque, `sudo apt install python3-tk`.

## Interface (v2.0.0)

Une **barre de navigation verticale** à gauche, une page à droite. Raccourcis : `Ctrl+1` … `Ctrl+6` pour changer de page, `F5` pour actualiser.

| Page | Fonctionnalités |
| --- | --- |
| **Tableau de bord** | chiffres clés, prochaine course avec compte à rebours, podium de la dernière course |
| **Coureurs** | ajouter / modifier / supprimer, recherche par nom, prénom ou email |
| **Marathons** | gérer les éditions (nom, date, ville ; l'année est déduite de la date) |
| **Participations** | inscrire un coureur (dossard automatique ou choisi), enregistrer le temps, passer en Abandon / Non-partant / Inscrit, désinscrire |
| **Classement** | classement d'une édition (ex-æquo gérés, podium coloré), filtre Hommes / Femmes, tuiles de statistiques |
| **Historique** | toutes les participations d'un coureur et son meilleur temps |

Formats de saisie : date `AAAA-MM-JJ` ou `JJ/MM/AAAA` ; temps `HH:MM:SS`.

## Architecture (couches)

```
main.py                      point d'entrée (choix GUI / console)
gestion_marathon/
├── app.py                   Application : assemble base, dépôts et services
├── config.py  exceptions.py configuration ; exceptions métier (MarathonError et dérivées)
├── database.py              Database : connexion SQLite, schéma, traduction des erreurs
├── models/                  dataclasses : Coureur, Marathon, Participation, vues de lecture
├── repositories/            accès SQL, une classe par table (BaseRepository générique)
├── services/                règles métier et validations (CoureurService, ...)
├── utils/                   validators.py, time_utils.py
├── demo.py                  jeu de données d'exemple
└── ui/
    ├── console.py, menus.py interface console
    └── gui/                 interface Tkinter
        ├── main_window.py   MainWindow : barre latérale + en-tête + pages + barre d'état
        ├── sidebar.py       BarreLaterale / ItemNavigation (navigation verticale)
        ├── theme.py         palette, polices et styles ttk
        ├── widgets.py       Carte, TuileStat, TableauDonnees, ListeEntites, helpers
        ├── base_page.py     BasePage + décorateur @gerer_erreurs
        └── *_page.py        une classe par page (dashboard, coureurs, marathons, ...)
tests/                       tests des services, de la démo et de l'interface
```

Flux : `UI (pages) → Services (règles) → Repositories (SQL) → Database (SQLite)`.
L'interface n'écrit jamais de SQL ; les services lèvent des `MarathonError` que `@gerer_erreurs`
transforme en boîtes de dialogue lisibles.

Pour ajouter une page : créer une classe héritant de `BasePage` (avec `TITRE`, `SOUS_TITRE`, `ICONE`
et `refresh`) puis l'ajouter au tuple `MainWindow.PAGES` ; la barre latérale se met à jour seule.

## Base de données

Trois tables (`COUREURS`, `MARATHONS`, `PARTICIPATIONS`), clés étrangères activées. Contraintes :
email unique, dossard unique par marathon, un coureur ne s'inscrit qu'une fois par marathon,
et cohérence statut/temps (un temps n'existe que pour le statut « Terminé »).
Un coureur ou un marathon ayant des participations ne peut pas être supprimé.


