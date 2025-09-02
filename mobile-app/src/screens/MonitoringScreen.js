import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  RefreshControl
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  List,
  Chip,
  Button,
  ActivityIndicator
} from 'react-native-paper';
import { useBackend } from '../services/BackendService';

const MonitoringScreen = () => {
  const { status, logs, isConnected, getStatus, getLogs } = useBackend();
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      await Promise.all([getStatus(), getLogs()]);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  };

  const getStatusColor = (isActive) => {
    return isActive ? '#4caf50' : '#f44336';
  };

  const getStatusText = (isActive) => {
    return isActive ? 'Active' : 'Inactive';
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#6200ea" />
        <Paragraph style={styles.loadingText}>Loading monitoring data...</Paragraph>
      </View>
    );
  }

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Connection Status */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Connection Status</Title>
          <View style={styles.statusRow}>
            <Paragraph>Backend Server:</Paragraph>
            <Chip 
              style={[styles.statusChip, { backgroundColor: getStatusColor(isConnected) }]}
              textStyle={{ color: 'white' }}
            >
              {getStatusText(isConnected)}
            </Chip>
          </View>
        </Card.Content>
      </Card>

      {/* Service Status */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Service Status</Title>
          {status ? (
            <>
              <View style={styles.statusRow}>
                <Paragraph>Speech-to-Text:</Paragraph>
                <Chip 
                  style={[styles.statusChip, { backgroundColor: getStatusColor(status.services?.stt) }]}
                  textStyle={{ color: 'white' }}
                >
                  {getStatusText(status.services?.stt)}
                </Chip>
              </View>
              <View style={styles.statusRow}>
                <Paragraph>Text-to-Speech:</Paragraph>
                <Chip 
                  style={[styles.statusChip, { backgroundColor: getStatusColor(status.services?.tts) }]}
                  textStyle={{ color: 'white' }}
                >
                  {getStatusText(status.services?.tts)}
                </Chip>
              </View>
              <View style={styles.statusRow}>
                <Paragraph>LLM Service:</Paragraph>
                <Chip 
                  style={[styles.statusChip, { backgroundColor: getStatusColor(status.services?.llm) }]}
                  textStyle={{ color: 'white' }}
                >
                  {getStatusText(status.services?.llm)}
                </Chip>
              </View>
            </>
          ) : (
            <Paragraph>No status data available</Paragraph>
          )}
        </Card.Content>
      </Card>

      {/* Configuration Info */}
      {status?.config && (
        <Card style={styles.card}>
          <Card.Content>
            <Title>Current Configuration</Title>
            <List.Item
              title="STT Provider"
              description={status.config.stt_provider || 'Not configured'}
              left={(props) => <List.Icon {...props} icon="microphone" />}
            />
            <List.Item
              title="TTS Provider"
              description={status.config.tts_provider || 'Not configured'}
              left={(props) => <List.Icon {...props} icon="volume-high" />}
            />
            <List.Item
              title="LLM Provider"
              description={status.config.llm_provider || 'Not configured'}
              left={(props) => <List.Icon {...props} icon="brain" />}
            />
          </Card.Content>
        </Card>
      )}

      {/* System Logs */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Recent Logs</Title>
          {logs && logs.length > 0 ? (
            <ScrollView style={styles.logsContainer} nestedScrollEnabled>
              {logs.slice(0, 20).map((log, index) => (
                <View key={index} style={styles.logEntry}>
                  <Paragraph style={styles.logTimestamp}>
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </Paragraph>
                  <Paragraph style={[
                    styles.logLevel,
                    { color: getLogLevelColor(log.level) }
                  ]}>
                    [{log.level}]
                  </Paragraph>
                  <Paragraph style={styles.logMessage}>{log.message}</Paragraph>
                </View>
              ))}
            </ScrollView>
          ) : (
            <Paragraph>No logs available</Paragraph>
          )}
        </Card.Content>
      </Card>

      {/* Performance Metrics */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Performance Metrics</Title>
          <List.Item
            title="Uptime"
            description="2h 34m"
            left={(props) => <List.Icon {...props} icon="clock" />}
          />
          <List.Item
            title="Total Requests"
            description="147"
            left={(props) => <List.Icon {...props} icon="counter" />}
          />
          <List.Item
            title="Average Response Time"
            description="1.2s"
            left={(props) => <List.Icon {...props} icon="speedometer" />}
          />
          <List.Item
            title="Error Rate"
            description="2.1%"
            left={(props) => <List.Icon {...props} icon="alert-circle" />}
          />
        </Card.Content>
      </Card>

      {/* Refresh Button */}
      <Button
        mode="contained"
        onPress={onRefresh}
        style={styles.refreshButton}
        loading={refreshing}
      >
        Refresh Data
      </Button>
    </ScrollView>
  );
};

const getLogLevelColor = (level) => {
  switch (level?.toLowerCase()) {
    case 'error': return '#f44336';
    case 'warning': return '#ff9800';
    case 'info': return '#2196f3';
    case 'debug': return '#9e9e9e';
    default: return '#000000';
  }
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 16,
    textAlign: 'center',
  },
  card: {
    marginBottom: 16,
    elevation: 4,
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginVertical: 4,
  },
  statusChip: {
    paddingHorizontal: 8,
  },
  logsContainer: {
    maxHeight: 300,
    backgroundColor: '#f8f8f8',
    borderRadius: 8,
    padding: 8,
    marginTop: 8,
  },
  logEntry: {
    marginBottom: 8,
    padding: 8,
    backgroundColor: 'white',
    borderRadius: 4,
    borderLeftWidth: 3,
    borderLeftColor: '#6200ea',
  },
  logTimestamp: {
    fontSize: 12,
    color: '#666',
  },
  logLevel: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  logMessage: {
    fontSize: 14,
    marginTop: 2,
  },
  refreshButton: {
    marginVertical: 20,
    paddingVertical: 8,
  },
});

export default MonitoringScreen;
