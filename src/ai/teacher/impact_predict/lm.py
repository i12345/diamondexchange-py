from discourse.discourse import DiscourseFeatures
from discourse.ingestor import DiscourseChunk, DiscourseChunkIngestorContext
from src.ai.teacher.student import Student
from teacher.impact_predict.base import TeachingDeviceImpactCollector, TeachingDeviceImpactPredictor
from teacher.teaching_device import TeachingDevice, TeachingImpact
from dspy import Signature, InputField, OutputField, TypedPredictor

class TeachingDeviceImpactPredictorSignature(Signature):
    """Predicts the learning outcomes reached by a given teaching device"""

    context: DiscourseFeatures = InputField()
    teaching_device: TeachingDevice = InputField()
    student: str = InputField(description="Who to predict the impact of the teaching device for")
    teaching_impact: TeachingImpact = OutputField(description="The impact that this teaching device had for the student")

class TeachingDeviceImpactPredictorWithLM(TeachingDeviceImpactPredictor):
    def __init__(self, collector: TeachingDeviceImpactCollector, student: Student):
        super().__init__(self, collector=collector, student=student)
        self.predictor = TypedPredictor(TeachingDeviceImpactPredictorSignature)

    def ingest(self, new_chunk: DiscourseChunk, context: DiscourseChunkIngestorContext):
        self.predictor(student=self.student, new_chunk=new_chunk, context=context)