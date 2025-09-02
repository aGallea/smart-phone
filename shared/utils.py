"""
Shared utility functions
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path


def setup_logging(name: str, level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def load_json_config(file_path: str, default_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Load configuration from JSON file with fallback to defaults"""
    config_path = Path(file_path)
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading config from {file_path}: {e}")
    
    return default_config or {}


def save_json_config(config: Dict[str, Any], file_path: str) -> bool:
    """Save configuration to JSON file"""
    try:
        config_path = Path(file_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Error saving config to {file_path}: {e}")
        return False


def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two configuration dictionaries"""
    result = base_config.copy()
    
    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result


def sanitize_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Remove sensitive information from config for logging/display"""
    sensitive_keys = ['api_key', 'password', 'secret', 'token', 'key']
    sanitized = {}
    
    for key, value in config.items():
        if isinstance(value, dict):
            sanitized[key] = sanitize_config(value)
        elif any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = '***' if value else ''
        else:
            sanitized[key] = value
    
    return sanitized


async def retry_async(func, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Retry async function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            wait_time = delay * (backoff ** attempt)
            logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)


def validate_audio_format(audio_data: bytes) -> bool:
    """Basic validation of audio data"""
    if not audio_data or len(audio_data) < 44:  # Minimum WAV header size
        return False
    
    # Check for WAV header
    if audio_data[:4] == b'RIFF' and audio_data[8:12] == b'WAVE':
        return True
    
    return False


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.0f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


class AsyncEventEmitter:
    """Simple async event emitter for component communication"""
    
    def __init__(self):
        self._listeners = {}
    
    def on(self, event: str, callback):
        """Add event listener"""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)
    
    def off(self, event: str, callback):
        """Remove event listener"""
        if event in self._listeners:
            try:
                self._listeners[event].remove(callback)
            except ValueError:
                pass
    
    async def emit(self, event: str, *args, **kwargs):
        """Emit event to all listeners"""
        if event in self._listeners:
            for callback in self._listeners[event]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(*args, **kwargs)
                    else:
                        callback(*args, **kwargs)
                except Exception as e:
                    logging.error(f"Error in event listener for {event}: {e}")


def get_local_ip() -> str:
    """Get local IP address for network configuration"""
    import socket
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
