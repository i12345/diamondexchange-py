from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field

from src.ai.discourse.textual_context import TextualContext

class CommunicationRole(Enum):
    SPEAKER = "speaker"
    AUDIENCE = "audience"
    TEACHER = "teacher"
    STUDENT = "student"
    CONVERSANT = "conversant"
    LISTENER = "listener"
    SINGER = "singer"
    FACILITATOR = "facilitator"
    AUTHOR = "author"
    WRITER = "writer"
    READER = "reader"

class Person(BaseModel):
    name: str
    desc: str

class DiscourseMember(BaseModel):
    roles: list[CommunicationRole]
    person: Person

class DiscourseType(Enum):
    CONVERSATION = "conversation"
    DISCOURSE = "discourse"
    BOOK = "book"
    LETTER = "letter"
    SONG = "song"

class DiscourseFeatures(BaseModel):
    types: list[DiscourseType] = []
    members: list[DiscourseMember] = []

class DiscourseContext(BaseModel):
    textual_context: TextualContext = Field(default_factory=TextualContext)

class DiscourseChunk(BaseModel):
    text: str = Field(default="")
    communicator: DiscourseMember = Field(default_factory=DiscourseMember)
    index: str = Field(default="", description="index of chunk in discourse")
    context_at_start: DiscourseContext = Field(default_factory=DiscourseContext, description="Context before reading/listening to this discourse chunk")

class PartialDiscourseWithoutContextAtEnd(BaseModel):
    features: DiscourseFeatures = Field(default_factory=DiscourseFeatures)
    is_truncated_prev: bool = Field(description="Whether there are previous chunks not in this partial discourse", default=False)
    is_truncated_next: bool = Field(description="Whether there are following chunks not in this partial discourse", default=True)
    chunks: list[DiscourseChunk] = Field(description="Section of discourse in chunks. The last entry is a new chunk to consider.", default_factory=lambda: [])

class PartialDiscourse(PartialDiscourseWithoutContextAtEnd):
    context_at_end: DiscourseContext = Field(default_factory=DiscourseContext, description="Context after reading/listening to partial discourse chunks")

class CompletedDiscourse(PartialDiscourse):
    is_truncated_prev: Literal[False] = False
    is_truncated_next: Literal[False] = False