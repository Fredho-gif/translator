"""
images.py — Extraction des images natives d'une page PDF.

Utilise PyMuPDF (fitz) pour extraire les images embarquées avec leur
position exacte, puis lance l'OCR (module ocr.py) pour détecter un
éventuel texte à traduire.
"""

from pathlib import Path

from PIL import Image as PILImage

from ..config import TAILLE_MIN_IMAGE_PIXELS
from ..ocr import extraire_texte_image_ocr


def extraire_images(doc_fitz, num_page: int, dossier_tmp: Path, langue_source: str = "en") -> list:
    """Extrait les images natives d'une page avec leur position verticale,
    et détecte par OCR si elles contiennent du texte à traduire."""
    blocs = []
    page_fitz = doc_fitz[num_page]
    try:
        infos = page_fitz.get_image_info(xrefs=True)
    except Exception:
        infos = []

    for i, info in enumerate(infos):
        xref = info.get("xref", 0)
        bbox = info.get("bbox", (0, 0, 0, 0))
        if xref == 0:
            continue
        try:
            base_image = doc_fitz.extract_image(xref)
        except Exception:
            continue
        donnees = base_image["image"]
        ext = base_image.get("ext", "png")
        chemin_image = dossier_tmp / f"page{num_page + 1}_img{i}.{ext}"
        with open(chemin_image, "wb") as f:
            f.write(donnees)

        # Ignore les images trop petites (souvent des puces/icônes décoratives)
        try:
            with PILImage.open(chemin_image) as im:
                largeur, hauteur = im.size
            if largeur < TAILLE_MIN_IMAGE_PIXELS or hauteur < TAILLE_MIN_IMAGE_PIXELS:
                continue
        except Exception:
            pass

        texte_ocr = extraire_texte_image_ocr(str(chemin_image), langue_source)

        blocs.append({
            "type": "image",
            "top": bbox[1],
            "bottom": bbox[3],
            "content": str(chemin_image),
            "texte_ocr": texte_ocr,
        })
    return blocs
