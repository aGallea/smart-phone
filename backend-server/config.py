"""
Backend server configuration management
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for the backend server"""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_default_config()
        self.load_config()

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            "server": {"host": "0.0.0.0", "port": 8000, "reload": False},
            "stt": {
                "provider": "openai",  # openai, google, azure
                "openai_api_key": "",
                "model": "whisper-1",
            },
            "tts": {
                "provider": "openai",  # openai, google, azure, elevenlabs
                "openai_api_key": "",
                "voice": "alloy",
                "model": "tts-1",
            },
            "llm": {
                "provider": "openai",  # openai, anthropic, ollama
                "openai_api_key": "",
                "model": "gpt-3.5-turbo",
                "max_tokens": 150,
                "temperature": 0.7,
                "system_prompt": "You are a helpful personal assistant robot. Keep responses concise and friendly.",
            },
            "logging": {"level": "INFO", "file": "backend.log"},
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
        """Get configuration value using dot notation"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()

    def get_sanitized_config(self) -> Dict[str, Any]:
        """Get configuration with sensitive data removed"""
        sanitized = json.loads(json.dumps(self.config))  # Deep copy

        # Remove sensitive keys
        sensitive_keys = ["api_key", "password", "secret", "token"]

        def remove_sensitive(obj):
            if isinstance(obj, dict):
                for key in list(obj.keys()):
                    if any(sensitive in key.lower() for sensitive in sensitive_keys):
                        obj[key] = "***"
                    else:
                        remove_sensitive(obj[key])

        remove_sensitive(sanitized)
        return sanitized
