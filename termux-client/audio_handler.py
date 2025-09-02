"""
Audio handling for Termux environment
Handles microphone input and speaker output
"""

import asyncio
import logging
import wave
import pyaudio
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class AudioHandler:
    """Handles audio recording and playback operations"""
    
    def __init__(self):
        self.audio = None
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024
        self.format = pyaudio.paInt16
        
        # Recording state
        self.is_recording = False
        self.recorded_frames = []
    
    async def initialize(self):
        """Initialize audio system"""
        try:
            self.audio = pyaudio.PyAudio()
            logger.info("Audio system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize audio: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup audio resources"""
        if self.audio:
            self.audio.terminate()
            logger.info("Audio system cleaned up")
    
    async def record_audio(self, duration: float = 5.0) -> Optional[bytes]:
        """
        Record audio for specified duration
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Audio data as bytes or None if failed
        """
        if not self.audio:
            logger.error("Audio system not initialized")
            return None
        
        try:
            logger.info(f"Recording audio for {duration} seconds...")
            
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            frames = []
            for _ in range(int(self.sample_rate / self.chunk_size * duration)):
                data = stream.read(self.chunk_size)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            # Convert to bytes
            audio_data = b''.join(frames)
            logger.info("Audio recording completed")
            return audio_data
            
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            return None
    
    async def start_continuous_recording(self):
        """Start continuous recording until stopped"""
        if not self.audio or self.is_recording:
            return
        
        try:
            logger.info("Starting continuous recording...")
            self.is_recording = True
            self.recorded_frames = []
            
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
        except Exception as e:
            logger.error(f"Error starting continuous recording: {e}")
            self.is_recording = False
    
    async def stop_continuous_recording(self) -> Optional[bytes]:
        """Stop continuous recording and return audio data"""
        if not self.is_recording:
            return None
        
        try:
            self.is_recording = False
            self.stream.stop_stream()
            self.stream.close()
            
            if self.recorded_frames:
                audio_data = b''.join(self.recorded_frames)
                logger.info("Continuous recording stopped")
                return audio_data
            
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
        
        return None
    
    async def get_audio_chunk(self) -> Optional[bytes]:
        """Get a chunk of audio during continuous recording"""
        if not self.is_recording or not hasattr(self, 'stream'):
            return None
        
        try:
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            self.recorded_frames.append(data)
            return data
        except Exception as e:
            logger.error(f"Error getting audio chunk: {e}")
            return None
    
    async def play_audio(self, audio_data: bytes):
        """
        Play audio data through speakers
        
        Args:
            audio_data: Audio data to play
        """
        if not self.audio:
            logger.error("Audio system not initialized")
            return
        
        try:
            logger.info("Playing audio...")
            
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                output=True
            )
            
            # Play audio in chunks
            chunk_size = 1024
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                stream.write(chunk)
            
            stream.stop_stream()
            stream.close()
            logger.info("Audio playback completed")
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
    
    async def play_audio_file(self, file_path: Path):
        """Play audio from file"""
        try:
            with wave.open(str(file_path), 'rb') as wf:
                audio_data = wf.readframes(wf.getnframes())
                await self.play_audio(audio_data)
        except Exception as e:
            logger.error(f"Error playing audio file: {e}")
    
    async def save_audio_to_file(self, audio_data: bytes, file_path: Path):
        """Save audio data to WAV file"""
        try:
            with wave.open(str(file_path), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data)
            logger.info(f"Audio saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving audio file: {e}")
