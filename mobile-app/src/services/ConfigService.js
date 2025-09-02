import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';

const ConfigContext = createContext();

export const useConfig = () => {
  const context = useContext(ConfigContext);
  if (!context) {
    throw new Error('useConfig must be used within a ConfigProvider');
  }
  return context;
};

const DEFAULT_CONFIG = {
  backend: {
    url: 'http://192.168.1.100:8000',
    apiKey: '',
    timeout: 30000
  },
  openai: {
    apiKey: '',
    model: 'gpt-3.5-turbo',
    temperature: 0.7,
    maxTokens: 150
  },
  tts: {
    voice: 'alloy',
    speed: 1.0,
    provider: 'openai'
  },
  robot: {
    name: 'Robot',
    wakeWord: 'hey robot',
    wakeWordEnabled: true,
    systemPrompt: 'You are a helpful personal assistant robot. Keep responses concise and friendly.'
  },
  audio: {
    sampleRate: 16000,
    recordingDuration: 5.0,
    continuousListening: false
  },
  app: {
    autoConnect: true,
    theme: 'light'
  },
  notifications: {
    enabled: true,
    soundEnabled: true
  },
  ui: {
    darkMode: false
  }
};

export const ConfigProvider = ({ children }) => {
  const [config, setConfig] = useState(DEFAULT_CONFIG);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const savedConfig = await AsyncStorage.getItem('@smart_robot_config');
      if (savedConfig) {
        const parsedConfig = JSON.parse(savedConfig);
        setConfig({ ...DEFAULT_CONFIG, ...parsedConfig });
      }
    } catch (error) {
      console.error('Error loading config:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveConfig = async (newConfig) => {
    try {
      await AsyncStorage.setItem('@smart_robot_config', JSON.stringify(newConfig));
      return true;
    } catch (error) {
      console.error('Error saving config:', error);
      throw error;
    }
  };

  const updateConfig = async (newConfig) => {
    try {
      const updatedConfig = { ...config, ...newConfig };
      await saveConfig(updatedConfig);
      setConfig(updatedConfig);
      return updatedConfig;
    } catch (error) {
      throw error;
    }
  };

  const resetConfig = async () => {
    try {
      await saveConfig(DEFAULT_CONFIG);
      setConfig(DEFAULT_CONFIG);
      return DEFAULT_CONFIG;
    } catch (error) {
      throw error;
    }
  };

  const exportConfig = async () => {
    try {
      const configString = JSON.stringify(config, null, 2);
      const fileName = `smart_robot_config_${new Date().toISOString().split('T')[0]}.json`;
      const fileUri = FileSystem.documentDirectory + fileName;

      await FileSystem.writeAsStringAsync(fileUri, configString);

      if (await Sharing.isAvailableAsync()) {
        await Sharing.shareAsync(fileUri);
      }

      return fileUri;
    } catch (error) {
      console.error('Error exporting config:', error);
      throw error;
    }
  };

  const importConfig = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: 'application/json',
        copyToCacheDirectory: true
      });

      if (result.type === 'success') {
        const configString = await FileSystem.readAsStringAsync(result.uri);
        const importedConfig = JSON.parse(configString);

        // Validate config structure
        const validatedConfig = { ...DEFAULT_CONFIG, ...importedConfig };

        await updateConfig(validatedConfig);
        return validatedConfig;
      }
    } catch (error) {
      console.error('Error importing config:', error);
      throw error;
    }
  };

  const getConfigValue = (path, defaultValue = null) => {
    const keys = path.split('.');
    let value = config;

    for (const key of keys) {
      if (value && typeof value === 'object' && key in value) {
        value = value[key];
      } else {
        return defaultValue;
      }
    }

    return value;
  };

  const setConfigValue = async (path, value) => {
    const keys = path.split('.');
    const newConfig = { ...config };
    let current = newConfig;

    for (let i = 0; i < keys.length - 1; i++) {
      const key = keys[i];
      if (!(key in current) || typeof current[key] !== 'object') {
        current[key] = {};
      }
      current = current[key];
    }

    current[keys[keys.length - 1]] = value;

    return await updateConfig(newConfig);
  };

  const contextValue = {
    config,
    loading,
    updateConfig,
    resetConfig,
    exportConfig,
    importConfig,
    getConfigValue,
    setConfigValue,
    saveConfig,
    loadConfig
  };

  return (
    <ConfigContext.Provider value={contextValue}>
      {children}
    </ConfigContext.Provider>
  );
};
