from .database import SessionLocal
from .models import Document
from datetime import datetime

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_document_raw(filename: str, content: str):
    db = next(get_db())
    doc = Document(filename=filename, content=content, created_at=datetime.utcnow())
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def get_documents(skip: int = 0, limit: int = 100):
    db = next(get_db())
    return db.query(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit).all()

def get_all_documents():
    db = next(get_db())
    return db.query(Document).order_by(Document.created_at.desc()).all()

def get_document(doc_id: int):
    db = next(get_db())
    return db.query(Document).filter(Document.id == doc_id).first()

def delete_document(doc_id: int):
    db = next(get_db())
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if doc:
        db.delete(doc)
        db.commit()
