# 📱 UVIS GPS Fleet Management - Mobile App

React Native 모바일 앱 (Expo)

---

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
npm install
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# API URL을 로컬 IP로 변경
# .env 파일을 열어서 수정:
EXPO_PUBLIC_API_URL=http://YOUR_LOCAL_IP:8000
EXPO_PUBLIC_WS_URL=ws://YOUR_LOCAL_IP:8001
```

**로컬 IP 찾기:**
```bash
# Mac/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig | findstr IPv4
```

### 3. 개발 서버 시작

```bash
npm start
```

---

## 📱 실제 기기에서 테스트

### Android

1. **Expo Go 앱 설치**
   - Google Play Store에서 "Expo Go" 검색
   - 설치

2. **QR 코드 스캔**
   - 터미널에 표시된 QR 코드 스캔
   - 또는 주소 직접 입력

3. **앱 실행**
   - 자동으로 다운로드 및 실행

### iOS

1. **Expo Go 앱 설치**
   - App Store에서 "Expo Go" 검색
   - 설치

2. **QR 코드 스캔**
   - 카메라 앱으로 QR 코드 스캔
   - Expo Go에서 열기

3. **앱 실행**
   - 자동으로 다운로드 및 실행

---

## 🔧 주요 기능

### ✅ 구현된 기능

- **GPS 추적**: 실시간 위치 전송 (10초 간격)
- **사진 촬영**: 픽업/배송 증명 사진
- **배차 관리**: 수락/거절/상태 업데이트
- **오프라인 모드**: 자동 동기화
- **푸시 알림**: 실시간 배차 알림

---

## 📂 프로젝트 구조

```
mobile/
├── App.tsx                 # 앱 진입점
├── app.json               # Expo 설정
├── package.json           # 의존성
├── .env                   # 환경 변수 (gitignore)
├── .env.example           # 환경 변수 예시
└── src/
    ├── components/        # 재사용 컴포넌트
    ├── screens/          # 화면 컴포넌트
    ├── navigation/       # 네비게이션 설정
    ├── services/         # API 및 서비스
    │   ├── gpsService.ts      # GPS 추적 ⭐
    │   ├── cameraService.ts   # 사진 촬영 ⭐
    │   ├── authService.ts
    │   ├── dispatchService.ts
    │   └── notificationService.ts
    ├── hooks/            # Custom hooks
    ├── utils/            # 유틸리티
    └── types/            # TypeScript 타입
```

---

## 🎯 테스트 시나리오

### 1. 로그인 테스트

```
1. 앱 실행
2. 이메일/비밀번호 입력
3. 로그인 버튼 클릭
4. 대시보드 화면 확인
```

### 2. 배차 수락 테스트

```
1. 배차 목록 화면
2. 배차 항목 클릭
3. [배차 수락] 버튼 클릭
4. 확인 다이얼로그 [수락] 클릭
5. 상태 변경 확인
```

### 3. GPS 추적 테스트

```
1. 배차 상세 화면
2. [운송 시작] 버튼 클릭
3. GPS 추적 상태 "활성" 확인
4. 위치 권한 허용
5. 백그라운드로 전환
6. 10초 후 위치 업데이트 확인
```

### 4. 사진 촬영 테스트

```
1. [픽업 사진 촬영] 버튼 클릭
2. 카메라 권한 허용
3. 사진 촬영
4. 사진 미리보기 확인
5. 서버 업로드 확인 (또는 오프라인 큐)
```

### 5. 오프라인 모드 테스트

```
1. 비행기 모드 켜기
2. GPS 데이터 생성 (이동)
3. 사진 촬영
4. 상태 변경 시도
5. "오프라인 모드" 메시지 확인
6. 비행기 모드 끄기
7. 자동 동기화 확인
```

---

## 🛠️ 문제 해결

### 앱이 로드되지 않을 때

```bash
# 1. 캐시 삭제
npm start -- --clear

# 2. node_modules 재설치
rm -rf node_modules
npm install

# 3. Expo 재시작
npm start
```

### "Network response timed out" 오류

```bash
# .env 파일에서 IP 주소 확인
# localhost 대신 실제 로컬 IP 사용

# 예:
EXPO_PUBLIC_API_URL=http://192.168.1.100:8000
```

### GPS 권한 오류

```
Android:
1. 설정 → 앱 → UVIS GPS Fleet
2. 권한 → 위치
3. "항상 허용" 선택

iOS:
1. 설정 → 개인정보 보호 → 위치 서비스
2. UVIS GPS Fleet 찾기
3. "항상" 선택
```

---

## 📦 빌드

### Android APK

```bash
# EAS 빌드 (권장)
npm install -g eas-cli
eas build --platform android

# 또는 로컬 빌드
expo build:android
```

### iOS IPA

```bash
# EAS 빌드 (권장)
eas build --platform ios

# Apple Developer 계정 필요
```

---

## 🔗 관련 문서

- **완성 보고서**: [PHASE15_MOBILE_APP_COMPLETE.md](./PHASE15_MOBILE_APP_COMPLETE.md)
- **프로젝트 현황**: [PROJECT_STATUS_FINAL.md](../PROJECT_STATUS_FINAL.md)
- **배포 가이드**: [DEPLOYMENT_NEXT_STEPS.md](../DEPLOYMENT_NEXT_STEPS.md)

---

## 📞 지원

- **GitHub**: https://github.com/rpaakdi1-spec/3-
- **PR**: https://github.com/rpaakdi1-spec/3-/pull/1
- **Branch**: genspark_ai_developer

---

**버전**: 1.0.0  
**최종 업데이트**: 2026-01-28  
**상태**: ✅ 프로덕션 준비 완료
