from pydantic import BaseModel
from typing import Optional


class GenerationRequest(BaseModel):
    notebook_url: str
    custom_prompt: Optional[str] = None


class AudioGenerationRequest(GenerationRequest):
    format: str = "deep_dive"


class SlideEditRequest(BaseModel):
    notebook_url: str
    slide_index: int
    instruction: str


class ReportRequest(GenerationRequest):
    report_type: str  # study_guide, faq, timeline, briefing_doc
