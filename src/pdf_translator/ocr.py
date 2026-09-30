"""
ocr.py — Reconnaissance de texte (OCR) dans les images du PDF.

Le texte natif du PDF est traduit directement, mais une image (capture
d'écran, diagramme, photo de texte) peut aussi contenir du texte que
pdfplumber ne voit pas. Ce module utilise Tesseract pour le détecter,
afin de pouvoir le traduire et l'afficher en légende.
"""

from PIL import Image as PILImage

from .config import CODES_LANGUE_TESSERACT, OCR_MIN_LETTRES, OCR_RATIO_MIN_LETTRES

try:
    import pytesseract
    OCR_DISPONIBLE = True
except ImportError:
    OCR_DISPONIBLE = False


def extraire_texte_image_ocr(chemin_image: str, langue_source: str) -> str:
    """
    Reconnaît le texte présent DANS une image via OCR. Retourne une chaîne
    vide si aucun texte significatif n'est détecté (image décorative), ou
    si Tesseract n'est pas installé sur la machine.
    """
    if not OCR_DISPONIBLE:
        return ""

    code_tesseract = CODES_LANGUE_TESSERACT.get(langue_source, "eng")
    try:
        with PILImage.open(chemin_image) as img:
            texte = pytesseract.image_to_string(img, lang=code_tesseract)
    except Exception:
        return ""

    texte = texte.strip()
    if not texte:
        return ""

    # Filtre anti-bruit : ignore les résultats trop courts ou qui ne
    # contiennent presque aucune lettre (bruit typique sur des images
    # purement graphiques/décoratives).
    nb_lettres = sum(1 for c in texte if c.isalpha())
    if nb_lettres < OCR_MIN_LETTRES or nb_lettres < len(texte) * OCR_RATIO_MIN_LETTRES:
        return ""

    return texte
