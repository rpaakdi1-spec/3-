# UI 깨짐 원인 분석

## 🔴 문제 원인

### 명령어 분석
```bash
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/
```

이 명령은 `dist/` 내부의 **모든 파일과 폴더**를 복사하지만, **문제점**이 있습니다:

### ❌ 문제 1: 점(.) 사용의 함정
- `dist/.` 는 dist 내부의 모든 내용을 의미
- 하지만 **숨김 파일**이나 **디렉토리 구조**가 제대로 복사 안될 수 있음
- **기존 파일 덮어쓰기** 방식이라 일부 파일만 업데이트되고 나머지는 남아있을 수 있음

### ❌ 문제 2: 파일 권한
- Docker cp는 파일 권한을 유지하지만, 소유권은 root로 변경될 수 있음
- Nginx는 보통 nginx 또는 www-data 사용자로 실행
- 권한 불일치로 CSS/JS 로딩 실패 가능

### ❌ 문제 3: 혼합된 파일 상태
- 이전 빌드의 오래된 파일 + 새 빌드의 파일이 섞임
- index.html은 새 asset을 참조하는데, 실제로는 이전 asset이 남아있을 수 있음
- 특히 파일명이 해시로 된 경우 (예: `index-C4lYGKXx.js` → `index-ABC123.js`) 문제 발생

## ✅ 올바른 방법

### 방법 1: 디렉토리 완전 교체
```bash
# 기존 html 삭제하고 새로 복사
docker exec uvis-frontend rm -rf /usr/share/nginx/html/*
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/
```

### 방법 2: 백업 후 교체
```bash
# 백업
docker exec uvis-frontend mv /usr/share/nginx/html /usr/share/nginx/html.old

# 새 디렉토리 생성 후 복사
docker exec uvis-frontend mkdir -p /usr/share/nginx/html
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/

# Nginx 재시작
docker exec uvis-frontend nginx -s reload
```

### 방법 3: Docker 이미지 재빌드 (가장 안전)
```bash
cd /root/uvis
docker-compose build uvis-frontend
docker-compose up -d uvis-frontend
```

## 🔍 현재 상태 확인 방법

```bash
# 1. index.html의 asset 참조 확인
docker exec uvis-frontend grep -o 'src="/assets/[^"]*"' /usr/share/nginx/html/index.html | head -5

# 2. 실제 assets 디렉토리 파일 확인
docker exec uvis-frontend ls /usr/share/nginx/html/assets/*.js | head -5

# 3. CSS 파일 존재 여부
docker exec uvis-frontend ls /usr/share/nginx/html/assets/*.css
```

## 📋 복구 절차

1. **백업에서 복원** (UI가 완전히 망가진 경우)
2. **전체 디렉토리 교체** (파일 섞임 방지)
3. **권한 수정** (필요시)
4. **Nginx 재시작**
5. **브라우저 캐시 삭제**
6. **테스트**
