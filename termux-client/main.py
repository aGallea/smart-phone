#!/usr/bin/env python3
"""
Termux Client - Smart Robot Assistant
Main application that runs on old smartphone via Termux
"""

import asyncio
import json
import logging
from pathlib import Path

from audio_handler import AudioHandler
from api_client import BackendClient
from config import Config
from voice_processor import VoiceProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SmartRobotClient:
    """Main client application for the smart robot assistant"""
    
    def __init__(self):
        self.config = Config()
        self.audio_handler = AudioHandler()
        self.backend_client = BackendClient(self.config.backend_url)
        self.voice_processor = VoiceProcessor(self.audio_handler, self.backend_client)
        self.running = False
    
    async def start(self):
        """Start the smart robot client"""
        logger.info("Starting Smart Robot Client...")
        
        try:
            # Initialize components
            await self.audio_handler.initialize()
            await self.backend_client.connect()
            
            self.running = True
            logger.info("Smart Robot Client started successfully")
            
            # Main loop
            await self.main_loop()
            
        except Exception as e:
            logger.error(f"Error starting client: {e}")
            await self.stop()
    
    async def main_loop(self):
        """Main processing loop"""
        while self.running:
            try:
                # Listen for wake word or continuous listening based on config
                if self.config.wake_word_enabled:
                    await self.voice_processor.listen_for_wake_word()
                else:
                    await self.voice_processor.process_voice_command()
                
                # Small delay to prevent CPU overload
                await asyncio.sleep(0.1)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(1)  # Wait before retrying
    
    async def stop(self):
        """Stop the smart robot client"""
        logger.info("Stopping Smart Robot Client...")
        self.running = False
        
        if hasattr(self, 'audio_handler'):
            await self.audio_handler.cleanup()
        if hasattr(self, 'backend_client'):
            await self.backend_client.disconnect()
        
        logger.info("Smart Robot Client stopped")


async def main():
    """Main entry point"""
    client = SmartRobotClient()
    
    try:
        await client.start()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    finally:
        await client.stop()


if __name__ == "__main__":
    asyncio.run(main())
