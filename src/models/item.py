# Base Item Model
from datetime import datetime
from typing import ForwardRef, Optional

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import event

# from src.models.item_collection import CollectionItemChild

class Item(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default=None)
    author_id: int = Field(foreign_key='author.id')

    containing_collection_child: list["CollectionItemChild"] = Relationship(back_populates="child")

# Listener function to update `updated_at` before commit
def before_update_listener(mapper, connection, target):
    target.updated_at = datetime.utcnow()

# Attaching the listener function to the `Item` class
event.listen(Item, 'before_update', before_update_listener)