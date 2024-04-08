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
    types: list[DiscourseType]
    members: list[DiscourseMember]

class DiscourseChunk(BaseModel):
    text: str
    communicator: DiscourseMember
    index: str = Field(description="index of chunk in discourse")
    textual_context: TextualContext | None

class PartialDiscourse(DiscourseFeatures):
    is_truncated: bool = Field(description="Whether there were previous chunks that have been elided from this partial discourse", default=False)
    prev_chunks: list[DiscourseChunk] = Field(description="Previous chunks of the discourse, not necessarily all", default=[])
