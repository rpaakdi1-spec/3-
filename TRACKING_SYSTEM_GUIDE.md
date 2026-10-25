# 실시간 배송 추적 시스템 구현 완료

## ✅ 구현 완료 사항

### 1. 백엔드 API

#### 데이터베이스 테이블
- ✅ `dispatch_documents` - 배차 서류 (거래명세표, 온도기록지, 서명)
- ✅ `dispatch_tracking` - 고객 공개용 추적 번호

#### API 엔드포인트
- ✅ `POST /api/v1/dispatch/documents/upload` - 서류 업로드
- ✅ `GET /api/v1/dispatch/documents` - 서류 목록 조회
- ✅ `PATCH /api/v1/dispatch/documents/{id}/verify` - 서류 검증
- ✅ `POST /api/v1/dispatch/tracking/generate` - 추적 번호 생성
- ✅ `GET /api/v1/dispatch/tracking/public/{tracking_number}` - 공개 추적 (인증 불필요)

### 2. 프론트엔드

#### 공개 추적 페이지
- ✅ `/track/{추적번호}` - 고객용 공개 추적 페이지
- ✅ 실시간 위치 표시
- ✅ 배송 경로 및 진행률
- ✅ 서류 다운로드 기능
- ✅ 30초 자동 새로고침

---

## 📋 사용 방법

### 1. 추적 번호 생성 (관리자)

배차 생성 후 추적 번호를 생성합니다:

```bash
curl -X POST http://139.150.11.99/api/v1/dispatch/tracking/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dispatch_id": 123,
    "customer_name": "동원F&B",
    "customer_email": "dongwon@example.com",
    "customer_phone": "010-1234-5678",
    "expires_days": 7
  }'
```

**응답 예시:**
```json
{
  "id": 1,
  "dispatch_id": 123,
  "tracking_number": "TRK-20260311-A3F5B2C1",
  "is_active": true,
  "customer_name": "동원F&B",
  "customer_email": "dongwon@example.com",
  "view_count": 0,
  "created_at": "2026-03-11T12:00:00"
}
```

### 2. 고객에게 추적 번호 전달

생성된 추적 번호를 고객에게 문자/이메일로 전송:

```
[UVIS 배송 알림]
배송이 시작되었습니다.
추적 번호: TRK-20260311-A3F5B2C1

실시간 위치 확인:
http://139.150.11.99/track/TRK-20260311-A3F5B2C1
```

### 3. 기사님이 서류 업로드

**출발 시:**
```bash
curl -X POST http://139.150.11.99/api/v1/dispatch/documents/upload \
  -H "Authorization: Bearer DRIVER_TOKEN" \
  -F "file=@transaction_statement_departure.pdf" \
  -F "dispatch_id=123" \
  -F "document_type=거래명세표" \
  -F "stage=출발" \
  -F "latitude=37.5665" \
  -F "longitude=126.978"
```

**도착 시:**
```bash
curl -X POST http://139.150.11.99/api/v1/dispatch/documents/upload \
  -H "Authorization: Bearer DRIVER_TOKEN" \
  -F "file=@transaction_statement_arrival.pdf" \
  -F "dispatch_id=123" \
  -F "document_type=거래명세표" \
  -F "stage=도착" \
  -F "latitude=37.4563" \
  -F "longitude=126.7052"
```

### 4. 고객이 실시간 추적

브라우저에서 접속 (로그인 불필요):
```
http://139.150.11.99/track/TRK-20260311-A3F5B2C1
```

**표시 내용:**
- ✅ 현재 차량 위치 (GPS)
- ✅ 배송 경로 및 진행률
- ✅ 예상 도착 시간
- ✅ 업로드된 서류 다운로드
- ✅ 차량 번호, 기사님 정보

---

## 🔧 통합 방법

### 배차 페이지에 추적 번호 생성 버튼 추가

`frontend/src/pages/DispatchesPage.tsx`에 다음 기능 추가:

```typescript
import { Share2 } from 'lucide-react';

const generateTrackingNumber = async (dispatchId: number) => {
  try {
    const response = await apiClient.post('/dispatch/tracking/generate', {
      dispatch_id: dispatchId,
      expires_days: 7
    });
    
    const trackingNumber = response.data.tracking_number;
    const trackingUrl = `http://139.150.11.99/track/${trackingNumber}`;
    
    // 클립보드에 복사
    navigator.clipboard.writeText(trackingUrl);
    toast.success('추적 URL이 복사되었습니다!');
    
    // 또는 바로 공유
    if (navigator.share) {
      await navigator.share({
        title: '배송 추적',
        text: `실시간 배송 위치를 확인하세요`,
        url: trackingUrl
      });
    }
  } catch (error) {
    toast.error('추적 번호 생성 실패');
  }
};

// 배차 목록 각 행에 추가
<button
  onClick={() => generateTrackingNumber(dispatch.id)}
  className="p-2 text-blue-600 hover:bg-blue-50 rounded"
  title="추적 번호 생성"
>
  <Share2 className="w-5 h-5" />
</button>
```

---

## 📱 기사 앱 연동

### 서류 업로드 기능

기사 앱에서 카메라로 서류를 촬영하고 업로드:

```typescript
// React Native 예시
import { launchCamera } from 'react-native-image-picker';

