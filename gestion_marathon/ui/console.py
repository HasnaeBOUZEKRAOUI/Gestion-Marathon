"""Fonctions d'entrée/sortie console réutilisables."""

from datetime import date
from typing import Optional, Sequence

from ..exceptions import ValidationError
from ..utils.validators import parser_date


# ------------------------------------------------------------------------ affichage
def titre(texte: str) -> None:
    print(f"\n{'=' * 60}\n  {texte}\n{'=' * 60}")


def succes(message: str) -> None:
    print(f"  ✔ {message}")


def erreur(message: str) -> None:
    print(f"  ✘ {message}")


def info(message: str) -> None:
    print(f"  {message}")


def afficher_tableau(entetes: Sequence[str], lignes: Sequence[Sequence]) -> None:
    """Affiche un tableau aligné ; message simple si aucune ligne."""
    if not lignes:
        info("(aucun résultat)")
        return
    textes = [["" if v is None else str(v) for v in ligne] for ligne in lignes]
    largeurs = [
        max(len(entetes[i]), *(len(ligne[i]) for ligne in textes)) for i in range(len(entetes))
    ]
    separateur = "-+-".join("-" * w for w in largeurs)
    print(" | ".join(e.ljust(w) for e, w in zip(entetes, largeurs)))
    print(separateur)
    for ligne in textes:
        print(" | ".join(v.ljust(w) for v, w in zip(ligne, largeurs)))
    print(f"\n  {len(textes)} ligne(s)")


# --------------------------------------------------------------------------- saisie
def saisir_texte(invite: str, defaut: Optional[str] = None, obligatoire: bool = True) -> str:
    """Lit un texte. Si ``defaut`` est fourni, Entrée le conserve."""
    suffixe = f" [{defaut}]" if defaut else ""
    while True:
        valeur = input(f"  {invite}{suffixe} : ").strip()
        if valeur:
            return valeur
        if defaut is not None:
            return defaut
        if not obligatoire:
            return ""
        erreur("Saisie obligatoire.")


def saisir_entier(
    invite: str, defaut: Optional[int] = None, obligatoire: bool = True
) -> Optional[int]:
    """Lit un entier ; retourne None si vide et non obligatoire."""
    suffixe = f" [{defaut}]" if defaut is not None else ""
    while True:
        valeur = input(f"  {invite}{suffixe} : ").strip()
        if not valeur:
            if defaut is not None:
                return defaut
            if not obligatoire:
                return None
            erreur("Saisie obligatoire.")
            continue
        try:
            return int(valeur)
        except ValueError:
            erreur("Veuillez saisir un nombre entier.")


def saisir_date(
    invite: str, defaut: Optional[date] = None, obligatoire: bool = True
) -> Optional[date]:
    """Lit une date (AAAA-MM-JJ ou JJ/MM/AAAA) ; None si vide et non obligatoire."""
    suffixe = f" [{defaut.isoformat()}]" if defaut else ""
    while True:
        valeur = input(f"  {invite}{suffixe} : ").strip()
        if not valeur:
            if defaut is not None:
                return defaut
            if not obligatoire:
                return None
            erreur("Saisie obligatoire.")
            continue
        try:
            return parser_date(valeur, invite)
        except ValidationError as exc:
            erreur(str(exc))


def confirmer(question: str) -> bool:
    return input(f"  {question} (o/N) : ").strip().lower() in ("o", "oui", "y", "yes")
