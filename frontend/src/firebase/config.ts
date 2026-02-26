/**
 * Firebase 설정 및 초기화
 */

import { initializeApp, FirebaseApp } from 'firebase/app';
import { getMessaging, Messaging } from 'firebase/messaging';

// Firebase 설정 (환경변수에서 가져오기)
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

// Firebase 앱 초기화
let firebaseApp: FirebaseApp | null = null;
let messaging: Messaging | null = null;

try {
  firebaseApp = initializeApp(firebaseConfig);
  console.log('✅ Firebase App initialized');

  // Firebase Messaging 초기화 (브라우저 지원 확인)
  if ('Notification' in window && 'serviceWorker' in navigator) {
    messaging = getMessaging(firebaseApp);
    console.log('✅ Firebase Messaging initialized');
  } else {
    console.warn('⚠️ Browser does not support notifications or service workers');
  }
} catch (error) {
  console.error('❌ Firebase initialization failed:', error);
}

export { firebaseApp, messaging };
