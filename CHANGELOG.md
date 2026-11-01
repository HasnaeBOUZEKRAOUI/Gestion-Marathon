# Journal des modifications

## 2.0.0

### Nouvelle interface
- **Barre de navigation verticale** (menu latéral sombre) à la place des onglets : page active
  mise en évidence, effet de survol, actions rapides en bas (Actualiser, Données de démo, À propos).
- **Design moderne** : fond clair, cartes blanches, champs et boutons à contour fin, bouton principal
  bleu et bouton de suppression rouge, tableaux aérés avec en-têtes alignés et barre de défilement fine.
- **Nouveau « Tableau de bord »** : chiffres clés, prochaine course avec compte à rebours,
  podium de la dernière course avec résultats.
- **Tuiles de statistiques** (inscrits, terminés, abandons, meilleur temps, temps moyen) dans le
  Classement et l'Historique.
- Raccourcis clavier : `Ctrl+1` à `Ctrl+6` (pages) et `F5` (actualiser).

### Changements internes
- Les « onglets » deviennent des « pages » : `*_tab.py` → `*_page.py`, `BaseTab` → `BasePage`.
- Nouveaux composants : `Carte`, `TuileStat` (widgets.py) et `BarreLaterale` (sidebar.py).
- Le thème (`theme.py`) centralise palette, polices et styles.
- Le back-end (modèles, dépôts, services, base SQLite) et l'interface console sont inchangés.
- L'archive ne contient plus de fichier parasite (`tk-0.1.0-py3-none-any.whl` présent par erreur en 1.0.0).

## 1.0.0
- Première version : back-end en couches (modèles, dépôts, services), interface console et interface Tkinter à onglets.
