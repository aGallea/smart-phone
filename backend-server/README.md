# Backend Server - J.A.R.V.I.S

FastAPI server providing LLM operations with J.A.R.V.I.S

## Features

- **Speech-to-Text (STT)**: Convert audio to text using OpenAI Whisper, Google Cloud Speech, or Azure
- **Text-to-Speech (TTS)**: Generate speech from text using OpenAI, Google Cloud, Azure, or ElevenLabs
- **LLM Integration**: Generate responses using OpenAI GPT, Anthropic Claude, or local Ollama models
- **RESTful API**: Clean API endpoints for client communication
- **Multi-provider Support**: Easy switching between different AI service providers

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configuration
Copy `config.json.example` to `config.json` and configure:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000
  },
  "stt": {
    "provider": "openai",
    "openai_api_key": "your-openai-api-key"
  },
  "tts": {
    "provider": "openai",
    "openai_api_key": "your-openai-api-key",
    "voice": "alloy"
  },
  "llm": {
    "provider": "openai",
    "openai_api_key": "your-openai-api-key",
    "model": "gpt-3.5-turbo",
    "system_prompt": "You are a helpful personal assistant robot."
  }
}
```

### 3. Run Server
```bash
# Development
python main.py

# Production with Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
```
GET /health
```

### Status
```
GET /api/status
```

### Speech-to-Text
```
POST /api/stt
Content-Type: multipart/form-data
Body: audio file (WAV recommended)
```

### Text-to-Speech
```
POST /api/tts
Content-Type: application/json
Body: {"text": "Hello world"}
```

### Generate LLM Response
```
POST /api/generate
Content-Type: application/json
Body: {
  "user_input": "What time is it?",
  "context": {"location": "home"}
}
```

### Update Configuration
```
POST /api/config
Content-Type: application/json
Body: {
  "config": {
    "llm.temperature": 0.8,
    "tts.voice": "nova"
  }
}
```

## Supported Providers

### STT (Speech-to-Text)
- **OpenAI Whisper**: `openai` (Recommended)
- **Google Cloud Speech**: `google`
- **Azure Cognitive Services**: `azure`

### TTS (Text-to-Speech)
- **OpenAI**: `openai` (Recommended)
- **Google Cloud Text-to-Speech**: `google`
- **Azure Cognitive Services**: `azure`
- **ElevenLabs**: `elevenlabs`

### LLM (Language Models)
- **OpenAI GPT**: `openai` (gpt-3.5-turbo, gpt-4)
- **Anthropic Claude**: `anthropic`
- **Ollama**: `ollama` (Local models)

## Environment Variables

Create a `.env` file for sensitive configuration:
```bash
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
ELEVENLABS_API_KEY=your-elevenlabs-key
GOOGLE_APPLICATION_CREDENTIALS=path/to/google-credentials.json
AZURE_SPEECH_KEY=your-azure-key
AZURE_SPEECH_REGION=your-azure-region
```

## File Structure
- `main.py` - FastAPI application and routes
- `config.py` - Configuration management
- `services/` - Service implementations
  - `stt_service.py` - Speech-to-Text service
  - `tts_service.py` - Text-to-Speech service
  - `llm_service.py` - LLM service
- `models/` - Pydantic models
  - `requests.py` - Request models
  - `responses.py` - Response models

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Systemd Service
Create `/etc/systemd/system/smart-robot-backend.service`:
```ini
[Unit]
Description=J.A.R.V.I.S Backend
After=network.target

[Service]
Type=simple
User=robot
WorkingDirectory=/path/to/backend-server
ExecStart=/path/to/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```
