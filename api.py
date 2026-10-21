"""api.py — Serveur web de pdf_translator_pro (version temporaire, avant réorganisation)."""
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="pdf_translator_pro API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev uniquement
    allow_methods=["*"],
    allow_headers=["*"],
)

fake_chapters = [
    {"id": 1, "title": "Chapitre 1 — L'aube",
     "content": "Il était une fois un écrivain qui découvrait FastAPI..."},
    {"id": 2, "title": "Chapitre 2 — La nuit",
     "content": "La nuit tomba sur le clavier, et le code devint poésie."},
]


class ChapterUpdate(BaseModel):
    content: str


@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Le serveur pdf_translator_pro est vivant 🚀"}


@app.get("/chapters")
def list_chapters():
    return {"chapters": fake_chapters}


@app.put("/chapters/{chapter_id}")
def update_chapter(chapter_id: int, payload: ChapterUpdate):
    for ch in fake_chapters:
        if ch["id"] == chapter_id:
            ch["content"] = payload.content
            return {"status": "ok", "chapter": ch}
    raise HTTPException(status_code=404, detail="Chapitre introuvable")


# Le montage statique doit rester en dernier
app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)