"""Fonctions de validation et de normalisation des saisies."""

import re
from datetime import date, datetime
from typing import Optional

from ..config import FORMATS_DATE
from ..exceptions import ValidationError

_EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


def valider_texte(valeur, champ: str, longueur_max: int = 50) -> str:
    """Retourne le texte nettoyé (espaces normalisés) ou lève ValidationError."""
    if valeur is None or not str(valeur).strip():
        raise ValidationError(f"Le champ « {champ} » est obligatoire.")
    texte = " ".join(str(valeur).split())
    if len(texte) > longueur_max:
        raise ValidationError(
            f"Le champ « {champ} » ne doit pas dépasser {longueur_max} caractères."
        )
    return texte


def valider_email(valeur) -> str:
    email = valider_texte(valeur, "email", 100).lower()
    if not _EMAIL_RE.match(email):
        raise ValidationError(f"Adresse email invalide : {email}")
    return email


def valider_sexe(valeur) -> str:
    sexe = valider_texte(valeur, "sexe", 1).upper()
    if sexe not in ("M", "F"):
        raise ValidationError("Le sexe doit être 'M' ou 'F'.")
    return sexe


def parser_date(valeur, champ: str = "date") -> date:
    """Convertit une saisie (date ou texte) en objet ``date``."""
    if isinstance(valeur, datetime):
        return valeur.date()
    if isinstance(valeur, date):
        return valeur
    texte = valider_texte(valeur, champ, 10)
    for fmt in FORMATS_DATE:
        try:
            return datetime.strptime(texte, fmt).date()
        except ValueError:
            continue
    raise ValidationError(
        f"Date invalide pour « {champ} » : '{texte}' (formats : AAAA-MM-JJ ou JJ/MM/AAAA)."
    )


def parser_date_optionnelle(valeur, champ: str = "date") -> Optional[date]:
    """Comme ``parser_date`` mais accepte une valeur vide (retourne None)."""
    if valeur is None or (isinstance(valeur, str) and not valeur.strip()):
        return None
    return parser_date(valeur, champ)
