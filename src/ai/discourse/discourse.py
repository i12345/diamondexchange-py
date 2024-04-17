from enum import Enum
from pydantic import BaseModel, Field

from discourse.textual_context import TextualContext

class CommunicationRole(Enum):
    SPEAKER = "speaker"
    AUDIENCE = "audience"
    TEACHER = "teacher"
    STUDENT = "student"
    CONVERSANT = "conversant"
    LISTENER = "listener"
    FACILITATOR = "facilitator"

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
    is_truncated: bool = Field(description="Whether there were previous chunks that have been elided from this partial discourse", default=False)
    prev_chunks: list[DiscourseChunk] = Field(description="Previous chunks of the discourse, not necessarily all", default_factory=lambda: [])

class PartialDiscourse(PartialDiscourseWithoutContextAtEnd):
    context_at_end: DiscourseContext = Field(default_factory=DiscourseContext, description="Context after reading/listening to the previous discourse chunks")

class CompletedDiscourse(PartialDiscourse):
    is_truncated = False