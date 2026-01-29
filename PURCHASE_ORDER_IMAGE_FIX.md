# 발주서 이미지 표시 문제 해결 가이드

## 📋 문제 요약
발주서 작성 시 이미지를 업로드했으나 미리보기 또는 상세보기에서 이미지가 보이지 않는 문제

## 🔍 원인 분석

### 1. 가능한 원인들
1. **이미지 경로 문제**
   - 백엔드 API가 반환하는 경로: `/uploads/purchase_orders/파일명.jpg`
   - 프론트엔드가 잘못된 경로 사용: `//uploads/...` 또는 잘못된 base URL

2. **CORS 문제**
   - 백엔드와 프론트엔드가 다른 포트에서 실행
   - 이미지 요청이 CORS 정책에 의해 차단

3. **파일 권한 문제**
   - 업로드된 파일의 읽기 권한 없음
   - 디렉토리 권한 문제

4. **캐싱 문제**
   - 브라우저가 이전 버전을 캐싱
   - 서버 재시작 후 경로 변경

## ✅ 적용된 해결 방법

### 1. 이미지 로딩 상태 추적
```typescript
<img
  src={url}  // ✅ 올바른 경로 사용 (추가 슬래시 없음)
  onLoad={() => console.log('✅ 이미지 로딩 성공:', url)}
  onError={(e) => {
    console.error('❌ 이미지 로딩 실패:', url);
    console.error('  - 전체 URL:', window.location.origin + url);
    // 에러 메시지 표시
  }}
/>
```

### 2. 시각적 에러 메시지
이미지 로딩 실패 시:
- 🔴 빨간색 테두리 박스 표시
- ⚠️ 경고 아이콘과 메시지
- 실패한 이미지 URL 표시

### 3. 디버깅 정보 강화
- 콘솔에 성공/실패 로그 명확히 표시
- 전체 URL 경로 출력
- 에러 발생 시점과 이유 추적

## 🛠️ 문제 해결 체크리스트

### 백엔드 확인
```bash
# 1. 이미지 파일 존재 확인
ls -la /home/user/webapp/backend/uploads/purchase_orders/

# 2. 파일 권한 확인
ls -l /home/user/webapp/backend/uploads/purchase_orders/*.jpg

# 3. 백엔드에서 이미지 접근 테스트
curl -I http://localhost:8000/uploads/purchase_orders/파일명.jpg
# ✅ 200 OK가 나와야 함

# 4. API 응답 확인
curl http://localhost:8000/api/v1/purchase-orders/ID | python3 -m json.tool
# image_urls가 ["/uploads/purchase_orders/파일명.jpg"] 형식이어야 함
```

### 프론트엔드 확인
```bash
# 1. 프록시를 통한 이미지 접근 테스트
curl -I http://localhost:3000/uploads/purchase_orders/파일명.jpg
# ✅ 200 OK가 나와야 함

# 2. Vite 프록시 설정 확인
cat /home/user/webapp/frontend/vite.config.ts
# /uploads 경로가 http://localhost:8000으로 프록시되어야 함
```

### 브라우저 확인
1. **개발자 도구 > Console 확인**
   - "✅ 이미지 로딩 성공" 메시지가 나오면 정상
   - "❌ 이미지 로딩 실패" 메시지가 나오면 URL 확인

2. **개발자 도구 > Network 탭**
   - 이미지 요청의 Status Code 확인
   - 200: 정상
   - 404: 파일 없음
   - 403: 권한 없음
   - CORS 에러: 프록시 설정 문제

3. **강력 새로고침**
   - Windows/Linux: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

## 📊 테스트 결과

### 테스트 케이스 1: 실제 이미지 업로드
```bash
# 발주서 ID 6, 7 생성 완료
# 이미지: /uploads/purchase_orders/20260121_095538_KakaoTalk_20260116_164253166.jpg
# 이미지: /uploads/purchase_orders/test_image_small.jpg
```

**결과:**
- ✅ 백엔드에서 이미지 정상 제공 (200 OK)
- ✅ 프론트엔드 프록시를 통해 이미지 접근 가능
- ✅ API 응답에 올바른 경로 포함
- ✅ 브라우저에서 이미지 로딩 가능

