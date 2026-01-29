# 공지사항 이미지 표시 문제 해결 가이드

## 📋 문제 상황
공지사항에 업로드한 이미지가 웹 페이지에서 표시되지 않는 문제

## 🔍 원인 분석

### 1. **이미지 경로 문제**
프론트엔드에서 이미지 URL을 잘못 참조하고 있습니다.

**현재 코드 (NoticeBoard.tsx):**
```typescript
// 라인 306: 이미지 미리보기
<img src={`/${formData.image_url}`} alt="Preview" />

// 라인 392: 상세보기 모달
<img src={`/${selectedNotice.image_url}`} alt="공지사항 이미지" />
```

**문제점:**
- 백엔드에서 반환하는 `image_url`은 이미 `/uploads/notices/파일명` 형식입니다
- 프론트엔드에서 추가로 `/`를 앞에 붙이면 `//uploads/notices/파일명`이 되어 잘못된 경로가 됩니다

### 2. **정적 파일 마운트 확인**
**main.py (라인 130-132):**
```python
UPLOAD_DIR = Path("/home/user/webapp/backend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
```

✅ 정적 파일 마운트는 올바르게 설정되어 있습니다.

### 3. **이미지 저장 경로 확인**
**notices.py (라인 17-18):**
```python
UPLOAD_DIR = Path("/home/user/webapp/backend/uploads/notices")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
```

✅ 업로드 디렉토리는 올바르게 설정되어 있습니다.

## ✅ 해결 방법

### 방법 1: 프론트엔드 코드 수정 (권장)

**NoticeBoard.tsx 파일 수정:**

1. **이미지 미리보기 부분 (라인 303-311):**
```typescript
// 수정 전
{formData.image_url && (
  <div style={{ marginTop: '10px' }}>
    <img
      src={`/${formData.image_url}`}  // ❌ 잘못된 경로
      alt="Preview"
      style={{ maxWidth: '200px', borderRadius: '4px', border: '1px solid #ddd' }}
    />
  </div>
)}

// 수정 후
{formData.image_url && (
  <div style={{ marginTop: '10px' }}>
    <img
      src={formData.image_url}  // ✅ 올바른 경로
      alt="Preview"
      style={{ maxWidth: '200px', borderRadius: '4px', border: '1px solid #ddd' }}
    />
  </div>
)}
```

2. **상세보기 모달 이미지 부분 (라인 390-396):**
```typescript
// 수정 전
{selectedNotice.image_url && (
  <img
    src={`/${selectedNotice.image_url}`}  // ❌ 잘못된 경로
    alt="공지사항 이미지"
    style={{ maxWidth: '100%', marginBottom: '20px', borderRadius: '4px' }}
  />
)}

// 수정 후
{selectedNotice.image_url && (
  <img
    src={selectedNotice.image_url}  // ✅ 올바른 경로
    alt="공지사항 이미지"
    style={{ maxWidth: '100%', marginBottom: '20px', borderRadius: '4px' }}
  />
)}
```

### 방법 2: 이미지 URL 헬퍼 함수 사용 (더 안전한 방법)

```typescript
// NoticeBoard.tsx 상단에 추가
const getImageUrl = (imageUrl?: string): string => {
  if (!imageUrl) return '';
  
  // 이미 절대 경로로 시작하면 그대로 반환
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl;
  }
  
  // 슬래시로 시작하면 그대로, 아니면 추가
  return imageUrl.startsWith('/') ? imageUrl : `/${imageUrl}`;
};

// 사용 예시
<img src={getImageUrl(formData.image_url)} alt="Preview" />
<img src={getImageUrl(selectedNotice.image_url)} alt="공지사항 이미지" />
```

## 🔧 수정 적용 방법

### 1. 파일 수정
```bash
cd /home/user/webapp/frontend
# NoticeBoard.tsx 파일을 편집기로 열어 위의 수정사항 적용
```

### 2. 변경사항 확인
프론트엔드를 재시작하여 변경사항 적용:
```bash
cd /home/user/webapp/frontend
npm run dev
```

