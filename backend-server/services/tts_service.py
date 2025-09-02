"""
Text-to-Speech service using various providers
"""

import logging
import io
from typing import Optional
from config import Config

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech service with multiple provider support"""
    
    def __init__(self, config: Config):
        self.config = config
        self.provider = None
        self.client = None
        self._available = False
    
    async def initialize(self):
        """Initialize TTS service with configured provider"""
        provider_name = self.config.get("tts.provider", "openai")
        
        try:
            if provider_name == "openai":
                await self._init_openai()
            elif provider_name == "google":
                await self._init_google()
            elif provider_name == "azure":
                await self._init_azure()
            elif provider_name == "elevenlabs":
                await self._init_elevenlabs()
            else:
                logger.error(f"Unknown TTS provider: {provider_name}")
                return
            
            self.provider = provider_name
            self._available = True
            logger.info(f"TTS service initialized with provider: {provider_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS service: {e}")
            self._available = False
    
    async def _init_openai(self):
        """Initialize OpenAI TTS"""
        try:
            import openai
            api_key = self.config.get("tts.openai_api_key")
            if not api_key:
                raise ValueError("OpenAI API key not configured")
            
            openai.api_key = api_key
            self.client = openai
            
        except ImportError:
            logger.error("OpenAI library not installed")
            raise
    
    async def _init_google(self):
        """Initialize Google Cloud TTS"""
        try:
            from google.cloud import texttospeech
            self.client = texttospeech.TextToSpeechClient()
            
        except ImportError:
            logger.error("Google Cloud Text-to-Speech library not installed")
            raise
    
    async def _init_azure(self):
        """Initialize Azure Cognitive Services TTS"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            speech_key = self.config.get("tts.azure_speech_key")
            service_region = self.config.get("tts.azure_region")
            
            if not speech_key or not service_region:
                raise ValueError("Azure Speech key or region not configured")
            
            speech_config = speechsdk.SpeechConfig(
                subscription=speech_key, 
                region=service_region
            )
            self.client = speech_config
            
        except ImportError:
            logger.error("Azure Speech SDK not installed")
            raise
    
    async def _init_elevenlabs(self):
        """Initialize ElevenLabs TTS"""
        try:
            import elevenlabs
            api_key = self.config.get("tts.elevenlabs_api_key")
            if not api_key:
                raise ValueError("ElevenLabs API key not configured")
            
            elevenlabs.set_api_key(api_key)
            self.client = elevenlabs
            
        except ImportError:
            logger.error("ElevenLabs library not installed")
            raise
    
    async def cleanup(self):
        """Cleanup TTS service"""
        self.client = None
        self._available = False
        logger.info("TTS service cleaned up")
    
    def is_available(self) -> bool:
        """Check if TTS service is available"""
        return self._available
    
    async def synthesize(self, text: str, voice: Optional[str] = None) -> Optional[bytes]:
        """
        Synthesize text to speech
        
        Args:
            text: Text to synthesize
            voice: Optional voice to use (provider-specific)
            
        Returns:
            Audio data as bytes or None if failed
        """
        if not self._available or not self.client:
            logger.error("TTS service not available")
            return None
        
        try:
            if self.provider == "openai":
                return await self._synthesize_openai(text, voice)
            elif self.provider == "google":
                return await self._synthesize_google(text, voice)
            elif self.provider == "azure":
                return await self._synthesize_azure(text, voice)
            elif self.provider == "elevenlabs":
                return await self._synthesize_elevenlabs(text, voice)
            else:
                logger.error(f"Unknown provider: {self.provider}")
                return None
                
        except Exception as e:
            logger.error(f"Error in TTS synthesis: {e}")
            return None
    
    async def _synthesize_openai(self, text: str, voice: Optional[str]) -> Optional[bytes]:
        """Synthesize using OpenAI TTS"""
        try:
            voice_name = voice or self.config.get("tts.voice", "alloy")
            model = self.config.get("tts.model", "tts-1")
            
            response = self.client.audio.speech.create(
                model=model,
                voice=voice_name,
                input=text
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"OpenAI TTS error: {e}")
            return None
    
    async def _synthesize_google(self, text: str, voice: Optional[str]) -> Optional[bytes]:
        """Synthesize using Google Cloud Text-to-Speech"""
        try:
            from google.cloud import texttospeech
            
            # Set up the text input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Build the voice request
            voice_params = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            
            # Select the type of audio file
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16
            )
            
            # Perform the text-to-speech request
            response = self.client.synthesize_speech(
                input=synthesis_input, 
                voice=voice_params, 
                audio_config=audio_config
            )
            
            return response.audio_content
            
        except Exception as e:
            logger.error(f"Google TTS error: {e}")
            return None
    
    async def _synthesize_azure(self, text: str, voice: Optional[str]) -> Optional[bytes]:
        """Synthesize using Azure Cognitive Services"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.client)
            
            # Perform synthesis
            result = synthesizer.speak_text(text)
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data
            else:
                logger.warning(f"Azure TTS failed: {result.reason}")
                return None
                
        except Exception as e:
            logger.error(f"Azure TTS error: {e}")
            return None
    
    async def _synthesize_elevenlabs(self, text: str, voice: Optional[str]) -> Optional[bytes]:
        """Synthesize using ElevenLabs"""
        try:
            voice_name = voice or self.config.get("tts.voice", "Adam")
            
            audio = self.client.generate(
                text=text,
                voice=voice_name,
                model="eleven_monolingual_v1"
            )
            
            # Convert generator to bytes
            audio_bytes = b"".join(audio)
            return audio_bytes
            
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {e}")
            return None