const uploadDocument = async (dispatchId: number, stage: 'departure' | 'arrival') => {
  // 1. 카메라로 촬영
  const result = await launchCamera({
    mediaType: 'photo',
    quality: 0.8,
  });
  
  if (result.assets && result.assets[0]) {
    const photo = result.assets[0];
    
    // 2. FormData 생성
    const formData = new FormData();
    formData.append('file', {
      uri: photo.uri,
      type: 'image/jpeg',
      name: 'transaction_statement.jpg',
    });
    formData.append('dispatch_id', dispatchId.toString());
    formData.append('document_type', '거래명세표');
    formData.append('stage', stage === 'departure' ? '출발' : '도착');
    
    // 3. 현재 위치 가져오기
    const location = await getCurrentPosition();
    formData.append('latitude', location.latitude.toString());
    formData.append('longitude', location.longitude.toString());
    
    // 4. 업로드
    const response = await fetch(
      'http://139.150.11.99/api/v1/dispatch/documents/upload',
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      }
    );
    
    if (response.ok) {
      alert('서류가 업로드되었습니다.');
    }
  }
};
```

---

## 🚗 외부 용차 (1회성 차량) 지원

### GPS 추적 방법

외부 용차도 동일하게 추적 가능합니다:

1. **기사 앱 설치**
   - 외부 기사님께 UVIS 기사 앱 설치
   - 계정 생성 (임시 계정 가능)

2. **배차 할당**
   - 차량을 "외부용차" 타입으로 등록
   - 외부 기사에게 배차 할당

3. **GPS 추적**
   - 기사 앱이 자동으로 GPS 전송
   - `vehicle_locations` 테이블에 저장
   - 공개 추적 페이지에서 실시간 표시

4. **서류 업로드**
   - 외부 기사도 동일하게 서류 업로드 가능

---

## 🔒 보안 고려사항

### 추적 번호 특징
- **추측 불가능**: 랜덤 8자리 해시
- **기간 제한**: 기본 7일 (설정 가능)
- **조회 통계**: 조회수 기록
- **만료 후 비활성화**: 자동 비활성화

### 공개 정보 제한
공개 추적 페이지에서는 다음 정보만 표시:
- ✅ 차량 번호
- ✅ 기사 이름 (성만)
- ✅ 현재 위치
- ✅ 배송 경로
- ✅ 업로드된 서류
- ❌ 기사 전화번호 (비공개)
- ❌ 상세 주소 (건물명만)
- ❌ 배차 비용 정보 (비공개)

---

## 📊 다음 단계

### 추가 개선 사항

1. **알림 기능**
   - ✉️ 이메일 알림 (출발/도착 시)
   - 📱 SMS 알림
   - 🔔 앱 푸시 알림

2. **지도 통합**
   - 🗺️ Kakao Map / Naver Map 연동
   - 📍 경로 시각화
   - 🚦 교통 상황 표시

3. **AI 예측**
   - ⏰ 정확한 도착 시간 예측
   - 🚧 지연 위험 알림

4. **통계 및 분석**
   - 📈 배송 완료율
   - ⭐ 고객 만족도
   - 📊 평균 배송 시간

---

## 🎯 테스트

### 1. 추적 번호 생성 테스트
```bash
# 추적 번호 생성
TRACKING=$(curl -X POST http://139.150.11.99/api/v1/dispatch/tracking/generate \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dispatch_id":123}' | jq -r '.tracking_number')

echo "추적 번호: $TRACKING"
echo "추적 URL: http://139.150.11.99/track/$TRACKING"
```

### 2. 공개 추적 테스트
```bash
# 브라우저로 열기 (인증 불필요)
xdg-open "http://139.150.11.99/track/$TRACKING"
```

### 3. 서류 업로드 테스트
```bash
# 출발 서류 업로드
curl -X POST http://139.150.11.99/api/v1/dispatch/documents/upload \
  -H "Authorization: Bearer $DRIVER_TOKEN" \
  -F "file=@test_document.pdf" \
  -F "dispatch_id=123" \
  -F "document_type=거래명세표" \
  -F "stage=출발"

# 공개 추적 페이지에서 서류 확인
```

---

## 📝 배포 완료

### 서버: 139.150.11.99

1. **데이터베이스**: ✅ 테이블 생성 완료
2. **백엔드 API**: ✅ 엔드포인트 추가 완료
3. **프론트엔드**: ⏳ 빌드 및 배포 필요

### 배포 명령어
```bash
cd /root/uvis

# 백엔드 재시작 (새 API 적용)
docker compose restart backend

# 프론트엔드 빌드 및 재시작
docker compose build frontend
docker compose up -d frontend
```

---

## 💡 사용 시나리오

### 시나리오 1: 동원F&B 배송

1. **배차 생성**: 동원 이천 → 동원 대전
2. **추적 번호 생성**: `TRK-20260311-A3F5B2C1`
3. **고객 전달**: 동원F&B 담당자에게 URL 전송
4. **출발**: 기사님이 거래명세표 촬영/업로드
5. **실시간 추적**: 동원F&B에서 실시간 위치 확인
6. **도착**: 기사님이 도착 서류 업로드
7. **서류 확인**: 동원F&B에서 서류 다운로드

### 시나리오 2: 외부 용차

1. **외부 차량 등록**: 1회성 용차 정보 입력
2. **임시 기사 계정**: 외부 기사 앱 로그인
3. **배차 할당**: 외부 차량에 배차 할당
4. **추적 시작**: GPS 자동 전송
5. **고객 추적**: 동일한 추적 페이지 사용
6. **서류 업로드**: 외부 기사도 서류 업로드

---

## ✅ 완료!

실시간 배송 추적 시스템이 구현되었습니다.
고객사는 이제 로그인 없이 실시간으로 배송 위치를 확인하고 서류를 다운로드할 수 있습니다.

**공개 추적 URL 형식:**
```
http://139.150.11.99/track/TRK-YYYYMMDD-XXXXXXXX
```
