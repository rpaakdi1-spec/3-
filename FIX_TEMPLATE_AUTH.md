# Template Management 401 Error 해결 가이드

## 문제 상황
- 템플릿 관리 페이지에서 즐겨찾기, 활성화, 복사, 삭제 등의 기능 사용 시 401 Unauthorized 오류 발생
- Network 탭에서 PUT/POST/DELETE 요청의 **Authorization 헤더가 누락**됨
- 콘솔에서 직접 fetch 테스트 시에는 정상 작동

## 원인 분석
브라우저가 **이전 빌드의 JavaScript 파일을 캐시**하고 있어서, Authorization 헤더를 추가하는 최신 코드가 실행되지 않음

## 해결 방법

### 1단계: Nginx 캐시 설정 확인 및 수정

```bash
cd /root/uvis

# 현재 nginx 설정 확인
docker compose exec frontend cat /etc/nginx/conf.d/default.conf

# 캐시 방지 설정 추가
cat > frontend/nginx.conf <<'EOF'
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # API 프록시
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # React 앱 - 캐시 방지 설정 추가
    location / {
        try_files $uri $uri/ /index.html;
        
        # HTML과 JS 파일은 캐시하지 않음 (매번 최신 버전 요청)
        location ~* \.(html|js|json)$ {
            add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0";
            add_header Pragma "no-cache";
            add_header Expires "0";
            etag off;
        }
        
        # CSS, 이미지 등 정적 자원은 짧은 캐시
        location ~* \.(css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            add_header Cache-Control "public, max-age=3600";
        }
    }

    # 추가 보안 헤더
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
EOF

echo "✅ Nginx 설정 파일 생성 완료"
```

### 2단계: Dockerfile에 nginx 설정 복사 추가

```bash
cd /root/uvis

# frontend Dockerfile 확인 및 수정
cat > /tmp/fix_dockerfile.py <<'PYTHON'
#!/usr/bin/env python3
import re

dockerfile_path = "frontend/Dockerfile"

with open(dockerfile_path, 'r', encoding='utf-8') as f:
    content = f.read()

# nginx 설정 복사 라인 추가 (아직 없다면)
if 'COPY nginx.conf' not in content:
    # COPY --from=build 라인 찾기
    pattern = r'(COPY --from=build /app/dist /usr/share/nginx/html)'
    
    if re.search(pattern, content):
        replacement = r'\1\n\n# Copy custom nginx configuration\nCOPY nginx.conf /etc/nginx/conf.d/default.conf'
        content = re.sub(pattern, replacement, content)
        
        with open(dockerfile_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print('✅ Dockerfile에 nginx 설정 복사 라인 추가 완료')
    else:
        print('⚠️ Dockerfile 수정 필요: COPY --from=build 라인을 찾을 수 없습니다')
else:
    print('✅ Dockerfile에 이미 nginx 설정이 포함되어 있습니다')

PYTHON

python3 /tmp/fix_dockerfile.py
```

### 3단계: 프론트엔드 완전 재빌드 (캐시 없이)

```bash
cd /root/uvis

echo "=== 1. 기존 이미지 및 컨테이너 제거 ==="
docker compose stop frontend
docker compose rm -f frontend
docker rmi uvis-frontend 2>/dev/null || true

echo ""
echo "=== 2. 완전 재빌드 (--no-cache) ==="
docker compose build --no-cache frontend

echo ""
echo "=== 3. 컨테이너 재시작 ==="
docker compose up -d frontend

echo ""
echo "=== 4. 상태 확인 ==="
docker compose ps frontend
docker compose logs frontend --tail=20

echo ""
echo "✅ 프론트엔드 재배포 완료"
```

### 4단계: 브라우저 캐시 완전 제거

#### 방법 A: 개발자 도구 사용 (권장)
1. **F12**를 눌러 개발자 도구 열기
2. **Network** 탭 클릭
3. **Disable cache** 체크박스 활성화
4. **개발자 도구를 연 상태**에서 **Ctrl + Shift + R** (강력 새로고침)

#### 방법 B: 브라우저 설정에서 캐시 삭제
1. **Ctrl + Shift + Delete** 눌러 기록 삭제 창 열기
2. **쿠키 및 기타 사이트 데이터** 체크
3. **캐시된 이미지 및 파일** 체크
4. 기간: **전체 기간** 선택
5. **데이터 삭제** 클릭

#### 방법 C: 시크릿 모드 (가장 확실)
1. **Ctrl + Shift + N** (Chrome) 또는 **Ctrl + Shift + P** (Firefox)
2. 시크릿 창에서 `http://139.150.11.99` 접속
3. 로그인 후 템플릿 관리 페이지 테스트

