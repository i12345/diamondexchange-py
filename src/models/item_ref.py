from typing import Optional
from pydantic import BaseModel

class ItemRef(BaseModel):
    root: int
    path: Optional[list[str]] = None

    def extend(self, label: Optional[str]) -> "ItemRef":
        return self if label is None else ItemRef(root=self.root, path=(self.path if self.path is not None else []) + [label])
