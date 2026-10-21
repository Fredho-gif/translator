"""
api.py — Le serveur web de pdf_translator_pro.

Ce fichier expose ton moteur Python (PDF, OCR, IA) sous forme
d'API HTTP, que le navigateur pourra appeler plus tard.

Pour lancer : python api.py
"""
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


# 1. On crée l'application FastAPI
app = FastAPI(title="pdf_translator_pro API", version="0.1.0")


# 2. On autorise le navigateur à appeler cette API.
#    (Sans ça, le HTML plus tard serait bloqué par sécurité.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # en dev uniquement — on restreindra plus tard
    allow_methods=["*"],
    allow_headers=["*"],
)


# 3. Notre première route : /ping
#    Elle répond juste {"status": "ok"} pour vérifier que ça marche.
@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Le serveur pdf_translator_pro est vivant 🚀"}

# ---- ROUTES POUR LES CHAPITRES ----
# Pour l'instant, on renvoie des chapitres bidon ("mock").
# Plus tard, ils viendront de la vraie base de données / du moteur PDF.

# Faux chapitres en mémoire (temporaire)
fake_chapters = [
    {
        "id": 1,
        "title": "Chapitre 1 — L'aube",
        "content": "Il était une fois un écrivain qui découvrait FastAPI..."
    },
    {
        "id": 2,
        "title": "Chapitre 2 — La nuit",
        "content": "La nuit tomba sur le clavier, et le code devint poésie."
    },
]


@app.get("/chapters")
def list_chapters():
    """Renvoie la liste des chapitres (version de test pour l'instant)."""
    return {"chapters": fake_chapters}

# 4. Point d'entrée : quand tu tapes `python api.py`, ça lance le serveur.
if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)

"""
api.py — Le serveur web de pdf_translator_pro.

Ce fichier expose ton moteur Python (PDF, OCR, IA) sous forme
d'API HTTP, que le navigateur pourra appeler plus tard.

Pour lancer : python api.py
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


# 1. On crée l'application FastAPI
app = FastAPI(title="pdf_translator_pro API", version="0.1.0")


# 2. On autorise le navigateur à appeler cette API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# 3. Route de santé : /ping
@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Le serveur pdf_translator_pro est vivant 🚀"}


# ⬇️⬇️⬇️ AJOUT — ROUTES POUR LES CHAPITRES ⬇️⬇️⬇️

# Faux chapitres en mémoire (temporaire, pour tester)
fake_chapters = [
    {
        "id": 1,
        "title": "Chapitre 1 — L'aube",
        "content": "Il était une fois un écrivain qui découvrait FastAPI..."
    },
    {
        "id": 2,
        "title": "Chapitre 2 — La nuit",
        "content": "La nuit tomba sur le clavier, et le code devint poésie."
    },
]


@app.get("/chapters")
def list_chapters():
    """Renvoie la liste des chapitres (version de test pour l'instant)."""
    return {"chapters": fake_chapters}

# ⬆️⬆️⬆️ FIN DE L'AJOUT ⬆️⬆️⬆️

# ---- Sert la page HTML du dossier frontend/ ----

# Accessible sur : /app/
app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")
from pydantic import BaseModel

class ChapterUpdate(BaseModel):
    content: str

@app.put("/chapters/{chapter_id}")
def update_chapter(chapter_id: int, payload: ChapterUpdate):
    for ch in fake_chapters:
        if ch["id"] == chapter_id:
            ch["content"] = payload.content
            return {"status": "ok", "chapter": ch}
    return {"status": "error", "message": "Chapitre introuvable"}
    
# 4. Point d'entrée : quand tu tapes `python api.py`, ça lance le serveur.
if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)