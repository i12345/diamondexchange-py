from typing import Union
from fastapi import APIRouter, HTTPException, Path, Body, Depends
from sqlmodel import Session, select
from src.models.item_collection import CollectionItem, CollectionItemCreate, CollectionItemRead, CollectionItemUpdate, CollectionItemChild, CollectionItemChildCreate, CollectionItemChildUpdate, CollectionChildDisplayClass
from src.db.database import get_session

router = APIRouter()

@router.post("/collections/", response_model=CollectionItemRead)
def create_collection(collection: CollectionItemCreate, session: Session = Depends(get_session)):
    db_collection = CollectionItem()

    db_collection.author_id = collection.author_id
    db_collection.child_display_class = collection.child_display_class
    db_collection.name = collection.name

    for child_create in collection.children:
        child = CollectionItemChild(
                local_index=child_create.local_index or len(collection.children),
                local_label=child_create.local_index,
                child_id=child_create.child_id
            ) if child_create is CollectionItemChildCreate else child_create
        session.add(child)
        db_collection.children.insert(child.local_index, child)
        for i in range(len(db_collection.children)):
            db_collection.children[i].local_index = i

    session.add(db_collection)
    session.commit()
    session.refresh(db_collection)
    return db_collection

@router.get("/collections/{collection_id}", response_model=CollectionItemRead)
def read_collection(collection_id: int, session: Session = Depends(get_session)):
    collection = session.get(CollectionItem, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection

@router.put("/collections/{collection_id}", response_model=CollectionItemRead)
def update_collection(collection_id: int, collection_update: CollectionItemUpdate, session: Session = Depends(get_session)):
    db_collection = session.get(CollectionItem, collection_id)
    if not db_collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    session.add(db_collection)

    for child_create in collection_update.children_create:
        child = CollectionItemChild(
                local_index=child_create.local_index or len(db_collection.children),
                local_label=child_create.local_index,
                child_id=child_create.child_id
            ) if child_create is CollectionItemChildCreate else child_create
        session.add(child)
        db_collection.children.insert(child.local_index, child)
        session.commit()
        for i in range(len(db_collection.children)):
            db_collection.children[i].local_index = i

    for child_update in collection_update.children_update:
        child = next(child_search for child_search in db_collection.children if child_search.id == child_update.id)
        session.add(child)
        if child_update.local_index is not None and child_update.local_index != child.local_index:
            db_collection.children.remove(child)
            db_collection.children.insert(child.local_index, child)
            for i in range(len(db_collection.children)):
                db_collection.children[i].local_index = i

    for child_delete in collection_update.children_delete:
        child = next(child_search for child_search in db_collection.children if child_search.id == child_delete.id)
        db_collection.children.remove(child)
        session.delete(child)
        session.commit()
        for i in range(len(db_collection.children)):
            db_collection.children[i].local_index = i

    session.commit()
    session.refresh(db_collection)
    return db_collection

@router.delete("/collections/{collection_id}", response_model=CollectionItemRead)
def delete_collection(collection_id: int, session: Session = Depends(get_session)):
    collection = session.get(CollectionItem, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    for child in collection.children:
        session.delete(child)
    session.delete(collection)
    session.commit()
    return collection
