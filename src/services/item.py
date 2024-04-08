from typing import AsyncGenerator

from sqlmodel import or_, select
from src.models.item_collection import CollectionItemChild
from src.models.item_ref import ItemRef
from src.db.database import async_session  # Assuming async_session is your async database session

async def get_absolute_item_ids(item_ref: ItemRef) -> AsyncGenerator[int, None]:
    if item_ref.path is not None:
        async with async_session() as session:
            result = await session.execute(
                select(CollectionItemChild.childId).where(
                    CollectionItemChild.collectionId == item_ref.root,
                    or_(
                        CollectionItemChild.local_label == item_ref.path[0],
                        CollectionItemChild.local_label == None
                    )
                )
            )
            children = result.scalars().all()

        next_path = item_ref.path[1:]

        for child in children:
            async for child_id in get_absolute_item_ids(ItemRef(root=child.childId, path=next_path)):
                yield child_id
    else:
        yield item_ref.root