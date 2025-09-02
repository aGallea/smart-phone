"""
Audio handling for Termux environment
Handles microphone input and speaker output with fallback options
"""

import logging
import wave
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import pyaudio, fallback to alternative if not available
try:
    import pyaudio

    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logger.warning("pyaudio not available, will use alternative audio handler")

# Import alternative audio handler
if not PYAUDIO_AVAILABLE:
    try:
        from alternative_audio_handler import AlternativeAudioHandler

        ALTERNATIVE_AVAILABLE = True
    except ImportError:
        ALTERNATIVE_AVAILABLE = False
        logger.error("Alternative audio handler not available")


class AudioHandler:
    """Handles audio recording and playback operations with fallback support"""

    def __init__(self):
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024
        self.format = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None

        # Audio system
        self.audio = None
        self.alternative_handler = None

        # Recording state
        self.is_recording = False
        self.recorded_frames = []

        # Determine which audio system to use
        self.use_pyaudio = PYAUDIO_AVAILABLE

    async def initialize(self):
        """Initialize audio system"""
        if self.use_pyaudio and PYAUDIO_AVAILABLE:
            try:
                self.audio = pyaudio.PyAudio()
                logger.info("Audio system initialized with pyaudio")
                return True
            except Exception as e:
                logger.warning(
                    f"pyaudio initialization failed: {e}, trying alternative"
                )
                self.use_pyaudio = False

        if not self.use_pyaudio and ALTERNATIVE_AVAILABLE:
            try:
                self.alternative_handler = AlternativeAudioHandler()
                success = await self.alternative_handler.initialize()
                if success:
                    logger.info("Audio system initialized with alternative handler")
                    return True
            except Exception as e:
                logger.error(f"Alternative audio handler initialization failed: {e}")

        logger.error("Failed to initialize any audio system")
        return False

    async def cleanup(self):
        """Cleanup audio resources"""
        if self.use_pyaudio and self.audio:
            self.audio.terminate()
            logger.info("pyaudio system cleaned up")
        elif self.alternative_handler:
            await self.alternative_handler.cleanup()

    async def record_audio(self, duration: float = 5.0) -> Optional[bytes]:
        """
        Record audio for specified duration

        Args:
            duration: Recording duration in seconds

        Returns:
            Audio data as bytes or None if failed
        """
        if self.use_pyaudio:
            return await self._record_with_pyaudio(duration)
        elif self.alternative_handler:
            return await self.alternative_handler.record_audio(duration)
        else:
            logger.error("No audio recording system available")
            return None

    async def _record_with_pyaudio(self, duration: float) -> Optional[bytes]:
        """Record audio using pyaudio"""
        if not self.audio or not self.format:
            logger.error("pyaudio not initialized")
            return None

        try:
            logger.info(f"Recording audio for {duration} seconds...")

            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
            )

            frames = []
            for _ in range(int(self.sample_rate / self.chunk_size * duration)):
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)

            stream.stop_stream()
            stream.close()

            # Convert to bytes
            audio_data = b"".join(frames)
            logger.info("Audio recording completed")
            return audio_data

        except Exception as e:
            logger.error(f"Error recording audio with pyaudio: {e}")
            return None

    async def play_audio(self, audio_data: bytes):
        """
        Play audio data through speakers

        Args:
            audio_data: Audio data to play
        """
        if self.use_pyaudio:
            await self._play_with_pyaudio(audio_data)
        elif self.alternative_handler:
            await self.alternative_handler.play_audio(audio_data)
        else:
            logger.error("No audio playback system available")

    async def _play_with_pyaudio(self, audio_data: bytes):
        """Play audio using pyaudio"""
        if not self.audio or not self.format:
            logger.error("pyaudio not initialized")
            return

        try:
            logger.info("Playing audio...")

            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
            )

            # Play audio in chunks
            chunk_size = 1024
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i : i + chunk_size]
                stream.write(chunk)

            stream.stop_stream()
            stream.close()
            logger.info("Audio playback completed")

        except Exception as e:
            logger.error(f"Error playing audio with pyaudio: {e}")

    async def play_audio_file(self, file_path: Path):
        """Play audio from file"""
        if self.alternative_handler and not self.use_pyaudio:
            await self.alternative_handler.play_audio_file(file_path)
        else:
            try:
                with wave.open(str(file_path), "rb") as wf:
                    audio_data = wf.readframes(wf.getnframes())
                    await self.play_audio(audio_data)
            except Exception as e:
                logger.error(f"Error playing audio file: {e}")

    async def save_audio_to_file(self, audio_data: bytes, file_path: Path):
        """Save audio data to WAV file"""
        if self.alternative_handler and not self.use_pyaudio:
            await self.alternative_handler.save_audio_to_file(audio_data, file_path)
        else:
            try:
                with wave.open(str(file_path), "wb") as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(audio_data)
                logger.info(f"Audio saved to {file_path}")
            except Exception as e:
                logger.error(f"Error saving audio file: {e}")

    # Continuous recording methods
    async def start_continuous_recording(self):
        """Start continuous recording until stopped"""
        if self.alternative_handler and not self.use_pyaudio:
            await self.alternative_handler.start_continuous_recording()
        elif self.use_pyaudio and self.audio and not self.is_recording:
            try:
                logger.info("Starting continuous recording with pyaudio...")
                self.is_recording = True
                self.recorded_frames = []

                self.stream = self.audio.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    frames_per_buffer=self.chunk_size,
                )

            except Exception as e:
                logger.error(f"Error starting continuous recording: {e}")
                self.is_recording = False

    async def stop_continuous_recording(self) -> Optional[bytes]:
        """Stop continuous recording and return audio data"""
        if self.alternative_handler and not self.use_pyaudio:
            return await self.alternative_handler.stop_continuous_recording()
        elif self.use_pyaudio and self.is_recording:
            try:
                self.is_recording = False
                self.stream.stop_stream()
                self.stream.close()

                if self.recorded_frames:
                    audio_data = b"".join(self.recorded_frames)
                    logger.info("Continuous recording stopped")
                    return audio_data

            except Exception as e:
                logger.error(f"Error stopping recording: {e}")

        return None

    async def get_audio_chunk(self) -> Optional[bytes]:
        """Get a chunk of audio during continuous recording"""
        if self.alternative_handler and not self.use_pyaudio:
            return await self.alternative_handler.get_audio_chunk()
        elif self.use_pyaudio and self.is_recording and hasattr(self, "stream"):
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.recorded_frames.append(data)
                return data
            except Exception as e:
                logger.error(f"Error getting audio chunk: {e}")
                return None

        return None
