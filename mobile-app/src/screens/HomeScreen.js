import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Alert
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Chip,
  Surface,
  ActivityIndicator
} from 'react-native-paper';
import { useBackend } from '../services/BackendService';

const HomeScreen = () => {
  const { status, sendCommand, isConnected, connect, disconnect } = useBackend();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Auto-connect on component mount
    if (!isConnected) {
      connect();
    }
  }, []);

  const handleQuickCommand = async (command) => {
    setLoading(true);
    try {
      const response = await sendCommand(command);
      Alert.alert('Response', response || 'Command sent successfully');
    } catch (error) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const quickCommands = [
    'What time is it?',
    'How is the weather?',
    'Tell me a joke',
    'What can you do?'
  ];

  return (
    <ScrollView style={styles.container}>
      {/* Connection Status */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Connection Status</Title>
          <View style={styles.statusContainer}>
            <Chip 
              icon={isConnected ? 'check-circle' : 'alert-circle'}
              style={[
                styles.statusChip,
                { backgroundColor: isConnected ? '#4caf50' : '#f44336' }
              ]}
              textStyle={{ color: 'white' }}
            >
              {isConnected ? 'Connected' : 'Disconnected'}
            </Chip>
            {!isConnected && (
              <Button 
                mode="contained" 
                onPress={connect}
                style={styles.connectButton}
              >
                Connect
              </Button>
            )}
          </View>
        </Card.Content>
      </Card>

      {/* System Status */}
      {status && (
        <Card style={styles.card}>
          <Card.Content>
            <Title>System Status</Title>
            <View style={styles.serviceStatus}>
              <Paragraph>Speech-to-Text: {status.services?.stt ? '✅' : '❌'}</Paragraph>
              <Paragraph>Text-to-Speech: {status.services?.tts ? '✅' : '❌'}</Paragraph>
              <Paragraph>LLM Service: {status.services?.llm ? '✅' : '❌'}</Paragraph>
            </View>
          </Card.Content>
        </Card>
      )}

      {/* Quick Commands */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Quick Commands</Title>
          <Paragraph style={styles.subtitle}>
            Send these commands directly to your robot
          </Paragraph>
          <View style={styles.commandGrid}>
            {quickCommands.map((command, index) => (
              <Surface key={index} style={styles.commandButton}>
                <Button
                  mode="outlined"
                  onPress={() => handleQuickCommand(command)}
                  disabled={!isConnected || loading}
                  loading={loading}
                  style={styles.commandButtonInner}
                >
                  {command}
                </Button>
              </Surface>
            ))}
          </View>
        </Card.Content>
      </Card>

      {/* Robot Controls */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Robot Controls</Title>
          <View style={styles.controlButtons}>
            <Button
              mode="contained"
              onPress={() => handleQuickCommand('Start listening')}
              disabled={!isConnected}
              style={styles.controlButton}
            >
              Start Listening
            </Button>
            <Button
              mode="outlined"
              onPress={() => handleQuickCommand('Stop listening')}
              disabled={!isConnected}
              style={styles.controlButton}
            >
              Stop Listening
            </Button>
            <Button
              mode="contained"
              onPress={() => handleQuickCommand('Test audio')}
              disabled={!isConnected}
              style={styles.controlButton}
              buttonColor="#ff9800"
            >
              Test Audio
            </Button>
          </View>
        </Card.Content>
      </Card>

      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#6200ea" />
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  card: {
    marginBottom: 16,
    elevation: 4,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  statusChip: {
    paddingHorizontal: 8,
  },
  connectButton: {
    marginLeft: 16,
  },
  serviceStatus: {
    marginTop: 8,
  },
  subtitle: {
    marginBottom: 16,
    color: '#666',
  },
  commandGrid: {
    gap: 8,
  },
  commandButton: {
    marginBottom: 8,
    borderRadius: 8,
    elevation: 2,
  },
  commandButtonInner: {
    margin: 8,
  },
  controlButtons: {
    gap: 12,
    marginTop: 8,
  },
  controlButton: {
    marginBottom: 8,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default HomeScreen;
