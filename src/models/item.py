# Base Item Model
from datetime import datetime
from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import event

class ItemChildrenDisplayClass(str, Enum):
    INLINE = 'INLINE'
    BLOCK = 'BLOCK'
    PAGINATION = 'PAGINATION'
    TABS = 'TABS'
    ACCORDION = 'ACCORDION'
    TABLE_OF_CONTENTS = "TABLE_OF_CONTENTS"
    TABLE = 'TABLE'
    TABLE_ROW = 'TABLE_ROW'

ITEM_TEXT_DELETE = "<DELETE>"

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # author_id: int = Field(foreign_key='author.id')

    text: Optional[str]

    children_display_class: ItemChildrenDisplayClass = Field(default=ItemChildrenDisplayClass.BLOCK)

    children: list["ItemChild"] = Relationship(back_populates='parent', sa_relationship_kwargs={"foreign_keys": "ItemChild.parent_id"})
    containing_item_child: list["ItemChild"] = Relationship(back_populates="child", sa_relationship_kwargs={"foreign_keys": "ItemChild.child_id"})

class ItemChild(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    added_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # adder_id: int = Field(foreign_key='author.id')

    local_index: int
    label: Optional[str]

    parent_id: Optional[int] = Field(default=None, foreign_key='item.id')
    child_id: int = Field(foreign_key='item.id')

    parent: Optional[Item] = Relationship(back_populates='children', sa_relationship_kwargs={"foreign_keys": "[ItemChild.parent_id]"})
    child: Item = Relationship(back_populates='containing_item_child', sa_relationship_kwargs={"foreign_keys": "[ItemChild.child_id]"})

    # parent: Optional[Item] = Relationship(back_populates='children', foreign_keys=[parent_id])
    # child: Item = Relationship(back_populates='containing_item_child', foreign_keys=[child_id])

# Listener function to update `updated_at` before commit
def before_update_listener(mapper, connection, target):
    target.updated_at = datetime.utcnow()

# Attaching the listener function to the `Item` class
event.listen(Item, 'before_update', before_update_listener)
event.listen(ItemChild, 'before_update', before_update_listener)

class ItemReference(BaseModel):
    id: int

class ItemChildReference(BaseModel):
    id: int

class ItemChildCreate(BaseModel):
    label: Optional[str]
    child: Union[ItemReference, "ItemCreate"]

class ItemCreate(BaseModel):
    text: Optional[str]
    children_display_class: Optional[ItemChildrenDisplayClass]
    children: list[ItemChildReference | ItemChildCreate]

class ItemChildRead(BaseModel):
    id: int
    local_index: int
    label: Optional[str]
    child: Union[ItemReference, "ItemRead"]

class ItemRead(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    author_id: int

    text: Optional[str]
    children: list[ItemChildRead]

class ItemChildUpdate(BaseModel):
    id: int
    local_index: Optional[int]
    label: Optional[str]
    child: Optional[Union[ItemCreate, "ItemUpdate"]]

class ItemUpdate(BaseModel):
    text: Optional[str]
    child_display_class: Optional[ItemChildrenDisplayClass]
    children_create: Optional[list[ItemChildCreate]]
    children_update: Optional[list[ItemChildUpdate]]
    children_remove: Optional[list["ItemChildRemove"]]

class ItemChildRemove(BaseModel):
    id: int
