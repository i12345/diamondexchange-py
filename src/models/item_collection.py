from enum import Enum
from typing import Optional
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
    collection_id: Optional[int] = Field(foreign_key='collectionitem.id')
    child_id: int = Field(foreign_key='item.id')
    # Relationship to CollectionItem
    collection: 'CollectionItem' = Relationship(back_populates='children')
    # Relationship to ItemBase (assuming inheritance or direct relation)
    child: 'Item' = Relationship(back_populates='containing_collection_child')

class CollectionItemChildCreate(BaseModel):
    local_index: Optional[int]
    local_label: Optional[str]
    child_id: int

class CollectionItemChildRead(BaseModel):
    id: int
    local_index: int
    local_label: Optional[str]
    child_id: int

class CollectionItemChildUpdate(BaseModel):
    id: int
    local_index: Optional[int]
    local_label: Optional[str]

class CollectionItemChildDelete(BaseModel):
    id: int

class CollectionItem(Item, table=True):
    name: Optional[str] = None
    child_display_class: CollectionChildDisplayClass = Field(default=CollectionChildDisplayClass.BLOCK)
    # Relationship to CollectionItemChild
    children: list[CollectionItemChild] = Relationship(back_populates='collection')

class CollectionItemCreate(CollectionItem):
    id: None = None
    children: list[CollectionItemChild | CollectionItemChildCreate]

class CollectionItemRead(CollectionItem):
    children: list[CollectionItemChildRead]

class CollectionItemUpdate(CollectionItem):
    child_display_class: Optional[CollectionChildDisplayClass]
    children_create: Optional[list[CollectionItemChildCreate]]
    children_update: Optional[list[CollectionItemChildUpdate]]
    children_delete: Optional[list[CollectionItemChildDelete]]