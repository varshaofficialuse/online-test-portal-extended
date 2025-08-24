from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.core.database import get_db
from app.core.config import settings
from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteOut
from  app.api.routers.auth import admin_required
import os



router = APIRouter()
auth_scheme = HTTPBearer()


@router.post("/", response_model=NoteOut)
def create_note(data: NoteCreate, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    note = Note(user_id=current_user.id, title=data.title, content=data.content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/", response_model=list[NoteOut])
def list_notes(db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    return db.query(Note).filter(Note.user_id == current_user.id).all()

@router.get("/{note_id}", response_model=NoteOut)
def get_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"ok": True}
