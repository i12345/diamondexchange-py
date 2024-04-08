from pydantic import Field
from teacher.teaching_devices.text import TextTeachingDevice
from simulator.mind import MindObject
from teacher.teaching_device import TeachingDevice, TeachingDeviceGenerator, TeachingImpact
from dspy import Signature, InputField, OutputField, TypedPredictor

class IllustrationTeachingDevice(TextTeachingDevice):
    type: str = Field(default="illustration")
    # comparand: str = Field(description="The object of comparison")

class ZeroShotIllustratorSignature(Signature):
    """Makes an illustration to teach learning outcomes (with given degrees of importance)"""

    learning_outcome: list[TeachingImpact] = InputField()
    current_mind: MindObject = InputField()
    new_illustration: IllustrationTeachingDevice = OutputField()

class ZeroShotIllustrationGenerator(TeachingDeviceGenerator):
    def __init__(self, n_max: int = 10):
        self.generator = TypedPredictor(ZeroShotIllustratorSignature, n=n_max)

    def generate(self, impacts: list[TeachingImpact], mind: MindObject, n: int) -> list[TeachingDevice]:
        result = self.generator(learning_outcome=impacts, current_mind=mind)
        return result.completions.new_illustration
    
class RefiningIllustratorSignature(ZeroShotIllustratorSignature):
    """Refine an illustration that teaches learning outcomes (with given degrees of importance)"""

    current_illustration: IllustrationTeachingDevice = InputField()

