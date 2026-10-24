"""Configuration globale de l'application."""

from pathlib import Path

# Racine du projet (dossier qui contient main.py)
RACINE_PROJET = Path(__file__).resolve().parent.parent

# Fichier SQLite utilisé par défaut
CHEMIN_BD_PAR_DEFAUT = RACINE_PROJET / "marathon.db"

# Valeurs possibles du champ « sexe »
SEXES = ("M", "F")

# Formats de date acceptés à la saisie (le premier est le format de stockage ISO)
FORMATS_DATE = ("%Y-%m-%d", "%d/%m/%Y")
