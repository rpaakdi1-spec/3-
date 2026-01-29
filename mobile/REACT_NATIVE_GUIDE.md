# React Native 모바일 앱 구현 가이드

## 📱 프로젝트 개요

Cold Chain Dispatch 시스템의 모바일 앱 (React Native + Expo)

### 주요 기능
- ✅ 사용자 인증 (로그인/로그아웃)
- ✅ 배차 관리 (조회, 상세, 상태 변경)
- ✅ 주문 관리 (조회, 상세, 서명)
- ✅ 실시간 GPS 추적
- ✅ 온도 모니터링
- ✅ FCM 푸시 알림
- ✅ QR 코드 스캔
- ✅ 카메라 (배송 증빙 사진)
- ✅ 오프라인 모드 지원

---

## 🚀 시작하기

### 사전 요구사항
- Node.js 18+
- Expo CLI
- iOS Simulator (Mac) 또는 Android Emulator
- 실제 디바이스 (Expo Go 앱 설치)

### 설치 및 실행

```bash
cd /home/user/webapp/mobile

# 의존성 설치
npm install

# Expo 개발 서버 시작
npm start

# iOS 시뮬레이터 실행
npm run ios

# Android 에뮬레이터 실행
npm run android

# 웹 브라우저 실행
npm run web
```

---

## 📂 프로젝트 구조

```
mobile/
├── app.json                  # Expo 설정
├── package.json             # npm 의존성
├── App.tsx                  # 메인 앱 컴포넌트
├── src/
│   ├── navigation/          # 네비게이션
│   │   ├── AppNavigator.tsx
│   │   ├── AuthNavigator.tsx
│   │   └── MainTabNavigator.tsx
│   ├── screens/             # 화면 컴포넌트
│   │   ├── auth/
│   │   │   ├── LoginScreen.tsx
│   │   │   └── RegisterScreen.tsx
│   │   ├── dispatches/
│   │   │   ├── DispatchListScreen.tsx
│   │   │   └── DispatchDetailScreen.tsx
│   │   ├── orders/
│   │   │   ├── OrderListScreen.tsx
│   │   │   └── OrderDetailScreen.tsx
│   │   ├── tracking/
│   │   │   └── MapTrackingScreen.tsx
│   │   └── profile/
│   │       └── ProfileScreen.tsx
│   ├── components/          # 재사용 컴포넌트
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   └── Loading.tsx
│   │   └── dispatch/
│   │       ├── DispatchCard.tsx
│   │       └── DispatchStatus.tsx
│   ├── services/            # API 서비스
│   │   ├── api.ts
│   │   ├── authService.ts
│   │   ├── dispatchService.ts
│   │   ├── orderService.ts
│   │   └── notificationService.ts
│   ├── hooks/               # Custom Hooks
│   │   ├── useAuth.ts
│   │   ├── useNotifications.ts
│   │   └── useLocation.ts
│   ├── store/               # 상태 관리 (Context API 또는 Zustand)
│   │   ├── authStore.ts
│   │   ├── dispatchStore.ts
│   │   └── notificationStore.ts
│   ├── utils/               # 유틸리티 함수
│   │   ├── storage.ts
│   │   ├── formatter.ts
│   │   └── validation.ts
│   ├── types/               # TypeScript 타입
│   │   ├── auth.ts
│   │   ├── dispatch.ts
│   │   └── order.ts
│   └── constants/           # 상수
│       ├── colors.ts
│       └── api.ts
└── assets/                  # 이미지, 폰트 등
    ├── icon.png
    ├── splash.png
    └── adaptive-icon.png
```

---

## 🔐 인증 (Authentication)

### 로그인 플로우

```typescript
// src/services/authService.ts
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'https://8000-i16kcdhvw5ng6rusdg7lj-ad490db5.sandbox.novita.ai/api/v1';

export const login = async (username: string, password: string) => {
  const response = await axios.post(`${API_URL}/auth/login`, {
    username,
    password
  });
  
  const { access_token, user } = response.data;
  
  // 토큰 저장
  await AsyncStorage.setItem('access_token', access_token);
  await AsyncStorage.setItem('user', JSON.stringify(user));
  
  return { access_token, user };
};

export const logout = async () => {
  await AsyncStorage.removeItem('access_token');
  await AsyncStorage.removeItem('user');
};

export const getStoredToken = async () => {
  return await AsyncStorage.getItem('access_token');
};
```

---

## 🔔 FCM 푸시 알림 설정

