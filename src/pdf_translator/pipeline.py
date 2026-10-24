"""
pipeline.py — Orchestre le processus complet : extraction -> traduction
-> génération. C'est le point d'entrée "métier" du package, utilisable
depuis un script CLI, une interface web, ou un futur SaaS.
"""

import tempfile
from pathlib import Path

import fitz  # PyMuPDF
import pdfplumber

from .core.blocks import bloc_vers_dict
from .core.errors import OutputError, PdfNotFoundError
from .core.languages import valider_langues
from .extraction import extraire_contenu_page
from .extraction.headers_footers import detecter_entetes_pieds
from .formatting import detecter_taille_corps_habituelle
from .generation import generer_pdf
from .translation import appliquer_traductions, collecter_textes_uniques, traduire_en_parallele


def translate_pdf(chemin_entree: str, chemin_sortie=None,
                   source: str = "en", cible: str = "fr",
                   cle_deepl: str = None,
                   on_log=print) -> str:
    """
    Traduit un PDF de la langue source vers la langue cible, en conservant
    le texte, les tableaux, les images et la mise en forme (titres, gras,
    italique). Le texte détecté dans les images (OCR) est aussi traduit et
    affiché en légende.

    cle_deepl : clé API DeepL (recommandé pour une traduction plus fidèle
    au sens et au contexte plutôt que mot à mot). Si absente, la clé du
    fichier .env est utilisée ; sinon Google Translate (+ secours MyMemory).

    on_log : fonction appelée avec chaque message de progression (par
    défaut `print` ; peut être remplacée pour rediriger vers une UI web).
    """
    source, cible = valider_langues(source, cible)

    chemin_entree = Path(chemin_entree)
    if not chemin_entree.exists():
        raise PdfNotFoundError(f"Fichier introuvable : {chemin_entree}")

    if chemin_sortie is None:
        chemin_sortie = str(chemin_entree.with_name(f"{chemin_entree.stem}_{cible}.pdf"))
    elif not str(chemin_sortie).lower().endswith(".pdf"):
        chemin_sortie = str(chemin_sortie) + ".pdf"

    with tempfile.TemporaryDirectory() as dossier_tmp_str:
        dossier_tmp = Path(dossier_tmp_str)

        on_log(f"[1/3] Extraction du contenu (texte, tableaux, images) : {chemin_entree}")
        doc_fitz = fitz.open(str(chemin_entree))
        pages_blocs = []
        with pdfplumber.open(str(chemin_entree)) as pdf:
            nb_pages = len(pdf.pages)
            premiere_page = pdf.pages[0]
            taille_page = (premiere_page.width, premiere_page.height)

            on_log("  Détection des en-têtes / pieds de page récurrents...")
            entetes_pieds = detecter_entetes_pieds(pdf)
            if entetes_pieds:
                on_log(f"  {len(entetes_pieds)} en-tête(s)/pied(s) de page détecté(s) et exclu(s)")

            on_log("  Détection de la mise en forme (titres, sous-titres, italique)...")
            taille_corps = detecter_taille_corps_habituelle(pdf)
            on_log(f"  Taille de police du corps de texte estimée : {taille_corps:.0f}pt")

            for num_page, page_plumber in enumerate(pdf.pages):
                blocs = extraire_contenu_page(page_plumber, doc_fitz, num_page, dossier_tmp,
                                               entetes_pieds, taille_corps, source)
                # Temporaire : on repasse en dictionnaires le temps de migrer
                # la traduction et la génération vers les classes.
                blocs = [bloc_vers_dict(b) for b in blocs]
                _log_progression_extraction(on_log, num_page, nb_pages, blocs)
                pages_blocs.append(blocs)

        on_log(f"[2/3] Traduction {source} -> {cible} (en parallèle)...")
        textes_uniques = collecter_textes_uniques(pages_blocs)
        on_log(f"  {len(textes_uniques)} texte(s) unique(s) à traduire "
               f"(doublons ignorés pour gagner du temps)")
        cache = traduire_en_parallele(textes_uniques, source, cible, cle_deepl=cle_deepl)
        pages_blocs = appliquer_traductions(pages_blocs, cache)

        on_log(f"[3/3] Génération du PDF final : {chemin_sortie}")
        generer_pdf(pages_blocs, chemin_sortie, taille_page=taille_page)

    return _verifier_resultat(chemin_sortie, on_log)


def _log_progression_extraction(on_log, num_page: int, nb_pages: int, blocs: list):
    nb_tableaux = sum(1 for b in blocs if b["type"] == "table")
    nb_images = sum(1 for b in blocs if b["type"] == "image")
    nb_images_avec_texte = sum(
        1 for b in blocs if b["type"] == "image" and b.get("texte_ocr", "").strip()
    )
    nb_titres = sum(1 for b in blocs if b.get("style") in ("titre1", "titre2"))
    on_log(f"  [extraction] page {num_page + 1}/{nb_pages} "
           f"-> {len(blocs)} bloc(s) ({nb_tableaux} tableau(x), {nb_images} image(s) "
           f"dont {nb_images_avec_texte} avec texte détecté, "
           f"{nb_titres} titre(s)/sous-titre(s))")


def _verifier_resultat(chemin_sortie: str, on_log) -> str:
    """Vérifie que le fichier existe vraiment et n'est pas vide, pour ne
    jamais retourner un faux succès silencieux."""
    chemin_final = Path(chemin_sortie)
    if not chemin_final.exists():
        raise OutputError(f"Le fichier de sortie n'a pas été créé : {chemin_final}")
    taille_ko = chemin_final.stat().st_size / 1024
    if taille_ko < 1:
        raise OutputError(f"Le fichier généré est vide ou corrompu : {chemin_final}")

    on_log(f"Terminé. Fichier généré : {chemin_final.resolve()} ({taille_ko:.0f} Ko)")
    return str(chemin_final.resolve())