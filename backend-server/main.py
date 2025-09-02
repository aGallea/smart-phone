"""
Smart Robot Backend Server
FastAPI server providing LLM operations for the smart robot
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import logging
from io import BytesIO
from typing import Dict, Any, Optional

from config import Config
from services.stt_service import STTService
from services.tts_service import TTSService
from services.llm_service import LLMService
from models.requests import GenerateRequest, ConfigUpdateRequest
from models.responses import StatusResponse, GenerateResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Smart Robot Backend",
    description="Backend server for Smart Robot Assistant",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
config = Config()
stt_service = STTService(config)
tts_service = TTSService(config)
llm_service = LLMService(config)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Smart Robot Backend Server...")

    # Initialize services
    await stt_service.initialize()
    await tts_service.initialize()
    await llm_service.initialize()

    logger.info("Backend server started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Smart Robot Backend Server...")

    await stt_service.cleanup()
    await tts_service.cleanup()
    await llm_service.cleanup()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Smart Robot Backend is running"}


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Get server status and service information"""
    return StatusResponse(
        status="running",
        services={
            "stt": stt_service.is_available(),
            "tts": tts_service.is_available(),
            "llm": llm_service.is_available(),
        },
        config={
            "stt_provider": config.get("stt.provider"),
            "tts_provider": config.get("tts.provider"),
            "llm_provider": config.get("llm.provider"),
        },
    )


@app.post("/api/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    """
    Convert speech to text

    Args:
        audio: Audio file (WAV format recommended)

    Returns:
        Transcribed text
    """
    if not stt_service.is_available():
        raise HTTPException(status_code=503, detail="STT service not available")

    try:
        # Read audio data
        audio_data = await audio.read()

        # Process STT
        text = await stt_service.transcribe(audio_data)

        if text is None:
            raise HTTPException(status_code=500, detail="Failed to transcribe audio")

        return {"text": text}

    except Exception as e:
        logger.error(f"Error in STT: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tts")
async def text_to_speech(request: Dict[str, str]):
    """
    Convert text to speech

    Args:
        request: Dictionary containing 'text' field

    Returns:
        Audio data as streaming response
    """
    if not tts_service.is_available():
        raise HTTPException(status_code=503, detail="TTS service not available")

    text = request.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Text field is required")

    try:
        # Generate TTS audio
        audio_data = await tts_service.synthesize(text)

        if audio_data is None:
            raise HTTPException(status_code=500, detail="Failed to generate speech")

        # Return audio as streaming response
        return StreamingResponse(
            BytesIO(audio_data),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=speech.wav"},
        )

    except Exception as e:
        logger.error(f"Error in TTS: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_response(request: GenerateRequest):
    """
    Generate LLM response to user input

    Args:
        request: Generate request containing user input and context

    Returns:
        Generated response
    """
    if not llm_service.is_available():
        raise HTTPException(status_code=503, detail="LLM service not available")

    try:
        # Generate response using LLM
        response = await llm_service.generate_response(
            user_input=request.user_input, context=request.context or {}
        )

        if response is None:
            raise HTTPException(status_code=500, detail="Failed to generate response")

        return GenerateResponse(response=response)

    except Exception as e:
        logger.error(f"Error in LLM generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config")
async def update_config(request: ConfigUpdateRequest):
    """
    Update server configuration

    Args:
        request: Configuration update request

    Returns:
        Success status
    """
    try:
        # Update configuration
        for key, value in request.config.items():
            config.set(key, value)

        # Reinitialize services if needed
        if any(
            key.startswith(("stt.", "tts.", "llm.")) for key in request.config.keys()
        ):
            logger.info("Reinitializing services due to config change...")
            await stt_service.initialize()
            await tts_service.initialize()
            await llm_service.initialize()

        return {"status": "success", "message": "Configuration updated"}

    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config")
async def get_config():
    """Get current configuration (sanitized)"""
    try:
        # Return sanitized config (remove sensitive information)
        sanitized_config = config.get_sanitized_config()
        return {"config": sanitized_config}

    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Run server
    uvicorn.run(
        "main:app",
        host=config.get("server.host", "0.0.0.0"),
        port=config.get("server.port", 8000),
        reload=config.get("server.reload", False),
    )
