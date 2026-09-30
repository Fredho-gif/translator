"""
flowables.py — Construit les éléments reportlab (Table, Image) à partir
des blocs extraits du PDF source.
"""

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, Table, TableStyle
from PIL import Image as PILImage


def construire_flowable_tableau(donnees: list, largeur_utile: float, style_cellule) -> Table:
    donnees_formatees = [
        [Paragraph(str(c) if c else "", style_cellule) for c in ligne]
        for ligne in donnees
    ]
    nb_colonnes = max(len(l) for l in donnees_formatees) if donnees_formatees else 1
    largeur_colonne = largeur_utile / nb_colonnes

    table = Table(donnees_formatees, colWidths=[largeur_colonne] * nb_colonnes)
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def construire_flowable_image(chemin_image: str, largeur_utile: float, hauteur_page: float):
    try:
        with PILImage.open(chemin_image) as im:
            largeur_px, hauteur_px = im.size
        ratio = hauteur_px / largeur_px
        largeur = min(largeur_utile, largeur_px)
        hauteur = largeur * ratio
        hauteur_max = hauteur_page - 5 * cm
        if hauteur > hauteur_max:
            hauteur = hauteur_max
            largeur = hauteur / ratio
        return RLImage(chemin_image, width=largeur, height=hauteur)
    except Exception as e:
        print(f"    ! impossible d'insérer l'image {chemin_image} : {e}")
        return None
