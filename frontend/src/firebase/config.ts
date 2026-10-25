/**
 * Firebase 설정 및 초기화
 * VITE_FIREBASE_* 환경변수가 없으면 Firebase를 비활성화 (에러 없이 graceful 처리)
 */

import { initializeApp, FirebaseApp } from 'firebase/app';
import { getMessaging, Messaging } from 'firebase/messaging';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || '',
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || '',
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || '',
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || '',
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || '',
  appId: import.meta.env.VITE_FIREBASE_APP_ID || '',
};

// projectId / apiKey / appId 중 하나라도 없으면 Firebase 완전 비활성화
export const isFirebaseConfigured = !!(
  firebaseConfig.projectId &&
  firebaseConfig.apiKey &&
  firebaseConfig.appId
);

let firebaseApp: FirebaseApp | null = null;
let messaging: Messaging | null = null;

if (isFirebaseConfigured) {
  try {
    firebaseApp = initializeApp(firebaseConfig);

    if (typeof window !== 'undefined' && 'Notification' in window && 'serviceWorker' in navigator) {
      messaging = getMessaging(firebaseApp);
    }
  } catch {
    // 초기화 실패 시 조용히 비활성화
    firebaseApp = null;
    messaging = null;
  }
}

export { firebaseApp, messaging };
