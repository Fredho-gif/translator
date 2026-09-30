"""
translation — Traduction des textes extraits (moteur + orchestration par lots).
"""

from .batch import appliquer_traductions, collecter_textes_uniques, traduire_en_parallele
from .engine import traduire_un_texte

__all__ = [
    "traduire_un_texte",
    "collecter_textes_uniques",
    "traduire_en_parallele",
    "appliquer_traductions",
]
