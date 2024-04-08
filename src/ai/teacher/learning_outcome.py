from pydantic import BaseModel, Field

class LearningOutcome(BaseModel):
    thought: str = Field(description="The fact, feeling, or motive to be learned")