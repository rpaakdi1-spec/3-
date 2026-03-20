# 🚀 실시간 배송 추적 시스템 배포 가이드

## ✅ 완료 사항

### Git Push 완료
- **Branch**: `genspark_ai_developer`
- **Commit**: `e0613c3`
- **Repository**: https://github.com/rpaakdi1-spec/3-

### 구현 완료
1. ✅ 백엔드 API 및 데이터베이스
2. ✅ 공개 추적 페이지 (프론트엔드)
3. ✅ 서류 업로드 시스템
4. ✅ 외부 용차 지원

---

## 📦 서버 배포 (139.150.11.99)

### 1단계: 코드 업데이트

```bash
cd /root/uvis

# 최신 코드 pull
git pull origin genspark_ai_developer

# 백엔드 재시작 (새 API 반영)
docker compose restart backend

# 로그 확인
docker compose logs backend --tail=50
```

### 2단계: 프론트엔드 빌드

```bash
cd /root/uvis

# 프론트엔드 재빌드 (새 페이지 반영)
docker compose build frontend

# 재시작
docker compose up -d frontend

# 상태 확인
docker compose ps
```

### 3단계: 데이터베이스 확인

테이블이 이미 생성되어 있습니다:
```bash
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT tablename FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename LIKE 'dispatch_%' 
ORDER BY tablename;
"
```

예상 출력:
```
dispatch_documents
dispatch_routes  
dispatch_tracking
dispatches
```

---

## 🧪 테스트

### 1. 추적 번호 생성 테스트

```bash
# 관리자 토큰으로 추적 번호 생성
curl -X POST http://139.150.11.99/api/v1/dispatch/tracking/generate \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dispatch_id": 1,
    "customer_name": "테스트 고객사",
    "customer_email": "test@example.com",
    "expires_days": 7
  }'
```

예상 응답:
```json
{
  "id": 1,
  "dispatch_id": 1,
  "tracking_number": "TRK-20260311-A3F5B2C1",
  "is_active": true,
  "customer_name": "테스트 고객사",
  "customer_email": "test@example.com",
  "view_count": 0,
  "created_at": "2026-03-11T..."
}
```

### 2. 공개 추적 페이지 테스트

브라우저에서 접속 (로그인 불필요):
```
http://139.150.11.99/track/TRK-20260311-A3F5B2C1
```

확인 사항:
- ✅ 페이지가 정상 로드
- ✅ 배차 정보 표시
- ✅ 진행률 표시
- ✅ 경로 목록 표시
- ✅ 30초 자동 새로고침

### 3. 서류 업로드 테스트

```bash
# 테스트 PDF 파일 생성
echo "Test Document" > test_document.txt
# (실제로는 PDF나 이미지 파일 사용)

# 서류 업로드
curl -X POST http://139.150.11.99/api/v1/dispatch/documents/upload \
  -H "Authorization: Bearer YOUR_DRIVER_TOKEN" \
  -F "file=@test_document.txt" \
  -F "dispatch_id=1" \
  -F "document_type=거래명세표" \
  -F "stage=출발" \
  -F "notes=출발 시 거래명세표"
```

### 4. 공개 추적에서 서류 확인

다시 추적 페이지 접속:
```
http://139.150.11.99/track/TRK-20260311-A3F5B2C1
```

"배송 서류" 섹션에서:
- ✅ 업로드된 서류 목록 표시
- ✅ 다운로드 아이콘 클릭 시 파일 다운로드

---

## 📱 프론트엔드 통합

### 배차 페이지에 추적 번호 생성 버튼 추가

`frontend/src/pages/DispatchesPage.tsx` 수정:

```typescript
import { Share2, Link } from 'lucide-react';
import apiClient from '../api/client';

// 추적 번호 생성 함수
const handleGenerateTracking = async (dispatch: Dispatch) => {
  try {
    const response = await apiClient.post('/dispatch/tracking/generate', {
      dispatch_id: dispatch.id,
      customer_name: dispatch.client_name,
      expires_days: 7
    });
    
    const trackingNumber = response.data.tracking_number;
    const trackingUrl = `http://139.150.11.99/track/${trackingNumber}`;
    
    // 클립보드에 복사
    await navigator.clipboard.writeText(trackingUrl);
    
    toast.success(
      `추적 URL이 복사되었습니다!\n${trackingUrl}`,
      { duration: 5000 }
    );
    
    // 또는 공유 기능 사용 (모바일)
    if (navigator.share) {
      await navigator.share({
        title: '배송 추적',
        text: `${dispatch.client_name} 배송을 실시간으로 확인하세요`,
        url: trackingUrl
      });
    }
  } catch (error: any) {
    if (error.response?.status === 409) {
      toast.error('이미 추적 번호가 생성되었습니다.');
    } else {
      toast.error('추적 번호 생성 실패');
    }
  }
};

