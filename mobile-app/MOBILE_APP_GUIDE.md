# 🚚 기사용 모바일 앱 가이드

**Cold Chain Dispatch System - Driver Mobile App**

## 📱 개요

기사용 모바일 앱은 React Native로 개발된 냉장/냉동 물류 배차 관리 시스템의 모바일 클라이언트입니다. 기사들이 배차 조회, 경로 확인, 상/하차 체크, 사진 업로드, 실시간 GPS 위치 전송 등을 수행할 수 있습니다.

---

## 🎯 주요 기능

### 1. 인증 및 로그인
- JWT 기반 인증
- 자동 로그인 (토큰 저장)
- 로그아웃 및 세션 관리

### 2. 배차 관리
- **오늘의 배차 목록** 조회
- **배차 상세 정보** 확인
  - 차량 정보
  - 배차 번호
  - 총 팔레트/중량
  - 경로 목록

### 3. 경로 관리
- **경로 상세 정보**
  - 상차지/하차지 정보
  - 예상 작업 시간
  - 현재 팔레트/중량
- **작업 상태 업데이트**
  - 출발 → 도착 → 작업 중 → 완료
  - 작업 시작/종료 시간 기록

### 4. 카메라 기능
- **상차/하차 사진 촬영**
- 미리보기 및 재촬영
- 서버 업로드

### 5. GPS 위치 추적
- **실시간 위치 전송** (30초 간격)
- **백그라운드 위치 추적**
- 위치 권한 관리
- 100m 이동 시 자동 업데이트

### 6. 푸시 알림
- **배차 할당 알림**
- 경로 업데이트 알림
- FCM (Firebase Cloud Messaging) 기반

### 7. 오프라인 모드
- 오프라인 작업 큐
- 온라인 복귀 시 자동 동기화
- 배차 정보 로컬 캐시

---

## 🛠 기술 스택

| Category | Technology |
|----------|-----------|
| **Framework** | React Native 0.73.0 |
| **Language** | TypeScript 5.0.4 |
| **Navigation** | React Navigation 6.x |
| **State Management** | React Hooks (useState, useEffect, useContext) |
| **HTTP Client** | Axios 1.6.5 |
| **Storage** | AsyncStorage |
| **GPS** | React Native Geolocation, Background Geolocation |
| **Camera** | React Native Vision Camera 3.6.10 |
| **Push Notifications** | Firebase Cloud Messaging (FCM) |
| **Offline Sync** | NetInfo + AsyncStorage |

---

## 📂 프로젝트 구조

```
mobile-app/
├── App.tsx                           # 앱 진입점 (네비게이션)
├── package.json                      # 의존성
├── tsconfig.json                     # TypeScript 설정
│
├── src/
│   ├── components/                   # 공통 컴포넌트
│   │   └── (미래 확장)
│   │
│   ├── screens/                      # 화면
│   │   ├── auth/
│   │   │   └── LoginScreen.tsx      # 로그인 화면
│   │   └── dispatch/
│   │       ├── HomeScreen.tsx        # 오늘의 배차
│   │       ├── DispatchDetailScreen.tsx  # 배차 상세
│   │       ├── RouteDetailScreen.tsx     # 경로 상세
│   │       └── CameraScreen.tsx          # 카메라
│   │
│   ├── services/                     # API 및 서비스
│   │   ├── api.ts                   # Axios API 클라이언트
│   │   ├── gpsService.ts            # GPS 위치 추적
│   │   ├── notificationService.ts   # 푸시 알림
│   │   └── offlineService.ts        # 오프라인 동기화
│   │
│   ├── hooks/                        # Custom Hooks
│   │   └── useAuth.tsx              # 인증 Hook
│   │
│   ├── types/                        # TypeScript 타입
│   │   └── navigation.ts            # 네비게이션 타입
│   │
│   └── assets/                       # 이미지, 아이콘 (미래 확장)
│
├── android/                          # Android 네이티브 코드
└── ios/                              # iOS 네이티브 코드
```

---

## 🚀 설치 및 실행

### 1. 사전 요구사항

- **Node.js** 18+
- **React Native CLI**
- **Android Studio** (Android 빌드)
- **Xcode** (iOS 빌드, macOS만)

### 2. 의존성 설치

```bash
cd mobile-app
npm install

# iOS Pod 설치 (macOS만)
cd ios
pod install
cd ..
```

### 3. 환경 변수 설정

`src/services/api.ts`에서 백엔드 API URL 설정:

```typescript
const API_BASE_URL = 'http://localhost:8000/api/v1';  // 개발 환경
// const API_BASE_URL = 'https://api.yourcompany.com/api/v1';  // 프로덕션
```

### 4. Android 실행

```bash
npm run android
```

### 5. iOS 실행 (macOS만)

```bash
npm run ios
```

---

## 📦 주요 의존성

### Core

```json
{
  "react": "18.2.0",
  "react-native": "0.73.0",
  "typescript": "5.0.4"
}
```

