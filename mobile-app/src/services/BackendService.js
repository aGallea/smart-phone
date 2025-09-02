import React, { createContext, useContext, useState, useEffect } from 'react';
import { useConfig } from './ConfigService';

const BackendContext = createContext();

export const useBackend = () => {
  const context = useContext(BackendContext);
  if (!context) {
    throw new Error('useBackend must be used within a BackendProvider');
  }
  return context;
};

export const BackendProvider = ({ children }) => {
  const { config } = useConfig();
  const [isConnected, setIsConnected] = useState(false);
  const [status, setStatus] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  const baseUrl = config?.backend?.url || 'http://192.168.1.100:8000';
  const apiKey = config?.backend?.apiKey;
  const timeout = config?.backend?.timeout || 30000;

  useEffect(() => {
    if (config?.app?.autoConnect) {
      connect();
    }
  }, [config]);

  const getHeaders = () => {
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (apiKey) {
      headers['Authorization'] = `Bearer ${apiKey}`;
    }
    
    return headers;
  };

  const makeRequest = async (endpoint, options = {}) => {
    const url = `${baseUrl}${endpoint}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...getHeaders(),
          ...options.headers,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      
      throw error;
    }
  };

  const connect = async () => {
    setLoading(true);
    try {
      const response = await makeRequest('/health');
      const data = await response.json();
      
      if (data.status === 'healthy') {
        setIsConnected(true);
        await getStatus();
      } else {
        throw new Error('Backend server is not healthy');
      }
    } catch (error) {
      setIsConnected(false);
      console.error('Connection failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const disconnect = () => {
    setIsConnected(false);
    setStatus(null);
    setLogs([]);
  };

  const getStatus = async () => {
    try {
      const response = await makeRequest('/api/status');
      const data = await response.json();
      setStatus(data);
      return data;
    } catch (error) {
      console.error('Error getting status:', error);
      throw error;
    }
  };

  const sendCommand = async (command, context = {}) => {
    if (!isConnected) {
      throw new Error('Not connected to backend server');
    }

    try {
      const response = await makeRequest('/api/generate', {
        method: 'POST',
        body: JSON.stringify({
          user_input: command,
          context: context
        }),
      });

      const data = await response.json();
      
      // Add to logs
      addLog('info', `Command sent: ${command}`);
      addLog('info', `Response: ${data.response}`);
      
      return data.response;
    } catch (error) {
      addLog('error', `Command failed: ${error.message}`);
      throw error;
    }
  };

  const speechToText = async (audioBlob) => {
    if (!isConnected) {
      throw new Error('Not connected to backend server');
    }

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'audio.wav');

      const response = await makeRequest('/api/stt', {
        method: 'POST',
        headers: {
          // Don't set Content-Type for FormData
          ...(apiKey && { 'Authorization': `Bearer ${apiKey}` }),
        },
        body: formData,
      });

      const data = await response.json();
      addLog('info', `STT result: ${data.text}`);
      return data.text;
    } catch (error) {
      addLog('error', `STT failed: ${error.message}`);
      throw error;
    }
  };

  const textToSpeech = async (text) => {
    if (!isConnected) {
      throw new Error('Not connected to backend server');
    }

    try {
      const response = await makeRequest('/api/tts', {
        method: 'POST',
        body: JSON.stringify({ text }),
      });

      const audioBlob = await response.blob();
      addLog('info', `TTS generated for: ${text}`);
      return audioBlob;
    } catch (error) {
      addLog('error', `TTS failed: ${error.message}`);
      throw error;
    }
  };

  const updateBackendConfig = async (newConfig) => {
    if (!isConnected) {
      throw new Error('Not connected to backend server');
    }

    try {
      const response = await makeRequest('/api/config', {
        method: 'POST',
        body: JSON.stringify({ config: newConfig }),
      });

      const data = await response.json();
      addLog('info', 'Backend configuration updated');
      return data;
    } catch (error) {
      addLog('error', `Config update failed: ${error.message}`);
      throw error;
    }
  };

  const getBackendConfig = async () => {
    if (!isConnected) {
      throw new Error('Not connected to backend server');
    }

    try {
      const response = await makeRequest('/api/config');
      const data = await response.json();
      return data.config;
    } catch (error) {
      console.error('Error getting backend config:', error);
      throw error;
    }
  };

  const getLogs = async () => {
    // This would typically fetch logs from the backend
    // For now, return the local logs
    return logs;
  };

  const addLog = (level, message) => {
    const log = {
      timestamp: new Date().toISOString(),
      level,
      message,
    };
    
    setLogs(prevLogs => [log, ...prevLogs.slice(0, 99)]); // Keep last 100 logs
  };

  const clearLogs = () => {
    setLogs([]);
  };

  const contextValue = {
    isConnected,
    status,
    logs,
    loading,
    connect,
    disconnect,
    getStatus,
    sendCommand,
    speechToText,
    textToSpeech,
    updateBackendConfig,
    getBackendConfig,
    getLogs,
    addLog,
    clearLogs,
  };

  return (
    <BackendContext.Provider value={contextValue}>
      {children}
    </BackendContext.Provider>
  );
};
