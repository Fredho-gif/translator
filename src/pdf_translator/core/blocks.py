"""blocks.py — Les blocs de contenu extraits d'un PDF (texte, tableau, image)."""
from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar


class StyleLigne(str, Enum):
    """Style d'un bloc de texte. Hérite de str : 'titre1' == StyleLigne.TITRE1."""
    TITRE1 = "titre1"
    TITRE2 = "titre2"
    ITALIQUE = "italique"
    GRAS = "gras"
    NORMAL = "normal"


@dataclass
class Block:
    """Base commune : position verticale sur la page."""
    type: ClassVar[str] = ""
    top: float
    bottom: float


@dataclass
class TextBlock(Block):
    type: ClassVar[str] = "text"
    content: str = ""
    style: StyleLigne = StyleLigne.NORMAL


@dataclass
class TableBlock(Block):
    type: ClassVar[str] = "table"
    content: list = field(default_factory=list)  # liste de lignes, chaque ligne = liste de cellules


@dataclass
class ImageBlock(Block):
    type: ClassVar[str] = "image"
    content: str = ""            # chemin du fichier image
    texte_ocr: str = ""
    texte_ocr_traduit: str = ""


def bloc_depuis_dict(d: dict) -> Block:
    """Convertit un ancien bloc (dictionnaire) en classe."""
    genre = d["type"]
    if genre == "text":
        return TextBlock(top=d["top"], bottom=d["bottom"], content=d.get("content", ""),
                         style=StyleLigne(d.get("style", "normal")))
    if genre == "table":
        return TableBlock(top=d["top"], bottom=d["bottom"], content=d.get("content", []))
    if genre == "image":
        return ImageBlock(top=d["top"], bottom=d["bottom"], content=d.get("content", ""),
                          texte_ocr=d.get("texte_ocr", ""),
                          texte_ocr_traduit=d.get("texte_ocr_traduit", ""))
    raise ValueError(f"Type de bloc inconnu : {genre!r}")


def bloc_vers_dict(b: Block) -> dict:
    """Convertit une classe en ancien format (dictionnaire)."""
    d = {"type": b.type, "top": b.top, "bottom": b.bottom, "content": b.content}
    if isinstance(b, TextBlock):
        d["style"] = b.style.value
    elif isinstance(b, ImageBlock):
        d["texte_ocr"] = b.texte_ocr
        if b.texte_ocr_traduit:
            d["texte_ocr_traduit"] = b.texte_ocr_traduit
    return d