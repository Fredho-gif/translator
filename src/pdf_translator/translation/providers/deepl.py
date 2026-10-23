"""deepl.py — Appel direct à l'API DeepL (sans deep-translator)."""
import logging

import requests

logger = logging.getLogger(__name__)

_URL_GRATUITE = "https://api-free.deepl.com/v2/translate"
_URL_PRO = "https://api.deepl.com/v2/translate"


def traduire_deepl(texte: str, source: str, cible: str, cle: str,
                   timeout: int = 20) -> str | None:
    """Traduit via DeepL. Retourne None en cas d'échec (avec un log de la cause)."""
    cle = cle.strip()
    url = _URL_GRATUITE if cle.endswith(":fx") else _URL_PRO
    try:
        r = requests.post(
            url,
            headers={"Authorization": f"DeepL-Auth-Key {cle}"},
            data={
                "text": texte,
                "source_lang": source.split("-")[0].upper(),
                "target_lang": cible.upper(),
            },
            timeout=timeout,
        )
    except requests.RequestException as e:
        logger.warning("DeepL : erreur réseau (%s)", type(e).__name__)
        return None

    if r.status_code != 200:
        logger.warning("DeepL : code HTTP %s", r.status_code)
        return None

    return r.json()["translations"][0]["text"]