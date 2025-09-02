# Termux Client - Smart Robot Assistant

This component runs on an old smartphone via Termux and handles:
- Audio recording via microphone
- Audio playback via speakers
- Voice command processing
- Communication with backend server

## Setup for Termux (Android)

### 1. Install Termux
Download Termux from F-Droid (recommended) or Google Play Store.

### 2. Install System Dependencies
```bash
# Update packages
pkg update && pkg upgrade

# Install Python and audio dependencies
pkg install python python-pip portaudio

# Install additional packages for audio processing
pkg install ffmpeg sox
```

### 3. Install Python Dependencies
```bash
# Install required Python packages
pip install -r requirements.txt
```

### 4. Grant Permissions
In Android settings, grant Termux:
- Microphone permission
- Storage permission

### 5. Configuration
Copy `config.json.example` to `config.json` and update:
```json
{
  "backend_url": "http://YOUR_BACKEND_IP:8000",
  "wake_word": "hey robot",
  "audio": {
    "sample_rate": 16000,
    "channels": 1
  }
}
```

## Usage

### Run the Client
```bash
python main.py
```

### Wake Word Mode
The client listens for the wake word "hey robot" (configurable), then activates to listen for commands.

### Commands
- "What time is it?"
- "What's the date?"
- "Hello"
- Any other question (processed by LLM backend)

## File Structure
- `main.py` - Main application entry point
- `audio_handler.py` - Audio recording and playback
- `api_client.py` - Backend server communication
- `config.py` - Configuration management
- `voice_processor.py` - Voice processing and command handling
- `requirements.txt` - Python dependencies

## Troubleshooting

### Audio Issues
If you get audio errors:
```bash
# Reinstall portaudio
pkg reinstall portaudio

# Check audio devices
python -c "import pyaudio; p=pyaudio.PyAudio(); print([p.get_device_info_by_index(i) for i in range(p.get_device_count())])"
```

### Network Issues
- Ensure backend server is running and accessible
- Check firewall settings on backend server
- Verify IP address in config.json

### Performance
- Lower sample rate if performance is poor
- Adjust chunk_size in config for better responsiveness
- Use WiFi instead of mobile data for better latency
