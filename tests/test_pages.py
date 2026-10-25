import pytest

from pdf_translator.core.pages import InvalidPageRangeError, analyser_pages


def test_plage_simple():
    assert analyser_pages("2-4", 10) == [1, 2, 3]


def test_liste_et_plages():
    assert analyser_pages("1,3,5-6", 10) == [0, 2, 4, 5]


def test_une_seule_page():
    assert analyser_pages("7", 10) == [6]


def test_hors_du_document():
    with pytest.raises(InvalidPageRangeError):
        analyser_pages("5-20", 10)


def test_texte_invalide():
    with pytest.raises(InvalidPageRangeError):
        analyser_pages("abc", 10)


def test_plage_inversee():
    with pytest.raises(InvalidPageRangeError):
        analyser_pages("6-2", 10)