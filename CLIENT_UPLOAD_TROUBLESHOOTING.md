# 🔍 거래처 관리 엑셀 업로드 문제 해결 가이드

## 📋 발견된 문제

### 증상
```
Failed to load resource: the server responded with a status of 401 (Unauthorized)
Error fetching AB test stats: AxiosError: Request failed with status code 401
api/v1/dispatches?status=%EC%A7%84%ED%96%89%EC%A4%91:1 Failed to load resource: 502 (Bad Gateway)
```

### 문제 분석

1. **401 Unauthorized**: 
   - ABTest 모니터링 엔드포인트 인증 실패 (부수적 문제)
   - 거래처 업로드 시 401 발생 가능성

2. **502 Bad Gateway**:
   - Backend 서버 연결 문제
   - 일부 API 엔드포인트가 응답하지 않음

3. **Insecure connection warning**:
   - HTTP 사용 (HTTPS 아님) - 무시 가능한 경고

---

## 🔧 진단 및 해결

### 1단계: 문제 진단

```bash
cd /root/uvis
git fetch origin main
git reset --hard origin/main

# 진단 스크립트 실행
./diagnose_client_upload.sh
```

**진단 스크립트가 확인하는 것**:
- ✅ Backend health 상태
- ✅ 거래처 API 엔드포인트 접근 가능 여부
- ✅ 업로드 엔드포인트 테스트
- ✅ 401/502 에러 원인 파악
- ✅ CORS 설정 확인

### 2단계: 백엔드 재시작

**502 Bad Gateway 해결**:
```bash
cd /root/uvis
docker-compose -f docker-compose.prod.yml restart backend
sleep 30
curl http://localhost:8000/health
```

**예상 결과**:
```json
{"status": "healthy"}
```

### 3단계: 코드 동기화 (필요 시)

만약 API 코드가 업데이트되지 않은 경우:
```bash
cd /root/uvis
./rebuild_backend_auto.sh
```

---

## 🎯 거래처 업로드 API 상세

### 엔드포인트
```
POST /api/v1/clients/upload?auto_geocode=true
Content-Type: multipart/form-data
```

### 파라미터
- **file** (required): Excel 파일 (.xlsx, .xls)
- **auto_geocode** (optional): 자동 지오코딩 여부 (default: true)

### 응답 예시

**성공 (200 OK)**:
```json
{
  "created": 5,
  "failed": 0,
  "errors": []
}
```

**실패 (400 Bad Request)**:
```json
{
  "detail": "엑셀 파일만 업로드 가능합니다"
}
```

**인증 실패 (401 Unauthorized)**:
```json
{
  "detail": "Unauthorized"
}
```

---

## 🔍 401 에러 원인 및 해결

### 가능한 원인

1. **인증 미들웨어 활성화**
   - 일부 엔드포인트에 인증이 필요할 수 있음
   - `/clients/upload`가 인증 필요 엔드포인트일 가능성

