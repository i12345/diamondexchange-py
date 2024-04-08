from abc import ABC
from discourse.discourse import Person
from discourse.ingestor import DiscourseChunkIngestor
from teacher.student import Student
from teacher.teaching_device import TeachingDevice, TeachingImpact

class TeachingDeviceImpactCollector():
    impacts: dict[str, list[TeachingImpact]] = {}

    def collect(self, student: str, teaching_device: TeachingDevice) -> None:
        if student not in self.impacts:
            self.impacts[student] = []
        self.impacts[student].append(teaching_device)

class TeachingDeviceImpactPredictor(DiscourseChunkIngestor, ABC):
    def __init__(self, teaching_device: TeachingDevice, student: Student, collector: TeachingDeviceImpactCollector):
        super().__init__()
        self.teaching_device = teaching_device
        self.student = student
        self.collector = collector

class TeachingDeviceImpactPredictorFactory(ABC):
    def instance(teaching_device: TeachingDevice, student: Student, collector: TeachingDeviceImpactCollector)