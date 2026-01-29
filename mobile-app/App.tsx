import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useAuth } from './hooks/useAuth';
import gpsService from './services/gpsService';

// Auth Screens
import LoginScreen from './screens/auth/LoginScreen';

// Dispatch Screens
import HomeScreen from './screens/dispatch/HomeScreen';
import DispatchDetailScreen from './screens/dispatch/DispatchDetailScreen';
import RouteDetailScreen from './screens/dispatch/RouteDetailScreen';
import CameraScreen from './screens/dispatch/CameraScreen';

// Types
import { RootStackParamList, DispatchStackParamList } from './types/navigation';

const Stack = createNativeStackNavigator<RootStackParamList>();
const DispatchStack = createNativeStackNavigator<DispatchStackParamList>();
const Tab = createBottomTabNavigator();

// Dispatch Stack Navigator
const DispatchStackNavigator = () => {
  return (
    <DispatchStack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: '#F2F2F7',
        },
        headerTintColor: '#007AFF',
        headerTitleStyle: {
          fontWeight: '600',
        },
      }}
    >
      <DispatchStack.Screen
        name="Home"
        component={HomeScreen}
        options={{ title: '오늘의 배차' }}
      />
      <DispatchStack.Screen
        name="DispatchDetail"
        component={DispatchDetailScreen}
        options={{ title: '배차 상세' }}
      />
      <DispatchStack.Screen
        name="RouteDetail"
        component={RouteDetailScreen}
        options={{ title: '경로 상세' }}
      />
      <DispatchStack.Screen
        name="Camera"
        component={CameraScreen}
        options={{
          headerShown: false,
          presentation: 'fullScreenModal',
        }}
      />
    </DispatchStack.Navigator>
  );
};

// Main Tab Navigator (Future: Add more tabs like Profile, Settings)
const MainTabNavigator = () => {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: '#8E8E93',
        tabBarStyle: {
          backgroundColor: '#F2F2F7',
          borderTopColor: '#C6C6C8',
        },
      }}
    >
      <Tab.Screen
        name="DispatchTab"
        component={DispatchStackNavigator}
        options={{
          title: '배차',
          tabBarIcon: ({ color, size }) => (
            // Icon component would go here (e.g., from react-native-vector-icons)
            <></>
          ),
        }}
      />
      {/* Future tabs: Profile, Settings, etc. */}
    </Tab.Navigator>
  );
};

const App = () => {
  const { isAuthenticated, isLoading, checkAuth } = useAuth();

  useEffect(() => {
    checkAuth();
  }, []);

  useEffect(() => {
    // GPS 추적 시작 (인증된 사용자)
    if (isAuthenticated) {
      const startGPS = async () => {
        const hasPermission = await gpsService.requestLocationPermission();
        if (hasPermission) {
          // 백그라운드 위치 추적 시작
          await gpsService.startBackgroundTracking();
          console.log('GPS tracking started');
        }
      };
      startGPS();
    } else {
      // 로그아웃 시 GPS 추적 중지
      gpsService.stopAllTracking();
    }

    return () => {
      // 앱 종료 시 GPS 추적 중지
      gpsService.stopAllTracking();
    };
  }, [isAuthenticated]);

  if (isLoading) {
    return null; // Or a loading screen
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isAuthenticated ? (
          <Stack.Screen name="Main" component={MainTabNavigator} />
        ) : (
          <Stack.Screen name="Login" component={LoginScreen} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default App;
