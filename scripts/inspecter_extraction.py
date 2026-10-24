"""inspecter_extraction.py — Affiche ce que l'extraction voit, sans traduire.

Usage : python scripts/inspecter_extraction.py mon.pdf [nb_pages] [langue] [complet]
"""
import sys
import tempfile
from pathlib import Path

import fitz
import pdfplumber

from pdf_translator.core.blocks import ImageBlock, TableBlock, TextBlock
from pdf_translator.extraction import extraire_contenu_page
from pdf_translator.extraction.headers_footers import detecter_entetes_pieds
from pdf_translator.formatting import detecter_taille_corps_habituelle


def main(chemin: str, pages_max: int = 2, langue: str = "en", complet: bool = False):
    with tempfile.TemporaryDirectory() as tmp:
        doc = fitz.open(chemin)
        with pdfplumber.open(chemin) as pdf:
            entetes = detecter_entetes_pieds(pdf)
            corps = detecter_taille_corps_habituelle(pdf)
            print(f"{len(pdf.pages)} pages, corps ≈ {corps:.0f}pt, "
                  f"{len(entetes)} en-tête(s)/pied(s) exclu(s)")
            for n, page in enumerate(pdf.pages[:pages_max]):
                print(f"\n=== Page {n + 1} ===")
                blocs = extraire_contenu_page(page, doc, n, Path(tmp), entetes, corps, langue)
                for b in blocs:
                    if isinstance(b, TextBlock):
                        texte = b.content if complet else b.content[:110]
                        print(f"[texte {b.style.value:8}] y={b.top:5.0f} {len(b.content):5} car.  {texte!r}")
                    elif isinstance(b, TableBlock):
                        print(f"[tableau        ] y={b.top:5.0f}  {len(b.content)} ligne(s)")
                    elif isinstance(b, ImageBlock):
                        print(f"[image          ] y={b.top:5.0f}  ocr={b.texte_ocr[:40]!r}")


if __name__ == "__main__":
    main(sys.argv[1],
         int(sys.argv[2]) if len(sys.argv) > 2 else 2,
         sys.argv[3] if len(sys.argv) > 3 else "en",
         len(sys.argv) > 4 and sys.argv[4] == "complet")