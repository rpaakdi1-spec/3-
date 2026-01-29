# 📱 기사용 모바일 앱 설치 가이드

**Cold Chain Dispatch System - Driver Mobile App Installation Guide**

---

## 📋 목차

1. [사전 요구사항](#사전-요구사항)
2. [개발 환경 설정](#개발-환경-설정)
3. [프로젝트 설치](#프로젝트-설치)
4. [Android 설정](#android-설정)
5. [iOS 설정](#ios-설정)
6. [빌드 및 실행](#빌드-및-실행)
7. [문제 해결](#문제-해결)

---

## 사전 요구사항

### 1. Node.js 설치

**버전**: 18.x 이상

```bash
# macOS (Homebrew)
brew install node@18

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 버전 확인
node -v  # v18.x.x
npm -v   # 9.x.x
```

### 2. React Native CLI 설치

```bash
npm install -g react-native-cli
```

### 3. Android Studio 설치 (Android 개발)

1. [Android Studio 다운로드](https://developer.android.com/studio)
2. Android Studio 설치
3. SDK Manager에서 다음 설치:
   - Android SDK Platform 33 (Android 13)
   - Android SDK Build-Tools 33.0.0
   - Android Emulator
   - Intel x86 Emulator Accelerator (HAXM)

4. 환경 변수 설정:

```bash
# macOS/Linux (~/.bashrc 또는 ~/.zshrc)
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools

# Windows (환경 변수)
ANDROID_HOME=C:\Users\YOUR_USERNAME\AppData\Local\Android\Sdk
Path=%ANDROID_HOME%\platform-tools;%ANDROID_HOME%\tools;...
```

5. 확인:

```bash
adb version
# Android Debug Bridge version 1.0.41
```

### 4. Xcode 설치 (iOS 개발, macOS만)

1. App Store에서 Xcode 설치
2. Xcode Command Line Tools 설치:

```bash
xcode-select --install
```

3. CocoaPods 설치:

```bash
sudo gem install cocoapods
```

---

## 개발 환경 설정

### 1. Git 클론

```bash
cd ~/projects
git clone https://github.com/your-repo/cold-chain-dispatch.git
cd cold-chain-dispatch/mobile-app
```

### 2. 환경 변수 설정

`src/services/api.ts` 파일에서 백엔드 API URL 설정:

```typescript
const API_BASE_URL = 'http://10.0.2.2:8000/api/v1';  // Android Emulator
// const API_BASE_URL = 'http://localhost:8000/api/v1';  // iOS Simulator
// const API_BASE_URL = 'http://192.168.x.x:8000/api/v1';  // 실제 디바이스 (로컬 네트워크 IP)
// const API_BASE_URL = 'https://api.yourcompany.com/api/v1';  // 프로덕션
```

**중요**: 실제 디바이스에서 테스트 시 로컬 네트워크 IP를 사용해야 합니다.

```bash
# macOS/Linux에서 IP 확인
ifconfig | grep "inet "

# Windows에서 IP 확인
ipconfig
```

---

## 프로젝트 설치

### 1. 의존성 설치

```bash
cd mobile-app
npm install
```

### 2. iOS Pod 설치 (macOS만)

```bash
cd ios
pod install
cd ..
```

---

## Android 설정

### 1. Android 권한 설정

`android/app/src/main/AndroidManifest.xml` 확인:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
```

### 2. Firebase 설정 (푸시 알림)

1. [Firebase Console](https://console.firebase.google.com/)에서 프로젝트 생성
2. Android 앱 추가 (패키지명: `com.coldchaindispatch.driver`)
3. `google-services.json` 다운로드
4. `android/app/` 디렉토리에 복사

```bash
cp ~/Downloads/google-services.json android/app/
```

5. `android/build.gradle` 확인:

```gradle
buildscript {
    dependencies {
        classpath 'com.google.gms:google-services:4.3.15'
    }
}
```

6. `android/app/build.gradle` 확인:

```gradle
apply plugin: 'com.google.gms.google-services'
```

### 3. Android Emulator 실행

```bash
# Emulator 목록 확인
emulator -list-avds

# Emulator 실행
emulator -avd Pixel_5_API_33
```

### 4. 실제 Android 디바이스 연결

1. 디바이스에서 **개발자 옵션** 활성화
2. **USB 디버깅** 활성화
3. USB 케이블로 연결

```bash
# 디바이스 확인
adb devices
# List of devices attached
# 1234567890ABCDEF    device
```

---

## iOS 설정 (macOS만)

### 1. iOS 권한 설정

`ios/ColdChainDriver/Info.plist` 확인:

```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>배차 위치 추적을 위해 위치 권한이 필요합니다.</string>

<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>배차 중 실시간 위치 추적을 위해 백그라운드 위치 권한이 필요합니다.</string>

<key>NSCameraUsageDescription</key>
<string>상하차 사진 촬영을 위해 카메라 권한이 필요합니다.</string>

<key>NSPhotoLibraryUsageDescription</key>
<string>사진 저장을 위해 앨범 접근 권한이 필요합니다.</string>
```

### 2. Firebase 설정 (푸시 알림)

1. Firebase Console에서 iOS 앱 추가 (Bundle ID: `com.coldchaindispatch.driver`)
2. `GoogleService-Info.plist` 다운로드
3. Xcode에서 프로젝트에 추가

```bash
cp ~/Downloads/GoogleService-Info.plist ios/ColdChainDriver/
```

4. Xcode에서 **Signing & Capabilities** 설정:
   - Team 선택
   - Push Notifications 추가
   - Background Modes 추가:
     - Location updates
     - Background fetch
     - Remote notifications

### 3. iOS Simulator 실행

```bash
# Simulator 목록 확인
xcrun simctl list devices

# Simulator 실행
open -a Simulator
```

---

## 빌드 및 실행

### Android

#### 개발 모드 실행

```bash
npm run android
```

또는

```bash
react-native run-android
```

#### Release APK 빌드

```bash
cd android
./gradlew assembleRelease

# APK 위치: android/app/build/outputs/apk/release/app-release.apk
```

#### Release APK 설치

```bash
adb install android/app/build/outputs/apk/release/app-release.apk
```

### iOS (macOS만)

#### 개발 모드 실행

```bash
npm run ios
```

또는

```bash
react-native run-ios
```

#### 특정 시뮬레이터 지정

```bash
react-native run-ios --simulator="iPhone 14"
```

#### Release IPA 빌드 (Xcode 사용)

1. Xcode에서 프로젝트 열기:
   ```bash
   open ios/ColdChainDriver.xcworkspace
   ```

2. Product → Archive
3. Distribute App → Ad Hoc / App Store

---

## 개발 서버 시작

### Metro Bundler 시작

```bash
npm start
```

또는

```bash
react-native start
```

### 캐시 클리어

```bash
npm start -- --reset-cache
```

---

## 문제 해결

### 1. Android 빌드 실패

#### Gradle 빌드 오류

```bash
cd android
./gradlew clean
./gradlew build
```

#### SDK 버전 문제

`android/app/build.gradle` 확인:

```gradle
android {
    compileSdkVersion 33
    defaultConfig {
        minSdkVersion 21
        targetSdkVersion 33
    }
}
```

### 2. iOS 빌드 실패

#### Pod 설치 문제

```bash
cd ios
pod deintegrate
pod install
cd ..
```

#### Xcode 캐시 삭제

```bash
cd ios
rm -rf ~/Library/Developer/Xcode/DerivedData
xcodebuild clean
cd ..
```

### 3. Metro Bundler 포트 충돌

```bash
lsof -i :8081
kill -9 <PID>
npm start
```

### 4. GPS 위치 가져오기 실패

- 위치 권한 확인
- GPS 활성화 확인
- Simulator의 경우: Features → Location → Custom Location

### 5. 카메라 접근 실패

- 카메라 권한 확인
- Simulator는 카메라 지원 안 함 (실제 디바이스 필요)

### 6. 푸시 알림 수신 실패

- `google-services.json` / `GoogleService-Info.plist` 확인
- FCM 서버 키 확인
- 앱 재설치 후 토큰 갱신

### 7. 네트워크 요청 실패

- API URL 확인
- 네트워크 연결 확인
- Android Emulator: `http://10.0.2.2:8000`
- iOS Simulator: `http://localhost:8000`
- 실제 디바이스: 로컬 네트워크 IP 사용

---

## 디버깅

### React Native Debugger

```bash
# Chrome DevTools
npm run android
# 앱에서 Shake → Debug
# Chrome에서 http://localhost:8081/debugger-ui 열기
```

### 로그 확인

```bash
# Android
adb logcat | grep ReactNative

# iOS
react-native log-ios
```

### 네트워크 디버깅

```bash
# Reactotron 설치 (선택 사항)
npm install --save-dev reactotron-react-native
```

---

## 추가 도구

### React Native CLI 업그레이드

```bash
npm install -g react-native-cli@latest
```

### 프로젝트 의존성 업데이트

```bash
npm update
```

### TypeScript 체크

```bash
npm run tsc
```

---

## 배포 체크리스트

### Android

- [ ] Release 키스토어 생성
- [ ] `android/gradle.properties`에 키스토어 설정
- [ ] ProGuard 규칙 확인
- [ ] Release APK 빌드 및 테스트
- [ ] Google Play Console에 업로드

### iOS

- [ ] Apple Developer 계정 준비
- [ ] Provisioning Profile 생성
- [ ] App ID 등록
- [ ] Push Notification 인증서 생성
- [ ] Archive 및 IPA 생성
- [ ] App Store Connect에 업로드

---

## 참고 자료

- [React Native 공식 문서](https://reactnative.dev/)
- [React Navigation](https://reactnavigation.org/)
- [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)
- [React Native Vision Camera](https://github.com/mrousavy/react-native-vision-camera)
- [Background Geolocation](https://github.com/transistorsoft/react-native-background-geolocation)

---

**작성일**: 2026-01-27  
**버전**: 1.0.0  
**작성자**: GenSpark AI Developer
