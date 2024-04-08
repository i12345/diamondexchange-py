from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from discourse.discourse import DiscourseChunkIngestor, DiscourseChunkIngestorContext, Person
from teacher.learning_outcome import LearningOutcome

class TeachingImpact(BaseModel):
    LO: LearningOutcome = Field()
    focus: float = Field(gt=0, le=1, description="How well the learning outcome is reached (1 = main point, 0.5 = detail, 0 = not taught at all)")

class TeachingDevice(ABC, BaseModel):
    type: str

class TeachingDeviceGenerator(ABC):
    @abstractmethod
    def generate(self, impacts: list[TeachingImpact], student: Person, n: int) -> list[TeachingDevice]:
        pass

class TeachingDeviceCollector():
    teaching_devices: list[TeachingDevice] = []

    def collect(self, teaching_device: TeachingDevice) -> None:
        self.teaching_devices.append(teaching_device)

class TeachingDeviceExtractorContext(DiscourseChunkIngestorContext):
    pass

class TeachingDeviceExtractorResult:
    new_context: TeachingDeviceExtractorContext
    extracted_teaching_devices: list[TeachingDevice]

class TeachingDeviceExtractor(DiscourseChunkIngestor, ABC):
    def __init__(self, collector: TeachingDeviceCollector):
        super(TeachingDeviceExtractor, self).__init__()
        self.collector = collector

    def ingest(self, prev_chunk: str, new_chunk: str, context_initial: TeachingDeviceExtractorContext) -> TeachingDeviceExtractorContext:
        result = self.extract(prev_chunk=prev_chunk, new_chunk=new_chunk, context_initial=context_initial)
        for teaching_device in result.extracted_teaching_devices:
            self.collector.collect(teaching_device=teaching_device)
        return result.new_context

    @abstractmethod
    def extract(self, prev_chunk: str, new_chunk: str, context_initial: TeachingDeviceExtractorContext) -> TeachingDeviceExtractorResult:
        pass