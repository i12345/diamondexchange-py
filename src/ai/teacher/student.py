from pydantic import Field
from discourse.discourse import Person

class Student(Person):
    focus: str = Field(description="What the student is currently focused on studying")