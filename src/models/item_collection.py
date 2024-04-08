from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from src.models.item import Item

class CollectionChildDisplayClass(str, Enum):
    INLINE = 'INLINE'
    BLOCK = 'BLOCK'
    PAGINATION = 'PAGINATION'
    TABS = 'TABS'
    ACCORDION = 'ACCORDION'
    TABLE = 'TABLE'
    TABLE_ROW = 'TABLE_ROW'

class CollectionItemChild(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint('collection_id', 'local_index', name='collection_local_index_unique'),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    local_index: int
    local_label: Optional[str]
    collection_id: int = Field(foreign_key='collectionitem.id')
    child_id: int = Field(foreign_key='item.id')
    # Relationship to CollectionItem
    collection: 'CollectionItem' = Relationship(back_populates='children')
    # Relationship to ItemBase (assuming inheritance or direct relation)
    child: 'Item' = Relationship(back_populates='containing_collection_child')

class CollectionItemChildCreate(BaseModel):
    local_index: int
    local_label: str
    collection_id: int
    child_id: int

class CollectionItemChildUpdate(BaseModel):
    local_index: Optional[int]
    local_label: Optional[str]

class CollectionItem(Item, table=True):
    name: Optional[str] = None
    child_display_class: CollectionChildDisplayClass = Field(default=CollectionChildDisplayClass.BLOCK)
    # Relationship to CollectionItemChild
    children: List[CollectionItemChild] = Relationship(back_populates='collection')

class CollectionItemCreate(CollectionItem):
    del id
    children: List[CollectionItemChild | CollectionItemChildCreate]

class CollectionItemUpdate(CollectionItem):
    child_display_class: Optional[CollectionChildDisplayClass]
    children_create: Optional[List[CollectionItemChildCreate]]
    children_update: Optional[List[CollectionItemChildUpdate]]
    children_delete: Optional[List[int]]