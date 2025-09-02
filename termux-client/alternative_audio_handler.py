"""
Alternative audio handling using simpleaudio and sounddevice
Fallback for when pyaudio is not available or fails to install
"""

import asyncio
import logging
import wave
import tempfile
from pathlib import Path
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)

try:
    import sounddevice as sd

    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    logger.warning("sounddevice not available")

try:
    import simpleaudio as sa

    SIMPLEAUDIO_AVAILABLE = True
except ImportError:
    SIMPLEAUDIO_AVAILABLE = False
    logger.warning("simpleaudio not available")


class AlternativeAudioHandler:
    """Alternative audio handler using sounddevice and simpleaudio"""

    def __init__(self):
        self.sample_rate = 16000
        self.channels = 1
        self.dtype = np.int16

        # Recording state
        self.is_recording = False
        self.recorded_data = None
        self.stream = None

    async def initialize(self):
        """Initialize audio system"""
        try:
            if SOUNDDEVICE_AVAILABLE:
                # Test sounddevice
                sd.check_output_settings()
                sd.check_input_settings()
                logger.info("Audio system initialized with sounddevice")
                return True
            elif SIMPLEAUDIO_AVAILABLE:
                logger.info("Audio system initialized with simpleaudio (playback only)")
                return True
            else:
                logger.error("No audio libraries available")
                return False
        except Exception as e:
            logger.error(f"Failed to initialize audio: {e}")
            return False

    async def cleanup(self):
        """Cleanup audio resources"""
        if self.stream:
            self.stream.stop()
            self.stream.close()
        logger.info("Audio system cleaned up")

    async def record_audio(self, duration: float = 5.0) -> Optional[bytes]:
        """
        Record audio for specified duration using sounddevice

        Args:
            duration: Recording duration in seconds

        Returns:
            Audio data as bytes or None if failed
        """
        if not SOUNDDEVICE_AVAILABLE:
            logger.error("sounddevice not available for recording")
            return None

        try:
            logger.info(f"Recording audio for {duration} seconds...")

            # Record audio
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
            )
            sd.wait()  # Wait until recording is finished

            # Convert to bytes
            audio_bytes = audio_data.tobytes()
            logger.info("Audio recording completed")
            return audio_bytes

        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            return None

    async def play_audio(self, audio_data: bytes):
        """
        Play audio data through speakers

        Args:
            audio_data: Audio data to play
        """
        try:
            if SOUNDDEVICE_AVAILABLE:
                await self._play_with_sounddevice(audio_data)
            elif SIMPLEAUDIO_AVAILABLE:
                await self._play_with_simpleaudio(audio_data)
            else:
                logger.error("No audio playback libraries available")

        except Exception as e:
            logger.error(f"Error playing audio: {e}")

    async def _play_with_sounddevice(self, audio_data: bytes):
        """Play audio using sounddevice"""
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=self.dtype)

            # Reshape if stereo
            if self.channels == 2:
                audio_array = audio_array.reshape(-1, 2)

            logger.info("Playing audio with sounddevice...")
            sd.play(audio_array, samplerate=self.sample_rate)
            sd.wait()  # Wait until playback is finished
            logger.info("Audio playback completed")

        except Exception as e:
            logger.error(f"sounddevice playback error: {e}")
            raise

    async def _play_with_simpleaudio(self, audio_data: bytes):
        """Play audio using simpleaudio"""
        try:
            logger.info("Playing audio with simpleaudio...")

            # simpleaudio expects specific format
            play_obj = sa.play_buffer(
                audio_data,
                num_channels=self.channels,
                bytes_per_sample=2,  # 16-bit = 2 bytes
                sample_rate=self.sample_rate,
            )

            # Wait for playback to finish
            play_obj.wait_done()
            logger.info("Audio playback completed")

        except Exception as e:
            logger.error(f"simpleaudio playback error: {e}")
            raise

    async def play_audio_file(self, file_path: Path):
        """Play audio from WAV file"""
        try:
            with wave.open(str(file_path), "rb") as wf:
                frames = wf.readframes(wf.getnframes())
                await self.play_audio(frames)
        except Exception as e:
            logger.error(f"Error playing audio file: {e}")

    async def save_audio_to_file(self, audio_data: bytes, file_path: Path):
        """Save audio data to WAV file"""
        try:
            with wave.open(str(file_path), "wb") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit = 2 bytes
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data)
            logger.info(f"Audio saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving audio file: {e}")

    # Continuous recording methods for compatibility
    async def start_continuous_recording(self):
        """Start continuous recording"""
        if not SOUNDDEVICE_AVAILABLE:
            logger.error("Continuous recording requires sounddevice")
            return

        self.is_recording = True
        self.recorded_data = []

        def audio_callback(indata, frames, time, status):
            if status:
                logger.warning(f"Audio callback status: {status}")
            if self.is_recording:
                self.recorded_data.append(indata.copy())

        try:
            self.stream = sd.InputStream(
                callback=audio_callback,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
            )
            self.stream.start()
            logger.info("Started continuous recording")
        except Exception as e:
            logger.error(f"Error starting continuous recording: {e}")
            self.is_recording = False

    async def stop_continuous_recording(self) -> Optional[bytes]:
        """Stop continuous recording and return audio data"""
        if not self.is_recording or not self.stream:
            return None

        try:
            self.is_recording = False
            self.stream.stop()
            self.stream.close()
            self.stream = None

            if self.recorded_data:
                # Concatenate all recorded chunks
                audio_array = np.concatenate(self.recorded_data, axis=0)
                audio_bytes = audio_array.tobytes()
                logger.info("Continuous recording stopped")
                return audio_bytes

        except Exception as e:
            logger.error(f"Error stopping recording: {e}")

        return None

    async def get_audio_chunk(self) -> Optional[bytes]:
        """Get a chunk of audio during continuous recording"""
        # For this implementation, we collect everything and return in stop_continuous_recording
        # This is a simplified version - in practice you might want to yield chunks
        if self.is_recording and self.recorded_data:
            return b"chunk"  # Placeholder
        return None
