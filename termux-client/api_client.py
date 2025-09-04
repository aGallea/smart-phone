"""
API client for communicating with backend server
"""

import aiohttp
import asyncio
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class BackendClient:
    """Client for communicating with the backend server"""

    def __init__(self, backend_url: str):
        self.backend_url = backend_url.rstrip("/")
        self.session = None
        self.connected = False

    async def connect(self):
        """Establish connection to backend server"""
        try:
            # Configure connector to limit connection reuse and handle keep-alive properly
            connector = aiohttp.TCPConnector(
                limit_per_host=1,  # Limit connections per host
                enable_cleanup_closed=True,  # Clean up closed connections
                keepalive_timeout=30,  # Keep-alive timeout
                limit=10,  # Total connection pool limit
            )

            self.session = aiohttp.ClientSession(connector=connector)
            # Test connection
            async with self.session.get(f"{self.backend_url}/health") as response:
                if response.status == 200:
                    self.connected = True
                    logger.info("Connected to backend server")
                else:
                    logger.error(f"Backend server returned status {response.status}")
        except Exception as e:
            logger.error(f"Failed to connect to backend: {e}")
            if self.session:
                await self.session.close()
                self.session = None

    async def disconnect(self):
        """Close connection to backend server"""
        if self.session:
            await self.session.close()
            self.session = None
        self.connected = False
        logger.info("Disconnected from backend server")

    async def speech_to_text(self, audio_data: bytes) -> Optional[str]:
        """
        Convert speech to text using backend API

        Args:
            audio_data: Audio data in bytes

        Returns:
            Transcribed text or None if failed
        """
        if not self.connected or not self.session:
            logger.error("Not connected to backend server")
            return None

        if not audio_data:
            logger.error("No audio data provided")
            return None

        if len(audio_data) == 0:
            logger.error("Empty audio data provided")
            return None

        try:
            # Prepare multipart form data with proper headers
            data = aiohttp.FormData()
            data.add_field(
                "audio", audio_data, filename="audio.wav", content_type="audio/wav"
            )

            # Add timeout and force connection close to avoid reuse issues
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {"Connection": "close"}  # Force connection close

            async with self.session.post(
                f"{self.backend_url}/api/stt",
                data=data,
                timeout=timeout,
                headers=headers,
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("text")
                else:
                    error_text = await response.text()
                    logger.error(
                        f"STT request failed with status {response.status}: {error_text}"
                    )
                    return None

        except aiohttp.ClientPayloadError as e:
            logger.error(
                f"Payload error in speech-to-text (possibly invalid audio data): {e}"
            )
            return None
        except aiohttp.ClientConnectionError as e:
            logger.error(f"Connection error in speech-to-text: {e}")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Client error in speech-to-text: {e}")
            return None
        except asyncio.TimeoutError:
            logger.error("Timeout error in speech-to-text request")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in speech-to-text: {e}")
            return None

    async def text_to_speech(self, text: str) -> Optional[bytes]:
        """
        Convert text to speech using backend API

        Args:
            text: Text to convert to speech

        Returns:
            Audio data as bytes or None if failed
        """
        if not self.connected or not self.session:
            logger.error("Not connected to backend server")
            return None

        try:
            payload = {"text": text}
            async with self.session.post(
                f"{self.backend_url}/api/tts", json=payload
            ) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    logger.error(f"TTS request failed with status {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            return None

    async def generate_response(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Generate LLM response using backend API

        Args:
            user_input: User's input text
            context: Optional context dictionary

        Returns:
            Generated response text or None if failed
        """
        if not self.connected or not self.session:
            logger.error("Not connected to backend server")
            return None

        try:
            payload = {"user_input": user_input, "context": context or {}}

            async with self.session.post(
                f"{self.backend_url}/api/generate", json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response")
                else:
                    logger.error(
                        f"Generate response failed with status {response.status}"
                    )
                    return None

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None

    async def update_config(self, config_data: Dict[str, Any]) -> bool:
        """
        Update configuration on backend server

        Args:
            config_data: Configuration dictionary

        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.session:
            logger.error("Not connected to backend server")
            return False

        try:
            async with self.session.post(
                f"{self.backend_url}/api/config", json=config_data
            ) as response:
                return response.status == 200

        except Exception as e:
            logger.error(f"Error updating config: {e}")
            return False

    async def get_status(self) -> Optional[Dict[str, Any]]:
        """Get backend server status"""
        if not self.connected or not self.session:
            return None

        try:
            async with self.session.get(f"{self.backend_url}/api/status") as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return None
