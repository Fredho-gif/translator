"""languages.py — Langues supportées et validation des codes de langue."""
import re

from .errors import InvalidLanguageError

LANGUES_SUPPORTEES = {
    "en": "Anglais", "fr": "Français", "es": "Espagnol",
    "pt": "Portugais", "de": "Allemand", "it": "Italien", "ar": "Arabe",
}

# 2 lettres, avec une région optionnelle : "fr", "pt-br"
_MOTIF_CODE = re.compile(r"[a-z]{2}(-[a-z]{2})?")


def valider_code_langue(code: str, nom: str) -> str:
    """Valide et normalise un code de langue (ex: ' FR ' -> 'fr')."""
    if not isinstance(code, str):
        raise InvalidLanguageError(f"Le code de langue {nom} doit être une chaîne de caractères.")
    code_normalise = code.strip().lower()
    if not _MOTIF_CODE.fullmatch(code_normalise):
        raise InvalidLanguageError(
            f"Le code de langue {nom} est invalide : '{code}'. "
            "Utilise un code comme 'fr', 'en', 'es' ou 'pt-br'."
        )
    return code_normalise


def valider_langues(source: str, cible: str) -> tuple[str, str]:
    """Valide la paire source/cible et vérifie qu'elles sont différentes."""
    source = valider_code_langue(source, "source")
    cible = valider_code_langue(cible, "cible")
    if source == cible:
        raise InvalidLanguageError("La langue source et la langue cible doivent être différentes.")
    return source, cible