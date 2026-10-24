"""google.py — Fournisseur Google Translate (via deep-translator)."""
import logging
import time

from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)


def traduire_google(texte: str, source: str, cible: str, tentatives: int = 3) -> str | None:
    """Traduit via Google. Retourne None après échec de toutes les tentatives."""
    traducteur = GoogleTranslator(source=source, target=cible)
    for essai in range(1, tentatives + 1):
        try:
            traduit = traducteur.translate(texte)
            if traduit:
                return traduit
        except Exception as e:
            logger.warning("Google : %s (essai %d/%d)", type(e).__name__, essai, tentatives)
            if essai < tentatives:
                time.sleep(0.5 * essai)
    return None