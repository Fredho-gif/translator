import pytest

from pdf_translator import __version__
from pdf_translator.cli import main
from pdf_translator.pipeline import translate_pdf


def test_cli_supports_version_flag(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert __version__ in captured.out


def test_translate_pdf_rejects_identical_languages():
    with pytest.raises(ValueError, match="source.*cible|cible.*source"):
        translate_pdf("document.pdf", source="fr", cible="fr")
