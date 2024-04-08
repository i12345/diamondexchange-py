from fastapi import APIRouter, HTTPException, Path, Body, Depends
from sqlmodel import Session, select
from src.models.item_collection import ItemCollection, ItemCollectionCreate, ItemCollectionUpdate, ItemCollectionChild
from src.db.database import get_session

router = APIRouter()

@router.post("/collections/", response_model=ItemCollection)
def create_collection(collection: ItemCollectionCreate, session: Session = Depends(get_session)):
    session.add(collection)
    session.commit()
    session.refresh(collection)
    return collection

@router.get("/collections/{collection_id}", response_model=ItemCollection)
def read_collection(collection_id: int, session: Session = Depends(get_session)):
    collection = session.get(ItemCollection, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection

@router.put("/collections/{collection_id}", response_model=ItemCollection)
def update_collection(collection_id: int, collection: ItemCollectionUpdate, session: Session = Depends(get_session)):
    db_collection = session.get(ItemCollection, collection_id)
    if not db_collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    collection_data = collection.dict(exclude_unset=True)
    for key, value in collection_data.items():
        setattr(db_collection, key, value)
    session.add(db_collection)
    session.commit()
    session.refresh(db_collection)
    return db_collection

@router.delete("/collections/{collection_id}", response_model=ItemCollection)
def delete_collection(collection_id: int, session: Session = Depends(get_session)):
    collection = session.get(ItemCollection, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    session.delete(collection)
    session.commit()
    return collection

@router.post("/collections/{collection_id}/add_child", response_model=ItemCollection)
def add_collection_child(collection_id: int, child: ItemCollectionChild, session: Session = Depends(get_session)):
    collection = session.get(ItemCollection, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    collection.children.append(child)
    session.commit()
    return collection

@router.delete("/collections/{collection_id}/remove_child/{child_id}", response_model=ItemCollection)
def remove_collection_child(collection_id: int, child_id: int, session: Session = Depends(get_session)):
    collection = session.get(ItemCollection, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    child_to_remove = [child for child in collection.children if child.id == child_id]
    if not child_to_remove:
        raise HTTPException(status_code=404, detail="Child not found in collection")
    collection.children.remove(child_to_remove[0])
    session.commit()
    return collection