### 3. 브라우저에서 테스트
1. 공지사항 작성 페이지에서 이미지 업로드
2. 미리보기가 정상적으로 표시되는지 확인
3. 공지사항 저장 후 상세보기에서 이미지가 표시되는지 확인

## 🧪 디버깅 방법

### 1. 업로드된 파일 확인
```bash
# 업로드 디렉토리 확인
ls -la /home/user/webapp/backend/uploads/notices/

# 파일 권한 확인
ls -l /home/user/webapp/backend/uploads/notices/*
```

### 2. API 응답 확인
브라우저 개발자 도구(F12)에서:
- Network 탭 열기
- 이미지 업로드 시 응답 확인
- 반환된 `image_url` 값 확인 (예: `/uploads/notices/20240121_120000_image.jpg`)

### 3. 이미지 URL 직접 접근
브라우저 주소창에 직접 입력:
```
http://localhost:3000/uploads/notices/파일명.jpg
```

이미지가 표시되면 정적 파일 서빙은 정상이고, 프론트엔드 경로 문제입니다.

## 📝 추가 확인 사항

### 1. CORS 설정 확인
이미지가 다른 도메인에서 로드되는 경우 CORS 오류가 발생할 수 있습니다.

**main.py 확인:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. 파일 권한 확인
```bash
# 업로드 디렉토리 권한 확인
ls -ld /home/user/webapp/backend/uploads/notices/

# 필요시 권한 수정
chmod 755 /home/user/webapp/backend/uploads/notices/
chmod 644 /home/user/webapp/backend/uploads/notices/*
```

### 3. 프록시 설정 확인 (개발 환경)
Vite를 사용하는 경우 `vite.config.ts` 확인:

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/uploads': {  // 이 부분이 필요할 수 있음
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

## 🎯 빠른 해결 체크리스트

- [ ] NoticeBoard.tsx에서 이미지 src에 불필요한 `/` 제거
- [ ] 브라우저 캐시 클리어 (Ctrl + Shift + R)
- [ ] 프론트엔드 서버 재시작
- [ ] 백엔드 서버 재시작
- [ ] 업로드 디렉토리 권한 확인
- [ ] 브라우저 개발자 도구에서 네트워크 오류 확인
- [ ] 이미지 URL을 직접 브라우저에서 접근하여 테스트

## 🚀 예방 조치

### 1. 환경별 베이스 URL 관리
```typescript
// src/config.ts
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// 사용
const imageUrl = `${API_BASE_URL}${formData.image_url}`;
```

### 2. 이미지 로딩 오류 처리
```typescript
<img
  src={formData.image_url}
  alt="Preview"
  onError={(e) => {
    console.error('이미지 로딩 실패:', formData.image_url);
    e.currentTarget.src = '/placeholder-image.png'; // 대체 이미지
  }}
/>
```

### 3. 이미지 업로드 실패 처리 강화
```typescript
const handleImageUpload = async () => {
  if (!imageFile) return;

  setUploadingImage(true);
  try {
    const formData = new FormData();
    formData.append('file', imageFile);

    const response = await fetch('/api/v1/notices/upload-image/', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`업로드 실패: ${response.status}`);
    }

    const data = await response.json();
    
    // URL 검증
    if (!data.image_url) {
      throw new Error('이미지 URL을 받지 못했습니다');
    }
    
    console.log('업로드된 이미지 URL:', data.image_url);
    setFormData(prev => ({ ...prev, image_url: data.image_url }));
    alert('이미지가 업로드되었습니다!');
    setImageFile(null);
  } catch (error) {
    console.error('이미지 업로드 실패:', error);
    alert(`이미지 업로드에 실패했습니다: ${error.message}`);
  } finally {
    setUploadingImage(false);
  }
};
```

## 📞 추가 지원

문제가 계속되면 다음 정보를 함께 제공해주세요:
1. 브라우저 콘솔의 오류 메시지
2. Network 탭의 실패한 요청 상세 정보
3. 업로드 시도한 이미지 파일 형식 및 크기
4. 백엔드 로그 (`logs/app.log`)

---

**작성일**: 2026-01-21
**버전**: 1.0
