from pdf_translator.extraction.text_blocks import extraire_paragraphes


class FausseePage:
    height = 800

    def __init__(self, lignes):
        self._lignes = lignes

    def extract_text_lines(self):
        return self._lignes


def ligne(top, texte, x0=72.0, x1=500.0):
    return {"top": top, "bottom": top + 14, "x0": x0, "x1": x1, "text": texte, "chars": []}


def textes(lignes):
    blocs = extraire_paragraphes(FausseePage(lignes), [], set(), 14.0)
    return [b["content"] for b in blocs]


def test_ecart_important_separe_deux_elements():
    resultat = textes([
        ligne(100, "7. PREMIER element qui continue", x0=90.7),
        ligne(116.2, "sur une deuxieme ligne et finit ici.", x1=300),
        ligne(142.2, "8. SECOND element qui commence", x0=90.7),
        ligne(158.4, "et finit sur cette ligne.", x1=250),
    ])
    assert len(resultat) == 2
    assert resultat[1].startswith("8. SECOND")


def test_retrait_seul_separe_deux_elements():
    resultat = textes([
        ligne(100, "7. PREMIER element qui continue", x0=90.7),
        ligne(116.2, "sur une deuxieme ligne qui continue encore"),
        ligne(132.4, "et une troisieme ligne qui continue aussi"),
        ligne(148.6, "avant de finir ici.", x1=300),
        ligne(164.8, "8. SECOND element qui commence", x0=90.7),
        ligne(181.0, "et finit sur cette ligne.", x1=250),
    ])
    assert len(resultat) == 2
    assert resultat[1].startswith("8. SECOND")


def test_paragraphe_normal_reste_entier():
    resultat = textes([
        ligne(100, "Une phrase qui commence ici et"),
        ligne(116.2, "continue sur la ligne suivante puis"),
        ligne(132.4, "se termine sur la troisieme ligne.", x1=300),
    ])
    assert len(resultat) == 1


def test_retrait_suspendu_ne_coupe_pas():
    resultat = textes([
        ligne(100, "1. element de liste qui continue"),
        ligne(116.2, "sur la ligne suivante en retrait.", x0=90.7, x1=300),
    ])
    assert len(resultat) == 1