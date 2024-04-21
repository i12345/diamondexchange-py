from typing import Optional
from pydantic import BaseModel, Field

class PronounReference(BaseModel):
    pronoun: str
    reference: str = Field("short description of resolution for pronoun")

class SyntacticContext(BaseModel):
    pronouns: list[PronounReference] = Field(description="Potential pronoun resolutions", default_factory=list)

class NarrativeSetting(BaseModel):
    time: Optional[str] = None
    place: Optional[str] = None
    other_setting_info: Optional[str] = None

class TextualGenre(BaseModel):
    narrative_pace: Optional[float] = Field(default=None, ge=0, le=1, description="Degree whether discourse is narrative (1) or merely expository, descriptive, or otherwise static [even if it were narrative] (0)")
    persuasive: Optional[float] = Field(default=None, ge=0, le=1, description="Degree whether discourse is attempting to persuade (1) or merely inform/describe (0)")

class TextualContext(BaseModel):
    syntactic_context: SyntacticContext = Field(default_factory=SyntacticContext)
    tone: Optional[str] = Field(default=None)
    genre: TextualGenre = Field(default_factory=TextualGenre)
    setting: NarrativeSetting = Field(description="Setting if discourse is narrative", default_factory=NarrativeSetting)