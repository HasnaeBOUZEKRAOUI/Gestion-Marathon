"""Point d'entrée : python main.py [--db fichier.db] [--demo] [--console]"""

import argparse
import sys

from gestion_marathon.app import Application
from gestion_marathon.config import CHEMIN_BD_PAR_DEFAUT
from gestion_marathon.demo import charger_demo


def lancer_interface_graphique(app: Application) -> int:
    try:
        from gestion_marathon.ui.gui import lancer
    except ImportError as exc:  # Tkinter absent (ex. Linux sans python3-tk)
        print(f"Tkinter est indisponible ({exc}).")
        print("Installez-le (Linux : sudo apt install python3-tk) ou utilisez --console.")
        return 1
    lancer(app)
    return 0


def lancer_console(app: Application) -> int:
    from gestion_marathon.ui import MenuPrincipal

    try:
        MenuPrincipal(app).run()
    except (KeyboardInterrupt, EOFError):
        print()
    print("Au revoir !")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Application de gestion de marathons.")
    parser.add_argument(
        "--db",
        default=str(CHEMIN_BD_PAR_DEFAUT),
        help="chemin du fichier SQLite (défaut : %(default)s)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="charge des données d'exemple si la base est vide",
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="utilise l'interface en ligne de commande au lieu de l'interface graphique",
    )
    args = parser.parse_args(argv)

    with Application(args.db) as app:
        if args.demo:
            if charger_demo(app):
                print("Données de démonstration chargées.")
            else:
                print("La base contient déjà des données : démonstration ignorée.")
        return lancer_console(app) if args.console else lancer_interface_graphique(app)


if __name__ == "__main__":
    sys.exit(main())
