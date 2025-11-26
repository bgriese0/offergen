from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from typing import List
import os
from .database import engine, Base
from . import crud, schemas, utils
from datetime import datetime

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Offergen")

# mount static frontend
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

UPLOAD_DIR = os.path.join(os.getcwd(), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/upload", response_model=schemas.Document)
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    text = None
    try:
        text = content.decode('utf-8')
    except Exception:
        text = f"[binary file saved: {file.filename}]"

    filename = f"{int(datetime.utcnow().timestamp())}_{file.filename}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(content)

    db_doc = crud.create_document_raw(filename=filename, content=text)
    return db_doc

@app.get("/api/documents", response_model=List[schemas.Document])
def list_documents(skip: int = 0, limit: int = 100):
    return crud.get_documents(skip=skip, limit=limit)

@app.get("/api/documents/{doc_id}", response_model=schemas.Document)
def get_document(doc_id: int):
    doc = crud.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@app.delete("/api/documents/{doc_id}")
def delete_document(doc_id: int):
    crud.delete_document(doc_id)
    return {"status": "ok"}

@app.post("/api/chat")
def chat(prompt: str = Form(...)):
    docs = crud.get_all_documents()
    if len(docs) == 0:
        return {"answer": "Keine Dokumente in der Datenbank. Bitte lade Dokumente hoch."}

    texts = [d.content for d in docs]
    topk = int(os.getenv("TOP_K", 3))
    retrieved = utils.retrieve_relevant(texts, prompt, k=topk)
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key:
        answer = utils.generate_with_openai(prompt, retrieved, openai_key)
    else:
        answer = utils.generate_fallback(prompt, retrieved)
    return {"answer": answer, "retrieved": retrieved}
