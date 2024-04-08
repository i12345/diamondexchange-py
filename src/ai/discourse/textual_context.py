from pydantic import BaseModel, Field

class SyntacticContext(BaseModel):
    pronouns: dict[str, list[str]] = Field(description="Potential pronoun resolutions")

class NarrativeSetting(BaseModel):
    time: str
    place: str
    other_setting_info: str

class TextualGenre(BaseModel):
    narrative_pace: float = Field(ge=0, le=1, description="Degree whether discourse is narrative (1) or merely expository, descriptive, or otherwise static [even if it were narrative] (0)")
    persuasive: float = Field(ge=0, le=1, description="Degree whether discourse is attempting to persuade (1) or merely inform/describe (0)")

class TextualContext(BaseModel):
    syntactic_context: SyntacticContext
    tone: str
    genre: TextualGenre
    setting: NarrativeSetting = Field(description="Setting if discourse is narrative")