### Navigation

```json
{
  "@react-navigation/native": "^6.1.9",
  "@react-navigation/native-stack": "^6.9.17",
  "@react-navigation/bottom-tabs": "^6.5.11",
  "react-native-screens": "^3.29.0",
  "react-native-safe-area-context": "^4.8.2"
}
```

### API & Storage

```json
{
  "axios": "^1.6.5",
  "@react-native-async-storage/async-storage": "^1.21.0"
}
```

### GPS & Location

```json
{
  "@react-native-community/geolocation": "^3.1.0",
  "react-native-background-geolocation": "^4.14.0"
}
```

### Camera

```json
{
  "react-native-vision-camera": "^3.6.10"
}
```

### Push Notifications

```json
{
  "@react-native-firebase/app": "^19.0.0",
  "@react-native-firebase/messaging": "^19.0.0"
}
```

### Network & Offline

```json
{
  "@react-native-community/netinfo": "^11.2.0"
}
```

---

## 🔐 인증 시스템

### JWT 토큰 관리

```typescript
// 로그인
const response = await api.login(username, password);
const { access_token, user } = response.data;

// 토큰 저장
await AsyncStorage.setItem('access_token', access_token);
await AsyncStorage.setItem('user', JSON.stringify(user));

// 토큰 자동 포함 (Axios Interceptor)
api.interceptors.request.use(config => {
  const token = await AsyncStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 401 Unauthorized 처리
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // 자동 로그아웃
      await AsyncStorage.clear();
      // 로그인 화면으로 이동
    }
    return Promise.reject(error);
  }
);
```

---

## 📍 GPS 위치 추적

### 포그라운드 추적

```typescript
import gpsService from './services/gpsService';

// 위치 추적 시작 (30초 간격)
await gpsService.startForegroundTracking(30000);

// 현재 위치 가져오기
const position = await gpsService.getCurrentPosition();
console.log(position); // { latitude: 37.5665, longitude: 126.9780 }

// 위치 추적 중지
gpsService.stopForegroundTracking();
```

### 백그라운드 추적

```typescript
// 백그라운드 위치 추적 시작
await gpsService.startBackgroundTracking();

// 추적 상태 확인
const isTracking = await gpsService.isTracking(); // true/false

// 백그라운드 위치 추적 중지
await gpsService.stopBackgroundTracking();
```

### 위치 전송

```typescript
// 서버로 위치 전송
await api.sendGPSLocation(latitude, longitude);
```

---

## 📸 카메라 기능

### 사진 촬영 및 업로드

```typescript
// 카메라 화면으로 이동
navigation.navigate('Camera', {
  dispatchId: 1,
  routeId: 5,
  photoType: 'pickup', // 'pickup' | 'delivery'
});

// 사진 업로드
const formData = new FormData();
formData.append('file', {
  uri: capturedPhoto,
  type: 'image/jpeg',
  name: `pickup_${Date.now()}.jpg`,
});
formData.append('dispatch_id', '1');
formData.append('route_id', '5');
formData.append('photo_type', 'pickup');

await api.uploadPhoto(formData);
```

---

## 🔔 푸시 알림

### FCM 초기화

```typescript
import notificationService from './services/notificationService';

// App.tsx에서 초기화
useEffect(() => {
  notificationService.initialize();
}, []);

// FCM 토큰 가져오기
const token = await notificationService.getFCMToken();
console.log('FCM Token:', token);
```

### 알림 수신

```typescript
// 포그라운드 알림
messaging().onMessage(async (remoteMessage) => {
  Alert.alert(
    remoteMessage.notification?.title,
    remoteMessage.notification?.body
  );
});

// 백그라운드 알림
messaging().setBackgroundMessageHandler(async (remoteMessage) => {
  console.log('Background message:', remoteMessage);
});

// 알림 탭하여 앱 열기
messaging().onNotificationOpenedApp((remoteMessage) => {
  const dispatchId = remoteMessage.data?.dispatch_id;
  navigation.navigate('DispatchDetail', { dispatchId });
});
```

---

## 📴 오프라인 모드

### 네트워크 상태 확인

```typescript
import offlineService from './services/offlineService';

// 초기화
offlineService.initialize();

// 온라인 상태 확인
const isOnline = await offlineService.checkOnlineStatus();

// 오프라인 상태 확인
if (offlineService.isOffline()) {
  Alert.alert('오프라인', '인터넷 연결을 확인해주세요.');
}
```

### 오프라인 액션 큐

```typescript
// 오프라인 시 액션 저장
await offlineService.addToOfflineQueue({
  type: 'update_route_status',
  data: { dispatchId: 1, routeId: 5, status: 'completed' },
});

// 온라인 복귀 시 자동 동기화
offlineService.syncOfflineData();

// 큐 조회
const queue = await offlineService.getOfflineQueue();
console.log('Offline queue:', queue.length);
```

### 캐시 관리

