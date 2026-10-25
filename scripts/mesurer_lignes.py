"""mesurer_lignes.py — Largeur, retrait et écart de chaque ligne d'une page.

Usage : python scripts/mesurer_lignes.py mon.pdf [page]
"""
import sys

import pdfplumber

chemin = sys.argv[1]
num = int(sys.argv[2]) if len(sys.argv) > 2 else 1

with pdfplumber.open(chemin) as pdf:
    lignes = sorted(pdf.pages[num - 1].extract_text_lines(), key=lambda l: l["top"])
    largeur_max = max(l["x1"] - l["x0"] for l in lignes)
    precedent = None
    for l in lignes:
        ratio = (l["x1"] - l["x0"]) / largeur_max
        ecart = (l["top"] - precedent) if precedent is not None else 0
        t = l["text"]
        print(f"{ratio:4.2f} x0={l['x0']:5.1f} ecart={ecart:4.1f} | {t[:28]!r} ... {t[-18:]!r}")
        precedent = l["bottom"]