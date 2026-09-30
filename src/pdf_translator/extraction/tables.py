"""
tables.py — Extraction des tableaux d'une page PDF.
"""


def extraire_tableaux(page_plumber) -> list:
    """Retourne les tableaux d'une page avec leur position verticale (top)."""
    blocs = []
    try:
        tables = page_plumber.find_tables()
    except Exception:
        tables = []
    for table in tables:
        try:
            contenu = table.extract()
        except Exception:
            continue
        if contenu:
            blocs.append({
                "type": "table",
                "top": table.bbox[1],
                "bottom": table.bbox[3],
                "content": contenu,
            })
    return blocs
