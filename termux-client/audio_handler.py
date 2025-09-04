"""
Audio handling for Termux environment
Handles microphone input and speaker output with fallback options
"""

import logging
from pathlib import Path
from typing import Optional
from alternative_audio_handler import AlternativeAudioHandler

logger = logging.getLogger(__name__)

class AudioHandler:
    """Handles audio recording and playback operations with fallback support"""

    def __init__(self):
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024
        # self.format = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None

        # Audio system
        self.audio = None
        self.alternative_handler = None

        # Recording state
        self.is_recording = False
        self.recorded_frames = []

        # Determine which audio system to use
        # self.use_pyaudio = PYAUDIO_AVAILABLE

    async def initialize(self):
        self.alternative_handler = AlternativeAudioHandler()
        success = await self.alternative_handler.initialize()
        if success:
            logger.info("Audio system initialized with alternative handler")
            return True
        logger.error("Failed to initialize audio system")
        return False

    async def cleanup(self):
        """Cleanup audio resources"""
        if self.alternative_handler:
            await self.alternative_handler.cleanup()

    async def record_audio(self, duration: float = 5.0) -> Optional[bytes]:
        """
        Record audio for specified duration

        Args:
            duration: Recording duration in seconds

        Returns:
            Audio data as bytes or None if failed
        """
        if self.alternative_handler:
            return await self.alternative_handler.record_audio(duration)
        else:
            logger.error("No audio recording system available")
            return None

    def record_voice_until_silence(self):
        if self.alternative_handler:
            return self.alternative_handler.record_voice_until_silence()
        else:
            logger.error("No audio recording system available")
            return None

    async def play_audio(self, audio_data: bytes):
        """
        Play audio data through speakers

        Args:
            audio_data: Audio data to play
        """
        if self.alternative_handler:
            await self.alternative_handler.play_audio(audio_data)
        else:
            logger.error("No audio playback system available")

    async def play_audio_file(self, file_path: Path):
        """Play audio from file"""
        if self.alternative_handler:
            await self.alternative_handler.play_audio_file(file_path)

    async def save_audio_to_file(self, audio_data: bytes, file_path: Path):
        """Save audio data to WAV file"""
        if self.alternative_handler:
            await self.alternative_handler.save_audio_to_file(audio_data, file_path)

    # Continuous recording methods
    async def start_continuous_recording(self):
        """Start continuous recording until stopped"""
        if self.alternative_handler:
            await self.alternative_handler.start_continuous_recording()

    async def stop_continuous_recording(self) -> Optional[bytes]:
        """Stop continuous recording and return audio data"""
        if self.alternative_handler:
            return await self.alternative_handler.stop_continuous_recording()

        return None

    async def get_audio_chunk(self) -> Optional[bytes]:
        """Get a chunk of audio during continuous recording"""
        if self.alternative_handler:
            return await self.alternative_handler.get_audio_chunk()

        return None
