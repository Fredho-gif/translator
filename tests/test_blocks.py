from pdf_translator.core.blocks import TableBlock, TextBlock


def test_texte_traduit_sans_modifier_l_original():
    cache = {"Hello": "Bonjour"}
    t = TextBlock(top=0, bottom=1, content="Hello")
    t2 = t.appliquer(cache)
    assert t.content == "Hello"
    assert t2.content == "Bonjour"
    assert t.textes_a_traduire() == {"Hello"}


def test_tableau_cellules_vides_et_chiffres():
    cache = {"Price": "Prix", "Hello": "Bonjour"}
    tab = TableBlock(top=0, bottom=1, content=[["Price", None], ["Hello", "3"]])
    assert tab.appliquer(cache).content == [["Prix", ""], ["Bonjour", "3"]]
    assert tab.textes_a_traduire() == {"Price", "Hello", "3"}