from abc import ABC, abstractmethod
from discourse.ingestor import DiscourseChunkIngestor
from teacher.student import Student
from teacher.teaching_device import TeachingDevice, TeachingImpact

class TeachingDeviceImpactCollector():
    impacts: dict[Student, dict[TeachingDevice, list[TeachingImpact]]] = {}

    def collect(self, student: Student, teaching_device: TeachingDevice, teaching_impact: TeachingImpact) -> None:
        if student not in self.impacts:
            self.impacts[student] = dict()
        if teaching_device not in self.impacts[student]:
            self.impacts[student][teaching_device] = []
        self.impacts[student][teaching_device].append(teaching_impact)

class TeachingDeviceImpactPredictor(DiscourseChunkIngestor, ABC):
    def __init__(self, teaching_device: TeachingDevice, student: Student, collector: TeachingDeviceImpactCollector):
        super().__init__()
        self.teaching_device = teaching_device
        self.student = student
        self.collector = collector

class TeachingDeviceImpactPredictorFactory(ABC):
    @abstractmethod
    def instance(teaching_device: TeachingDevice, student: Student, collector: TeachingDeviceImpactCollector) -> TeachingDeviceImpactPredictor:
        pass
