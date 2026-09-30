"""
extraction — Tout ce qui concerne la lecture du PDF source : tableaux,
paragraphes de texte, en-têtes/pieds de page récurrents, images.
"""

from .page import extraire_contenu_page

__all__ = ["extraire_contenu_page"]