### 5단계: 로그아웃 & 재로그인

```javascript
// 브라우저 콘솔(F12)에서 실행
localStorage.clear();
sessionStorage.clear();
location.href = '/login';
```

로그인 후 템플릿 관리 페이지로 이동: `http://139.150.11.99/template-management`

### 6단계: Authorization 헤더 확인

1. **F12** → **Network** 탭 열기
2. 템플릿 즐겨찾기 아이콘 ⭐ 클릭
3. `templates/40` PUT 요청 찾기
4. **Request Headers** 확인:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

✅ **Authorization 헤더가 있으면** → 정상
❌ **Authorization 헤더가 없으면** → 4단계(브라우저 캐시 삭제) 다시 실행

### 7단계: 기능 테스트

- [ ] ⭐ **즐겨찾기 추가/제거** → 토스트 메시지, 별 색상 변경
- [ ] ⚡ **활성화/비활성화** → 토스트 메시지, "비활성" 배지 표시
- [ ] 📋 **템플릿 복제** → 토스트 메시지, "(복사본)" 템플릿 생성
- [ ] 🗑️ **템플릿 삭제** → 확인 다이얼로그, 삭제 후 목록에서 제거
- [ ] 🔍 **검색** → 템플릿명/고객명으로 필터링
- [ ] 🎛️ **고객 필터** → 드롭다운에서 고객 선택
- [ ] 📊 **정렬** → 최신순/사용횟수/이름순 변경

### 8단계: DB에서 변경사항 확인

```bash
cd /root/uvis

# 즐겨찾기 테스트 후 확인
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT id, name, is_favorite, is_active, updated_at 
FROM dispatch_form_templates 
ORDER BY updated_at DESC 
LIMIT 5;
"

# 전체 템플릿 개수 확인
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT COUNT(*) as total FROM dispatch_form_templates;
"

# 복사본 확인
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT id, name, created_at 
FROM dispatch_form_templates 
WHERE name LIKE '%(복사본)%' 
ORDER BY created_at DESC;
"
```

## 트러블슈팅

### 여전히 401 오류 발생 시

#### 1. 토큰 만료 시간 확인
```bash
cd /root/uvis
grep "ACCESS_TOKEN_EXPIRE" .env
# 출력: ACCESS_TOKEN_EXPIRE_MINUTES=1440 (24시간)
```

#### 2. 백엔드 로그 확인
```bash
docker compose logs backend --tail=50 | grep "dispatch-form/templates"
```

#### 3. 프론트엔드 빌드 로그 확인
```bash
docker compose logs frontend --tail=30
```

#### 4. API 직접 테스트 (서버에서)
```bash
# 토큰 획득 (브라우저 콘솔에서 복사)
TOKEN="eyJhbGciOiJIUzI1NiIsInR..."

# GET 테스트
curl -H "Authorization: Bearer $TOKEN" \
  http://139.150.11.99/api/v1/dispatch-form/templates

# PUT 테스트 (즐겨찾기)
curl -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_favorite": true}' \
  http://139.150.11.99/api/v1/dispatch-form/templates/40
```

## 최종 체크리스트

- [x] nginx 캐시 방지 설정 추가
- [x] frontend Dockerfile 수정
- [x] 프론트엔드 완전 재빌드 (--no-cache)
- [x] 컨테이너 재시작
- [ ] 브라우저 캐시 완전 삭제 (시크릿 모드 권장)
- [ ] 로그아웃 & 재로그인
- [ ] Network 탭에서 Authorization 헤더 확인
- [ ] 모든 기능 테스트 (즐겨찾기, 활성화, 복제, 삭제)
- [ ] DB에서 변경사항 확인

## 예상 결과

✅ **성공 시**:
```
Network 탭:
PUT http://139.150.11.99/api/v1/dispatch-form/templates/40
Status: 200 OK
Request Headers:
  Authorization: Bearer eyJhbGci...
  Content-Type: application/json
Response: {"id":40,"name":"도미노 백암 → 밀양","is_favorite":true,...}
```

❌ **실패 시**:
```
Network 탭:
PUT http://139.150.11.99/api/v1/dispatch-form/templates/40
Status: 401 Unauthorized
Request Headers:
  ❌ Authorization 헤더 없음
```

## 문의사항

문제가 해결되지 않으면 다음 정보를 제공해주세요:
1. Network 탭 스크린샷 (Request Headers 부분)
2. 브라우저 콘솔 에러 메시지
3. 백엔드 로그 최근 30줄
4. 사용 중인 브라우저 및 버전
