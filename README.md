# Smart Robot Project

A comprehensive smart robot system that can listen, speak, and receive commands. This project consists of three main components:

1. **Termux Client** - Python application running on an old smartphone (Galaxy S8) via Termux
2. **Backend Server** - Python FastAPI server providing AI services
3. **Mobile App** - React Native application for managing and operating the robot

## Quick Start

### Automated Installation (Recommended)

For Python 3.12+ compatibility issues, use the automated installer:

```bash
# Make installation script executable and run
chmod +x install.sh
./install.sh
```

### Test Installation

After installation, verify everything works:

```bash
python3 test_installation.py
```

### Manual Installation

If you prefer manual setup, see the individual component README files in each directory.

## Python 3.12+ Compatibility

This project includes special handling for Python 3.12+ compatibility issues:

- **Audio Libraries**: Uses sounddevice and simpleaudio as fallbacks when pyaudio fails
- **Pydantic**: Updated to version 2.6.1 with compatibility flags
- **FastAPI**: Updated to version 0.109.2 for Python 3.12 support

## Project Structure

```
smart-phone/
├── install.sh             # Automated installation script
├── test_installation.py   # Installation verification
├── termux-client/          # Python client for Android (Termux)
│   ├── main.py            # Main application entry point
│   ├── audio_handler.py   # Multi-library audio support
│   ├── wake_word.py       # Wake word detection
│   ├── api_client.py      # Backend API communication
│   ├── config.py          # Configuration management
│   └── requirements.txt   # Python dependencies
├── backend-server/         # FastAPI backend server
│   ├── main.py            # FastAPI application
│   ├── services/          # AI services (STT, TTS, LLM)
│   ├── models/            # Data models
│   ├── config.py          # Configuration management
│   └── requirements.txt   # Python dependencies
├── mobile-app/            # React Native mobile application
│   ├── App.js             # Main application component
│   ├── screens/           # Application screens
│   ├── services/          # API services
│   └── package.json       # Node.js dependencies
└── README.md              # This file
```

## Components

### 1. Termux Client (`termux-client/`)
Python application that runs on an old smartphone (Galaxy S8) using Termux. Handles:
- Audio recording via microphone with fallback libraries
- Audio playback via speakers
- Voice command processing with wake word detection
- Communication with backend server

### 2. Backend Server (`backend-server/`)
Python FastAPI server that provides AI services:
- Speech-to-Text (STT) conversion using OpenAI Whisper
- Text-to-Speech (TTS) generation
- LLM integration for intelligent responses
- RESTful API endpoints for client communication

### 3. Mobile App (`mobile-app/`)
React Native management application:
- Configuration management (prompts, API keys, server settings)
- Real-time monitoring of robot status
- Direct communication with backend server
- User-friendly interface for robot control

## Getting Started

1. **Run the installer**: `./install.sh`
2. **Test the installation**: `python3 test_installation.py`
3. **Configure API keys** in `backend-server/config.json`
4. **Start the backend server**:
   ```bash
   cd backend-server
   source venv/bin/activate
   python main.py
   ```
5. **Set up Termux on Android** (see termux-client/README.md)
6. **Launch mobile app**:
   ```bash
   cd mobile-app
   npm start
   ```

## Troubleshooting

### Python 3.12+ Issues
- If pydantic-core fails to build: Use `--no-binary=pydantic-core` flag
- If pyaudio installation fails: The project will use sounddevice/simpleaudio automatically

### Audio Issues in Termux
```bash
pkg install portaudio pulseaudio
pip install --force-reinstall sounddevice
```

## Architecture

```
[User] <-> [Mobile App] <-> [Backend Server] <-> [OpenAI APIs]
                |                   |
                |                   v
                |            [LLM Processing]
                |                   |
                v                   v
        [Termux Client] <----------'
        (Old Android Phone)
```
