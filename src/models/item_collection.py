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
    collection_id: Optional[int] = Field(foreign_key='collection_item.id')
    child_id: int = Field(foreign_key='item.id')
    # Relationship to CollectionItem
    collection: Optional["CollectionItem"] = Relationship(back_populates='children')
    # Relationship to ItemBase (assuming inheritance or direct relation)
    child: Item = Relationship(back_populates='containing_collection_child')

Item.model_rebuild()

class CollectionItem(Item, table=True):
    def __init__(self, name: Optional[str], child_display_class: Optional[CollectionChildDisplayClass], children: Optional[List["CollectionItemChild"]], **kwargs):
        super().__init__(self, **kwargs)
    
    containing_collection_child: list[CollectionItemChild] = Relationship(back_populates="child")

    name: Optional[str] = None
    child_display_class: CollectionChildDisplayClass = Field(default=CollectionChildDisplayClass.BLOCK)
    children: list[CollectionItemChild] = Relationship(back_populates='collection')
    # children = Relationship(back_populates='collection')

CollectionItemChild.model_rebuild()

class CollectionItemCreate(CollectionItem):
    id: None = None
    children: list["CollectionItemChild" | "CollectionItemChildCreate"]

class CollectionItemRead(CollectionItem):
    children: list["CollectionItemChildRead"]

class CollectionItemUpdate(CollectionItem):
    child_display_class: Optional[CollectionChildDisplayClass]
    children: Optional[list["CollectionItemChildUpdate"]]
    children_create: Optional[list["CollectionItemChildCreate"]]
    children_update: Optional[list["CollectionItemChildUpdate"]]
    children_delete: Optional[list["CollectionItemChildDelete"]]

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
