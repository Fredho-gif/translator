"""
engine.py — Traduit un texte unique en essayant les fournisseurs dans l'ordre :
  1. DeepL (si une clé est configurée)
  2. Google Translate
  3. MyMemory (secours)

Chaque fournisseur vit dans son propre fichier (providers/). Chaque
traduction compte ses résultats dans son propre TranslationReport.
"""

from ..config import TAILLE_MAX_BLOC_TRADUCTION, TENTATIVES_TRADUCTION
from ..core.report import TranslationReport
from ..settings import settings
from .providers.deepl import traduire_deepl
from .providers.google import traduire_google
from .providers.mymemory import traduire_mymemory


def decouper_en_blocs(texte: str, taille_max: int = TAILLE_MAX_BLOC_TRADUCTION) -> list:
    """Découpe un texte trop long en blocs traduisibles séparément, sans
    couper au milieu d'un mot."""
    if len(texte) <= taille_max:
        return [texte] if texte.strip() else []
    blocs, bloc_courant = [], ""
    for mot in texte.split(" "):
        candidat = (bloc_courant + " " + mot) if bloc_courant else mot
        if len(candidat) <= taille_max:
            bloc_courant = candidat
        else:
            if bloc_courant:
                blocs.append(bloc_courant)
            bloc_courant = mot
    if bloc_courant:
        blocs.append(bloc_courant)
    return blocs


def traduire_un_texte(texte: str, source: str, cible: str,
                       tentatives: int = TENTATIVES_TRADUCTION,
                       cle_deepl: str = None,
                       rapport: TranslationReport = None) -> str:
    """
    Traduit un texte (avec découpage si trop long).

    cle_deepl : clé API DeepL ; sinon celle des réglages (.env) ; sinon on
    passe directement à Google Translate.
    rapport : compte quel service a traduit chaque bloc (un par traduction).
    """
    if not texte or not texte.strip():
        return texte or ""

    rapport = rapport if rapport is not None else TranslationReport()
    cle_deepl = cle_deepl or settings.deepl_api_key

    # Chaque étape : (nom dans le rapport, fonction de traduction)
    fournisseurs = []
    if cle_deepl:
        fournisseurs.append(("deepl", lambda b: traduire_deepl(b, source, cible, cle_deepl)))
    fournisseurs.append(("google", lambda b: traduire_google(b, source, cible, tentatives)))
    fournisseurs.append(("secours", lambda b: traduire_mymemory(b, source, cible)))

    resultats = []
    for bloc in decouper_en_blocs(texte):
        traduit = None
        for nom, traduire in fournisseurs:
            traduit = traduire(bloc)
            if traduit:
                rapport.ajouter(nom)
                break
        if not traduit:
            rapport.ajouter("echecs")
            traduit = bloc  # dernier recours : on garde le texte original
        resultats.append(traduit)

    return " ".join(resultats)