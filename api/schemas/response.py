from pydantic import BaseModel, Field
from typing import List


class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    
    session_id: str = Field(..., description="Unique session identifier")
    match_percentage: float = Field(..., ge=0, le=100, description="Match percentage (0-100)")
    matching_skills: List[str] = Field(..., description="List of matching skills")
    matching_education: str = Field(..., description="Education match description")
    matching_experience: str = Field(..., description="Experience match description")
    highlighted_strengths: List[str] = Field(..., description="Key strengths (2-3 items)")
    identified_gaps: List[str] = Field(..., description="Missing requirements (2-3 items)")
    processing_time: float = Field(..., description="Processing time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "match_percentage": 78.5,
                "matching_skills": ["Python", "Django", "REST APIs", "PostgreSQL"],
                "matching_education": "Matches: Bachelor's in Computer Science",
                "matching_experience": "3+ years Python development confirmed",
                "highlighted_strengths": [
                    "Strong backend development with Django and FastAPI",
                    "Proven experience with REST API design",
                    "Database optimization skills"
                ],
                "identified_gaps": [
                    "No mention of Docker/containerization",
                    "Limited frontend framework experience"
                ],
                "processing_time": 4.23
            }
        }