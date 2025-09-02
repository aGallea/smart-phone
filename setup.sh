#!/bin/bash

# Smart Robot Project Setup Script

echo "🤖 Smart Robot Project Setup"
echo "=============================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to create Python virtual environment
setup_python_env() {
    local dir=$1
    echo "Setting up Python environment for $dir..."

    cd "$dir"

    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "✅ Created virtual environment"
    fi

    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Installed Python dependencies"

    cd ..
}

# Function to setup Node.js environment
setup_node_env() {
    local dir=$1
    echo "Setting up Node.js environment for $dir..."

    cd "$dir"
    npm install
    echo "✅ Installed Node.js dependencies"

    cd ..
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed"
    exit 1
fi

echo "✅ All prerequisites are available"

# Setup backend server
echo ""
echo "📦 Setting up Backend Server..."
setup_python_env "backend-server"

# Setup termux client
echo ""
echo "📱 Setting up Termux Client..."
setup_python_env "termux-client"

# Setup mobile app
echo ""
echo "📱 Setting up Mobile App..."
setup_node_env "mobile-app"

# Create configuration files from examples
echo ""
echo "⚙️  Creating configuration files..."

if [ ! -f "backend-server/config.json" ]; then
    cp "backend-server/config.json.example" "backend-server/config.json"
    echo "✅ Created backend-server/config.json"
    echo "⚠️  Please update API keys in backend-server/config.json"
fi

if [ ! -f "termux-client/config.json" ]; then
    cp "termux-client/config.json.example" "termux-client/config.json"
    echo "✅ Created termux-client/config.json"
fi

# Create .env file template
echo ""
echo "📝 Creating environment file template..."
cat > .env << EOF
# OpenAI API Key
OPENAI_API_KEY=your-openai-api-key-here

# Anthropic API Key (optional)
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# ElevenLabs API Key (optional)
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here

# Google Cloud credentials (optional)
GOOGLE_APPLICATION_CREDENTIALS=path/to/google-credentials.json

# Azure Speech Service (optional)
AZURE_SPEECH_KEY=your-azure-speech-key
AZURE_SPEECH_REGION=your-azure-region

# Backend Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
EOF

echo "✅ Created .env file template"

# Create logs directories
echo ""
echo "📁 Creating directories..."
mkdir -p backend-server/logs
mkdir -p termux-client/logs
echo "✅ Created log directories"

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Next Steps:"
echo "==========="
echo "1. Update API keys in backend-server/config.json or .env file"
echo "2. Start the backend server:"
echo "   cd backend-server && source venv/bin/activate && python main.py"
echo ""
echo "3. For Termux (Android):"
echo "   - Install Termux from F-Droid"
echo "   - Copy termux-client folder to your Android device"
echo "   - Follow termux-client/README.md for setup"
echo ""
echo "4. For Mobile App:"
echo "   cd mobile-app && npm start"
echo ""
echo "5. Optional - Docker deployment:"
echo "   docker-compose up -d"
echo ""
echo "📚 Documentation:"
echo "   - Project overview: README.md"
echo "   - Backend setup: backend-server/README.md"
echo "   - Termux setup: termux-client/README.md"
echo "   - Mobile app setup: mobile-app/README.md"
