from discourse.discourse import DiscourseFeatures, Person
from discourse.ingestor import DiscourseChunk, DiscourseChunkIngestorContext
from teacher.impact_predict.base import TeachingDeviceImpactCollector, TeachingDeviceImpactPredictor
from teacher.teaching_device import TeachingDevice, TeachingImpact
from dspy import Signature, InputField, OutputField, TypedPredictor

class TeachingDeviceImpactPredictorSignature(Signature):
    """Predicts the learning outcomes reached by a given teaching device"""

    context: DiscourseFeatures = InputField()
    teaching_device: TeachingDevice = InputField()
    student: str = InputField()
    real_teaching_impact: TeachingImpact = OutputField()

class TeachingDeviceImpactPredictorWithLM(TeachingDeviceImpactPredictor):
    def __init__(self, collector: TeachingDeviceImpactCollector, student: Person):
        super().__init__(self, collector=collector, student=student)
        self.predictor = TypedPredictor(TeachingDeviceImpactPredictorSignature)

    def ingest(self, new_chunk: DiscourseChunk, context_initial: DiscourseChunkIngestorContext):
        self.predictor(context=context_initial, )