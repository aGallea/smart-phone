"""
Speech-to-Text service using various providers
"""

import logging
import io
from typing import Optional
from config import Config

logger = logging.getLogger(__name__)


class STTService:
    """Speech-to-Text service with multiple provider support"""

    def __init__(self, config: Config):
        self.config = config
        self.provider = None
        self.client = None
        self._available = False

    async def initialize(self):
        """Initialize STT service with configured provider"""
        provider_name = self.config.get("stt.provider", "openai")

        try:
            if provider_name == "openai":
                await self._init_openai()
            elif provider_name == "google":
                await self._init_google()
            elif provider_name == "azure":
                await self._init_azure()
            else:
                logger.error(f"Unknown STT provider: {provider_name}")
                return

            self.provider = provider_name
            self._available = True
            logger.info(f"STT service initialized with provider: {provider_name}")

        except Exception as e:
            logger.error(f"Failed to initialize STT service: {e}")
            self._available = False

    async def _init_openai(self):
        """Initialize OpenAI STT"""
        try:
            import openai

            api_key = self.config.get("stt.openai_api_key")
            if not api_key:
                raise ValueError("OpenAI API key not configured")

            openai.api_key = api_key
            self.client = openai

        except ImportError:
            logger.error(
                "OpenAI library not installed. Install with: pip install openai"
            )
            raise

    async def _init_google(self):
        """Initialize Google Cloud STT"""
        try:
            from google.cloud import speech

            self.client = speech.SpeechClient()

        except ImportError:
            logger.error("Google Cloud Speech library not installed")
            raise

    async def _init_azure(self):
        """Initialize Azure Cognitive Services STT"""
        try:
            import azure.cognitiveservices.speech as speechsdk

            speech_key = self.config.get("stt.azure_speech_key")
            service_region = self.config.get("stt.azure_region")

            if not speech_key or not service_region:
                raise ValueError("Azure Speech key or region not configured")

            speech_config = speechsdk.SpeechConfig(
                subscription=speech_key, region=service_region
            )
            self.client = speech_config

        except ImportError:
            logger.error("Azure Speech SDK not installed")
            raise

    async def cleanup(self):
        """Cleanup STT service"""
        self.client = None
        self._available = False
        logger.info("STT service cleaned up")

    def is_available(self) -> bool:
        """Check if STT service is available"""
        return self._available

    async def transcribe(self, audio_data: bytes) -> Optional[str]:
        """
        Transcribe audio data to text

        Args:
            audio_data: Audio data in bytes

        Returns:
            Transcribed text or None if failed
        """
        if not self._available or not self.client:
            logger.error("STT service not available")
            return None

        try:
            if self.provider == "openai":
                return await self._transcribe_openai(audio_data)
            elif self.provider == "google":
                return await self._transcribe_google(audio_data)
            elif self.provider == "azure":
                return await self._transcribe_azure(audio_data)
            else:
                logger.error(f"Unknown provider: {self.provider}")
                return None

        except Exception as e:
            logger.error(f"Error in STT transcription: {e}")
            return None

    async def _transcribe_openai(self, audio_data: bytes) -> Optional[str]:
        """Transcribe using OpenAI Whisper"""
        try:
            # Create file-like object
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"

            # Use OpenAI Whisper API
            response = self.client.Audio.transcribe(
                model=self.config.get("stt.model", "whisper-1"), file=audio_file
            )

            return response.get("text", "").strip()

        except Exception as e:
            logger.error(f"OpenAI STT error: {e}")
            return None

    async def _transcribe_google(self, audio_data: bytes) -> Optional[str]:
        """Transcribe using Google Cloud Speech-to-Text"""
        try:
            from google.cloud import speech

            # Configure request
            audio = speech.RecognitionAudio(content=audio_data)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
            )

            # Perform recognition
            response = self.client.recognize(config=config, audio=audio)

            # Extract text from response
            if response.results:
                return response.results[0].alternatives[0].transcript
            return None

        except Exception as e:
            logger.error(f"Google STT error: {e}")
            return None

    async def _transcribe_azure(self, audio_data: bytes) -> Optional[str]:
        """Transcribe using Azure Cognitive Services"""
        try:
            import azure.cognitiveservices.speech as speechsdk

            # Create audio input from bytes
            audio_input = speechsdk.AudioDataStream(audio_data)
            audio_config = speechsdk.audio.AudioConfig(stream=audio_input)

            # Create speech recognizer
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.client, audio_config=audio_config
            )

            # Perform recognition
            result = speech_recognizer.recognize_once()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return result.text
            else:
                logger.warning(f"Azure STT failed: {result.reason}")
                return None

        except Exception as e:
            logger.error(f"Azure STT error: {e}")
            return None
