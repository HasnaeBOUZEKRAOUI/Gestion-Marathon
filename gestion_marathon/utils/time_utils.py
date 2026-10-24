"""Outils de manipulation des temps de course (format HH:MM:SS)."""

import re
from typing import Iterable, Optional

from ..exceptions import ValidationError

_TEMPS_RE = re.compile(r"^(\d{1,2}):([0-5]\d):([0-5]\d)$")


def normaliser_temps(valeur) -> str:
    """Valide un temps et le retourne au format fixe ``HH:MM:SS``.

    Le format fixe garantit que l'ordre alphabétique SQL correspond à l'ordre
    chronologique (utile pour établir un classement).
    """
    texte = str(valeur).strip() if valeur is not None else ""
    correspondance = _TEMPS_RE.match(texte)
    if not correspondance:
        raise ValidationError(
            f"Temps invalide : '{texte}'. Format attendu : HH:MM:SS (ex. 03:45:12)."
        )
    heures, minutes, secondes = (int(x) for x in correspondance.groups())
    if heures >= 24 or heures + minutes + secondes == 0:
        raise ValidationError("Le temps doit être compris entre 00:00:01 et 23:59:59.")
    return f"{heures:02d}:{minutes:02d}:{secondes:02d}"


def vers_secondes(temps: str) -> int:
    heures, minutes, secondes = (int(x) for x in temps.split(":"))
    return heures * 3600 + minutes * 60 + secondes


def depuis_secondes(total: float) -> str:
    total = int(round(total))
    return f"{total // 3600:02d}:{(total % 3600) // 60:02d}:{total % 60:02d}"


def temps_moyen(temps: Iterable[str]) -> Optional[str]:
    """Moyenne d'une collection de temps ``HH:MM:SS`` (None si vide)."""
    secondes = [vers_secondes(t) for t in temps]
    if not secondes:
        return None
    return depuis_secondes(sum(secondes) / len(secondes))
