"""
config.py — Configuration et constantes centralisées.

Regrouper ici toutes les valeurs "magiques" (seuils, tailles, timeouts)
évite d'avoir à les chercher dans tout le code quand on veut les ajuster.
"""

import socket

# --------------------------------------------------------------------------
# Réseau
# --------------------------------------------------------------------------

# IMPORTANT : deep-translator n'impose aucun timeout sur ses requêtes réseau.
# Sur une connexion instable ou bridée, un seul appel peut rester bloqué
# indéfiniment. Ce réglage global force une limite de 20 secondes par
# requête réseau dans tout le programme (appliqué une seule fois au chargement
# du package, voir pdf_translator/__init__.py).
TIMEOUT_RESEAU_SECONDES = 20


def appliquer_timeout_reseau():
    socket.setdefaulttimeout(TIMEOUT_RESEAU_SECONDES)


# --------------------------------------------------------------------------
# Traduction
# --------------------------------------------------------------------------

# Taille max (en caractères) d'un bloc de texte envoyé en une seule requête
# de traduction.
TAILLE_MAX_BLOC_TRADUCTION = 4500

# Nombre de tentatives avant de basculer sur le traducteur de secours
TENTATIVES_TRADUCTION = 3

# Nombre de traductions envoyées en parallèle
TRADUCTIONS_PARALLELES = 10


# --------------------------------------------------------------------------
# Mise en page / extraction
# --------------------------------------------------------------------------

# Ratio en dessous duquel une ligne est considérée "courte" (donc probablement
# un sous-titre, un élément de liste, ou un montant isolé plutôt qu'une ligne
# de prose qui continue sur la suivante).
RATIO_LIGNE_COURTE = 0.72

# Multiplicateur d'espacement vertical déclenchant un nouveau paragraphe.
RATIO_ESPACEMENT_NOUVEAU_PARAGRAPHE = 1.4

# Seuils de taille de police (relatifs à la taille du corps de texte) pour
# distinguer titre1 / titre2.
RATIO_TAILLE_TITRE1 = 1.35
RATIO_TAILLE_TITRE2 = 1.12

# Fraction de pages sur lesquelles un texte doit apparaître en haut/bas de
# page pour être considéré comme un en-tête/pied de page récurrent.
SEUIL_FREQUENCE_ENTETE_PIED = 0.35

# Taille minimale (en pixels) d'une image pour ne pas être considérée comme
# une simple puce/icône décorative.
TAILLE_MIN_IMAGE_PIXELS = 25

# Marge de page (reportlab, en cm) utilisée pour la génération du PDF final.
MARGE_PAGE_CM = 2


# --------------------------------------------------------------------------
# OCR (texte dans les images)
# --------------------------------------------------------------------------

# Correspondance code langue (ISO 639-1) -> code Tesseract
CODES_LANGUE_TESSERACT = {
    "en": "eng", "fr": "fra", "es": "spa", "pt": "por",
    "de": "deu", "it": "ita", "ar": "ara",
}

# Nombre minimal de lettres pour qu'un résultat OCR soit considéré comme du
# texte réel plutôt que du bruit
OCR_MIN_LETTRES = 4
# Fraction minimale de caractères alphabétiques dans le résultat OCR
OCR_RATIO_MIN_LETTRES = 0.4


# --------------------------------------------------------------------------
# Langues supportées (pour les interfaces utilisateur : CLI, web, SaaS)
# --------------------------------------------------------------------------

LANGUES_SUPPORTEES = {
    "en": "Anglais", "fr": "Français", "es": "Espagnol",
    "pt": "Portugais", "de": "Allemand", "it": "Italien", "ar": "Arabe",
}
