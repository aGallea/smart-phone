#!/bin/bash

# Smart Robot Installation Script with Python Version Check
# Handles Python 3.12+ compatibility issues

echo "🤖 Smart Robot Installation Script"
echo "=================================="

# Function to check Python version
check_python_version() {
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo "Detected Python version: $python_version"

    # Check if version is 3.12 or higher
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)"; then
        echo "⚠️  Python 3.12+ detected - using compatibility mode"
        return 0
    else
        echo "✅ Python version compatible"
        return 1
    fi
}

# Function to install packages with compatibility handling
install_python_packages() {
    local dir=$1
    local is_python312=$2

    echo "Installing Python packages for $dir..."
    cd "$dir"

    # Activate virtual environment
    source venv/bin/activate

    # Upgrade pip and setuptools
    pip install --upgrade pip setuptools wheel

    if [ "$is_python312" = "true" ]; then
        echo "Installing with Python 3.12 compatibility..."

        # Install packages one by one for better error handling
        while IFS= read -r package; do
            # Skip comments and empty lines
            if [[ $package =~ ^[[:space:]]*# ]] || [[ -z "$package" ]]; then
                continue
            fi

            echo "Installing: $package"
            if ! pip install "$package"; then
                echo "⚠️  Failed to install $package, trying alternatives..."

                # Handle specific package failures
                case $package in
                    "pyaudio"*)
                        echo "pyaudio failed, installing sounddevice instead"
                        pip install sounddevice simpleaudio
                        ;;
                    "pydantic"*)
                        echo "Installing pydantic with --no-binary flag"
                        pip install --no-binary=pydantic-core pydantic
                        ;;
                    *)
                        echo "Skipping $package"
                        ;;
                esac
            fi
        done < requirements.txt
    else
        # Standard installation
        pip install -r requirements.txt
    fi

    cd ..
}

# Check Python version
if check_python_version; then
    PYTHON312_MODE="true"
else
    PYTHON312_MODE="false"
fi

# Create virtual environments and install packages
echo ""
echo "📦 Setting up Backend Server..."
cd backend-server
python3 -m venv venv
install_python_packages "." "$PYTHON312_MODE"

echo ""
echo "📱 Setting up Termux Client..."
cd ../termux-client
python3 -m venv venv
install_python_packages "." "$PYTHON312_MODE"

echo ""
echo "📱 Setting up Mobile App..."
cd ../mobile-app
if command -v npm >/dev/null 2>&1; then
    npm install
    echo "✅ Mobile app dependencies installed"
else
    echo "❌ npm not found, skipping mobile app setup"
fi

cd ..

# Create configuration files
echo ""
echo "⚙️  Creating configuration files..."

if [ ! -f "backend-server/config.json" ]; then
    cp "backend-server/config.json.example" "backend-server/config.json"
    echo "✅ Created backend-server/config.json"
fi

if [ ! -f "termux-client/config.json" ]; then
    cp "termux-client/config.json.example" "termux-client/config.json"
    echo "✅ Created termux-client/config.json"
fi

# Create Python version specific instructions
echo ""
echo "📋 Installation Summary"
echo "======================"

if [ "$PYTHON312_MODE" = "true" ]; then
    echo "Python 3.12+ detected. Some compatibility adjustments were made:"
    echo "- Used alternative audio libraries (sounddevice, simpleaudio)"
    echo "- Installed pydantic with compatibility flags"
    echo ""
    echo "If you encounter issues:"
    echo "1. For audio problems in Termux:"
    echo "   pkg install portaudio pulseaudio"
    echo "   pip install --force-reinstall sounddevice"
    echo ""
    echo "2. For backend issues:"
    echo "   cd backend-server && source venv/bin/activate"
    echo "   pip install --no-binary=pydantic-core pydantic==2.6.1"
fi

echo ""
echo "🎉 Installation Complete!"
echo ""
echo "Next Steps:"
echo "1. Update API keys in backend-server/config.json"
echo "2. Start backend: cd backend-server && source venv/bin/activate && python main.py"
echo "3. For mobile app: cd mobile-app && npm start"
echo ""
echo "For Termux setup on Android:"
echo "1. Install Termux from F-Droid"
echo "2. Run: pkg update && pkg install python portaudio"
echo "3. Copy termux-client folder to your device"
echo "4. Follow termux-client/README.md"
