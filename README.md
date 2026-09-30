# pdf-translator

Traduit un PDF d'une langue vers une autre en conservant :
- le texte (traduit)
- les tableaux (structure + cellules traduites)
- les images (recopiées à leur place)
- la mise en forme (titres, sous-titres, gras, italique)
- le texte détecté **dans** les images (OCR), affiché en légende traduite

## Structure du projet

```
pdf_translator_pro/
├── src/pdf_translator/
│   ├── __init__.py          # point d'entrée du package (expose translate_pdf)
│   ├── __main__.py          # permet `python -m pdf_translator`
│   ├── cli.py                # interface en ligne de commande
│   ├── config.py              # constantes et seuils centralisés
│   ├── formatting.py          # détection gras/italique/titres
│   ├── ocr.py                 # reconnaissance de texte dans les images
│   ├── pipeline.py             # orchestration complète (translate_pdf)
│   ├── extraction/            # lecture du PDF source
│   │   ├── tables.py
│   │   ├── text_blocks.py
│   │   ├── images.py
│   │   ├── headers_footers.py
│   │   └── page.py
│   ├── translation/           # traduction des textes extraits
│   │   ├── engine.py           # Google Translate + secours MyMemory
│   │   └── batch.py            # déduplication + parallélisation
│   └── generation/             # reconstruction du PDF final
│       ├── styles.py
│       ├── flowables.py
│       └── pdf_builder.py
├── run.py                     # lancement rapide sans installation
├── pyproject.toml
├── requirements.txt
└── README.md
```

Chaque dossier a une seule responsabilité : si tu dois corriger un bug sur
les tableaux, tu sais que ça se passe dans `extraction/tables.py`, pas besoin
de fouiller un fichier de 800 lignes.

## Traduction avec DeepL (recommandé)

Par défaut, l'outil utilise Google Translate (traduction plutôt littérale,
parfois mot à mot). **DeepL donne une traduction bien plus fidèle au sens
et au contexte.** Si tu as une clé API DeepL :

```bash
# Option 1 : variable d'environnement (recommandé, la clé n'apparaît pas
# dans l'historique de commandes)
export DEEPL_API_KEY="ta-cle-ici:fx"      # Mac/Linux
setx DEEPL_API_KEY "ta-cle-ici:fx"        # Windows (PowerShell : $env:DEEPL_API_KEY="...")
pdf-translator document.pdf

# Option 2 : directement en argument
pdf-translator document.pdf --deepl-key "ta-cle-ici:fx"
```

**Note sur le format de la clé** : les clés gratuites DeepL se terminent
par `:fx` (ex: `a1b2c3d4-...:fx`) — le programme détecte automatiquement
s'il s'agit d'une clé gratuite ou payante (Pro) et utilise la bonne adresse
d'API en conséquence.

Si DeepL est indisponible (clé absente, invalide, ou quota mensuel
dépassé), le programme bascule automatiquement sur Google Translate, puis
sur MyMemory en dernier recours — la traduction ne s'arrête jamais
totalement à cause d'un seul service.

## Installation

### Option A — rapide, sans installation
```bash
pip install -r requirements.txt
python run.py document.pdf
```

### Option B — installation propre (commande système)
```bash
pip install -e .
pdf-translator document.pdf
```

### OCR (texte dans les images) — optionnel mais recommandé
Nécessite Tesseract installé sur la machine (pas seulement le module Python) :
- **Windows** : https://github.com/UB-Mannheim/tesseract/wiki (installer avec les packs de langue français + anglais)
- **Mac** : `brew install tesseract tesseract-lang`
- **Linux** : `apt install tesseract-ocr tesseract-ocr-fra`

Si Tesseract n'est pas installé, le programme continue de fonctionner
normalement — il ignore simplement la détection de texte dans les images.

## Utilisation

```bash
# Fenêtres de sélection de fichiers (par défaut si rien n'est précisé)
pdf-translator

# Ligne de commande directe
pdf-translator document.pdf -o document_fr.pdf --source en --cible fr

# En tant que module Python
python -c "from pdf_translator import translate_pdf; translate_pdf('doc.pdf')"
```

## Utilisation programmatique (pour intégration future : app web, SaaS)

```python
from pdf_translator import translate_pdf

def mon_log(message):
    # ex: envoyer le message à une interface web au lieu de print()
    ...

chemin_resultat = translate_pdf(
    "document.pdf",
    chemin_sortie="document_fr.pdf",
    source="en",
    cible="fr",
    on_log=mon_log,
)
```

## Limites connues

- La mise en forme (gras/italique) est détectée par ligne, pas mot par mot.
- Le texte dans les images est traduit et affiché en légende, mais l'image
  elle-même n'est pas modifiée (les pixels restent dans la langue d'origine).
- Le document reconstruit ne peut pas être identique à 100 % à l'original :
  c'est un nouveau PDF généré à partir du texte extrait, pas une copie
  pixel-perfect.

## Configuration des seuils

Tous les seuils (taille des lignes courtes, fréquence de détection des
en-têtes de page, taille des blocs de traduction...) sont centralisés dans
`src/pdf_translator/config.py`, pour être ajustés à un seul endroit.
