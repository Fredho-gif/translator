"""
cli.py — Interface en ligne de commande.

Usage :
    python -m pdf_translator document.pdf
    python -m pdf_translator document.pdf -o document_fr.pdf --source en --cible fr

Si le fichier d'entrée ou de sortie n'est pas fourni, des fenêtres de
sélection natives (tkinter) s'ouvrent automatiquement ; à défaut
(environnement sans interface graphique), une saisie au clavier est
proposée en repli.
"""

import argparse
import sys
import traceback
from pathlib import Path

from . import __version__
from .pipeline import translate_pdf


def _choisir_fichiers_interactivement(pdf_entree, output):
    """Ouvre des fenêtres de sélection natives, ou retombe sur la saisie clavier."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        fenetre_racine = tk.Tk()
        fenetre_racine.withdraw()
        fenetre_racine.attributes("-topmost", True)

        if not pdf_entree:
            print("Choisis le fichier PDF à traduire dans la fenêtre qui s'ouvre...")
            pdf_entree = filedialog.askopenfilename(
                title="Choisir le PDF à traduire",
                filetypes=[("Fichiers PDF", "*.pdf")],
            )

        if pdf_entree and not output:
            print("Choisis où enregistrer le PDF traduit...")
            nom_propose = Path(pdf_entree).stem + "_fr.pdf"
            output = filedialog.asksaveasfilename(
                title="Enregistrer le PDF traduit sous...",
                initialfile=nom_propose,
                defaultextension=".pdf",
                filetypes=[("Fichiers PDF", "*.pdf")],
            )

        fenetre_racine.destroy()
    except Exception:
        if not pdf_entree:
            pdf_entree = input("Chemin du fichier PDF à traduire : ").strip().strip('"').strip("'")
        if not output:
            reponse = input(
                "Chemin du fichier de sortie (laisser vide pour un nom automatique) : "
            ).strip().strip('"').strip("'")
            output = reponse if reponse else None

    return pdf_entree, output


def main(argv=None):
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        description="Traduit un PDF (texte, tableaux, images, mise en forme, texte dans les images)."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("pdf_entree", nargs="?", default=None,
                         help="Chemin du fichier PDF source")
    parser.add_argument("-o", "--output", help="Chemin du fichier de sortie", default=None)
    parser.add_argument("--source", default="en", help="Langue source (défaut: en)")
    parser.add_argument("--cible", default="fr", help="Langue cible (défaut: fr)")
    parser.add_argument("--deepl-key", default=None,
                         help="Clé API DeepL (sinon, la variable d'environnement "
                              "DEEPL_API_KEY est utilisée automatiquement si elle existe)")
    args = parser.parse_args(argv)

    pdf_entree, output = args.pdf_entree, args.output
    if not pdf_entree or not output:
        pdf_entree, output = _choisir_fichiers_interactivement(pdf_entree, output)

    if not pdf_entree:
        print("\n❌ Erreur : aucun fichier PDF sélectionné.", file=sys.stderr)
        sys.exit(2)

    if output and not output.lower().endswith(".pdf"):
        output += ".pdf"

    try:
        chemin = translate_pdf(pdf_entree, chemin_sortie=output or None,
                                source=args.source, cible=args.cible,
                                cle_deepl=args.deepl_key)
        print(f"\n✅ SUCCÈS — Fichier généré : {chemin}")
    except Exception as e:
        print(f"\n❌ Erreur : {e}", file=sys.stderr)
        print("\n--- Détail technique (à copier-coller pour obtenir de l'aide) ---", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
