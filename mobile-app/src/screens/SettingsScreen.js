import React, { useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Alert
} from 'react-native';
import {
  Card,
  Title,
  List,
  Button,
  Switch,
  Paragraph,
  Dialog,
  Portal,
  Text
} from 'react-native-paper';
import { useConfig } from '../services/ConfigService';

const SettingsScreen = () => {
  const { config, updateConfig, resetConfig, exportConfig, importConfig } = useConfig();
  const [showResetDialog, setShowResetDialog] = useState(false);
  const [notifications, setNotifications] = useState(config?.notifications?.enabled || false);
  const [darkMode, setDarkMode] = useState(config?.ui?.darkMode || false);
  const [autoConnect, setAutoConnect] = useState(config?.app?.autoConnect || true);

  const handleNotificationToggle = async (value) => {
    setNotifications(value);
    await updateConfig({
      ...config,
      notifications: {
        ...config.notifications,
        enabled: value
      }
    });
  };

  const handleDarkModeToggle = async (value) => {
    setDarkMode(value);
    await updateConfig({
      ...config,
      ui: {
        ...config.ui,
        darkMode: value
      }
    });
  };

  const handleAutoConnectToggle = async (value) => {
    setAutoConnect(value);
    await updateConfig({
      ...config,
      app: {
        ...config.app,
        autoConnect: value
      }
    });
  };

  const handleExportConfig = async () => {
    try {
      await exportConfig();
      Alert.alert('Success', 'Configuration exported successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to export configuration: ' + error.message);
    }
  };

  const handleImportConfig = async () => {
    try {
      await importConfig();
      Alert.alert('Success', 'Configuration imported successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to import configuration: ' + error.message);
    }
  };

  const handleResetConfig = async () => {
    try {
      await resetConfig();
      setShowResetDialog(false);
      Alert.alert('Success', 'Configuration reset to defaults');
    } catch (error) {
      Alert.alert('Error', 'Failed to reset configuration: ' + error.message);
    }
  };

  return (
    <ScrollView style={styles.container}>
      {/* App Settings */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>App Settings</Title>
          
          <View style={styles.settingRow}>
            <View style={styles.settingText}>
              <Paragraph>Dark Mode</Paragraph>
              <Text style={styles.settingDescription}>
                Enable dark theme for the app
              </Text>
            </View>
            <Switch
              value={darkMode}
              onValueChange={handleDarkModeToggle}
            />
          </View>

          <View style={styles.settingRow}>
            <View style={styles.settingText}>
              <Paragraph>Auto Connect</Paragraph>
              <Text style={styles.settingDescription}>
                Automatically connect to backend on app start
              </Text>
            </View>
            <Switch
              value={autoConnect}
              onValueChange={handleAutoConnectToggle}
            />
          </View>

          <View style={styles.settingRow}>
            <View style={styles.settingText}>
              <Paragraph>Push Notifications</Paragraph>
              <Text style={styles.settingDescription}>
                Receive notifications about robot status
              </Text>
            </View>
            <Switch
              value={notifications}
              onValueChange={handleNotificationToggle}
            />
          </View>
        </Card.Content>
      </Card>

      {/* Configuration Management */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Configuration Management</Title>
          
          <Button
            mode="outlined"
            onPress={handleExportConfig}
            style={styles.actionButton}
            icon="export"
          >
            Export Configuration
          </Button>

          <Button
            mode="outlined"
            onPress={handleImportConfig}
            style={styles.actionButton}
            icon="import"
          >
            Import Configuration
          </Button>

          <Button
            mode="outlined"
            onPress={() => setShowResetDialog(true)}
            style={[styles.actionButton, styles.dangerButton]}
            icon="restore"
          >
            Reset to Defaults
          </Button>
        </Card.Content>
      </Card>

      {/* About */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>About</Title>
          
          <List.Item
            title="Version"
            description="1.0.0"
            left={(props) => <List.Icon {...props} icon="information" />}
          />
          
          <List.Item
            title="Developer"
            description="Smart Robot Team"
            left={(props) => <List.Icon {...props} icon="account" />}
          />
          
          <List.Item
            title="License"
            description="MIT License"
            left={(props) => <List.Icon {...props} icon="license" />}
          />
        </Card.Content>
      </Card>

      {/* Support */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Support</Title>
          
          <Button
            mode="outlined"
            onPress={() => Alert.alert('Help', 'Help documentation will be available soon')}
            style={styles.actionButton}
            icon="help-circle"
          >
            Help & Documentation
          </Button>

          <Button
            mode="outlined"
            onPress={() => Alert.alert('Feedback', 'Please send feedback to: feedback@smartrobot.com')}
            style={styles.actionButton}
            icon="message"
          >
            Send Feedback
          </Button>

          <Button
            mode="outlined"
            onPress={() => Alert.alert('Bug Report', 'Please report bugs to: bugs@smartrobot.com')}
            style={styles.actionButton}
            icon="bug"
          >
            Report Bug
          </Button>
        </Card.Content>
      </Card>

      {/* Reset Confirmation Dialog */}
      <Portal>
        <Dialog visible={showResetDialog} onDismiss={() => setShowResetDialog(false)}>
          <Dialog.Title>Reset Configuration</Dialog.Title>
          <Dialog.Content>
            <Paragraph>
              Are you sure you want to reset all configuration to default values? 
              This action cannot be undone.
            </Paragraph>
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={() => setShowResetDialog(false)}>Cancel</Button>
            <Button onPress={handleResetConfig} mode="contained" buttonColor="#f44336">
              Reset
            </Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>
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
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  settingText: {
    flex: 1,
    marginRight: 16,
  },
  settingDescription: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  actionButton: {
    marginBottom: 12,
  },
  dangerButton: {
    borderColor: '#f44336',
  },
});

export default SettingsScreen;
