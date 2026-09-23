from pydantic import BaseModel, Field
from typing import List, Literal

class VendorAssessmentRequest(BaseModel):
    vendor_name: str = Field(
        ..., 
        description="The name of the vendor to be evaluated (e.g., Asteria AI Systems)."
    )
    platform_type: str = Field(
        ..., 
        description="The proposed technology or service type (e.g., Enterprise Generative AI platform)."
    )
    user_count: int = Field(
        ..., 
        description="The total number of intended employees or licensed users.",
        gt=0
    )
    data_classification: str = Field(
        ..., 
        description="The sensitivity of the data the platform will process (e.g., confidential corporate documents)."
    )
    required_risk_domains: List[str] = Field(
        default=["Security", "Procurement/Commercial", "Legal/Compliance", "AI Governance"],
        description="The required audit domains delegated to the specialist subagents."
    )
    allowed_recommendations: List[Literal["APPROVE", "CONDITIONAL APPROVAL", "REJECT"]] = Field(
        default=["APPROVE", "CONDITIONAL APPROVAL", "REJECT"],
        description="The permitted final decision categories the Deep Agent can select from."
    )