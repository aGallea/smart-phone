"""
Pydantic models for API requests
"""

from pydantic import BaseModel
from typing import Dict, Any, Optional


class GenerateRequest(BaseModel):
    """Request model for generate endpoint"""
    user_input: str
    context: Optional[Dict[str, Any]] = None


class ConfigUpdateRequest(BaseModel):
    """Request model for config update endpoint"""
    config: Dict[str, Any]


class TTSRequest(BaseModel):
    """Request model for TTS endpoint"""
    text: str
    voice: Optional[str] = None
    speed: Optional[float] = 1.0
