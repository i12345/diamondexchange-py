from typing import Generator, Optional
from sqlmodel import Session, or_, select
from src.models.item import Item, ItemChild
from src.models.item_ref import ItemRef

def get_absolute_item_ids(item_ref: ItemRef, session: Session) -> Generator[int, None, None]:
    if item_ref.path is not None and len(item_ref.path) > 0:
        result = session.exec(
            select(ItemChild.child_id).where(
                ItemChild.parent_id == item_ref.root,
                or_(
                    ItemChild.label == item_ref.path[0],
                    ItemChild.label == None
                )
            )
        )

        children = result.scalars().all()
        next_path = item_ref.path[1:]

        for child in children:
            for child_id in get_absolute_item_ids(ItemRef(root=child, path=next_path)):
                yield child_id
    else:
        yield item_ref.root

def get_items(item_ref: ItemRef, session: Optional[Session]) -> Generator[Item, None, None]:
    for item_id in get_absolute_item_ids(item_ref=item_ref, session=session):
        yield session.get(Item, item_id)
