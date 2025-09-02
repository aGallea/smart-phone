# Smart Robot Mobile App

React Native/Expo mobile application for managing and controlling the Smart Robot system.

## Features

- **System Monitoring**: Real-time status monitoring of robot and backend services
- **Configuration Management**: Configure backend server, AI services, and robot settings
- **Remote Control**: Send commands directly to the robot
- **Settings Management**: App preferences and configuration backup/restore

## Setup

### Prerequisites
- Node.js 16+
- Expo CLI (`npm install -g expo-cli`)
- Expo Go app on your phone (for development)

### Installation

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm start
   # or
   expo start
   ```

3. **Run on Device**
   - Scan QR code with Expo Go app (Android)
   - Scan QR code with Camera app (iOS)

### Building for Production

```bash
# Build APK (Android)
expo build:android

# Build IPA (iOS)
expo build:ios
```

## Configuration

### Backend Connection
Configure the backend server URL in the app settings:
- Default: `http://192.168.1.100:8000`
- Make sure your phone and backend server are on the same network

### AI Service Setup
Configure API keys for AI services:
- OpenAI API key for GPT and Whisper
- Other providers as needed (Google Cloud, Azure, etc.)

## Screens

### Home Screen
- Connection status display
- Quick command buttons
- Robot control buttons
- System status overview

### Monitoring Screen
- Real-time service status
- System logs
- Performance metrics
- Configuration overview

### Configuration Screen
- Backend server settings
- AI service configuration
- Robot behavior settings
- Audio configuration

### Settings Screen
- App preferences
- Configuration backup/restore
- About information
- Support options

## Architecture

```
App.js
├── src/
│   ├── screens/
│   │   ├── HomeScreen.js
│   │   ├── MonitoringScreen.js
│   │   ├── ConfigScreen.js
│   │   └── SettingsScreen.js
│   ├── services/
│   │   ├── ConfigService.js
│   │   └── BackendService.js
│   └── components/
│       └── (shared components)
```

## Services

### ConfigService
- Local configuration management
- AsyncStorage for persistence
- Configuration import/export
- Default configuration handling

### BackendService
- REST API communication with backend server
- Connection management
- Request/response handling
- Error handling and retries

## Development

### Project Structure
```
mobile-app/
├── App.js                 # Main app component
├── package.json          # Dependencies and scripts
├── src/
│   ├── screens/          # Screen components
│   ├── services/         # Business logic services
│   ├── components/       # Reusable UI components
│   └── utils/           # Utility functions
```

### Key Libraries
- **React Native Paper**: Material Design UI components
- **React Navigation**: Navigation between screens
- **AsyncStorage**: Local data persistence
- **Expo**: Development platform and build tools

### API Integration
The app communicates with the backend server through REST API:
- `/health` - Health check
- `/api/status` - System status
- `/api/generate` - Send commands
- `/api/config` - Configuration management

## Deployment

### Android
```bash
# Generate APK
expo build:android

# Generate AAB (for Play Store)
expo build:android -t app-bundle
```

### iOS
```bash
# Generate IPA
expo build:ios
```

### Web
```bash
# Build for web
expo build:web
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check backend server is running
   - Verify IP address in configuration
   - Ensure devices are on same network

2. **Build Errors**
   - Clear cache: `expo r -c`
   - Reinstall dependencies: `rm -rf node_modules && npm install`

3. **Performance Issues**
   - Enable developer mode in Expo Go
   - Check network latency to backend
   - Monitor device logs

### Network Configuration
- Backend server must be accessible from mobile device
- Use local IP address (not localhost) for backend URL
- Consider firewall settings on backend server

### Development Tips
- Use `expo logs` to view device logs
- Enable remote debugging in Expo Go
- Test on physical device for accurate performance
- Use Expo tunnel for testing over internet
