# 📱 모바일 앱 실제 기기 테스트 가이드

**작성일**: 2026-01-28  
**난이도**: ⭐⭐ (쉬움)  
**소요 시간**: 30분  
**상태**: ✅ 테스트 준비 완료

---

## 🎯 테스트 목표

UVIS Cold Chain Dispatch 모바일 앱을 실제 Android/iOS 기기에서 테스트합니다.

### 📋 테스트 항목

- ✅ 로그인 및 인증
- ✅ 배차 목록 조회
- ✅ 배차 상세 정보
- ✅ 배차 수락/거절
- ✅ GPS 위치 추적
- ✅ 사진 촬영 및 업로드
- ✅ 배송 상태 업데이트
- ✅ 푸시 알림 수신
- ✅ 오프라인 모드

---

## 🚀 Step 1: Expo 개발 서버 시작 완료!

### ✅ 서버 상태

```yaml
서비스: Expo Metro Bundler
포트: 8081
상태: ✅ 실행 중
URL: https://8081-i16kcdhvw5ng6rusdg7lj-ad490db5.sandbox.novita.ai
```

### 📱 Metro Bundler 접속

브라우저에서 Metro Bundler에 접속하세요:

**Metro Bundler URL**:  
🔗 **https://8081-i16kcdhvw5ng6rusdg7lj-ad490db5.sandbox.novita.ai**

---

## 📱 Step 2: 실제 기기에서 테스트

### Option A: Expo Go 앱 사용 (권장 - 가장 빠름)

#### 1️⃣ Expo Go 앱 설치

**Android**:  
- Google Play Store에서 "Expo Go" 검색 및 설치
- 또는 직접 링크: https://play.google.com/store/apps/details?id=host.exp.exponent

**iOS**:  
- App Store에서 "Expo Go" 검색 및 설치
- 또는 직접 링크: https://apps.apple.com/app/expo-go/id982107779

#### 2️⃣ 프로젝트 연결 방법

**방법 1: URL 직접 입력 (권장)**

1. Expo Go 앱 실행
2. "Enter URL manually" 선택
3. 다음 URL 입력:
   ```
   exp://8081-i16kcdhvw5ng6rusdg7lj-ad490db5.sandbox.novita.ai:8081
   ```
4. "Connect" 버튼 클릭

**방법 2: QR 코드 스캔**

QR 코드를 생성하여 스캔할 수 있습니다:

1. 브라우저에서 Metro Bundler 접속:
   ```
   https://8081-i16kcdhvw5ng6rusdg7lj-ad490db5.sandbox.novita.ai
   ```

2. Expo Go 앱에서 QR 코드 스캔

---

### Option B: Android 개발자 모드 (고급)

Android 기기를 USB로 연결하여 직접 설치:

```bash
# ADB 연결 확인
cd /home/user/webapp/mobile
npx expo run:android
```

**요구사항**:
- Android Studio 설치
- USB 디버깅 활성화
- ADB 드라이버 설치

---

### Option C: iOS 시뮬레이터 (Mac 필요)

Mac에서만 가능:

```bash
cd /home/user/webapp/mobile
npx expo run:ios
```

---

## 🧪 Step 3: 기능 테스트 체크리스트

### 1️⃣ 로그인 테스트

```yaml
테스트 계정:
  사용자명: driver1
  비밀번호: password123

테스트 항목:
  ✅ 로그인 화면 표시
  ✅ 아이디/비밀번호 입력
  ✅ 로그인 버튼 동작
  ✅ 인증 토큰 저장
  ✅ 대시보드로 이동
```

### 2️⃣ 배차 목록 테스트

```yaml
테스트 항목:
  ✅ 배차 목록 로딩
  ✅ 배차 카드 표시
  ✅ 상태별 필터링
  ✅ 새로고침 기능
  ✅ Pull to refresh
```

### 3️⃣ 배차 상세 테스트

```yaml
테스트 항목:
  ✅ 배차 상세 정보 표시
  ✅ 차량 정보 확인
  ✅ 운전자 정보 확인
  ✅ 일정 정보 확인
  ✅ 주문 목록 확인
```

### 4️⃣ 배차 수락/거절 테스트

```yaml
테스트 항목:
  ✅ 배차 수락 버튼
  ✅ 배차 거절 버튼
  ✅ 확인 다이얼로그
  ✅ 상태 업데이트
  ✅ 성공 메시지 표시
```

### 5️⃣ GPS 위치 추적 테스트

```yaml
테스트 항목:
  ✅ 위치 권한 요청
  ✅ GPS 활성화
  ✅ 현재 위치 가져오기
  ✅ 실시간 위치 업데이트 (10초마다)
  ✅ 백그라운드 위치 추적
  ✅ 서버로 위치 전송
```

