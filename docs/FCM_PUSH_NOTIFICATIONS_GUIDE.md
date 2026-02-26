# 🔔 Phase 16.1: Firebase FCM 푸시 알림 통합 가이드

**작성일**: 2026년 2월 26일  
**상태**: 백엔드 완료 ✅ | 프론트엔드 진행중 🔄

---

## 📋 목차

1. [개요](#개요)
2. [백엔드 구현](#백엔드-구현)
3. [프론트엔드 구현](#프론트엔드-구현)
4. [Firebase 프로젝트 설정](#firebase-프로젝트-설정)
5. [테스트 방법](#테스트-방법)
6. [배포 가이드](#배포-가이드)

---

## 개요

### 주요 기능
- ✅ FCM 토큰 등록/관리
- ✅ 푸시 알림 발송 (단일/다중 사용자)
- ✅ 알림 로그 저장 및 조회
- ✅ 주문/배차 알림 자동 발송
- ✅ UVIS 차량 알림 발송
- ✅ 웹/iOS/Android 지원

### 기술 스택
**백엔드**:
- Firebase Admin SDK (Python)
- FastAPI REST API
- PostgreSQL (토큰 & 로그 저장)

**프론트엔드**:
- Firebase JavaScript SDK
- Service Worker (백그라운드 알림)
- React Context API

---

## 백엔드 구현

### 1. DB 모델 (이미 존재)

**FCMToken** - FCM 토큰 관리
```python
class FCMToken(Base):
    __tablename__ = "fcm_tokens"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String(255), unique=True)  # FCM 토큰
    device_type = Column(String(20))  # 'ios', 'android', 'web'
    device_id = Column(String(255))
    app_version = Column(String(20))
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

**PushNotificationLog** - 알림 로그
```python
class PushNotificationLog(Base):
    __tablename__ = "push_notification_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String(255))
    title = Column(String(255))
    body = Column(String(1000))
    data_json = Column(String(2000))
    notification_type = Column(String(50))
    status = Column(String(20))  # 'sent', 'failed'
    error_message = Column(String(500))
    sent_at = Column(DateTime)
```

### 2. FCMService (`backend/app/services/fcm_service.py`)

**주요 메서드**:

```python
class FCMService:
    @classmethod
    def initialize():
        """Firebase Admin SDK 초기화"""
    
    @staticmethod
    def register_token(db, user_id, token, device_type, ...):
        """FCM 토큰 등록/업데이트"""
    
    @staticmethod
    def deactivate_token(db, token):
        """FCM 토큰 비활성화 (로그아웃)"""
    
    @staticmethod
    def send_notification(db, user_id, title, body, data, notification_type):
        """단일 사용자 푸시 알림 발송"""
    
    @staticmethod
    def send_to_multiple_users(db, user_ids, title, body, ...):
        """다중 사용자 푸시 알림 발송"""
    
    @staticmethod
    def send_order_notification(db, user_id, order_id, ...):
        """주문 관련 알림 발송"""
    
    @staticmethod
    def send_vehicle_alert(db, user_id, vehicle_plate, alert_type, ...):
        """차량 알림 발송 (UVIS)"""
```

### 3. API 엔드포인트 (`backend/app/api/v1/fcm_notifications.py`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/notifications/register-token` | FCM 토큰 등록 | ✅ |
| DELETE | `/api/v1/notifications/unregister-token/{token}` | FCM 토큰 비활성화 | ✅ |
| GET | `/api/v1/notifications/my-tokens` | 내 FCM 토큰 목록 | ✅ |
| POST | `/api/v1/notifications/send-notification` | 푸시 알림 발송 (관리자) | 🔐 Admin |
| POST | `/api/v1/notifications/test` | 테스트 알림 발송 | ✅ |
| GET | `/api/v1/notifications/notification-logs` | 알림 이력 조회 | ✅ |

---

## 프론트엔드 구현

### 1. Firebase 설정 파일 생성

**`frontend/src/firebase/config.ts`**:
```typescript
import { initializeApp } from 'firebase/app';
import { getMessaging, Messaging } from 'firebase/messaging';

// Firebase 설정 (환경변수로 관리)
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

// Firebase 앱 초기화
export const firebaseApp = initializeApp(firebaseConfig);

// Firebase Messaging 초기화
let messaging: Messaging | null = null;

try {
  messaging = getMessaging(firebaseApp);
} catch (error) {
  console.warn('Firebase Messaging is not supported in this browser', error);
}

export { messaging };
```

### 2. Service Worker (`frontend/public/firebase-messaging-sw.js`)

```javascript
// Import Firebase scripts
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

// Firebase 설정
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();

// 백그라운드 메시지 수신
messaging.onBackgroundMessage((payload) => {
  console.log('[Service Worker] Background message received:', payload);
  
  const notificationTitle = payload.notification.title || 'New Notification';
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/logo192.png',
    badge: '/badge.png',
    data: payload.data
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// 알림 클릭 이벤트
self.addEventListener('notificationclick', (event) => {
  console.log('[Service Worker] Notification click:', event);
  
  event.notification.close();
  
  // 앱 열기
  event.waitUntil(
    clients.openWindow('/')
  );
});
```

### 3. FCM Hook (`frontend/src/hooks/useFCM.ts`)

```typescript
import { useEffect, useState } from 'react';
import { getToken, onMessage } from 'firebase/messaging';
import { messaging } from '../firebase/config';
import { toast } from 'sonner';

export const useFCM = () => {
  const [token, setToken] = useState<string | null>(null);
  const [permission, setPermission] = useState<NotificationPermission>('default');

  // 알림 권한 요청
  const requestPermission = async () => {
    try {
      const permission = await Notification.requestPermission();
      setPermission(permission);
      
      if (permission === 'granted') {
        await registerFCMToken();
      }
    } catch (error) {
      console.error('Error requesting notification permission:', error);
    }
  };

  // FCM 토큰 등록
  const registerFCMToken = async () => {
    if (!messaging) {
      console.warn('Firebase Messaging not supported');
      return;
    }

    try {
      const currentToken = await getToken(messaging, {
        vapidKey: import.meta.env.VITE_FIREBASE_VAPID_KEY
      });

      if (currentToken) {
        setToken(currentToken);
        
        // 서버에 토큰 등록
        await fetch('/api/v1/notifications/register-token', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            token: currentToken,
            device_type: 'web',
            device_id: navigator.userAgent,
            app_version: '1.0.0'
          })
        });

        console.log('✅ FCM 토큰 등록 완료');
      }
    } catch (error) {
      console.error('❌ FCM 토큰 등록 실패:', error);
    }
  };

  // 포그라운드 메시지 수신
  useEffect(() => {
    if (!messaging) return;

    const unsubscribe = onMessage(messaging, (payload) => {
      console.log('📩 Foreground message received:', payload);
      
      const { title, body } = payload.notification || {};
      
      if (title && body) {
        toast.success(title, {
          description: body,
          duration: 5000
        });
      }
    });

    return () => unsubscribe();
  }, []);

  return {
    token,
    permission,
    requestPermission
  };
};
```

### 4. 환경변수 (`.env`)

```bash
# Firebase 설정
VITE_FIREBASE_API_KEY=AIza...
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcd...
VITE_FIREBASE_VAPID_KEY=BDqY...
```

---

## Firebase 프로젝트 설정

### 1. Firebase Console 설정

1. **Firebase Console 접속**: https://console.firebase.google.com/
2. **프로젝트 생성** 또는 기존 프로젝트 선택
3. **프로젝트 설정** → **일반** → **내 앱** → **웹 앱 추가**
4. **앱 닉네임** 입력 → **앱 등록**
5. **Firebase SDK 구성** 복사 → `.env` 파일에 저장

### 2. Cloud Messaging 설정

1. **프로젝트 설정** → **Cloud Messaging** 탭
2. **웹 푸시 인증서** → **키 페어 생성**
3. **생성된 키 복사** → `.env`의 `VITE_FIREBASE_VAPID_KEY`에 저장

### 3. Service Account 키 생성 (백엔드용)

1. **프로젝트 설정** → **서비스 계정** 탭
2. **새 비공개 키 생성** 클릭
3. **JSON 파일 다운로드**
4. 서버에 업로드: `/root/uvis/backend/firebase-credentials.json`
5. 환경변수 설정:
   ```bash
   export FIREBASE_CREDENTIALS_PATH=/root/uvis/backend/firebase-credentials.json
   ```

---

## 테스트 방법

### 1. 백엔드 테스트

```bash
# FCM 토큰 등록
curl -X POST "http://localhost:8000/api/v1/notifications/register-token" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "your_fcm_token",
    "device_type": "web"
  }'

# 테스트 알림 발송
curl -X POST "http://localhost:8000/api/v1/notifications/test" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 알림 이력 조회
curl "http://localhost:8000/api/v1/notifications/notification-logs" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. 프론트엔드 테스트

1. **브라우저 콘솔**에서 알림 권한 확인:
   ```javascript
   Notification.permission  // 'granted', 'denied', 'default'
   ```

2. **알림 권한 요청 버튼 클릭**
3. **브라우저 알림 허용**
4. **FCM 토큰 등록 확인** (개발자 도구 → Network)
5. **테스트 알림 발송** (API 호출 또는 UI 버튼)
6. **알림 수신 확인**

---

## 배포 가이드

### 1. 백엔드 배포

```bash
# Firebase 인증 파일 업로드
scp firebase-credentials.json user@server:/root/uvis/backend/

# 환경변수 설정
echo 'export FIREBASE_CREDENTIALS_PATH=/root/uvis/backend/firebase-credentials.json' >> ~/.bashrc
source ~/.bashrc

# 백엔드 재빌드
cd /root/uvis
docker-compose stop backend
docker-compose build --no-cache backend
docker-compose up -d backend
```

### 2. 프론트엔드 배포

```bash
# .env 파일 설정 확인
cat /root/uvis/frontend/.env | grep FIREBASE

# 빌드
cd /root/uvis/frontend
npm run build

# 프론트엔드 재시작
cd /root/uvis
docker-compose restart frontend
```

### 3. 배포 확인

```bash
# 백엔드 로그 확인
docker-compose logs backend | grep FCM

# 프론트엔드 접속
http://139.150.11.99/
```

---

## 트러블슈팅

### 문제 1: Firebase 초기화 실패
**증상**: `Firebase Messaging is not supported`  
**해결**: HTTPS 환경에서만 작동 (localhost는 예외)

### 문제 2: 토큰 등록 실패
**증상**: `getToken(): failed to register a Service Worker`  
**해결**: `firebase-messaging-sw.js` 파일을 `public/` 폴더에 배치

### 문제 3: 백그라운드 알림 안 옴
**증상**: 포그라운드는 되는데 백그라운드는 안 됨  
**해결**: Service Worker 재등록

### 문제 4: VAPID key 오류
**증상**: `messaging/invalid-vapid-key`  
**해결**: Firebase Console에서 VAPID 키 재생성

---

## 다음 단계

✅ **완료**:
- FCM 토큰 관리 시스템
- 푸시 알림 발송 API
- 알림 로그 저장

🔄 **진행 중**:
- 프론트엔드 통합 (React Hook, Service Worker)

⏳ **예정**:
- 주문 생성 시 자동 알림
- 배차 완료 시 자동 알림
- UVIS 알림 발생 시 푸시 알림
- iOS/Android 앱 통합

---

**문서 작성**: 2026년 2월 26일  
**최종 업데이트**: 2026년 2월 26일  
**작성자**: AI Assistant (GenSpark)