// 배차 테이블에 버튼 추가
<td>
  <div className="flex items-center gap-2">
    {/* 기존 버튼들 */}
    <button
      onClick={() => handleGenerateTracking(dispatch)}
      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
      title="추적 번호 생성"
    >
      <Share2 className="w-5 h-5" />
    </button>
  </div>
</td>
```

---

## 🚗 외부 용차 (1회성 차량) 지원

### 시나리오: 외부 용차 배송 추적

1. **외부 차량 등록**
   ```sql
   INSERT INTO vehicles (vehicle_number, vehicle_type, status)
   VALUES ('외부12가3456', '외부용차', 'ACTIVE');
   ```

2. **임시 기사 계정 생성**
   ```sql
   INSERT INTO users (username, password, role, full_name)
   VALUES ('temp_driver', 'temp_password', 'DRIVER', '외부기사');
   ```

3. **배차 할당**
   - 관리자가 외부 차량에 배차 할당
   - 외부 기사에게 배차 정보 전달

4. **GPS 추적**
   - 외부 기사가 기사 앱 설치 및 로그인
   - 앱이 자동으로 GPS 위치 전송
   - `vehicle_locations` 테이블에 저장

5. **추적 번호 생성 및 공유**
   ```bash
   # 추적 번호 생성
   curl -X POST http://139.150.11.99/api/v1/dispatch/tracking/generate \
     -H "Authorization: Bearer ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "dispatch_id": 456,
       "customer_name": "고객사명",
       "expires_days": 7
     }'
   
   # 고객사에 URL 전송
   # http://139.150.11.99/track/TRK-20260311-XXXXXXXX
   ```

6. **서류 업로드**
   - 외부 기사도 동일하게 출발/도착 시 서류 업로드
   - 고객사가 추적 페이지에서 다운로드

---

## 📊 데이터베이스 스키마

### dispatch_documents 테이블

```sql
CREATE TABLE dispatch_documents (
    id SERIAL PRIMARY KEY,
    dispatch_id INTEGER NOT NULL REFERENCES dispatches(id) ON DELETE CASCADE,
    route_id INTEGER REFERENCES dispatch_routes(id) ON DELETE CASCADE,
    order_id INTEGER REFERENCES orders(id) ON DELETE SET NULL,
    document_type VARCHAR(50) NOT NULL,  -- 거래명세표, 온도기록지, 서명
    stage VARCHAR(50) NOT NULL,           -- 출발, 도착, 운송중
    file_url VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    uploaded_at_location VARCHAR(500),
    uploaded_lat FLOAT,
    uploaded_lon FLOAT,
    notes TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    verified_at TIMESTAMP,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### dispatch_tracking 테이블

```sql
CREATE TABLE dispatch_tracking (
    id SERIAL PRIMARY KEY,
    dispatch_id INTEGER NOT NULL UNIQUE REFERENCES dispatches(id) ON DELETE CASCADE,
    tracking_number VARCHAR(50) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP,
    customer_name VARCHAR(200),
    customer_email VARCHAR(255),
    customer_phone VARCHAR(20),
    notify_on_departure BOOLEAN DEFAULT TRUE,
    notify_on_arrival BOOLEAN DEFAULT TRUE,
    notify_on_document_upload BOOLEAN DEFAULT TRUE,
    view_count INTEGER DEFAULT 0,
    last_viewed_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔍 모니터링 및 디버깅

### 추적 번호 조회

```bash
# 모든 추적 번호 조회
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT 
    tracking_number,
    dispatch_id,
    customer_name,
    is_active,
    view_count,
    created_at
FROM dispatch_tracking
ORDER BY created_at DESC
LIMIT 10;
"
```

### 업로드된 서류 조회

```bash
# 최근 업로드된 서류
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT 
    id,
    dispatch_id,
    document_type,
    stage,
    file_name,
    uploaded_at_location,
    created_at
FROM dispatch_documents
ORDER BY created_at DESC
LIMIT 10;
"
```

### API 로그 확인

```bash
# 추적 API 호출 로그
docker compose logs backend --tail=100 | grep "tracking/public"

# 서류 업로드 로그
docker compose logs backend --tail=100 | grep "documents/upload"
```

---

## 🎯 다음 단계

### 1. 알림 시스템 추가

출발/도착 시 고객에게 자동 알림:

```python
# backend/app/services/notification_service.py
async def notify_tracking_event(tracking: DispatchTracking, event: str):
    """배송 이벤트 알림"""
    if event == 'departure' and tracking.notify_on_departure:
        send_email(
            to=tracking.customer_email,
            subject='배송이 시작되었습니다',
            body=f'추적 URL: http://139.150.11.99/track/{tracking.tracking_number}'
        )
    elif event == 'arrival' and tracking.notify_on_arrival:
        send_email(
            to=tracking.customer_email,
            subject='배송이 완료되었습니다',
            body=f'서류 확인: http://139.150.11.99/track/{tracking.tracking_number}'
        )
```

### 2. 지도 통합

Kakao Map 또는 Naver Map 연동:

```typescript
// frontend/src/pages/PublicTrackingPage.tsx
import { Map, MapMarker, Polyline } from 'react-kakao-maps-sdk';

<Map center={{ lat: center[0], lng: center[1] }} level={3}>
  {/* 현재 위치 */}
  {currentLocation && (
    <MapMarker position={{ lat: currentLocation.latitude, lng: currentLocation.longitude }}>
      <div className="p-2">차량 위치</div>
    </MapMarker>
  )}
  
  {/* 경로 */}
  <Polyline
    path={routeCoordinates.map(([lat, lng]) => ({ lat, lng }))}
    strokeWeight={5}
    strokeColor="#007bff"
  />
</Map>
```

### 3. 모바일 앱 개선

React Native 기사 앱에 서류 업로드 기능 추가:

```typescript
// mobile/src/screens/DispatchDetailScreen.tsx
import { launchCamera } from 'react-native-image-picker';

const uploadDocument = async (stage: 'departure' | 'arrival') => {
  const result = await launchCamera({ mediaType: 'photo' });
  
  if (result.assets?.[0]) {
    const formData = new FormData();
    formData.append('file', {
      uri: result.assets[0].uri,
      type: 'image/jpeg',
      name: 'document.jpg',
    });
    formData.append('dispatch_id', dispatch.id);
    formData.append('document_type', '거래명세표');
    formData.append('stage', stage === 'departure' ? '출발' : '도착');
    
    await apiClient.post('/dispatch/documents/upload', formData);
    Alert.alert('성공', '서류가 업로드되었습니다.');
  }
};
```

---

## ✅ 배포 체크리스트

서버 139.150.11.99에서 다음 명령 실행:

```bash
cd /root/uvis

# ✅ 1. 코드 업데이트
git pull origin genspark_ai_developer

# ✅ 2. 백엔드 재시작
docker compose restart backend
sleep 5
docker compose logs backend --tail=20

# ✅ 3. 프론트엔드 빌드
docker compose build frontend
docker compose up -d frontend
docker compose logs frontend --tail=20

# ✅ 4. 상태 확인
docker compose ps

# ✅ 5. 테이블 확인
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT COUNT(*) FROM dispatch_documents;
SELECT COUNT(*) FROM dispatch_tracking;
"

# ✅ 6. API 테스트
curl http://139.150.11.99/api/v1/health
```

---

## 📞 문의사항

구현된 기능:
- ✅ 실시간 GPS 추적 (기사 핸드폰 기반)
- ✅ 고객사 전용 추적 페이지 (로그인 불필요)
- ✅ 서류 업로드 (거래명세표, 온도기록지, 서명)
- ✅ 외부 용차 지원 (1회성 차량)

추가 개발 필요 시:
- 이메일/SMS 알림
- 지도 통합 (Kakao/Naver)
- 모바일 앱 UI 개선
- AI 도착 시간 예측

---

## 🎉 완료!

실시간 배송 추적 시스템이 완전히 구현되었습니다!

**공개 추적 URL:**
```
http://139.150.11.99/track/{추적번호}
```

고객사는 이제 로그인 없이 실시간으로:
- 🚚 차량 위치 확인
- 📊 배송 진행률 확인
- 📄 서류 다운로드

가능합니다!
