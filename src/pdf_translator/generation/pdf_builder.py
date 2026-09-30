"""
pdf_builder.py — Assemble tous les blocs traduits (texte, tableaux,
images) en un PDF final avec reportlab.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from ..config import MARGE_PAGE_CM
from .flowables import construire_flowable_image, construire_flowable_tableau
from .styles import construire_styles


def _echapper_xml(texte: str) -> str:
    return (texte or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generer_pdf(pages_blocs: list, chemin_sortie: str, taille_page: tuple = A4):
    """Reconstruit le PDF final à partir des blocs traduits."""
    marge = MARGE_PAGE_CM * cm
    largeur_utile = taille_page[0] - 2 * marge

    doc = SimpleDocTemplate(
        chemin_sortie, pagesize=taille_page,
        leftMargin=marge, rightMargin=marge, topMargin=marge, bottomMargin=marge,
    )
    styles = construire_styles()

    story = []
    for i, blocs in enumerate(pages_blocs):
        for bloc in blocs:
            if bloc["type"] == "text":
                _ajouter_bloc_texte(story, bloc, styles)
            elif bloc["type"] == "table":
                story.append(construire_flowable_tableau(
                    bloc["content"], largeur_utile, styles["cellule_tableau"]
                ))
                story.append(Spacer(1, 10))
            elif bloc["type"] == "image":
                _ajouter_bloc_image(story, bloc, largeur_utile, taille_page[1], styles)
        if i < len(pages_blocs) - 1:
            story.append(PageBreak())

    doc.build(story)


def _ajouter_bloc_texte(story: list, bloc: dict, styles: dict):
    texte = _echapper_xml(bloc.get("content")).replace("\n", "<br/>")
    if not texte.strip():
        return
    style_bloc = styles.get(bloc.get("style", "normal"), styles["normal"])
    story.append(Paragraph(texte, style_bloc))
    story.append(Spacer(1, 4))


def _ajouter_bloc_image(story: list, bloc: dict, largeur_utile: float,
                         hauteur_page: float, styles: dict):
    img = construire_flowable_image(bloc["content"], largeur_utile, hauteur_page)
    if not img:
        return
    story.append(img)
    texte_ocr_traduit = (bloc.get("texte_ocr_traduit") or "").strip()
    if texte_ocr_traduit:
        legende = _echapper_xml(texte_ocr_traduit).replace("\n", " / ")
        story.append(Paragraph(f"[Texte de l'image] {legende}", styles["legende_image"]))
    story.append(Spacer(1, 10))
