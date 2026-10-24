"""report.py — Compte, pour UNE traduction, quel service a traduit chaque texte."""
import threading
from dataclasses import dataclass, field


@dataclass
class TranslationReport:
    deepl: int = 0
    google: int = 0
    secours: int = 0
    echecs: int = 0
    _verrou: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

    def ajouter(self, service: str) -> None:
        """Incrémente le compteur d'un service ('deepl', 'google', 'secours' ou 'echecs')."""
        with self._verrou:
            setattr(self, service, getattr(self, service) + 1)

    @property
    def total(self) -> int:
        return self.deepl + self.google + self.secours + self.echecs