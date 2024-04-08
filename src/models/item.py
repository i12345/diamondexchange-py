# Base Item Model
import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from src.models.item_collection import CollectionItemChild

class Item(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default=None)
    author_id: int = Field(foreign_key='author.id')

    containing_collection_child: list["CollectionItemChild"] = Relationship(back_populates="child")
