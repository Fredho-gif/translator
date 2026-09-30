"""
styles.py — Définit les styles reportlab (titres, corps, italique, gras,
légende d'image) utilisés pour reconstruire le PDF traduit.
"""

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet


def construire_styles() -> dict:
    """Retourne un dictionnaire {nom_style: ParagraphStyle} prêt à l'emploi."""
    styles = getSampleStyleSheet()

    style_corps = ParagraphStyle(
        "CorpsJustifie", parent=styles["Normal"],
        alignment=TA_JUSTIFY, fontSize=11, leading=15, spaceAfter=8,
    )
    style_titre1 = ParagraphStyle(
        "Titre1", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=17, leading=21,
        alignment=TA_LEFT, spaceBefore=16, spaceAfter=10,
    )
    style_titre2 = ParagraphStyle(
        "Titre2", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=13.5, leading=17,
        alignment=TA_LEFT, spaceBefore=12, spaceAfter=8,
    )
    style_italique = ParagraphStyle(
        "Italique", parent=style_corps,
        fontName="Helvetica-Oblique",
    )
    style_gras = ParagraphStyle(
        "Gras", parent=style_corps,
        fontName="Helvetica-Bold",
    )
    # Légende ajoutée sous une image quand du texte y a été détecté par OCR
    # et traduit : on ne modifie pas les pixels de l'image (fragile), on
    # affiche la traduction juste en dessous.
    style_legende_image = ParagraphStyle(
        "LegendeImage", parent=styles["Normal"],
        fontName="Helvetica-Oblique", fontSize=9, leading=12,
        textColor=colors.grey, spaceBefore=2, spaceAfter=8,
    )
    style_cellule_tableau = ParagraphStyle(
        "Cellule", parent=styles["Normal"], fontSize=9, leading=11
    )

    return {
        "titre1": style_titre1,
        "titre2": style_titre2,
        "italique": style_italique,
        "gras": style_gras,
        "normal": style_corps,
        "legende_image": style_legende_image,
        "cellule_tableau": style_cellule_tableau,
    }
