from pydantic import Field
from teacher.teaching_device import TeachingDevice

class TextTeachingDevice(TeachingDevice):
    text: str = Field(description="Text form")