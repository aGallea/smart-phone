# Smart Robot Assistant

A distributed smart robot system composed of three components:

## Components

### 1. Termux Client (`termux-client/`)
Python application that runs on an old smartphone (Galaxy S8) using Termux. Handles:
- Audio recording via microphone
- Audio playback via speakers
- Voice command processing
- Communication with backend server

### 2. Backend Server (`backend-server/`)
Python server that provides LLM operations:
- Speech-to-Text (STT) conversion
- Text-to-Speech (TTS) generation
- LLM integration for response generation
- API endpoints for client communication

### 3. Mobile App (`mobile-app/`)
Management application for the user's main phone:
- Configuration management (prompts, API keys, server settings)
- Bridge communication between termux client and backend
- System monitoring and control

### 4. Shared (`shared/`)
Common utilities and configurations used across components.

## Setup

See individual component READMEs for specific setup instructions:
- [Termux Client Setup](termux-client/README.md)
- [Backend Server Setup](backend-server/README.md)
- [Mobile App Setup](mobile-app/README.md)

## Architecture

```
[User] <-> [Mobile App] <-> [Backend Server] <-> [LLM APIs]
                |
                v
        [Termux Client (Old Phone)]
```