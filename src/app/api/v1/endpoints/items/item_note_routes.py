from fastapi import APIRouter, HTTPException, Path, Body, Depends
from sqlmodel import Session, select
from src.models.item_note import NoteItem, NoteItemCreate, NoteItemRead, NoteItemUpdate
from src.db.database import get_session

router = APIRouter()

@router.post("/notes/", response_model=NoteItem)
def create_note(note: NoteItemCreate, session: Session = Depends(get_session)):
    session.add(note)
    session.commit()
    session.refresh(note)
    return note

@router.get("/notes/{note_id}", response_model=NoteItemRead)
def read_note(note_id: int, session: Session = Depends(get_session)):
    note = session.get(NoteItem, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.put("/notes/{note_id}", response_model=NoteItem)
def update_note(note_id: int, note_update: NoteItemUpdate, session: Session = Depends(get_session)):
    note = session.get(NoteItem, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if note_update.text is not None:
        note.text = note_update.text
    
    session.add(note)
    session.commit()
    session.refresh(note)
    return note

@router.delete("/notes/{note_id}", response_model=NoteItem)
def delete_note(note_id: int, session: Session = Depends(get_session)):
    note = session.get(NoteItem, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    session.delete(note)
    session.commit()
    return note