### 테스트 케이스 2: 다중 이미지 업로드
- ✅ 최대 5개 이미지 업로드 제한 작동
- ✅ 각 이미지 개별 삭제 가능
- ✅ 미리보기 그리드 정상 표시

## 🔧 추가 개선 사항

### 1. 이미지 업로드 검증
```typescript
// 파일 크기 제한 (10MB)
if (imageFile.size > 10 * 1024 * 1024) {
  alert('이미지 크기는 10MB 이하여야 합니다.');
  return;
}

// 이미지 타입 확인
if (!imageFile.type.startsWith('image/')) {
  alert('이미지 파일만 업로드 가능합니다.');
  return;
}
```

### 2. 로딩 상태 표시
```typescript
{uploadingImage && (
  <div style={{ padding: '10px', backgroundColor: '#e3f2fd' }}>
    ⏳ 이미지 업로드 중...
  </div>
)}
```

### 3. 이미지 미리보기 개선
- ✅ 150x150px 그리드 레이아웃
- ✅ 개별 삭제 버튼 (빨간색 × )
- ✅ 업로드 개수 표시 (2/5개)
- ✅ 5개 도달 시 업로드 버튼 비활성화

## 📝 사용자 가이드

### 이미지 업로드 방법
1. 발주서 작성 폼에서 "파일 선택" 클릭
2. 이미지 파일 선택 (JPG, PNG 등)
3. "📤 업로드" 버튼 클릭
4. 미리보기에서 이미지 확인
5. 최대 5개까지 반복 가능
6. 불필요한 이미지는 × 버튼으로 삭제

### 이미지가 보이지 않을 때
1. **콘솔 확인**
   - F12 키를 눌러 개발자 도구 열기
   - Console 탭에서 에러 메시지 확인
   - "❌ 이미지 로딩 실패" 메시지와 URL 확인

2. **강력 새로고침**
   - Ctrl + Shift + R (Windows/Linux)
   - Cmd + Shift + R (Mac)

3. **시크릿 모드 테스트**
   - 시크릿/프라이빗 브라우징 모드에서 확인
   - 캐시 문제인지 확인

4. **관리자에게 문의**
   - 콘솔 에러 메시지 캡처
   - Network 탭 스크린샷 제공
   - 발주서 ID와 이미지 파일명 전달

## 🚀 배포 및 적용

### 변경 파일
- `frontend/src/components/PurchaseOrders.tsx` - 이미지 로딩 에러 핸들링 개선

### 커밋 정보
- **브랜치**: `genspark_ai_developer`
- **커밋 ID**: `4b94e7e`
- **커밋 메시지**: "fix(purchase-orders): 이미지 로딩 상태 개선 및 에러 핸들링 강화"

### 적용 방법
```bash
# 프론트엔드 재시작
cd /home/user/webapp/frontend
npm run dev -- --port 3000 --host 0.0.0.0
```

## 📊 기대 효과

### 이전
- ❌ 이미지 로딩 실패 시 아무 표시 없음
- ❌ 문제 원인 파악 어려움
- ❌ 사용자가 이미지가 업로드되었는지 확인 불가

### 현재
- ✅ 이미지 로딩 성공/실패 명확히 표시
- ✅ 콘솔에서 즉시 문제 확인 가능
- ✅ 시각적 에러 메시지로 사용자 인지
- ✅ 전체 URL 경로로 디버깅 용이

## 🔐 보안 고려사항

### 파일 업로드 보안
- ✅ 파일 타입 검증 (image/* only)
- ✅ 파일명 타임스탬프 추가 (충돌 방지)
- ✅ 업로드 디렉토리 외부 접근 차단
- ⚠️ 권장: 파일 크기 제한 추가 (10MB)
- ⚠️ 권장: 악성 파일 스캔 추가

## 📚 관련 문서
- [공지사항 이미지 표시 문제 해결](./NOTICE_IMAGE_FINAL_FIX.md)
- [발주서 작성 오류 해결](./PURCHASE_ORDER_FIX.md)
- [네이버밴드 메시지 시스템](./BAND_MESSAGE_SYSTEM.md)

---

**작성일**: 2026-01-23  
**작성자**: GenSpark AI Developer  
**상태**: ✅ 완료
