"""blocks.py — Les blocs de contenu extraits d'un PDF (texte, tableau, image)."""
from dataclasses import dataclass, field, replace
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

    def textes_a_traduire(self) -> set:
        """Les textes de ce bloc qu'il faut envoyer au traducteur."""
        return set()

    def appliquer(self, cache: dict) -> "Block":
        """Retourne un NOUVEAU bloc avec les traductions du cache appliquées."""
        return self


@dataclass
class TextBlock(Block):
    type: ClassVar[str] = "text"
    content: str = ""
    style: StyleLigne = StyleLigne.NORMAL

    def textes_a_traduire(self) -> set:
        return {self.content} if self.content.strip() else set()

    def appliquer(self, cache: dict) -> "TextBlock":
        return replace(self, content=cache.get(self.content, self.content))


@dataclass
class TableBlock(Block):
    type: ClassVar[str] = "table"
    content: list = field(default_factory=list)  # liste de lignes, chaque ligne = liste de cellules

    def textes_a_traduire(self) -> set:
        return {str(c) for ligne in self.content for c in ligne if c and str(c).strip()}

    def appliquer(self, cache: dict) -> "TableBlock":
        nouvelle_table = [
            [cache.get(str(c), str(c)) if c and str(c).strip() else (c or "") for c in ligne]
            for ligne in self.content
        ]
        return replace(self, content=nouvelle_table)


@dataclass
class ImageBlock(Block):
    type: ClassVar[str] = "image"
    content: str = ""            # chemin du fichier image
    texte_ocr: str = ""
    texte_ocr_traduit: str = ""

    def textes_a_traduire(self) -> set:
        return {self.texte_ocr} if self.texte_ocr.strip() else set()

    def appliquer(self, cache: dict) -> "ImageBlock":
        if not self.texte_ocr.strip():
            return self
        return replace(self, texte_ocr_traduit=cache.get(self.texte_ocr, self.texte_ocr))


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