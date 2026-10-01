from pydantic import BaseModel
from typing import Optional

class PhysicalMetrics(BaseModel):
    edge_sharpness: float
    ink_bleeding: float
    contrast: float
    noise_level: float

class VerificationResponse(BaseModel):
    status: str
    rule_triggered: str
    reason: str
    certificate_valid: bool
    physical_metrics: Optional[PhysicalMetrics] = None
    annotated_image_base64: Optional[str] = None
