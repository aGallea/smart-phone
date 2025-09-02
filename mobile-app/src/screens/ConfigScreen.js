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
  TextInput,
  Button,
  List,
  Divider,
  Switch,
  Paragraph
} from 'react-native-paper';
import { useConfig } from '../services/ConfigService';
import { useBackend } from '../services/BackendService';

const ConfigScreen = () => {
  const { config, updateConfig } = useConfig();
  const { updateBackendConfig } = useBackend();
  const [localConfig, setLocalConfig] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (config) {
      setLocalConfig(config);
    }
  }, [config]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateConfig(localConfig);
      await updateBackendConfig(localConfig);
      Alert.alert('Success', 'Configuration saved successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to save configuration: ' + error.message);
    } finally {
      setSaving(false);
    }
  };

  const updateField = (section, field, value) => {
    setLocalConfig(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  return (
    <ScrollView style={styles.container}>
      {/* Backend Server Configuration */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Backend Server</Title>
          <TextInput
            label="Server URL"
            value={localConfig.backend?.url || ''}
            onChangeText={(text) => updateField('backend', 'url', text)}
            style={styles.input}
            placeholder="http://192.168.1.100:8000"
          />
          <TextInput
            label="API Key"
            value={localConfig.backend?.apiKey || ''}
            onChangeText={(text) => updateField('backend', 'apiKey', text)}
            style={styles.input}
            secureTextEntry
            placeholder="Optional API key"
          />
        </Card.Content>
      </Card>

      {/* AI Services Configuration */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>AI Services</Title>
          
          {/* OpenAI Configuration */}
          <List.Subheader>OpenAI</List.Subheader>
          <TextInput
            label="OpenAI API Key"
            value={localConfig.openai?.apiKey || ''}
            onChangeText={(text) => updateField('openai', 'apiKey', text)}
            style={styles.input}
            secureTextEntry
            placeholder="sk-..."
          />
          <TextInput
            label="GPT Model"
            value={localConfig.openai?.model || ''}
            onChangeText={(text) => updateField('openai', 'model', text)}
            style={styles.input}
            placeholder="gpt-3.5-turbo"
          />
          
          <Divider style={styles.divider} />
          
          {/* TTS Configuration */}
          <List.Subheader>Text-to-Speech</List.Subheader>
          <TextInput
            label="Voice"
            value={localConfig.tts?.voice || ''}
            onChangeText={(text) => updateField('tts', 'voice', text)}
            style={styles.input}
            placeholder="alloy"
          />
          <TextInput
            label="Speed"
            value={localConfig.tts?.speed?.toString() || ''}
            onChangeText={(text) => updateField('tts', 'speed', parseFloat(text) || 1.0)}
            style={styles.input}
            placeholder="1.0"
            keyboardType="numeric"
          />
        </Card.Content>
      </Card>

      {/* Robot Configuration */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Robot Settings</Title>
          
          <View style={styles.switchRow}>
            <Paragraph>Wake Word Enabled</Paragraph>
            <Switch
              value={localConfig.robot?.wakeWordEnabled || false}
              onValueChange={(value) => updateField('robot', 'wakeWordEnabled', value)}
            />
          </View>
          
          <TextInput
            label="Wake Word"
            value={localConfig.robot?.wakeWord || ''}
            onChangeText={(text) => updateField('robot', 'wakeWord', text)}
            style={styles.input}
            placeholder="hey robot"
          />
          
          <TextInput
            label="Assistant Name"
            value={localConfig.robot?.name || ''}
            onChangeText={(text) => updateField('robot', 'name', text)}
            style={styles.input}
            placeholder="Robot"
          />
          
          <TextInput
            label="System Prompt"
            value={localConfig.robot?.systemPrompt || ''}
            onChangeText={(text) => updateField('robot', 'systemPrompt', text)}
            style={styles.input}
            multiline
            numberOfLines={4}
            placeholder="You are a helpful personal assistant robot..."
          />
        </Card.Content>
      </Card>

      {/* Audio Configuration */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Audio Settings</Title>
          
          <TextInput
            label="Sample Rate"
            value={localConfig.audio?.sampleRate?.toString() || ''}
            onChangeText={(text) => updateField('audio', 'sampleRate', parseInt(text) || 16000)}
            style={styles.input}
            placeholder="16000"
            keyboardType="numeric"
          />
          
          <TextInput
            label="Recording Duration (seconds)"
            value={localConfig.audio?.recordingDuration?.toString() || ''}
            onChangeText={(text) => updateField('audio', 'recordingDuration', parseFloat(text) || 5.0)}
            style={styles.input}
            placeholder="5.0"
            keyboardType="numeric"
          />
          
          <View style={styles.switchRow}>
            <Paragraph>Continuous Listening</Paragraph>
            <Switch
              value={localConfig.audio?.continuousListening || false}
              onValueChange={(value) => updateField('audio', 'continuousListening', value)}
            />
          </View>
        </Card.Content>
      </Card>

      {/* Save Button */}
      <Button
        mode="contained"
        onPress={handleSave}
        loading={saving}
        disabled={saving}
        style={styles.saveButton}
      >
        Save Configuration
      </Button>
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
  input: {
    marginBottom: 12,
  },
  divider: {
    marginVertical: 16,
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    marginBottom: 12,
  },
  saveButton: {
    marginVertical: 20,
    paddingVertical: 8,
  },
});

export default ConfigScreen;
