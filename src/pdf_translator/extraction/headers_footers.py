"""
headers_footers.py — Détection des en-têtes/pieds de page récurrents.

Un titre de livre ou un numéro de page qui se répète en haut/bas de
nombreuses pages doit être exclu du flux de texte normal, sinon il se
glisse au milieu des paragraphes et donne l'impression que le document
est désordonné.
"""

import re
from collections import Counter

from ..config import SEUIL_FREQUENCE_ENTETE_PIED


def normaliser_pour_comparaison(texte: str) -> str:
    """Normalise un texte pour comparer des en-têtes/pieds de page malgré les numéros qui changent."""
    return re.sub(r"\d+", "#", texte.strip().lower())


def detecter_entetes_pieds(pdf, seuil_frequence: float = SEUIL_FREQUENCE_ENTETE_PIED) -> set:
    """Repère les textes qui reviennent en haut/bas d'un grand nombre de pages."""
    compteur = Counter()
    nb_pages = len(pdf.pages)

    for page in pdf.pages:
        hauteur_page = page.height
        try:
            lignes = page.extract_text_lines() or []
        except Exception:
            lignes = []
        deja_vus_sur_page = set()
        for ligne in lignes:
            texte = ligne.get("text", "").strip()
            if not texte:
                continue
            zone_haute = ligne["top"] < hauteur_page * 0.08
            zone_basse = ligne["bottom"] > hauteur_page * 0.92
            if zone_haute or zone_basse:
                cle = normaliser_pour_comparaison(texte)
                if cle and cle not in deja_vus_sur_page:
                    compteur[cle] += 1
                    deja_vus_sur_page.add(cle)

    seuil_nb_pages = max(2, int(nb_pages * seuil_frequence))
    return {cle for cle, n in compteur.items() if n >= seuil_nb_pages}
