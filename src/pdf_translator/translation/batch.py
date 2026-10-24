"""
batch.py — Orchestration de la traduction pour un document entier :
  1. collecter_textes_uniques  : rassemble tous les textes à traduire, sans doublons
  2. traduire_en_parallele     : les traduit avec plusieurs requêtes simultanées
  3. appliquer_traductions     : remet les traductions à leur place dans les blocs
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..config import TENTATIVES_TRADUCTION, TRADUCTIONS_PARALLELES
from ..core.errors import TranslationFailedError
from ..core.report import TranslationReport
from .engine import traduire_un_texte

logger = logging.getLogger(__name__)


def collecter_textes_uniques(pages_blocs: list) -> set:
    """Rassemble tous les textes à traduire (paragraphes + cellules + texte OCR des images), sans doublons."""
    textes = set()
    for blocs in pages_blocs:
        for bloc in blocs:
            if bloc["type"] == "text" and bloc["content"].strip():
                textes.add(bloc["content"])
            elif bloc["type"] == "table":
                for ligne in bloc["content"]:
                    for cellule in ligne:
                        if cellule and str(cellule).strip():
                            textes.add(str(cellule))
            elif bloc["type"] == "image" and bloc.get("texte_ocr", "").strip():
                textes.add(bloc["texte_ocr"])
    return textes


def traduire_en_parallele(textes_uniques: set, source: str, cible: str,
                           max_workers: int = TRADUCTIONS_PARALLELES,
                           cle_deepl: str = None,
                           on_progress=None,
                           rapport: TranslationReport = None) -> dict:
    """
    Traduit un ensemble de textes uniques en parallèle.

    cle_deepl : clé API DeepL (prioritaire sur Google/MyMemory si fournie).
    on_progress : callback optionnel appelé (termines, total) après chaque
    texte traduit — pratique pour une barre de progression dans une UI web.
    rapport : TranslationReport propre à cette traduction (créé si absent).
    """
    cache = {}
    total = len(textes_uniques)
    if total == 0:
        return cache

    rapport = rapport if rapport is not None else TranslationReport()

    termines = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(traduire_un_texte, texte, source, cible,
                            TENTATIVES_TRADUCTION, cle_deepl, rapport): texte
            for texte in textes_uniques
        }
        for future in as_completed(futures):
            texte_original = futures[future]
            try:
                cache[texte_original] = future.result()
            except Exception as e:
                logger.warning("Échec inattendu de traduction : %s", type(e).__name__)
                rapport.ajouter("echecs")
                cache[texte_original] = texte_original
            termines += 1
            if on_progress:
                on_progress(termines, total)
            elif termines % 10 == 0 or termines == total:
                print(f"  [traduction] {termines}/{total} textes uniques traités")

        _afficher_rapport(rapport, total)
    if rapport.echecs >= total:
        raise TranslationFailedError(
            "Aucun texte n'a pu être traduit : tous les services ont échoué. "
            "Vérifie ta clé DeepL (.env) et ta connexion."
        )
    return cache


def _afficher_rapport(rapport: TranslationReport, total: int):
    """Informe clairement sur la façon dont les textes ont été traduits,
    plutôt que de terminer silencieusement "avec succès"."""
    if rapport.deepl:
        print(f"  ✅ {rapport.deepl} texte(s) traduits via DeepL (qualité contextuelle)")
    if rapport.google:
        print(f"  ℹ️  {rapport.google} texte(s) traduits via Google Translate "
              f"{'(DeepL indisponible pour ceux-là)' if rapport.deepl else ''}")
    if rapport.secours:
        print(f"  ℹ️  {rapport.secours} texte(s) ont utilisé le service de secours (MyMemory)")
    if rapport.echecs:
        pourcentage = 100 * rapport.echecs / total
        print(f"  ⚠️  ATTENTION : {rapport.echecs}/{total} texte(s) ({pourcentage:.0f}%) n'ont PAS pu "
              f"être traduits (tous les services ont échoué) — "
              f"ils resteront dans la langue d'origine dans le PDF final.")
        if pourcentage > 30:
            print("  ⚠️  Ce taux d'échec élevé indique probablement un blocage réseau vers les "
                  "services de traduction (pare-feu, antivirus, VPN, ou connexion instable).")


def appliquer_traductions(pages_blocs: list, cache: dict) -> list:
    """Remplace le contenu de chaque bloc par sa traduction déjà calculée."""
    for blocs in pages_blocs:
        for bloc in blocs:
            if bloc["type"] == "text":
                bloc["content"] = cache.get(bloc["content"], bloc["content"])
            elif bloc["type"] == "table":
                nouvelle_table = []
                for ligne in bloc["content"]:
                    nouvelle_ligne = []
                    for cellule in ligne:
                        if cellule and str(cellule).strip():
                            nouvelle_ligne.append(cache.get(str(cellule), str(cellule)))
                        else:
                            nouvelle_ligne.append(cellule or "")
                    nouvelle_table.append(nouvelle_ligne)
                bloc["content"] = nouvelle_table
            elif bloc["type"] == "image" and bloc.get("texte_ocr", "").strip():
                bloc["texte_ocr_traduit"] = cache.get(bloc["texte_ocr"], bloc["texte_ocr"])
    return pages_blocs