from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database setup
DATABASE_URL = "sqlite:///./notes.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class NoteDB(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)

Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()

# ✅ CORS fix: allow React frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all frontend ports (React 3000/3001)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NoteIn(BaseModel):
    text: str

@app.get("/notes")
def get_notes():
    db = SessionLocal()
    notes = db.query(NoteDB).all()
    db.close()
    return [{"id": note.id, "text": note.text} for note in notes]

@app.post("/notes")
def add_note(note: NoteIn):
    db = SessionLocal()
    db_note = NoteDB(text=note.text)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    db.close()
    return {"message": "Note added", "id": db_note.id, "text": db_note.text}

@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    db = SessionLocal()
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if note:
        db.delete(note)
        db.commit()
        db.close()
        return {"message": "Note deleted"}
    db.close()
    return {"error": "Note not found"}
