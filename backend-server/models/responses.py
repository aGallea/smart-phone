"""
Pydantic models for API responses
"""

from pydantic import BaseModel
from typing import Dict, Any


class StatusResponse(BaseModel):
    """Response model for status endpoint"""
    status: str
    services: Dict[str, bool]
    config: Dict[str, Any]


class GenerateResponse(BaseModel):
    """Response model for generate endpoint"""
    response: str


class STTResponse(BaseModel):
    """Response model for STT endpoint"""
    text: str
