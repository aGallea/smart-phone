"""
Speech-to-Text service using various providers
"""

import logging
import io
import tempfile
import os
import wave
import subprocess
from typing import Optional
from config import Config

# Fix OpenMP conflict between whisper and faster_whisper
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import whisper
# import faster_whisper


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
        provider_name = self.config.get("stt.provider", "whisper")

        try:
            if provider_name == "whisper":
                whisper_model = self.config.get("stt.whisper_model", "base")
                self.whisper_model = whisper.load_model(whisper_model)
                # self.whisper_model_ivrit = whisper.load_model("turbo")
                # self.whisper_model_ivrit = faster_whisper.WhisperModel(
                #     "ivrit-ai/whisper-large-v3-turbo-ct2"
                # )
                logger.info(f"Whisper model loaded: {whisper_model}")
            elif provider_name == "openai":
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

    def _create_wav_file(self, audio_data: bytes, temp_file_path: str) -> bool:
        """
        Create a proper WAV file from audio data

        Args:
            audio_data: Raw audio data in bytes
            temp_file_path: Path where to save the WAV file

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Processing audio data: {len(audio_data)} bytes")

            # Check if the data already has a WAV header
            if audio_data.startswith(b"RIFF") and b"WAVE" in audio_data[:12]:
                # Already a WAV file, write directly
                logger.info("Audio data already in WAV format")
                with open(temp_file_path, "wb") as f:
                    f.write(audio_data)
                return True

            # Check for other common audio formats
            if audio_data.startswith(b"ID3") or audio_data.startswith(b"\xff\xfb"):
                logger.warning(
                    "Audio data appears to be MP3 format - conversion needed"
                )
                # For MP3 and other formats, we'll write directly and let ffmpeg handle it
                # Change extension to match the actual format
                actual_path = temp_file_path.replace(".wav", ".mp3")
                with open(actual_path, "wb") as f:
                    f.write(audio_data)

                # Try to convert using ffmpeg if available
                try:
                    subprocess.run(
                        [
                            "ffmpeg",
                            "-i",
                            actual_path,
                            "-ar",
                            "16000",
                            "-ac",
                            "1",
                            "-f",
                            "wav",
                            temp_file_path,
                        ],
                        capture_output=True,
                        check=True,
                    )
                    os.unlink(actual_path)  # Remove the original file
                    logger.info("Successfully converted audio to WAV format")
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                    logger.warning(f"FFmpeg conversion failed: {e}")
                    # Fallback to direct write
                    os.rename(actual_path, temp_file_path)
                    return True

            # Assume raw PCM data, create WAV header
            # Default parameters - these might need adjustment based on your audio source
            sample_rate = 16000  # 16kHz sample rate
            channels = 1  # Mono
            bits_per_sample = 16  # 16-bit

            # Validate that the data length makes sense for PCM audio
            bytes_per_sample = bits_per_sample // 8
            expected_bytes_per_second = sample_rate * channels * bytes_per_sample
            audio_duration = len(audio_data) / expected_bytes_per_second

            if (
                audio_duration < 0.1 or audio_duration > 3600
            ):  # Less than 0.1s or more than 1 hour
                logger.warning(
                    f"Audio duration seems unusual: {audio_duration:.2f} seconds"
                )

            logger.info(
                f"Creating WAV file with: {sample_rate}Hz, {channels} channels, {bits_per_sample}-bit, duration: {audio_duration:.2f}s"
            )

            with wave.open(temp_file_path, "wb") as wav_file:
                wav_file.setnchannels(channels)
                wav_file.setsampwidth(bits_per_sample // 8)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data)

            logger.info(f"Successfully created WAV file: {temp_file_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating WAV file: {e}")
            return False

    async def transcribe(self, audio_data: bytes) -> Optional[str]:
        """
        Transcribe audio data to text

        Args:
            audio_data: Audio data in bytes format (will be written to temporary file for Whisper models)
                       For Whisper models, this bytes data will be saved as a temporary audio file
                       which is then passed as a file path to the model.

        Returns:
            Transcribed text or None if failed
        """

        try:
            if self.provider == "whisper":
                # Create temporary file for both whisper models
                with tempfile.NamedTemporaryFile(
                    suffix=".wav", delete=False
                ) as temp_file:
                    temp_file_path = temp_file.name

                # Create proper WAV file from audio data
                if not self._create_wav_file(audio_data, temp_file_path):
                    logger.error("Failed to create valid WAV file from audio data")
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                    return None

                try:
                    # Use standard whisper model
                    result = self.whisper_model.transcribe(temp_file_path)
                    transcribed_text = ""
                    if isinstance(result, dict) and "text" in result:
                        transcribed_text = str(result["text"]).strip()

                    # Also try Hebrew-specific model
                    # try:
                    #     transcribed_text_ivrit = self.whisper_model_ivrit.transcribe(
                    #         temp_file_path, #language="he"
                    #     )
                    #     #texts_ivrit = [s.text for s in segs]
                    #     # = " ".join(texts_ivrit)
                    #     logger.info(
                    #         f"Standard: {transcribed_text}, Hebrew: {transcribed_text_ivrit}"
                    #     )

                    #     # Return Hebrew transcription if it's longer/more substantial
                    #     # if len(transcribed_text_ivrit.strip()) > len(
                    #     #     transcribed_text.strip()
                    #     # ):
                    #     #     return transcribed_text_ivrit

                    # except Exception as ivrit_error:
                    #     logger.warning(f"Hebrew transcription failed: {ivrit_error}")

                    return transcribed_text

                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
            else:
                if not self._available or not self.client:
                    logger.error("STT service not available")
                    return None

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
