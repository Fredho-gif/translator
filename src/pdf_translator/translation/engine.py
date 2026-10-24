"""
engine.py — Moteur de traduction d'un texte unique.

Ordre de priorité :
  1. DeepL — si une clé API est fournie (appel direct à l'API).
  2. Google Translate — si DeepL est absent, en échec ou en quota dépassé.
  3. MyMemory — dernier recours.

Un blocage ponctuel d'un service ne bloque donc jamais toute la traduction.
Chaque traduction compte ses résultats dans son propre TranslationReport.
"""

import logging
import time

from deep_translator import GoogleTranslator, MyMemoryTranslator

from ..config import TAILLE_MAX_BLOC_TRADUCTION, TENTATIVES_TRADUCTION
from ..core.report import TranslationReport
from ..settings import settings
from .providers.deepl import traduire_deepl

logger = logging.getLogger(__name__)


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

    resultats = []
    for bloc in decouper_en_blocs(texte):
        traduit = None

        # 1) DeepL
        if cle_deepl:
            traduit = traduire_deepl(bloc, source, cible, cle_deepl)
            if traduit:
                rapport.ajouter("deepl")

        # 2) Google Translate
        if not traduit:
            traducteur_google = GoogleTranslator(source=source, target=cible)
            for essai in range(1, tentatives + 1):
                try:
                    traduit = traducteur_google.translate(bloc)
                    if traduit:
                        rapport.ajouter("google")
                        break
                except Exception as e:
                    logger.warning("Google : %s (essai %d/%d)",
                                   type(e).__name__, essai, tentatives)
                    if essai < tentatives:
                        time.sleep(0.5 * essai)

        # 3) MyMemory
        if not traduit:
            try:
                traduit = MyMemoryTranslator(source=source, target=cible).translate(bloc)
                if traduit:
                    rapport.ajouter("secours")
            except Exception as e:
                logger.warning("MyMemory : %s", type(e).__name__)
                traduit = None

        if not traduit:
            rapport.ajouter("echecs")
            traduit = bloc  # dernier recours : on garde le texte original

        resultats.append(traduit)

    return " ".join(resultats)