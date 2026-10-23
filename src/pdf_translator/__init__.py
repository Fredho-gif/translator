"""
pdf_translator — Traduction de PDF (texte, tableaux, images, mise en
forme, texte dans les images) avec conservation de la structure d'origine.

Utilisation simple :

    from pdf_translator import translate_pdf
    translate_pdf("document.pdf", "document_fr.pdf", source="en", cible="fr")
"""


from .pipeline import translate_pdf


__version__ = "3.1.0"
__all__ = ["translate_pdf", "__version__"]