2. **CORS 문제**
   - Frontend (http://139.150.11.99)에서 Backend (http://localhost:8000) 호출 시 CORS 에러

3. **토큰 만료**
   - 사용자 세션 토큰이 만료됨

### 해결 방법

#### A. 인증 미들웨어 확인

```bash
cd /root/uvis
docker exec uvis-backend cat /app/app/main.py | grep -A 20 "middleware\|auth"
```

**예상되는 미들웨어**:
- `SecurityHeadersMiddleware`
- `RateLimitMiddleware`
- `CORSMiddleware`

#### B. CORS 설정 확인

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://139.150.11.99", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### C. 엔드포인트 인증 제거 (필요 시)

만약 `/clients/upload`에 인증이 필요하지 않다면:

```python
# backend/app/api/clients.py
@router.post("/upload")
async def upload_clients_excel(
    file: UploadFile = File(...),
    auto_geocode: bool = Query(True),
    db: Session = Depends(get_db)
):
    # 인증 Dependency 제거됨
    ...
```

---

## 🔧 빠른 해결 방법

### 옵션 1: 백엔드 재시작 (가장 빠름)

```bash
cd /root/uvis
docker-compose -f docker-compose.prod.yml restart backend
sleep 30
```

### 옵션 2: 브라우저 캐시 삭제

1. 브라우저에서 `Ctrl + Shift + Delete`
2. 캐시 및 쿠키 삭제
3. 페이지 새로고침 (`Ctrl + Shift + R`)

### 옵션 3: 로그아웃 후 재로그인

1. 현재 세션 종료
2. 다시 로그인
3. 거래처 업로드 재시도

---

## 🧪 테스트 방법

### 1. API 직접 테스트

```bash
# 템플릿 다운로드 테스트
curl -o /tmp/template.xlsx http://localhost:8000/api/v1/clients/template/download
file /tmp/template.xlsx

# 업로드 테스트 (CSV로 간단 테스트)
cat > /tmp/test.csv << 'EOF'
거래처코드,거래처명,거래처구분,주소
TEST001,테스트거래처,BOTH,서울시 강남구
EOF

curl -X POST "http://localhost:8000/api/v1/clients/upload?auto_geocode=false" \
  -F "file=@/tmp/test.csv" \
  -H "Content-Type: multipart/form-data"
```

### 2. 브라우저에서 테스트

1. http://139.150.11.99/clients 접속
2. **엑셀 업로드** 버튼 클릭
3. 템플릿 다운로드
4. 샘플 데이터 입력
5. 업로드 시도

**예상 동작**:
- ✅ 파일 선택 가능
- ✅ 업로드 진행 표시
- ✅ 성공 메시지 표시
- ✅ 거래처 목록 갱신

---

## 📊 로그 분석

### 백엔드 로그 확인

```bash
# 최근 에러 확인
docker logs uvis-backend --tail 200 | grep -E "ERROR|401|Unauthorized|upload"

# 실시간 로그 모니터링
docker logs uvis-backend -f --tail 50
```

**정상 로그**:
```
INFO - Uploaded clients: 5 created, 0 failed
INFO - Created client: TEST001
```

**에러 로그 예시**:
```
ERROR - Error uploading clients: [상세 에러 메시지]
WARNING - ❌ 지오코딩 실패: TEST001 - 테스트거래처: [에러]
```

---

## 🔗 관련 파일

| 파일 | 설명 |
|-----|-----|
| `backend/app/api/clients.py` | 거래처 API 엔드포인트 |
| `backend/app/services/excel_upload_service.py` | 엑셀 업로드 서비스 |
| `frontend/src/components/ClientUpload.tsx` | 업로드 UI 컴포넌트 |
| `frontend/src/services/api.ts` | API 호출 함수 |
| `diagnose_client_upload.sh` | 진단 스크립트 |

---

## ✅ 문제 해결 체크리스트

진단 및 해결 순서:

- [ ] 1. **백엔드 헬스 체크**: `curl http://localhost:8000/health`
- [ ] 2. **진단 스크립트 실행**: `./diagnose_client_upload.sh`
- [ ] 3. **401 에러 확인**: 로그에서 인증 관련 에러 찾기
- [ ] 4. **502 에러 해결**: 백엔드 재시작
- [ ] 5. **브라우저 테스트**: 실제 파일 업로드 시도
- [ ] 6. **로그 확인**: 업로드 성공/실패 메시지 확인
- [ ] 7. **DB 확인**: 거래처가 실제로 생성되었는지 확인

---

## 🚀 즉시 실행 명령어

```bash
cd /root/uvis
git fetch origin main
git reset --hard origin/main

# 진단 실행
./diagnose_client_upload.sh

# 문제가 있으면 백엔드 재시작
docker-compose -f docker-compose.prod.yml restart backend
sleep 30

# 재진단
./diagnose_client_upload.sh
```

---

## 📞 추가 지원

문제가 계속되면 다음 정보 공유:

1. **진단 스크립트 출력 전체**
2. **백엔드 로그**:
   ```bash
   docker logs uvis-backend --tail 200 > backend_logs.txt
   ```
3. **브라우저 콘솔 에러** (F12 → Console 탭)
4. **Network 탭에서 실패한 요청** (Request/Response 헤더 포함)

**GitHub**: https://github.com/rpaakdi1-spec/3-  
**최신 커밋**: 7d12c97
