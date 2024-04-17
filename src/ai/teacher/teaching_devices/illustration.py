from abc import ABC
from typing import Generator, Literal
from pydantic import Field
from src.ai.discourse.discourse import PartialDiscourse
from src.ai.teacher.student import Student
from src.ai.teacher.teaching_device import TeachingDeviceRecommendation, TeachingImpact
from teacher.teaching_devices.text import TextTeachingDevice
from teacher.teaching_device import TeachingDeviceGenerationBaseSignature, TeachingDeviceGenerator, TeachingImpact
from dspy import InputField, OutputField, TypedPredictor, TypedChainOfThought, FunctionalModule

class IllustrationTeachingDevice(TextTeachingDevice):
    type: Literal["illustration"] = Field(default="illustration")
    object: str = Field(description="The object made into an illustration")

@ABC
class IllustrationGenerator(TeachingDeviceGenerator):
    pass

class ZeroShotIllustratorSignature(TeachingDeviceGenerationBaseSignature):
    """Makes an illustration to impacts learning outcomes (with given degrees of importance)"""
    new_illustration: IllustrationTeachingDevice = OutputField()

class ZeroShotIllustrationGenerator(IllustrationGenerator):
    def __init__(self):
        self.generator = TypedPredictor(ZeroShotIllustratorSignature)

    def generate(self, teaching_impacts: list[TeachingImpact], student: Student, discourse: PartialDiscourse, n: int) -> list[TeachingDeviceRecommendation]:
        result = self.generator(teaching_impacts=teaching_impacts, student=student, discourse=discourse)
        return result.new_illustration.completions
    
class RefiningIllustratorSignature(ZeroShotIllustratorSignature):
    """Refine an illustration that impacts learning outcomes (with given degrees of importance)"""

    current_illustration: IllustrationTeachingDevice = InputField()

class RefiningIllustrationGenerator(ZeroShotIllustrationGenerator):
    def __init__(self, refinements = 5):
        super().__init__(self)
        self.refinements = refinements
        self.refiners = [TypedChainOfThought(RefiningIllustrationGenerator) for i in range(refinements)]

    def generate(self, teaching_impacts: list[TeachingImpact], student: Student, discourse: PartialDiscourse) -> list[TeachingDeviceRecommendation]:
        current_illustrations = super().generate(teaching_impacts=teaching_impacts, student=student, discourse=discourse)

        for refiner in self.refiners:
            for i in range(len(current_illustrations)):
                refinement = refiner(teaching_impacts=teaching_impacts, student=student, discourse=discourse, current_illustration=current_illustrations[i])
                current_illustrations[i] = refinement.new_illustration

        return current_illustrations

class IllustrationObjectSelector(TeachingDeviceGenerationBaseSignature):
    """Identifies an object to make an illustration from"""
    object: str = OutputField()

class IllustrationObjectComparisonsIdentifier(TeachingDeviceGenerationBaseSignature):
    """Identifies comparisons of an object and desired teaching impacts"""
    object: str = InputField()
    similarities: list[str] = OutputField()

class IllustratationGeneratorFromObjectAndComparisons(TeachingDeviceGenerationBaseSignature):
    """Make an illustration expressing the given similarities between the object and teaching impacts desired"""
    object: str = InputField()
    similarities: list[str] = InputField()
    new_illustration: str = OutputField()

class IllustratationRefinerFromObjectAndComparisons(IllustratationGeneratorFromObjectAndComparisons):
    """Refine an illustration expressing the given similarities between the object and teaching impacts desired"""
    current_illustration: str = InputField()

class ThinkingIllustrationGenerator(FunctionalModule, IllustrationGenerator):
    def __init__(self, refinements = 5):
        super().__init__()
        self.refinements = refinements
        self.object_selector = TypedChainOfThought(IllustrationObjectSelector)
        self.object_similarity_identifier = TypedPredictor(IllustrationObjectComparisonsIdentifier)
        self.generator = TypedPredictor(IllustratationGeneratorFromObjectAndComparisons)
        self.refiners = [TypedChainOfThought(IllustratationRefinerFromObjectAndComparisons) for i in range(refinements)]

    def generate(self, teaching_impacts: list[TeachingImpact], student: Student, discourse: PartialDiscourse) -> Generator[TeachingDeviceRecommendation]:
        for object in self.object_selector(teaching_impacts=teaching_impacts, student=student, discourse=discourse).completions.object:
            for similarities in self.object_similarity_identifier(teaching_impacts=teaching_impacts, student=student, discourse=discourse, object=object).completions.similarities:
                def recurse_refine(current_illustration: str, i = 0) -> Generator[str]:
                    if i == self.refinements:
                        yield current_illustration
                    else:
                        for refined in self.refiners[i](teaching_impacts=teaching_impacts, student=student, discourse=discourse, object=object, similarities=similarities, current_illustration=current_illustration).completions.new_illustration:
                            for recursive_refinement in recurse_refine(refined, i=i+1):
                                yield recursive_refinement
                
                for illustration_0 in self.generator(teaching_impacts=teaching_impacts, student=student, discourse=discourse, object=object, similarities=similarities).completions.new_illustration:
                    for recursive_refinement in recurse_refine(illustration_0, i=0):
                        yield IllustrationTeachingDevice(text=recursive_refinement, object=object)
