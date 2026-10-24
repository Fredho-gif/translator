"""errors.py — Exceptions personnalisées du projet."""


class PdfTranslatorError(Exception):
    """Base de toutes les erreurs du projet."""


# Elles héritent aussi des exceptions standard pour que le code existant
# (qui attrape ValueError / FileNotFoundError) continue de fonctionner.
class InvalidLanguageError(PdfTranslatorError, ValueError):
    """Code de langue invalide ou source == cible."""


class PdfNotFoundError(PdfTranslatorError, FileNotFoundError):
    """Le PDF d'entrée n'existe pas."""


class OutputError(PdfTranslatorError, RuntimeError):
    """Le PDF généré est absent ou vide."""
    
class TranslationFailedError(PdfTranslatorError, RuntimeError):
    """Aucun texte n'a pu être traduit (tous les services ont échoué)."""