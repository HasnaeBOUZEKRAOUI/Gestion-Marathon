"""Couche d'accès aux données (une classe par table)."""

from .coureur_repository import CoureurRepository
from .marathon_repository import MarathonRepository
from .participation_repository import ParticipationRepository

__all__ = ["CoureurRepository", "MarathonRepository", "ParticipationRepository"]
