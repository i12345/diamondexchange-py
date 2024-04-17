from typing import Optional
from pydantic import BaseModel

class ItemRef(BaseModel):
    root: int
    path: Optional[list[str]] = None

    def __init__(self, root: int, path: Optional[list[str]] = None):
        super().__init__(root=root, path=path)

    def extend(self, local_index) -> "ItemRef":
        return ItemRef(root=self.root, path=(self.path if self.path is not None else []) + [local_index])
