import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { Ionicons } from '@expo/vector-icons';
import DashboardScreen from '../screens/dashboard/DashboardScreen';
import DispatchListScreen from '../screens/dispatch/DispatchListScreen';
import DispatchDetailScreen from '../screens/dispatch/DispatchDetailScreen';
import MapScreen from '../screens/dispatch/MapScreen';
import VehicleInfoScreen from '../screens/vehicle/VehicleInfoScreen';
import SettingsScreen from '../screens/settings/SettingsScreen';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// 배차 스택
function DispatchStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen 
        name="DispatchList" 
        component={DispatchListScreen}
        options={{ title: '배차 목록' }}
      />
      <Stack.Screen 
        name="DispatchDetail" 
        component={DispatchDetailScreen}
        options={{ title: '배차 상세' }}
      />
      <Stack.Screen 
        name="Map" 
        component={MapScreen}
        options={{ title: '경로 안내' }}
      />
    </Stack.Navigator>
  );
}

export default function MainNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: any;

          if (route.name === 'Dashboard') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Dispatch') {
            iconName = focused ? 'list' : 'list-outline';
          } else if (route.name === 'Vehicle') {
            iconName = focused ? 'car' : 'car-outline';
          } else if (route.name === 'Settings') {
            iconName = focused ? 'settings' : 'settings-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#3B82F6',
        tabBarInactiveTintColor: '#9CA3AF',
        headerShown: false,
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{ tabBarLabel: '홈' }}
      />
      <Tab.Screen 
        name="Dispatch" 
        component={DispatchStack}
        options={{ tabBarLabel: '배차' }}
      />
      <Tab.Screen 
        name="Vehicle" 
        component={VehicleInfoScreen}
        options={{ tabBarLabel: '차량' }}
      />
      <Tab.Screen 
        name="Settings" 
        component={SettingsScreen}
        options={{ tabBarLabel: '설정' }}
      />
    </Tab.Navigator>
  );
}