**GPS 테스트 방법**:
1. 배차를 수락하고 "운송 시작" 버튼 클릭
2. 위치 권한 허용
3. GPS가 활성화되면 10초마다 위치가 업데이트됨
4. 디버그 로그에서 위치 전송 확인

### 6️⃣ 사진 촬영 및 업로드 테스트

```yaml
테스트 항목:
  ✅ 카메라 권한 요청
  ✅ 사진 촬영
  ✅ 사진 미리보기
  ✅ GPS 메타데이터 포함
  ✅ 사진 업로드
  ✅ 업로드 진행률 표시
```

**사진 테스트 시나리오**:

1. **픽업 사진 촬영**:
   - 배차 수락 후 "픽업 사진 촬영" 버튼 클릭
   - 카메라 권한 허용
   - 사진 촬영 또는 갤러리에서 선택
   - 사진 업로드 확인

2. **배송 사진 촬영**:
   - 운송 시작 후 "배송 사진 촬영" 버튼 클릭
   - 사진 촬영
   - GPS 위치 자동 포함 확인
   - 업로드 완료 확인

### 7️⃣ 배송 상태 업데이트 테스트

```yaml
워크플로우:
  1. pending → assigned (배차 수락)
  2. assigned → in_progress (운송 시작)
  3. in_progress → completed (완료 처리)

각 단계에서 확인:
  ✅ 상태 변경 버튼 표시
  ✅ 확인 다이얼로그
  ✅ 상태 업데이트 요청
  ✅ UI 업데이트
  ✅ 성공 메시지
```

### 8️⃣ 푸시 알림 테스트

```yaml
테스트 항목:
  ✅ 알림 권한 요청
  ✅ Expo Push Token 생성
  ✅ 토큰 서버 전송
  ✅ 알림 수신
  ✅ 알림 클릭 처리
  ✅ 배경/포그라운드 알림
```

**알림 테스트 방법**:
1. 앱 시작 시 알림 권한 허용
2. 토큰이 생성되면 서버에 자동 전송
3. 백엔드에서 테스트 알림 발송:
   ```bash
   curl -X POST https://exp.host/--/api/v2/push/send \
     -H "Content-Type: application/json" \
     -d '{
       "to": "ExponentPushToken[xxxxxx]",
       "title": "새 배차 알림",
       "body": "새로운 배차가 할당되었습니다",
       "data": {"dispatchId": 123}
     }'
   ```

### 9️⃣ 오프라인 모드 테스트

```yaml
테스트 항목:
  ✅ 네트워크 끊김 감지
  ✅ 오프라인 UI 표시
  ✅ 로컬 데이터 저장
  ✅ 오프라인 큐에 작업 추가
  ✅ 네트워크 복구 시 자동 동기화
```

**오프라인 테스트 시나리오**:

1. **네트워크 끊김 테스트**:
   - Wi-Fi 및 모바일 데이터 끄기
   - 앱에서 오프라인 메시지 확인
   - GPS 위치는 계속 수집됨

2. **오프라인 작업 테스트**:
   - 오프라인 상태에서 상태 업데이트 시도
   - 작업이 큐에 저장됨
   - 네트워크 복구 시 자동 전송 확인

3. **데이터 동기화 테스트**:
   - Wi-Fi 다시 켜기
   - 큐에 있던 GPS 위치 자동 전송
   - 상태 업데이트 자동 완료

---

## 🐛 디버깅 및 로그

### 개발자 메뉴 열기

**Android**: 기기를 흔들거나 `Ctrl+M` (에뮬레이터)  
**iOS**: `Cmd+D` (시뮬레이터) 또는 기기를 흔들기

### 로그 확인

터미널에서 로그 실시간 확인:

```bash
# 전체 로그
cd /home/user/webapp/mobile
npx expo start --clear

# React Native 로그만
adb logcat *:S ReactNative:V ReactNativeJS:V
```

### Metro Bundler 로그

브라우저에서 Metro Bundler 접속:
```
https://8081-i16kcdhvw5ng6rusdg7lj-ad490db5.sandbox.novita.ai
```

---

## 📊 성능 모니터링

### 앱 성능 지표

```yaml
주요 지표:
  - 초기 로딩 시간: < 3초
  - API 응답 시간: < 1초
  - GPS 업데이트 주기: 10초
  - 사진 업로드 시간: < 5초
  - 메모리 사용량: < 150MB
  - 배터리 사용량: 보통 수준
```

### 성능 프로파일링

Expo Go 앱에서:
1. 개발자 메뉴 열기
2. "Performance Monitor" 선택
3. FPS, 메모리, CPU 사용량 확인

---

## 🔧 문제 해결 (Troubleshooting)

### 문제 1: 앱이 연결되지 않음

**해결 방법**:
```bash
# Metro Bundler 재시작
cd /home/user/webapp/mobile
npx expo start --clear

# 캐시 삭제
npx expo start -c
```

