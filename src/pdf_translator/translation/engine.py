"""
engine.py — Moteur de traduction d'un texte unique.

Ordre de priorité :
  1. DeepL — si une clé API est fournie. Nettement meilleur pour préserver
     le sens et le contexte plutôt que de traduire mot à mot.
  2. Google Translate — utilisé si DeepL est absent, en échec, ou en
     quota dépassé.
  3. MyMemory — dernier recours si les deux précédents échouent.

Un blocage ponctuel d'un service ne bloque donc jamais toute la traduction.
"""

import os
import time

from deep_translator import DeeplTranslator, GoogleTranslator, MyMemoryTranslator

from ..config import TAILLE_MAX_BLOC_TRADUCTION, TENTATIVES_TRADUCTION

# Statistiques globales (incréments simples, thread-safe grâce au GIL) sur
# quel service a traduit chaque texte — utilisées pour informer/avertir
# clairement l'utilisateur à la fin.
STATS_TRADUCTION = {"deepl": 0, "google": 0, "secours": 0, "echecs_complets": 0}


def reinitialiser_stats():
    for cle in STATS_TRADUCTION:
        STATS_TRADUCTION[cle] = 0


def decouper_en_blocs(texte: str, taille_max: int = TAILLE_MAX_BLOC_TRADUCTION) -> list:
    """Découpe un texte trop long en blocs traduisibles séparément, sans
    couper au milieu d'un mot."""
    if len(texte) <= taille_max:
        return [texte] if texte.strip() else []
    blocs, bloc_courant = [], ""
    for mot in texte.split(" "):
        candidat = (bloc_courant + " " + mot) if bloc_courant else mot
        if len(candidat) <= taille_max:
            bloc_courant = candidat
        else:
            if bloc_courant:
                blocs.append(bloc_courant)
            bloc_courant = mot
    if bloc_courant:
        blocs.append(bloc_courant)
    return blocs


def _cle_deepl_est_gratuite(cle: str) -> bool:
    """Les clés DeepL gratuites se terminent par ':fx' — elles utilisent une
    URL d'API différente des clés payantes (Pro)."""
    return cle.strip().endswith(":fx")


def _traduire_avec_deepl(bloc: str, source: str, cible: str, cle_deepl: str):
    """Tente une traduction via DeepL. Retourne None en cas d'échec (clé
    invalide, quota dépassé, réseau indisponible...)."""
    try:
        traducteur = DeeplTranslator(
            source=source, target=cible,
            api_key=cle_deepl.strip(),
            use_free_api=_cle_deepl_est_gratuite(cle_deepl),
        )
        return traducteur.translate(bloc)
    except Exception:
        return None


def traduire_un_texte(texte: str, source: str, cible: str,
                       tentatives: int = TENTATIVES_TRADUCTION,
                       cle_deepl: str = None) -> str:
    """
    Traduit un texte (avec découpage si trop long).

    cle_deepl : clé API DeepL. Si absente, on utilise automatiquement la
    variable d'environnement DEEPL_API_KEY (voir plus bas) ; sinon, on
    passe directement à Google Translate.
    """
    if not texte or not texte.strip():
        return texte or ""

    cle_deepl = cle_deepl or os.environ.get("DEEPL_API_KEY")

    blocs = decouper_en_blocs(texte)
    resultats = []

    for bloc in blocs:
        traduit = None

        # 1) DeepL (meilleure qualité contextuelle), si une clé est configurée
        if cle_deepl:
            traduit = _traduire_avec_deepl(bloc, source, cible, cle_deepl)
            if traduit:
                STATS_TRADUCTION["deepl"] += 1

        # 2) Google Translate si DeepL est absent ou a échoué
        if not traduit:
            traducteur_google = GoogleTranslator(source=source, target=cible)
            for essai in range(1, tentatives + 1):
                try:
                    traduit = traducteur_google.translate(bloc)
                    if traduit:
                        STATS_TRADUCTION["google"] += 1
                        break
                except Exception:
                    if essai < tentatives:
                        time.sleep(0.5 * essai)

        # 3) MyMemory en dernier recours
        if not traduit:
            try:
                traducteur_secours = MyMemoryTranslator(source=source, target=cible)
                traduit = traducteur_secours.translate(bloc)
                if traduit:
                    STATS_TRADUCTION["secours"] += 1
            except Exception:
                traduit = None

        if not traduit:
            STATS_TRADUCTION["echecs_complets"] += 1
            traduit = bloc  # dernier recours : on garde le texte original

        resultats.append(traduit)

    return " ".join(resultats)
