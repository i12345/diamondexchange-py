from typing import Generator

from sqlmodel import or_, select
from src.models.item import ItemChild
from src.models.item_ref import ItemRef
from src.db.database import get_session

def get_absolute_item_ids(item_ref: ItemRef) -> Generator[int, None]:
    if item_ref.path is not None:
        with get_session() as session:
            result = session.exec(
                select(ItemChild.childId).where(
                    ItemChild.collectionId == item_ref.root,
                    or_(
                        ItemChild.label == item_ref.path[0],
                        ItemChild.label == None
                    )
                )
            )
            children = result.scalars().all()

        next_path = item_ref.path[1:]

        for child in children:
            for child_id in get_absolute_item_ids(ItemRef(root=child.childId, path=next_path)):
                yield child_id
    else:
        yield item_ref.root