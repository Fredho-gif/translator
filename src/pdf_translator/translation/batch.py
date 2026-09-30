"""
batch.py — Orchestration de la traduction pour un document entier :
  1. collecter_textes_uniques  : rassemble tous les textes à traduire, sans doublons
  2. traduire_en_parallele     : les traduit avec plusieurs requêtes simultanées
  3. appliquer_traductions     : remet les traductions à leur place dans les blocs
"""

from concurrent.futures import ThreadPoolExecutor, as_completed

from ..config import TENTATIVES_TRADUCTION, TRADUCTIONS_PARALLELES
from .engine import STATS_TRADUCTION, reinitialiser_stats, traduire_un_texte


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
                           on_progress=None) -> dict:
    """
    Traduit un ensemble de textes uniques en parallèle.

    cle_deepl : clé API DeepL (prioritaire sur Google/MyMemory si fournie).
    on_progress : callback optionnel appelé (termines, total) après chaque
    texte traduit — pratique pour brancher une barre de progression dans
    une interface web sans dupliquer la logique.
    """
    cache = {}
    total = len(textes_uniques)
    if total == 0:
        return cache

    reinitialiser_stats()

    termines = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(traduire_un_texte, texte, source, cible, TENTATIVES_TRADUCTION, cle_deepl): texte
            for texte in textes_uniques
        }
        for future in as_completed(futures):
            texte_original = futures[future]
            try:
                cache[texte_original] = future.result()
            except Exception:
                cache[texte_original] = texte_original
            termines += 1
            if on_progress:
                on_progress(termines, total)
            elif termines % 10 == 0 or termines == total:
                print(f"  [traduction] {termines}/{total} textes uniques traités")

    _avertir_si_echecs(total)
    return cache


def _avertir_si_echecs(total: int):
    """Informe/avertit clairement sur la façon dont les textes ont été
    traduits, plutôt que de terminer silencieusement "avec succès"."""
    deepl = STATS_TRADUCTION["deepl"]
    google = STATS_TRADUCTION["google"]
    secours = STATS_TRADUCTION["secours"]
    echecs = STATS_TRADUCTION["echecs_complets"]

    if deepl:
        print(f"  ✅ {deepl} texte(s) traduits via DeepL (qualité contextuelle)")
    if google:
        print(f"  ℹ️  {google} texte(s) traduits via Google Translate "
              f"{'(DeepL indisponible pour ceux-là)' if deepl else ''}")
    if secours:
        print(f"  ℹ️  {secours} texte(s) ont utilisé le service de traduction de secours (MyMemory)")
    if echecs:
        pourcentage = 100 * echecs / total
        print(f"  ⚠️  ATTENTION : {echecs}/{total} texte(s) ({pourcentage:.0f}%) n'ont PAS pu être "
              f"traduits (tous les services ont échoué) — "
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
