from typing import Literal
from teacher.teaching_devices.text import TextTeachingDevice

class QuestionTeachingDevice(TextTeachingDevice):
    type: Literal["question"] = "question"
