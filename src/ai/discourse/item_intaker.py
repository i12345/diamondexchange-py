
from abc import ABC, abstractmethod
from typing import Optional
from src.ai.discourse.discourse import DiscourseChunk, DiscourseMember
from src.ai.discourse.ingestor import DiscourseIngestor

from src.models.item import Item
from src.models.item_ref import ItemRef

from tiktoken import Encoding, get_encoding

class ItemsIndex(ABC):
    @abstractmethod
    def extend(self, item: ItemRef) -> bool:
        pass

    @abstractmethod
    def to_string() -> str:
        pass

class ItemIndexer(ABC):
    @abstractmethod
    def index_new(self, ref: ItemRef) -> ItemsIndex:
        pass

    @abstractmethod
    def index_child_local(self, ref: ItemRef) -> str:
        pass

    @abstractmethod
    def index_parse(self, format: str) -> ItemsIndex:
        pass

class ItemIntaker:
    def __init__(self, discourse_ingestor: DiscourseIngestor, item_indexer: ItemIndexer, chunk_token_limit: int = 1024, token_enc: Encoding = get_encoding("cl100k_base")):
        self.discourse_ingestor = discourse_ingestor
        self.item_indexer = item_indexer
        self.current_chunk = None # type: DiscourseChunk | None
        self.current_index = None # type: ItemsIndex | None
        self.chunk_token_limit = chunk_token_limit
        self.token_enc = token_enc

    def item_communicator(self, item: Item) -> DiscourseMember:
        if len(self.discourse_ingestor.discourse_features.members) >= 1:
            return self.discourse_ingestor.discourse_features.members[0]
        else:
            raise NotImplementedError()

    def start_new_chunk(self, communicator: DiscourseMember, ref: ItemRef):
        if self.current_chunk is not None:
            self.finish_current_chunk()
        self.current_chunk = DiscourseChunk(text="", communicator=communicator)
        self.current_index = self.item_indexer.index_new(ref)

    def finish_current_chunk(self):
        self.current_chunk.index = self.current_index.to_string()
        self.discourse_ingestor.ingest(self.current_chunk)
        self.current_chunk = None
        self.current_index = None

    def add_to_current_chunk(self, text: Optional[str], communicator: DiscourseMember, ref: ItemRef):
        if (self.current_chunk is not None and
            text is not None and len(self.token_enc.encode(self.current_chunk.text + text)) >= self.chunk_token_limit):
            self.finish_current_chunk()

        if self.current_chunk is None:
            self.start_new_chunk(communicator=communicator, ref=ref)
        else:
            if self.current_index.extend(ref) == False:
                self.start_new_chunk(communicator=communicator, ref=ref)
        
        if text is not None:
            if len(self.current_chunk.text) == 0:
                self.current_chunk.text = text
            else:
                self.current_chunk.text += " " + text

    def intake(self, item: Item, ref: ItemRef, trail: dict[int, str] = dict()):
        def intake_recursive(item: Item, ref: ItemRef, trail: dict[int, str], was_last_child_labeled: bool):
            communicator = self.item_communicator(item)

            if self.current_chunk is None or communicator != self.current_chunk.communicator:
                self.start_new_chunk(communicator=communicator, ref=ref)

            text_to_add = self.item_indexer.index_child_local(ref) if was_last_child_labeled and ref.path is not None and len(ref.path) > 0 else None

            if item.id in trail:
                ref_index_str = f"({trail[item.id]})"
                if text_to_add is None:
                    text_to_add = ref_index_str
                else:
                    text_to_add += " " + ref_index_str
                
                self.add_to_current_chunk(text_to_add, communicator=communicator, ref=ref)
            else:
                trail[item.id] = self.item_indexer.index_new(ref).to_string()

                if item.text is not None:
                    if text_to_add is None:
                        text_to_add = item.text
                    else:
                        text_to_add += " " + item.text
                
                self.add_to_current_chunk(text_to_add, communicator=communicator, ref=ref)

                for child in item.children:
                    intake_recursive(child.child, ref.extend(child.label), trail=trail, was_last_child_labeled=child.label is not None)
        
        intake_recursive(item=item, ref=ref, trail=dict(), was_last_child_labeled=False)