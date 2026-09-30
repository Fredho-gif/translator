#!/usr/bin/env python3
"""
run.py — Point d'entrée simple : lance le traducteur sans avoir besoin
d'installer le package (utile pour un simple double-clic, ou
`python run.py` depuis ce dossier).

Pour une installation "propre" en tant que commande système, voir le
README.md (pip install -e .).
"""

import sys
from pathlib import Path

# Permet de lancer ce script directement depuis le dossier du projet,
# sans avoir à installer le package au préalable.
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf_translator.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
