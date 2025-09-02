import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Provider as PaperProvider } from 'react-native-paper';
import { StatusBar } from 'expo-status-bar';

// Screens
import HomeScreen from './src/screens/HomeScreen';
import ConfigScreen from './src/screens/ConfigScreen';
import MonitoringScreen from './src/screens/MonitoringScreen';
import SettingsScreen from './src/screens/SettingsScreen';

// Services
import { ConfigProvider } from './src/services/ConfigService';
import { BackendProvider } from './src/services/BackendService';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <PaperProvider>
      <ConfigProvider>
        <BackendProvider>
          <NavigationContainer>
            <StatusBar style="auto" />
            <Tab.Navigator
              screenOptions={{
                tabBarActiveTintColor: '#6200ea',
                tabBarInactiveTintColor: 'gray',
                headerStyle: {
                  backgroundColor: '#6200ea',
                },
                headerTintColor: '#fff',
                headerTitleStyle: {
                  fontWeight: 'bold',
                },
              }}
            >
              <Tab.Screen
                name="Home"
                component={HomeScreen}
                options={{
                  tabBarIcon: ({ color, size }) => (
                    <Ionicons name="home" size={size} color={color} />
                  ),
                  title: 'Smart Robot'
                }}
              />
              <Tab.Screen
                name="Monitor"
                component={MonitoringScreen}
                options={{
                  tabBarIcon: ({ color, size }) => (
                    <Ionicons name="analytics" size={size} color={color} />
                  ),
                  title: 'Monitoring'
                }}
              />
              <Tab.Screen
                name="Config"
                component={ConfigScreen}
                options={{
                  tabBarIcon: ({ color, size }) => (
                    <Ionicons name="settings" size={size} color={color} />
                  ),
                  title: 'Configuration'
                }}
              />
              <Tab.Screen
                name="Settings"
                component={SettingsScreen}
                options={{
                  tabBarIcon: ({ color, size }) => (
                    <Ionicons name="cog" size={size} color={color} />
                  ),
                  title: 'Settings'
                }}
              />
            </Tab.Navigator>
          </NavigationContainer>
        </BackendProvider>
      </ConfigProvider>
    </PaperProvider>
  );
}
