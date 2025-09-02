"""
Shared configuration constants and utilities
"""

# API Endpoints
API_ENDPOINTS = {
    "health": "/health",
    "status": "/api/status",
    "stt": "/api/stt",
    "tts": "/api/tts",
    "generate": "/api/generate",
    "config": "/api/config",
}

# Audio Configuration
AUDIO_CONFIG = {
    "sample_rate": 16000,
    "channels": 1,
    "chunk_size": 1024,
    "format": "WAV",
}

# Default System Prompts
SYSTEM_PROMPTS = {
    "default": "You are a helpful personal assistant robot. Keep responses concise and friendly.",
    "casual": "You are a friendly robot companion. Be conversational and helpful.",
    "professional": "You are a professional assistant robot. Provide clear, accurate information.",
    "creative": "You are a creative assistant robot. Be imaginative and inspiring in your responses.",
}

# Supported Voice Commands
VOICE_COMMANDS = {
    "wake_words": ["hey robot", "hello robot", "robot"],
    "stop_words": ["stop", "quiet", "pause"],
    "test_commands": [
        "what time is it",
        "what is the weather",
        "tell me a joke",
        "how are you",
        "what can you do",
    ],
}

# Error Messages
ERROR_MESSAGES = {
    "connection_failed": "Failed to connect to backend server",
    "audio_error": "Audio system error",
    "stt_failed": "Speech recognition failed",
    "tts_failed": "Speech synthesis failed",
    "llm_error": "Language model error",
    "config_error": "Configuration error",
}

# Status Codes
STATUS_CODES = {
    "healthy": "healthy",
    "unhealthy": "unhealthy",
    "connecting": "connecting",
    "disconnected": "disconnected",
    "error": "error",
}
