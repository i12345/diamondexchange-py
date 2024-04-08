from typing import Optional
from src.models.item import Item

class NoteItem(Item, table=True):
    text: str

class NoteItemCreate(NoteItem):
    pass

class NoteItemRead(NoteItem):
    pass

class NoteItemUpdate(NoteItem):
    text: Optional[str]