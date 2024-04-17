from typing import Generator, Literal
from ai.teacher.teaching_devices.text import TextTeachingDevice
from ai.teacher.teaching_device import TeachingDeviceGenerationBaseSignature, TeachingDeviceGenerator, TeachingDeviceRecommendation, TeachingImpact
from dspy import OutputField, TypedPredictor
from src.ai.discourse.discourse import PartialDiscourse

from src.ai.teacher.student import Student

class StatementTeachingDevice(TextTeachingDevice):
    type: Literal["statement"] = "statement"

class StatementTeachingDeviceGeneratorSignature(TeachingDeviceGenerationBaseSignature):
    """State a fact to effect desired teaching impacts"""

    statement: str = OutputField()

class StatementTeachingDeviceGenerator(TeachingDeviceGenerator):
    def __init__(self):
        super().__init__()
        self.module = TypedPredictor(StatementTeachingDeviceGeneratorSignature)

    def generate(self, teaching_impacts: list[TeachingImpact], student: Student, discourse: PartialDiscourse) -> Generator[TeachingDeviceRecommendation]:
        for statement in self.module(teaching_impacts=teaching_impacts, student=student, discourse=discourse).completions.statement:
            yield StatementTeachingDevice(text=statement)