### 1. Firebase 프로젝트 설정
1. [Firebase Console](https://console.firebase.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. iOS/Android 앱 등록
4. `google-services.json` (Android), `GoogleService-Info.plist` (iOS) 다운로드

### 2. Expo 알림 권한 요청

```typescript
// src/services/notificationService.ts
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import Constants from 'expo-constants';

// 알림 권한 요청 및 FCM 토큰 가져오기
export async function registerForPushNotificationsAsync() {
  let token;

  if (Device.isDevice) {
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    
    if (finalStatus !== 'granted') {
      alert('Failed to get push token for push notification!');
      return;
    }
    
    token = (await Notifications.getExpoPushTokenAsync({
      projectId: Constants.expoConfig?.extra?.eas?.projectId
    })).data;
  } else {
    alert('Must use physical device for Push Notifications');
  }

  return token;
}

// 토큰을 서버에 등록
export async function registerTokenWithBackend(token: string) {
  const accessToken = await AsyncStorage.getItem('access_token');
  
  await axios.post(`${API_URL}/notifications/register-token`, {
    token,
    device_type: Platform.OS, // 'ios' or 'android'
    app_version: Constants.expoConfig?.version
  }, {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
}
```

### 3. 알림 수신 핸들러

```typescript
// App.tsx
import React, { useEffect, useRef } from 'react';
import * as Notifications from 'expo-notifications';

// 알림 핸들러 설정
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

function App() {
  const notificationListener = useRef<any>();
  const responseListener = useRef<any>();

  useEffect(() => {
    // 알림 수신 리스너
    notificationListener.current = Notifications.addNotificationReceivedListener(notification => {
      console.log('Notification received:', notification);
    });

    // 알림 클릭 리스너
    responseListener.current = Notifications.addNotificationResponseReceivedListener(response => {
      console.log('Notification clicked:', response);
      
      // 알림 데이터 기반 화면 이동
      const data = response.notification.request.content.data;
      
      if (data.screen === 'DispatchDetail') {
        // 배차 상세 화면으로 이동
        navigation.navigate('DispatchDetail', { id: data.dispatch_id });
      }
    });

    return () => {
      Notifications.removeNotificationSubscription(notificationListener.current);
      Notifications.removeNotificationSubscription(responseListener.current);
    };
  }, []);

  // ...
}
```

---

## 📍 위치 추적 (GPS)

### 위치 권한 및 실시간 추적

```typescript
// src/hooks/useLocation.ts
import { useState, useEffect } from 'react';
import * as Location from 'expo-location';

export function useLocation() {
  const [location, setLocation] = useState<Location.LocationObject | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      // 위치 권한 요청
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        setErrorMsg('Permission to access location was denied');
        return;
      }

      // 현재 위치 가져오기
      let location = await Location.getCurrentPositionAsync({});
      setLocation(location);

      // 실시간 위치 추적 (배차 진행 중)
      const subscription = await Location.watchPositionAsync(
        {
          accuracy: Location.Accuracy.High,
          timeInterval: 5000, // 5초마다
          distanceInterval: 10, // 10m 이동 시
        },
        (newLocation) => {
          setLocation(newLocation);
          // 서버에 위치 전송
          sendLocationToServer(newLocation);
        }
      );

      return () => subscription.remove();
    })();
  }, []);

  return { location, errorMsg };
}

async function sendLocationToServer(location: Location.LocationObject) {
  const accessToken = await AsyncStorage.getItem('access_token');
  
  await axios.post(`${API_URL}/tracking/location`, {
    latitude: location.coords.latitude,
    longitude: location.coords.longitude,
    accuracy: location.coords.accuracy,
    speed: location.coords.speed,
    timestamp: new Date(location.timestamp).toISOString()
  }, {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
}
```

---

## 📷 카메라 (배송 증빙 사진)

```typescript
// src/screens/orders/OrderDetailScreen.tsx
import { Camera } from 'expo-camera';
import * as ImagePicker from 'expo-image-picker';

async function takePicture() {
  // 카메라 권한 요청
  const { status } = await Camera.requestCameraPermissionsAsync();
  
  if (status !== 'granted') {
    alert('Camera permission denied');
    return;
  }

  // 사진 촬영
  const result = await ImagePicker.launchCameraAsync({
    mediaTypes: ImagePicker.MediaTypeOptions.Images,
    allowsEditing: true,
    quality: 0.7,
  });

  if (!result.canceled) {
    // 서버에 업로드
    await uploadDeliveryProof(result.assets[0].uri);
  }
}

async function uploadDeliveryProof(imageUri: string) {
  const accessToken = await AsyncStorage.getItem('access_token');
  
  const formData = new FormData();
  formData.append('file', {
    uri: imageUri,
    type: 'image/jpeg',
    name: `delivery_${Date.now()}.jpg`,
  } as any);

  await axios.post(`${API_URL}/orders/${orderId}/upload-proof`, formData, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'multipart/form-data',
    },
  });
}
```

---

## 🗺️ 지도 (React Native Maps)

```typescript
// src/screens/tracking/MapTrackingScreen.tsx
import MapView, { Marker, Polyline } from 'react-native-maps';

function MapTrackingScreen() {
  const { location } = useLocation();

  return (
    <MapView
      style={{ flex: 1 }}
      region={{
        latitude: location?.coords.latitude || 37.5665,
        longitude: location?.coords.longitude || 126.9780,
        latitudeDelta: 0.05,
        longitudeDelta: 0.05,
      }}
    >
      {/* 현재 위치 마커 */}
      {location && (
        <Marker
          coordinate={{
            latitude: location.coords.latitude,
            longitude: location.coords.longitude,
          }}
          title="현재 위치"
        />
      )}
      
      {/* 배송 경로 */}
      <Polyline
        coordinates={route}
        strokeColor="#007AFF"
        strokeWidth={3}
      />
    </MapView>
  );
}
```

---

## 📦 오프라인 모드 지원

```typescript
// src/utils/storage.ts
import AsyncStorage from '@react-native-async-storage/async-storage';

// 오프라인 데이터 저장
export async function cacheData(key: string, data: any) {
  await AsyncStorage.setItem(key, JSON.stringify(data));
}

// 오프라인 데이터 조회
export async function getCachedData(key: string) {
  const data = await AsyncStorage.getItem(key);
  return data ? JSON.parse(data) : null;
}

// 네트워크 상태 확인
import NetInfo from '@react-native-community/netinfo';

export function useNetworkStatus() {
  const [isConnected, setIsConnected] = useState(true);

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener(state => {
      setIsConnected(state.isConnected ?? false);
    });

    return () => unsubscribe();
  }, []);

  return isConnected;
}
```

---

## 🧪 테스트

### Jest 테스트 설정

```bash
npm install --save-dev jest @testing-library/react-native
```

```json
// package.json
{
  "scripts": {
    "test": "jest"
  },
  "jest": {
    "preset": "react-native",
    "transformIgnorePatterns": [
      "node_modules/(?!((jest-)?react-native|@react-native(-community)?)|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|@unimodules/.*|unimodules|sentry-expo|native-base|react-native-svg)"
    ]
  }
}
```

---

## 📲 빌드 및 배포

### Expo Application Services (EAS) 사용

```bash
# EAS CLI 설치
npm install -g eas-cli

# EAS 로그인
eas login

# 빌드 설정
eas build:configure

# Android APK 빌드
eas build --platform android --profile preview

# iOS IPA 빌드
eas build --platform ios --profile preview

# App Store/Google Play 배포
eas submit --platform ios
eas submit --platform android
```

---

## 🔧 환경 변수 설정

```typescript
// app.config.js
export default {
  expo: {
    extra: {
      apiUrl: process.env.API_URL || 'https://api.coldchain.com',
      fcmServerKey: process.env.FCM_SERVER_KEY,
      eas: {
        projectId: "your-project-id"
      }
    }
  }
};

// 사용 예시
import Constants from 'expo-constants';

const API_URL = Constants.expoConfig?.extra?.apiUrl;
```

---

## 📝 API 엔드포인트 정리

### 인증
- `POST /api/v1/auth/login` - 로그인
- `POST /api/v1/auth/logout` - 로그아웃
- `POST /api/v1/auth/refresh` - 토큰 갱신

### 배차
- `GET /api/v1/dispatches` - 배차 목록
- `GET /api/v1/dispatches/{id}` - 배차 상세
- `PATCH /api/v1/dispatches/{id}/status` - 상태 변경

### 주문
- `GET /api/v1/orders` - 주문 목록
- `GET /api/v1/orders/{id}` - 주문 상세
- `POST /api/v1/orders/{id}/complete` - 주문 완료

### 푸시 알림
- `POST /api/v1/notifications/register-token` - FCM 토큰 등록
- `DELETE /api/v1/notifications/unregister-token/{token}` - 토큰 비활성화
- `GET /api/v1/notifications/notification-logs` - 알림 이력

### 실시간 추적
- `POST /api/v1/tracking/location` - GPS 위치 전송
- `GET /api/v1/realtime/dashboard` - 실시간 대시보드

---

## ⚠️ 주의사항

1. **실제 디바이스 테스트 필수**: FCM, GPS, 카메라는 실제 디바이스에서만 완전히 작동
2. **백그라운드 위치 추적**: iOS는 별도 설정 필요 (`UIBackgroundModes`)
3. **배터리 최적화**: 실시간 위치 추적은 배터리 소모가 큼
4. **네트워크 오류 처리**: 오프라인 모드 시 로컬 캐시 사용
5. **보안**: API 키, 토큰은 절대 하드코딩 금지

---

## 📚 참고 자료

- [Expo Documentation](https://docs.expo.dev/)
- [React Navigation](https://reactnavigation.org/)
- [Expo Notifications](https://docs.expo.dev/versions/latest/sdk/notifications/)
- [Expo Location](https://docs.expo.dev/versions/latest/sdk/location/)
- [React Native Maps](https://github.com/react-native-maps/react-native-maps)

---

**작성일**: 2026-01-28  
**버전**: 1.0.0  
**작성자**: GenSpark AI Development Team
