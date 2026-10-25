"""
text_blocks.py — Extraction des paragraphes de texte (hors tableaux).

Regroupe les lignes en paragraphes selon :
  - l'espacement vertical (un grand espace = nouveau paragraphe)
  - le retrait de la première ligne (retrait + fin de phrase avant)
  - la mise en forme (un changement titre <-> non-titre = nouveau bloc)
  - la "forme" de la ligne : une ligne courte ou qui se termine par un
    montant/nombre est traitée comme une rupture volontaire (sous-titre,
    élément de liste, répartition chiffrée) plutôt que recollée à la
    ligne suivante comme une phrase qui continue.
"""

import re
import statistics
from collections import Counter

from ..config import (
    ECART_MIN_NOUVEAU_PARAGRAPHE,
    RATIO_ECART_NOUVEAU_PARAGRAPHE,
    RATIO_ESPACEMENT_NOUVEAU_PARAGRAPHE,
    RATIO_LIGNE_COURTE,
    SEUIL_RETRAIT_PARAGRAPHE,
)
from ..formatting import classifier_style, detecter_style_ligne
from .headers_footers import normaliser_pour_comparaison

_FINS_DE_PHRASE = (".", "!", "?", "…", "”", "»", '"', ":")


def _marge_gauche(lignes: list) -> float:
    """Position x0 la plus fréquente : le bord gauche du texte courant."""
    if not lignes:
        return 0.0
    return float(Counter(round(l["x0"]) for l in lignes).most_common(1)[0][0])


def _ecart_median(lignes: list) -> float:
    """Écart vertical médian entre deux lignes consécutives (0 si indéterminé)."""
    ecarts = [b["top"] - a["bottom"] for a, b in zip(lignes, lignes[1:])]
    ecarts = [e for e in ecarts if e > 0]
    return statistics.median(ecarts) if ecarts else 0.0


def _finit_une_phrase(texte: str) -> bool:
    return texte.rstrip().endswith(_FINS_DE_PHRASE)

def _finit_par_cesure(texte: str) -> bool:
    """True si la ligne finit par un trait d'union collé à une lettre ('CERF-', 'exam-')."""
    t = texte.rstrip()
    return len(t) >= 2 and t.endswith("-") and t[-2].isalpha()


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

    marge_gauche = _marge_gauche(lignes_utiles)
    seuil_retrait = taille_corps * SEUIL_RETRAIT_PARAGRAPHE
    seuil_ecart = max(
        _ecart_median(lignes_utiles) * RATIO_ECART_NOUVEAU_PARAGRAPHE,
        ECART_MIN_NOUVEAU_PARAGRAPHE,
    )

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
    x0_precedent = None

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

        ecart = (ligne["top"] - bottom_precedent) if bottom_precedent is not None else 0
        rupture_espacement = (
            bottom_precedent is not None
            and (
                ecart > hauteur_ligne * RATIO_ESPACEMENT_NOUVEAU_PARAGRAPHE
                or ecart > seuil_ecart
            )
        )
        # Retrait : début de paragraphe si la ligne précédente finit une
        # phrase et n'était pas elle-même en retrait (liste à retrait
        # suspendu, citation : on ne coupe pas).
        rupture_retrait = (
            bool(para_segments)
            and (ligne["x0"] - marge_gauche) > seuil_retrait
            and x0_precedent is not None
            and (x0_precedent - marge_gauche) <= seuil_retrait
            and _finit_une_phrase(para_segments[-1][0])
        )
        # Rupture de style : isole un titre/sous-titre du texte normal qui
        # l'entoure, même sans grand espacement vertical.
        rupture_style = (
            style_precedent is not None
            and style_ligne != style_precedent
            and ("titre" in style_ligne or "titre" in style_precedent)
        )
        nouveau_paragraphe = rupture_espacement or rupture_retrait or rupture_style

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
            if _finit_par_cesure(texte_prec):
                para_segments.append((texte_ligne, largeur_ligne))
            elif ligne_est_une_rupture(texte_prec, largeur_prec):
                para_segments.append(("\n" + texte_ligne, largeur_ligne))
            else:
                para_segments.append((" " + texte_ligne, largeur_ligne))

        para_styles.append(style_ligne)
        if top_para is None:
            top_para = ligne["top"]
        bottom_precedent = ligne["bottom"]
        style_precedent = style_ligne
        x0_precedent = ligne["x0"]

    cloturer_paragraphe()

    return [p for p in paragraphes if p["content"].strip()]