# 🚀 규칙 타입 수정 배포 가이드

## 📋 수정 내용
규칙 관리 페이지의 수정 모달에서 **규칙 타입(assignment/constraint/optimization)이 변경되지 않는 문제**를 수정했습니다.

## ⚡ 서버 배포 방법

### 방법 1: 빌드된 파일 직접 배포 (권장)

빌드된 파일이 준비되어 있습니다: `/tmp/frontend-dist-fix.tar.gz` (526KB)

#### 1️⃣ 서버에 파일 업로드

```bash
# 로컬에서 서버로 파일 전송
scp /tmp/frontend-dist-fix.tar.gz root@139.150.11.99:/tmp/

# 또는 서버에서 직접 다운로드 (파일을 공유 저장소에 업로드한 경우)
# ssh root@139.150.11.99
# cd /tmp && wget [파일_URL]
```

#### 2️⃣ 서버에서 배포

```bash
# 서버에 SSH 접속
ssh root@139.150.11.99

# 백업 생성
cd /root/uvis/frontend
tar -czf dist-backup-$(date +%Y%m%d_%H%M%S).tar.gz dist/

# 기존 dist 폴더 삭제
rm -rf dist/

# 새 빌드 파일 압축 해제
mkdir -p dist
cd dist
tar -xzf /tmp/frontend-dist-fix.tar.gz

# 파일 확인
ls -la

# Docker 컨테이너 재시작
cd /root/uvis
docker-compose restart frontend

# 또는 컨테이너가 없으면 새로 빌드
docker-compose up -d --build frontend

# 배포 확인
docker-compose ps
curl -I http://localhost:80
```

#### 3️⃣ 브라우저 캐시 삭제

배포 후 반드시 브라우저 캐시를 삭제해야 합니다:

**Chrome/Edge:**
1. F12 → Network 탭
2. "Disable cache" 체크
3. Ctrl + F5 (강력 새로고침)

**또는:**
1. Ctrl + Shift + Delete
2. "전체 기간" 선택
3. "캐시된 이미지 및 파일" 체크
4. 삭제 후 브라우저 완전 종료
5. 브라우저 재시작 후 http://139.150.11.99 접속

**가장 확실한 방법:**
- 시크릿 모드 (Ctrl + Shift + N)에서 http://139.150.11.99 접속

---

### 방법 2: 서버에서 직접 빌드

#### 1️⃣ Git에서 최신 코드 받기

```bash
# 서버에 SSH 접속
ssh root@139.150.11.99

cd /root/uvis

# 최신 코드 가져오기
git fetch origin genspark_ai_developer
git checkout genspark_ai_developer
git pull origin genspark_ai_developer

# 또는 main 브랜치 (PR 병합 후)
# git checkout main
# git pull origin main
```

#### 2️⃣ 빌드 및 배포

```bash
cd /root/uvis/frontend

# 기존 dist 백업
tar -czf dist-backup-$(date +%Y%m%d_%H%M%S).tar.gz dist/

# 새로 빌드
rm -rf dist/
npm run build

# 빌드 결과 확인
ls -lh dist/
ls -lh dist/assets/*.js | grep DispatchRulesPage

# Docker 컨테이너 재시작
cd /root/uvis
docker-compose restart frontend

# 배포 확인
docker-compose ps
docker-compose logs frontend --tail=50
```

---

## 🔍 배포 검증

### 1. 규칙 관리 페이지 접속
```
http://139.150.11.99/dispatch-rules
```

### 2. 규칙 수정 테스트
1. 기존 규칙의 **수정 버튼** 클릭
2. **규칙 타입** 드롭다운 클릭
3. 다른 타입 선택 (예: assignment → constraint)
4. **수정** 버튼 클릭
5. 규칙이 수정되고 타입이 변경되었는지 확인

### 3. API 확인
```bash
# 규칙 목록 조회
curl http://139.150.11.99/api/v1/dispatch-rules

# 특정 규칙 조회
curl http://139.150.11.99/api/v1/dispatch-rules/1

# 규칙 타입 변경 테스트
curl -X PUT http://139.150.11.99/api/v1/dispatch-rules/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "테스트 규칙",
    "rule_type": "constraint",
    "priority": 50,
    "conditions": {},
    "actions": {}
  }'
```

---

## 📦 변경된 파일

```
frontend/src/pages/DispatchRulesPage.tsx
  - handleUpdate 함수에서 rule_type을 포함하도록 수정
  - 77-82줄: rule_type exclusion 로직 제거
```

### 변경 전:
```typescript
const { rule_type, ...updatePayload } = formData;
await DispatchRulesAPI.update(editingRuleId, updatePayload);
```

### 변경 후:
```typescript
await DispatchRulesAPI.update(editingRuleId, formData);
```

---

## ⚠️ 주의사항

1. **백업 필수**: 배포 전 기존 dist 폴더 백업
2. **브라우저 캐시**: 배포 후 반드시 캐시 삭제
3. **Docker 재시작**: 파일 변경 후 컨테이너 재시작 필수
4. **시크릿 모드 테스트**: 캐시 없이 정상 동작 확인

---

## 🔗 관련 링크

- **PR**: https://github.com/rpaakdi1-spec/3-/pull/12
- **커밋**: deddabe
- **빌드 파일**: /tmp/frontend-dist-fix.tar.gz (526KB)

---

## ✅ 체크리스트

배포 전:
- [ ] Git에서 최신 코드 확인
- [ ] 기존 dist 폴더 백업
- [ ] 빌드 성공 확인

배포 후:
- [ ] Docker 컨테이너 정상 실행 확인
- [ ] 브라우저 캐시 삭제
- [ ] 시크릿 모드에서 규칙 수정 테스트
- [ ] 규칙 타입 변경 정상 동작 확인

---

**배포 준비 완료!** ✅

문제가 발생하면 백업으로 복구:
```bash
cd /root/uvis/frontend
rm -rf dist/
tar -xzf dist-backup-[날짜].tar.gz
docker-compose restart frontend
```
