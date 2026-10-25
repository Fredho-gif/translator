"""pages.py — Lecture d'une sélection de pages ('20-60', '1,3,5-7')."""
from .errors import PdfTranslatorError


class InvalidPageRangeError(PdfTranslatorError, ValueError):
    """La sélection de pages est mal écrite ou hors du document."""


def analyser_pages(texte: str, nb_pages: int) -> list:
    """Retourne la liste triée des numéros de pages (indices à partir de 0).

    '20-60' -> pages 20 à 60 (numérotées à partir de 1, comme dans un lecteur PDF).
    '1,3,5-7' -> pages 1, 3, 5, 6 et 7.
    """
    pages = set()
    for morceau in texte.replace(" ", "").split(","):
        if not morceau:
            continue
        try:
            if "-" in morceau:
                debut, fin = morceau.split("-", 1)
                a, b = int(debut), int(fin)
            else:
                a = b = int(morceau)
        except ValueError:
            raise InvalidPageRangeError(f"Sélection de pages invalide : {morceau!r}")
        if a < 1 or b < a or b > nb_pages:
            raise InvalidPageRangeError(
                f"Pages {morceau!r} hors du document ({nb_pages} pages, numérotées de 1 à {nb_pages})."
            )
        pages.update(range(a - 1, b))
    if not pages:
        raise InvalidPageRangeError("Aucune page sélectionnée.")
    return sorted(pages)