from discourse.discourse import PartialDiscourse
from discourse.ingestor import DiscourseChunk, DiscourseChunkIngestorContext
from src.ai.teacher.student import Student
from teacher.impact_predict.base import TeachingDeviceImpactCollector, TeachingDeviceImpactPredictor, TeachingDeviceImpactPredictorFactory
from teacher.teaching_device import TeachingDevice, TeachingImpact
from dspy import Signature, InputField, OutputField, TypedPredictor

class TeachingDeviceImpactPredictorSignature(Signature):
    """Predicts the learning outcomes reached by a given teaching device"""

    discourse: PartialDiscourse = InputField()
    teaching_device: TeachingDevice = InputField()
    student: str = InputField(description="Who to predict the impact of the teaching device for")
    teaching_impacts: list[TeachingImpact] = OutputField(description="The impact(s) that this teaching device had for the student")

class TeachingDeviceImpactPredictorWithLM(TeachingDeviceImpactPredictor):
    def __init__(self, teaching_device: TeachingDevice, student: Student, collector: TeachingDeviceImpactCollector):
        super().__init__(self, teaching_device=teaching_device, student=student, collector=collector)
        self.predictor = TypedPredictor(TeachingDeviceImpactPredictorSignature)

    def ingest(self, new_chunk: DiscourseChunk, context: DiscourseChunkIngestorContext):
        for teaching_impact in self.predictor(student=self.student, new_chunk=new_chunk, context=context).completions.teaching_impacts:
            self.collector.collect(student=self.student, teaching_device=self.teaching_device, teaching_impact=teaching_impact)

class TeachingDeviceImpactPredictorWithLMFactory(TeachingDeviceImpactPredictorFactory):
    def instance(teaching_device: TeachingDevice, student: Student, collector: TeachingDeviceImpactCollector) -> TeachingDeviceImpactPredictor:
        return TeachingDeviceImpactPredictorWithLM(teaching_device=teaching_device, student=student, collector=collector)
