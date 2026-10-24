"""mymemory.py — Fournisseur MyMemory (secours), avec ses codes de langue régionaux."""
import logging

from deep_translator import MyMemoryTranslator

logger = logging.getLogger(__name__)

# MyMemory refuse "en" ou "fr" : il veut des codes régionaux.
_CODES_MYMEMORY = {
    "en": "en-GB", "fr": "fr-FR", "es": "es-ES", "pt": "pt-PT",
    "pt-br": "pt-BR", "de": "de-DE", "it": "it-IT", "ar": "ar-SA",
}


def traduire_mymemory(texte: str, source: str, cible: str) -> str | None:
    """Traduit via MyMemory. Retourne None en cas d'échec (avec un log de la cause)."""
    try:
        traducteur = MyMemoryTranslator(
            source=_CODES_MYMEMORY.get(source, source),
            target=_CODES_MYMEMORY.get(cible, cible),
        )
        return traducteur.translate(texte) or None
    except Exception as e:
        logger.warning("MyMemory : %s", type(e).__name__)
        return None