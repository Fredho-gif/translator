"""
formatting.py — Détection de la mise en forme d'origine du PDF.

Analyse les caractères fournis par pdfplumber (fontname, taille) pour
repérer le gras, l'italique, et classer chaque ligne (titre, sous-titre,
texte normal...) afin de reproduire un style proche de l'original dans
le PDF traduit.
"""

import re
from collections import Counter


def detecter_style_ligne(ligne: dict) -> dict:
    """
    Analyse les caractères d'une ligne (fournis par pdfplumber via
    extract_text_lines) pour déterminer sa mise en forme : gras, italique,
    et taille de police moyenne.
    """
    chars = ligne.get("chars") or []
    if not chars:
        return {"gras": False, "italique": False, "taille": 0}

    nb_gras = 0
    nb_italique = 0
    tailles = []
    for c in chars:
        police = (c.get("fontname") or "").lower()
        if "bold" in police or "black" in police or "heavy" in police or re.search(r"[-,]bd$", police):
            nb_gras += 1
        if "italic" in police or "oblique" in police:
            nb_italique += 1
        if c.get("size"):
            tailles.append(c["size"])

    nb_chars = len(chars)
    return {
        "gras": (nb_gras / nb_chars) > 0.6 if nb_chars else False,
        "italique": (nb_italique / nb_chars) > 0.6 if nb_chars else False,
        "taille": (sum(tailles) / len(tailles)) if tailles else 0,
    }


def detecter_taille_corps_habituelle(pdf) -> float:
    """Détermine la taille de police la plus fréquente sur l'ensemble du document."""
    compteur_tailles = Counter()
    for page in pdf.pages:
        try:
            lignes = page.extract_text_lines() or []
        except Exception:
            lignes = []
        for ligne in lignes:
            style = detecter_style_ligne(ligne)
            if style["taille"] > 0:
                compteur_tailles[round(style["taille"])] += 1
    if not compteur_tailles:
        return 11.0
    return float(compteur_tailles.most_common(1)[0][0])


def classifier_style(style: dict, taille_corps: float,
                      ratio_titre1: float = 1.35, ratio_titre2: float = 1.12) -> str:
    """Classe une ligne : titre1, titre2, italique, gras, ou normal."""
    taille = style["taille"] or taille_corps
    ratio = (taille / taille_corps) if taille_corps else 1.0

    if style["gras"] and ratio >= ratio_titre1:
        return "titre1"
    if style["gras"] and ratio >= ratio_titre2:
        return "titre2"
    if style["italique"] and not style["gras"]:
        return "italique"
    if style["gras"]:
        return "gras"
    return "normal"
