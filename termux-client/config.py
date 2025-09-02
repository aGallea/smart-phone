"""
Configuration management for termux client
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for the termux client"""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_default_config()
        self.load_config()

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            "backend_url": "http://192.168.1.100:8000",
            "wake_word_enabled": True,
            "wake_word": "hey robot",
            "audio": {
                "sample_rate": 16000,
                "channels": 1,
                "chunk_size": 1024,
                "recording_duration": 5.0,
            },
            "voice": {
                "voice_activation_threshold": 0.01,
                "silence_timeout": 2.0,
                "max_recording_duration": 30.0,
            },
            "assistant": {
                "name": "Robot",
                "personality": "helpful and friendly",
                "language": "en",
            },
            "logging": {"level": "INFO", "file": "robot_client.log"},
        }

    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                self.save_config()  # Create default config file
                logger.info("Created default configuration file")
        except Exception as e:
            logger.error(f"Error loading config: {e}")

    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def get(self, key: str, default=None):
        """Get configuration value"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()

    @property
    def backend_url(self) -> str:
        """Get backend server URL"""
        return self.get("backend_url", "http://localhost:8000")

    @property
    def wake_word_enabled(self) -> bool:
        """Check if wake word is enabled"""
        return self.get("wake_word_enabled", True)

    @property
    def wake_word(self) -> str:
        """Get wake word"""
        return self.get("wake_word", "hey robot")

    @property
    def sample_rate(self) -> int:
        """Get audio sample rate"""
        return self.get("audio.sample_rate", 16000)

    @property
    def channels(self) -> int:
        """Get audio channels"""
        return self.get("audio.channels", 1)

    @property
    def chunk_size(self) -> int:
        """Get audio chunk size"""
        return self.get("audio.chunk_size", 1024)

    @property
    def recording_duration(self) -> float:
        """Get default recording duration"""
        return self.get("audio.recording_duration", 5.0)

    @property
    def voice_activation_threshold(self) -> float:
        """Get voice activation threshold"""
        return self.get("voice.voice_activation_threshold", 0.01)

    @property
    def silence_timeout(self) -> float:
        """Get silence timeout"""
        return self.get("voice.silence_timeout", 2.0)

    @property
    def max_recording_duration(self) -> float:
        """Get maximum recording duration"""
        return self.get("voice.max_recording_duration", 30.0)

    @property
    def assistant_name(self) -> str:
        """Get assistant name"""
        return self.get("assistant.name", "Robot")

    @property
    def personality(self) -> str:
        """Get assistant personality"""
        return self.get("assistant.personality", "helpful and friendly")

    @property
    def language(self) -> str:
        """Get language"""
        return self.get("assistant.language", "en")
