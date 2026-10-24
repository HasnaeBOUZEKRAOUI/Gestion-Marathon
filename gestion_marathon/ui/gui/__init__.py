"""Interface graphique Tkinter.

Ce paquet n'est importé que si l'utilisateur lance l'interface graphique, afin
que le reste de l'application reste utilisable sans Tkinter (tests, console).
"""

from .main_window import MainWindow, lancer

__all__ = ["MainWindow", "lancer"]
