"""
page.py — Combine tableaux, paragraphes et images d'une page en un seul
flux, trié par position verticale pour respecter l'ordre de lecture.
"""

from pathlib import Path

from .images import extraire_images
from .tables import extraire_tableaux
from .text_blocks import extraire_paragraphes


def extraire_contenu_page(page_plumber, doc_fitz, num_page: int, dossier_tmp: Path,
                           entetes_pieds: set = None, taille_corps: float = 11.0,
                           langue_source: str = "en") -> list:
    """Combine texte, tableaux et images d'une page, triés par position verticale."""
    blocs_tableaux = extraire_tableaux(page_plumber)
    zones_tableaux = [(b["top"], b["bottom"]) for b in blocs_tableaux]
    blocs_texte = extraire_paragraphes(page_plumber, zones_tableaux, entetes_pieds, taille_corps)
    blocs_images = extraire_images(doc_fitz, num_page, dossier_tmp, langue_source)

    tous_les_blocs = blocs_tableaux + blocs_texte + blocs_images
    tous_les_blocs.sort(key=lambda b: b["top"])
    return tous_les_blocs
