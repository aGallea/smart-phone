"""
Voice processing module for wake word detection and voice commands
"""

import asyncio
import logging
import time
from typing import Optional

from audio_handler import AudioHandler
from api_client import BackendClient

logger = logging.getLogger(__name__)


class VoiceProcessor:
    """Handles voice processing including wake word detection and command processing"""
    
    def __init__(self, audio_handler: AudioHandler, backend_client: BackendClient):
        self.audio_handler = audio_handler
        self.backend_client = backend_client
        self.wake_word = "hey robot"
        self.is_listening = False
        self.last_activity_time = time.time()
    
    async def listen_for_wake_word(self):
        """Listen for wake word activation"""
        try:
            # Record short audio clip for wake word detection
            audio_data = await self.audio_handler.record_audio(duration=2.0)
            if not audio_data:
                return
            
            # Convert to text and check for wake word
            text = await self.backend_client.speech_to_text(audio_data)
            if text and self.wake_word.lower() in text.lower():
                logger.info("Wake word detected!")
                await self.handle_wake_word_activation()
                
        except Exception as e:
            logger.error(f"Error in wake word detection: {e}")
    
    async def handle_wake_word_activation(self):
        """Handle wake word activation and start listening for command"""
        try:
            # Play activation sound or speak confirmation
            await self.speak_response("Yes?")
            
            # Listen for actual command
            await self.process_voice_command()
            
        except Exception as e:
            logger.error(f"Error handling wake word activation: {e}")
    
    async def process_voice_command(self):
        """Process a voice command from user"""
        try:
            logger.info("Listening for voice command...")
            
            # Record user command
            audio_data = await self.audio_handler.record_audio(duration=5.0)
            if not audio_data:
                logger.warning("No audio data received")
                return
            
            # Convert speech to text
            user_input = await self.backend_client.speech_to_text(audio_data)
            if not user_input:
                logger.warning("Could not transcribe audio")
                await self.speak_response("I didn't catch that. Could you repeat?")
                return
            
            logger.info(f"User said: {user_input}")
            
            # Generate response using LLM
            response = await self.backend_client.generate_response(user_input)
            if not response:
                response = "I'm having trouble processing your request right now."
            
            # Convert response to speech and play
            await self.speak_response(response)
            
        except Exception as e:
            logger.error(f"Error processing voice command: {e}")
            await self.speak_response("Sorry, I encountered an error.")
    
    async def speak_response(self, text: str):
        """Convert text to speech and play it"""
        try:
            logger.info(f"Speaking: {text}")
            
            # Get audio from TTS service
            audio_data = await self.backend_client.text_to_speech(text)
            if audio_data:
                await self.audio_handler.play_audio(audio_data)
            else:
                logger.error("Failed to generate TTS audio")
                
        except Exception as e:
            logger.error(f"Error in speech response: {e}")
    
    async def start_continuous_listening(self):
        """Start continuous listening mode"""
        logger.info("Starting continuous listening mode...")
        self.is_listening = True
        
        await self.audio_handler.start_continuous_recording()
        
        try:
            while self.is_listening:
                # Get audio chunk
                audio_chunk = await self.audio_handler.get_audio_chunk()
                if audio_chunk:
                    # Simple voice activity detection (placeholder)
                    if self.detect_voice_activity(audio_chunk):
                        self.last_activity_time = time.time()
                        logger.debug("Voice activity detected")
                    
                    # Check for silence timeout
                    if time.time() - self.last_activity_time > 3.0:
                        logger.info("Silence detected, processing command...")
                        await self.process_recorded_command()
                        self.last_activity_time = time.time()
                
                await asyncio.sleep(0.1)
                
        finally:
            await self.audio_handler.stop_continuous_recording()
    
    async def stop_continuous_listening(self):
        """Stop continuous listening mode"""
        logger.info("Stopping continuous listening mode...")
        self.is_listening = False
    
    async def process_recorded_command(self):
        """Process command from continuous recording"""
        try:
            # Stop recording and get audio data
            audio_data = await self.audio_handler.stop_continuous_recording()
            if audio_data:
                # Process the command
                user_input = await self.backend_client.speech_to_text(audio_data)
                if user_input and user_input.strip():
                    logger.info(f"Continuous mode - User said: {user_input}")
                    
                    response = await self.backend_client.generate_response(user_input)
                    if response:
                        await self.speak_response(response)
            
            # Restart continuous recording
            await self.audio_handler.start_continuous_recording()
            
        except Exception as e:
            logger.error(f"Error processing recorded command: {e}")
    
    def detect_voice_activity(self, audio_chunk: bytes) -> bool:
        """
        Simple voice activity detection
        This is a placeholder - in a real implementation you'd use
        proper VAD algorithms or libraries
        """
        # Placeholder implementation
        # In reality, you'd analyze the audio amplitude, frequency, etc.
        return len(audio_chunk) > 0  # Simplified check
    
    async def execute_command(self, command: str) -> str:
        """
        Execute specific commands locally
        
        Args:
            command: Command to execute
            
        Returns:
            Response text
        """
        command_lower = command.lower().strip()
        
        # Basic local commands
        if "time" in command_lower:
            current_time = time.strftime("%H:%M %p")
            return f"The current time is {current_time}"
        
        elif "date" in command_lower:
            current_date = time.strftime("%A, %B %d, %Y")
            return f"Today is {current_date}"
        
        elif "hello" in command_lower or "hi" in command_lower:
            return "Hello! How can I help you today?"
        
        elif "goodbye" in command_lower or "bye" in command_lower:
            return "Goodbye! Have a great day!"
        
        # For other commands, use the backend LLM
        else:
            return await self.backend_client.generate_response(command)