### 문제 2: "Network request failed" 오류

**원인**: API 서버에 연결할 수 없음

**해결 방법**:
1. `.env` 파일의 `EXPO_PUBLIC_API_URL` 확인
2. 백엔드 서버가 실행 중인지 확인
3. 방화벽 설정 확인

### 문제 3: GPS 위치를 가져올 수 없음

**해결 방법**:
1. 위치 권한이 허용되었는지 확인
2. GPS가 활성화되었는지 확인
3. 실외에서 테스트 (GPS 신호 수신)

### 문제 4: 사진을 업로드할 수 없음

**해결 방법**:
1. 카메라/갤러리 권한 확인
2. 네트워크 연결 확인
3. 사진 크기 확인 (최대 5MB)

### 문제 5: 푸시 알림이 오지 않음

**해결 방법**:
1. 알림 권한이 허용되었는지 확인
2. Expo Push Token이 생성되었는지 확인
3. 백엔드에서 올바른 토큰으로 발송하는지 확인

---

## 📝 테스트 결과 보고

### 테스트 완료 체크리스트

```yaml
기능 테스트:
  ✅ 로그인/로그아웃
  ✅ 배차 목록 조회
  ✅ 배차 상세 정보
  ✅ 배차 수락/거절
  ✅ GPS 위치 추적
  ✅ 사진 촬영 및 업로드
  ✅ 배송 상태 업데이트
  ✅ 푸시 알림
  ✅ 오프라인 모드

성능 테스트:
  ✅ 로딩 속도
  ✅ API 응답 시간
  ✅ 메모리 사용량
  ✅ 배터리 소모
  ✅ 네트워크 사용량

사용성 테스트:
  ✅ UI/UX 직관성
  ✅ 버튼 반응성
  ✅ 오류 메시지 명확성
  ✅ 네비게이션 편의성
```

### 버그 리포트 양식

```markdown
## 버그 리포트

**제목**: [간단한 설명]

**발생 환경**:
- 기기: [Android/iOS]
- 모델: [기기 모델명]
- OS 버전: [Android 13 / iOS 16]
- 앱 버전: 1.0.0

**재현 단계**:
1. [단계 1]
2. [단계 2]
3. [단계 3]

**예상 동작**:
[예상했던 결과]

**실제 동작**:
[실제로 발생한 결과]

**스크린샷**:
[스크린샷 첨부]

**추가 정보**:
[오류 메시지, 로그 등]
```

---

## 🎉 테스트 완료 후

### 다음 단계

1. **버그 수정**:
   - 발견된 버그 수정
   - 성능 최적화
   - UI/UX 개선

2. **배포 준비**:
   - Android: Google Play Store
   - iOS: Apple App Store

3. **사용자 피드백**:
   - 베타 테스터 모집
   - 피드백 수집 및 반영

---

## 📚 참고 자료

### Expo 문서
- Expo Go: https://docs.expo.dev/get-started/expo-go/
- Metro Bundler: https://docs.expo.dev/guides/customizing-metro/
- Push Notifications: https://docs.expo.dev/push-notifications/overview/
- Location: https://docs.expo.dev/versions/latest/sdk/location/
- Camera: https://docs.expo.dev/versions/latest/sdk/camera/

### React Native 문서
- React Native Docs: https://reactnative.dev/docs/getting-started
- React Navigation: https://reactnavigation.org/docs/getting-started
- AsyncStorage: https://react-native-async-storage.github.io/async-storage/

### 프로젝트 문서
- Phase 15 완성 보고서: `PHASE15_MOBILE_APP_COMPLETE.md`
- Phase 15 요약: `PHASE15_SUMMARY.md`
- 모바일 앱 가이드: `mobile/REACT_NATIVE_GUIDE.md`

---

## 🔗 중요 링크

**Metro Bundler URL**:  
🔗 **https://8081-i16kcdhvw5ng6rusdg7lj-ad490db5.sandbox.novita.ai**

**Expo Go 다운로드**:
- Android: https://play.google.com/store/apps/details?id=host.exp.exponent
- iOS: https://apps.apple.com/app/expo-go/id982107779

**GitHub 저장소**:
- Repository: https://github.com/rpaakdi1-spec/3-
- Branch: genspark_ai_developer
- PR: https://github.com/rpaakdi1-spec/3-/pull/1

---

## 📞 지원

**문제가 발생하면**:
1. 이 문서의 "문제 해결" 섹션 참조
2. Expo 공식 문서 확인
3. GitHub Issues에 버그 리포트

---

**작성일**: 2026-01-28  
**버전**: 1.0.0  
**작성자**: GenSpark AI Developer  
**상태**: ✅ 테스트 준비 완료

**Happy Testing! 🚀📱**