```typescript
// 배차 목록 캐시 저장
await offlineService.cacheDispatches(dispatches);

// 캐시된 배차 목록 가져오기
const cachedDispatches = await offlineService.getCachedDispatches();

// 캐시 초기화
await offlineService.clearCache();
```

---

## 🎨 UI/UX 디자인

### 디자인 시스템

- **Primary Color**: `#007AFF` (iOS Blue)
- **Success Color**: `#34C759` (iOS Green)
- **Warning Color**: `#FF9500` (iOS Orange)
- **Danger Color**: `#FF3B30` (iOS Red)
- **Background**: `#F2F2F7` (iOS Light Gray)
- **Font**: San Francisco (iOS), Roboto (Android)

### 화면 흐름

```
LoginScreen (로그인)
    ↓
HomeScreen (오늘의 배차)
    ↓
DispatchDetailScreen (배차 상세)
    ↓
RouteDetailScreen (경로 상세)
    ↓
CameraScreen (카메라 - 상/하차 사진)
```

---

## 🧪 테스트

### 로컬 개발 환경

1. **백엔드 서버 실행**
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

2. **모바일 앱 실행**
   ```bash
   cd mobile-app
   npm run android  # 또는 npm run ios
   ```

3. **테스트 계정 로그인**
   - Username: `test_driver`
   - Password: `test123`

### 테스트 시나리오

1. **로그인** → 배차 목록 조회
2. **배차 선택** → 배차 상세 확인
3. **경로 선택** → 경로 상세 확인
4. **작업 시작** → 상태 업데이트
5. **사진 촬영** → 업로드
6. **작업 완료** → 다음 경로

---

## 📱 빌드 및 배포

### Android APK 빌드

```bash
cd android
./gradlew assembleRelease

# APK 위치
# android/app/build/outputs/apk/release/app-release.apk
```

### iOS IPA 빌드 (macOS)

```bash
cd ios
xcodebuild archive -workspace ColdChainDriver.xcworkspace \
  -scheme ColdChainDriver -archivePath build/ColdChainDriver.xcarchive

xcodebuild -exportArchive -archivePath build/ColdChainDriver.xcarchive \
  -exportPath build -exportOptionsPlist ExportOptions.plist
```

### 배포

- **Android**: Google Play Store
- **iOS**: Apple App Store

---

## 🐛 디버깅

### 로그 확인

```bash
# Android
adb logcat | grep ReactNative

# iOS
react-native log-ios
```

### 일반적인 문제

1. **GPS 위치 가져오기 실패**
   - 위치 권한 확인
   - GPS 활성화 확인

2. **카메라 접근 실패**
   - 카메라 권한 확인

3. **푸시 알림 수신 실패**
   - FCM 설정 확인
   - `google-services.json` (Android) / `GoogleService-Info.plist` (iOS) 확인

4. **네트워크 요청 실패**
   - API URL 확인
   - 네트워크 연결 확인
   - CORS 설정 확인 (백엔드)

---

## 📖 API 엔드포인트

### 인증

- `POST /api/v1/auth/login` - 로그인
- `GET /api/v1/auth/me` - 현재 사용자 정보

### 배차

- `GET /api/v1/dispatches/today` - 오늘의 배차 목록
- `GET /api/v1/dispatches/{id}` - 배차 상세

### 경로

- `PUT /api/v1/dispatches/{dispatch_id}/routes/{route_id}/status` - 경로 상태 업데이트

### GPS

- `POST /api/v1/vehicles/gps` - GPS 위치 전송

### 사진

- `POST /api/v1/dispatches/upload-photo` - 사진 업로드

---

## 🔮 향후 개발 계획

### Phase 1 (완료)
- ✅ 로그인 및 인증
- ✅ 배차 조회
- ✅ 경로 상세
- ✅ 카메라 기능
- ✅ GPS 위치 추적
- ✅ 푸시 알림
- ✅ 오프라인 모드

### Phase 2 (계획)
- 🔄 지도 기반 경로 안내 (Naver Map / Google Maps)
- 🔄 실시간 교통 정보
- 🔄 음성 안내
- 🔄 QR 코드 스캔
- 🔄 전자 서명
- 🔄 일일 업무 리포트

### Phase 3 (계획)
- 🔄 다국어 지원
- 🔄 다크 모드
- 🔄 성능 최적화
- 🔄 E2E 테스트
- 🔄 CI/CD 자동화

---

## 📄 라이센스

Proprietary - Cold Chain Dispatch System

---

## 👥 개발팀

- **Backend**: FastAPI + SQLAlchemy
- **Frontend**: React + TypeScript
- **Mobile**: React Native + TypeScript
- **DevOps**: Docker + GitHub Actions

---

## 📞 문의

문제 발생 시 GitHub Issues 또는 개발팀에 문의하세요.

**작성일**: 2026-01-27  
**버전**: 1.0.0  
**작성자**: GenSpark AI Developer
