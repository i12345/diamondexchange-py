import dspy
from teacher.learning_outcome import LearningOutcome
from teacher.teaching_device import TeachingImpact

class Teacher(dspy.Module):
    def __init__(self):
        pass

    def forward(self):
        pass

class LearningRecommender(dspy.Signature):
    current_learning_journey: list[TeachingImpact] = dspy.InputField()
    recommendation: list[LearningOutcome] = dspy.OutputField()
