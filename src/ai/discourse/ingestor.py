from abc import ABC, abstractmethod

from pydantic import BaseModel

from discourse.discourse import DiscourseChunk, DiscourseFeatures, PartialDiscourse, TextualContext
from discourse.ingestor import DiscourseChunkIngestorContext

from dspy import Signature, InputField, OutputField, TypedPredictor

class DiscourseChunkIngestorContext(BaseModel):
    partial_discourse: PartialDiscourse

class DiscourseChunkIngestor(ABC):
    @abstractmethod
    def ingest(self, new_chunk: DiscourseChunk, context: DiscourseChunkIngestorContext):
        pass

class DiscourseChunkIngestorTextualContextUpdater(ABC):
    @abstractmethod
    def update(self, new_chunk: DiscourseChunk, context: DiscourseChunkIngestorContext) -> TextualContext:
        pass

class DiscourseChunkIngestorTextualContextUpdaterWithLLMSignature(Signature):
    partial_discourse: PartialDiscourse = InputField()
    new_textual_context: TextualContext = OutputField(desc="New textual context for picking up reading/listening to the text/speech after last chunk")

class DiscourseChunkIngestorTextualContextUpdaterWithLLM(DiscourseChunkIngestorTextualContextUpdater):
    def __init__(self, ):
        super().__init__()
        self.updater = TypedPredictor(DiscourseChunkIngestorTextualContextUpdaterWithLLMSignature)

    def update(self, new_chunk: DiscourseChunk, context: DiscourseChunkIngestorContext) -> TextualContext:
        results = self.updater(partial_discourse=context.partial_discourse, new_chunk=new_chunk)
        return results.new_textual_context

class DiscourseChunkIngestorTextualContextUpdaterWithCachedResults(DiscourseChunkIngestorTextualContextUpdater):
    def update(self, new_chunk: DiscourseChunk, context: DiscourseChunkIngestorContext) -> TextualContext:
        return new_chunk.textual_context

class DiscourseIngestor:
    def __init__(self,
                 discourse_features: DiscourseFeatures,
                 ingestors: list[DiscourseChunkIngestor],
                 max_prev_chunks_length: int = 1024,
                 textual_context_updater: DiscourseChunkIngestorTextualContextUpdater = DiscourseChunkIngestorTextualContextUpdaterWithCachedResults()):
        self.discourse_features = discourse_features
        self.discourse = PartialDiscourse(types=discourse_features.types, members=discourse_features.members)
        self.ingestors = ingestors
        self.max_prev_chunks_length = max_prev_chunks_length
        self.textual_context_updater = textual_context_updater
        self.context = DiscourseChunkIngestorContext(discourse=self.discourse, textual_context=TextualContext())

    def ingest(self, new_chunk: DiscourseChunk):
        new_chunk.textual_context = self.textual_context_updater.update(new_chunk=new_chunk, context_initial=self.context)
        
        for ingestor in self.ingestors:
            ingestor.ingest(new_chunk=new_chunk, context=self.context)

        self.discourse.prev_chunks.append(new_chunk)
        if self.max_prev_chunks_length > 0:
            while sum(len(chunk.text) for chunk in self.discourse.prev_chunks) > self.max_prev_chunks_length:
                self.discourse.is_truncated = True
                self.discourse.prev_chunks.pop(0)