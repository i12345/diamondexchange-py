from abc import ABC, abstractmethod

from pydantic import BaseModel
from tiktoken import Encoding, get_encoding

from discourse.discourse import CompletedDiscourse, DiscourseChunk, DiscourseFeatures, PartialDiscourse, PartialDiscourseWithoutContextAtEnd, TextualContext
from discourse.ingestor import DiscourseChunkIngestorContext

from dspy import Signature, InputField, OutputField, TypedPredictor

class DiscourseChunkIngestorContext(BaseModel):
    partial_discourse: PartialDiscourse

@ABC
class DiscourseChunkIngestor():
    @abstractmethod
    def ingest(self, new_chunk: DiscourseChunk, context: DiscourseChunkIngestorContext) -> dict[str, any] | None:
        pass

@ABC
class DiscourseChunkIngestorContextUpdater(DiscourseChunkIngestor):
    pass

class DiscourseChunkIngestorTextualContextUpdaterWithLLMSignature(Signature):
    """Predicts textual context after reading/listening to discourse last chunk"""

    partial_discourse: PartialDiscourseWithoutContextAtEnd = InputField()
    textual_context_at_end: TextualContext = OutputField(description="New textual context for picking up reading/listening to the text/speech after last chunk")

class DiscourseChunkIngestorTextualContextUpdaterWithLLM(DiscourseChunkIngestorContextUpdater):
    def __init__(self, ):
        super().__init__()
        self.updater = TypedPredictor(DiscourseChunkIngestorTextualContextUpdaterWithLLMSignature)

    def ingest(self, new_chunk: DiscourseChunk, context: DiscourseChunkIngestorContext) -> dict[str, any] | None:
        partial_discourse_without_context = PartialDiscourseWithoutContextAtEnd(features=context.partial_discourse.features, is_truncated=context.partial_discourse.is_truncated, prev_chunks=context.partial_discourse.prev_chunks)
        results = self.updater(partial_discourse=partial_discourse_without_context)
        partial_discourse_context_updated = context.partial_discourse.context_at_end.model_copy(update={ "textual_context":results.textual_context_at_end })
        partial_discourse_updated = context.partial_discourse.model_copy(update={ "context_at_end": partial_discourse_context_updated })
        return { "partial_discourse": partial_discourse_updated }

class DiscourseChunkIngestorContextUpdaterWithCachedResults(DiscourseChunkIngestorContextUpdater):
    def __init__(self, true_discourse: CompletedDiscourse):
        self.true_discourse = true_discourse

    def ingest(self, new_chunk: DiscourseChunk, context: DiscourseChunkIngestorContext) -> dict[str, any] | None:
        index = next(i for i, chunk in enumerate(self.true_discourse.prev_chunks) if chunk.index == new_chunk.index)
        context_at_end = self.true_discourse.prev_chunks[index + 1].context_at_start if index + 1 < len(self.true_discourse.prev_chunks) else self.true_discourse.context_at_end
        partial_discourse_updated = context.partial_discourse.model_copy(update={"context_at_end": context_at_end })
        return { "partial_discourse": partial_discourse_updated }

class DiscourseIngestor:
    def __init__(self,
                 discourse_features: DiscourseFeatures,
                 ingestors: list[DiscourseChunkIngestor],
                 max_prev_chunks_tokens: int = 2048,
                 token_enc: Encoding = get_encoding("cl100k_base")):
        self.discourse_features = discourse_features
        self.discourse = PartialDiscourse(features=discourse_features)
        self.ingestors = ingestors
        self.max_prev_chunks_tokens = max_prev_chunks_tokens
        self.token_enc = token_enc
        self.prev_chunks_token_lengths = [] # type: list[int]
        self.context = DiscourseChunkIngestorContext(discourse=self.discourse)

    def ingest(self, new_chunk: DiscourseChunk):
        new_chunk.context_at_start = self.discourse.context_at_end
        
        for ingestor in self.ingestors:
            context_updates = ingestor.ingest(new_chunk=new_chunk, context=self.context)
            if context_updates != None:
                self.context = self.context.model_copy(update=context_updates)

        self.discourse.prev_chunks.append(new_chunk)
        self.prev_chunks_token_lengths.append(len(self.token_enc.encode(new_chunk.text)))
        
        if self.max_prev_chunks_tokens > 0:
            while sum(self.prev_chunks_token_lengths) > self.max_prev_chunks_tokens:
                self.discourse.is_truncated = True
                self.discourse.prev_chunks.pop(0)
                self.prev_chunks_token_lengths.pop(0)
