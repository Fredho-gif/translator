"""
text_blocks.py — Extraction des paragraphes de texte (hors tableaux).

Regroupe les lignes en paragraphes selon :
  - l'espacement vertical (un grand espace = nouveau paragraphe)
  - la mise en forme (un changement titre <-> non-titre = nouveau bloc)
  - la "forme" de la ligne : une ligne courte ou qui se termine par un
    montant/nombre est traitée comme une rupture volontaire (sous-titre,
    élément de liste, répartition chiffrée) plutôt que recollée à la
    ligne suivante comme une phrase qui continue.
"""

import re

from ..config import RATIO_ESPACEMENT_NOUVEAU_PARAGRAPHE, RATIO_LIGNE_COURTE
from ..formatting import classifier_style, detecter_style_ligne
from .headers_footers import normaliser_pour_comparaison


def extraire_paragraphes(page_plumber, zones_exclues: list, entetes_pieds: set = None,
                          taille_corps: float = 11.0) -> list:
    """
    Extrait les lignes de texte hors des zones de tableaux, puis les
    regroupe en paragraphes. Exclut aussi les en-têtes/pieds de page
    récurrents.
    """
    entetes_pieds = entetes_pieds or set()
    try:
        lignes = page_plumber.extract_text_lines() or []
    except Exception:
        lignes = []

    hauteur_page = page_plumber.height

    def dans_une_zone_exclue(ligne):
        milieu = (ligne["top"] + ligne["bottom"]) / 2
        for (haut, bas) in zones_exclues:
            if haut <= milieu <= bas:
                return True
        return False

    def est_entete_ou_pied(ligne):
        zone_haute = ligne["top"] < hauteur_page * 0.08
        zone_basse = ligne["bottom"] > hauteur_page * 0.92
        if not (zone_haute or zone_basse):
            return False
        cle = normaliser_pour_comparaison(ligne.get("text", ""))
        return cle in entetes_pieds

    lignes_utiles = [
        l for l in lignes
        if l.get("text", "").strip()
        and not dans_une_zone_exclue(l)
        and not est_entete_ou_pied(l)
    ]
    lignes_utiles.sort(key=lambda l: l["top"])

    largeurs = [l["x1"] - l["x0"] for l in lignes_utiles]
    largeur_normale = max(largeurs) if largeurs else 0
    seuil_ligne_courte = largeur_normale * RATIO_LIGNE_COURTE

    def ligne_est_une_rupture(ligne_texte: str, largeur_ligne: float) -> bool:
        """True si la ligne semble être une fin volontaire (titre, item de
        liste, montant) plutôt qu'une ligne qui continue automatiquement."""
        texte = ligne_texte.rstrip()
        if not texte or texte.endswith((".", "!", "?", ",")):
            return False
        if largeur_ligne < seuil_ligne_courte:
            return True
        # Ligne se terminant par un montant/nombre (ex: "Down payment: $1,000")
        if re.search(r"\d[\d,.\)\$]*$", texte):
            return True
        return False

    paragraphes = []
    para_segments = []
    para_styles = []
    top_para = None
    bottom_precedent = None
    style_precedent = None

    def cloturer_paragraphe():
        if not para_segments:
            return
        texte_complet = "".join(t for t, _ in para_segments)
        style_bloc = para_styles[0] if para_styles else "normal"
        paragraphes.append({
            "type": "text",
            "top": top_para,
            "bottom": bottom_precedent,
            "content": texte_complet,
            "style": style_bloc,
        })

    for ligne in lignes_utiles:
        hauteur_ligne = ligne["bottom"] - ligne["top"]
        style_ligne = classifier_style(detecter_style_ligne(ligne), taille_corps)

        rupture_espacement = (
            bottom_precedent is not None
            and (ligne["top"] - bottom_precedent) > hauteur_ligne * RATIO_ESPACEMENT_NOUVEAU_PARAGRAPHE
        )
        # Rupture de style : isole un titre/sous-titre du texte normal qui
        # l'entoure, même sans grand espacement vertical.
        rupture_style = (
            style_precedent is not None
            and style_ligne != style_precedent
            and ("titre" in style_ligne or "titre" in style_precedent)
        )
        nouveau_paragraphe = rupture_espacement or rupture_style

        if nouveau_paragraphe:
            cloturer_paragraphe()
            para_segments = []
            para_styles = []
            top_para = None

        texte_ligne = ligne["text"].strip()
        largeur_ligne = ligne["x1"] - ligne["x0"]

        if not para_segments:
            para_segments.append((texte_ligne, largeur_ligne))
        else:
            texte_prec, largeur_prec = para_segments[-1]
            if ligne_est_une_rupture(texte_prec, largeur_prec):
                para_segments.append(("\n" + texte_ligne, largeur_ligne))
            else:
                para_segments.append((" " + texte_ligne, largeur_ligne))

        para_styles.append(style_ligne)
        if top_para is None:
            top_para = ligne["top"]
        bottom_precedent = ligne["bottom"]
        style_precedent = style_ligne

    cloturer_paragraphe()

    return [p for p in paragraphes if p["content"].strip()]
