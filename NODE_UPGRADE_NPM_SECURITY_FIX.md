# Node.js 업그레이드 + npm 보안 수정 가이드

**작성일**: 2026-02-07  
**목표**: Node.js v18 → v20 업그레이드 + npm 보안 취약점 수정  
**예상 소요 시간**: 2-3시간  
**위험도**: 중간 (롤백 계획 포함)

---

## 📋 사전 체크리스트

### 1. 현재 환경 확인
```bash
# 프로덕션 서버에서 실행
cd /root/uvis

# Node.js 버전 확인
node --version
# 예상: v18.x.x

# npm 버전 확인
npm --version
# 예상: v9.x.x 또는 v10.x.x

# 프로젝트 Node.js 버전 확인
cat frontend/package.json | grep -A 2 '"engines"'

# 현재 설치된 패키지 확인
cd frontend
npm list --depth=0

# 보안 취약점 확인
npm audit
```

**예상 출력**:
```
found X vulnerabilities (Y low, Z moderate, W high, V critical)
```

---

## 🚀 Step 1: 백업 생성 (필수!)

### A. 프로젝트 전체 백업
```bash
cd /root
tar -czf uvis-backup-$(date +%Y%m%d-%H%M%S).tar.gz uvis/
ls -lh uvis-backup-*.tar.gz
```

### B. package.json 백업
```bash
cd /root/uvis/frontend
cp package.json package.json.backup
cp package-lock.json package-lock.json.backup
```

### C. Docker 이미지 백업
```bash
docker save uvis-frontend:latest > /root/uvis-frontend-backup.tar
docker images | grep uvis
```

---

## 🔧 Step 2: Node.js v20 업그레이드

### A. NodeSource 저장소 추가 (CentOS/RHEL)
```bash
# 현재 NodeSource 저장소 제거
sudo yum remove -y nodejs

# Node.js v20.x 저장소 추가
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -

# 설치 가능한 버전 확인
yum list available nodejs
```

### B. Node.js v20 설치
```bash
# Node.js v20 설치
sudo yum install -y nodejs

# 설치 확인
node --version
# 예상: v20.x.x (예: v20.11.0)

npm --version
# 예상: v10.x.x (예: v10.2.4)
```

### C. 글로벌 패키지 재설치 (필요시)
```bash
# 글로벌 패키지 목록 확인
npm list -g --depth=0

# 필요한 글로벌 패키지 재설치
npm install -g pm2 typescript
```

---

## 🔐 Step 3: npm 보안 취약점 수정

### A. npm 자체 업그레이드
```bash
cd /root/uvis/frontend

# npm을 최신 버전으로 업그레이드
sudo npm install -g npm@latest

# 버전 확인
npm --version
# 예상: v10.x.x
```

### B. 보안 감사 실행
```bash
cd /root/uvis/frontend

# 보안 취약점 상세 확인
npm audit

# 취약점 요약
npm audit --summary

# JSON 형식으로 출력 (분석용)
npm audit --json > npm-audit-before.json
```

### C. 자동 수정 시도
```bash
# 비파괴적 수정 (권장)
npm audit fix

# 수정 후 확인
npm audit

# 여전히 취약점이 남아있다면...
```

### D. 강제 수정 (주의: Breaking Changes 가능)
```bash
# ⚠️ 주의: 이 명령은 major 버전 업그레이드를 포함할 수 있음
npm audit fix --force

# 수정 후 확인
npm audit

# 비교
npm audit --json > npm-audit-after.json
```

### E. 수동 수정 (권장)
특정 패키지에 문제가 있는 경우:

```bash
# 1. 취약점 상세 확인
npm audit

# 예시 출력:
# lodash  <4.17.21
# Severity: high
# Prototype Pollution
# fix available via `npm update lodash`

# 2. 특정 패키지 업데이트
npm update lodash

# 3. 또는 최신 버전으로 직접 설치
npm install lodash@latest

# 4. package.json 확인
cat package.json | grep lodash
```

---

## 📦 Step 4: 프로젝트 의존성 업데이트

### A. 오래된 패키지 확인
```bash
cd /root/uvis/frontend

# 업데이트 가능한 패키지 확인
npm outdated

# 예상 출력:
# Package    Current  Wanted  Latest  Location
# react      18.2.0   18.2.0  18.3.1  frontend
# vite       4.5.0    4.5.3   5.0.11  frontend
```

### B. 안전한 업데이트 (Patch/Minor)
```bash
# package.json의 버전 범위 내에서 업데이트
npm update

# 변경사항 확인
git diff package.json package-lock.json
```

### C. 메이저 버전 업데이트 (선택적)
```bash
# 특정 패키지 메이저 업데이트 (주의!)
# npm install <package>@latest

# 예: React 18.3.x로 업데이트 (안전)
npm install react@latest react-dom@latest

# 예: Vite 5로 업데이트 (주의: breaking changes)
# npm install vite@latest
```

---

## 🧪 Step 5: 프로젝트 테스트

### A. 의존성 재설치
```bash
cd /root/uvis/frontend

# node_modules 삭제
rm -rf node_modules

# package-lock.json 삭제 (선택적)
# rm package-lock.json

# 클린 설치
npm ci  # 또는 npm install
```

### B. 빌드 테스트
```bash
cd /root/uvis/frontend

# 프로덕션 빌드
npm run build

# 빌드 성공 확인
ls -lh dist/
```

**예상 출력**:
```
✓ built in 12.49s
dist/index.html
dist/assets/...
```

### C. 로컬 개발 서버 테스트 (선택적)
```bash
# 개발 서버 시작
npm run dev

# 브라우저에서 확인
# http://localhost:5173/
```

---

## 🐳 Step 6: Docker 이미지 재빌드

### A. Dockerfile 확인
```bash
cd /root/uvis/frontend
cat Dockerfile
```

**Dockerfile 내용 확인**:
```dockerfile
FROM node:18-alpine as builder  # ← 이 부분을 v20으로 변경 고려
# ...
```

### B. Dockerfile 업데이트 (선택적)
```bash
# Node.js 20-alpine으로 변경
sed -i 's/node:18-alpine/node:20-alpine/g' Dockerfile

# 변경 확인
cat Dockerfile | grep "FROM node"
```

### C. Docker 이미지 재빌드
```bash
cd /root/uvis

# 프론트엔드 이미지 재빌드
docker-compose build --no-cache frontend

# 빌드 확인
docker images | grep uvis-frontend
```

---

## 🚀 Step 7: 프로덕션 배포

### A. 컨테이너 재시작
```bash
cd /root/uvis

# 프론트엔드 컨테이너 재시작
docker-compose up -d frontend

# 상태 확인
docker ps | grep uvis-frontend
```

### B. 로그 확인
```bash
# 프론트엔드 로그 확인
docker logs uvis-frontend --tail 50

# 에러 없이 시작되는지 확인
```

### C. 프로덕션 테스트
```bash
# 헬스 체크
curl http://139.150.11.99/

# 브라우저에서 확인
# http://139.150.11.99/
# 로그인: admin / admin123
```

---

## ✅ Step 8: 검증 체크리스트

### A. 버전 확인
```bash
# 서버 Node.js 버전
node --version  # v20.x.x

# Docker 내부 Node.js 버전
docker exec uvis-frontend node --version  # v20.x.x (Dockerfile 변경 시)

# npm 버전
npm --version  # v10.x.x
```

### B. 보안 감사 확인
```bash
cd /root/uvis/frontend
npm audit

# 예상 결과:
# found 0 vulnerabilities
# 또는
# found X vulnerabilities (only low/moderate, no high/critical)
```

### C. 애플리케이션 기능 테스트
```
□ 로그인 정상 동작
□ 대시보드 로드
□ Phase 8 페이지 모두 정상
  □ 재무 대시보드
  □ 요금 미리보기
  □ 자동 청구 스케줄
  □ 정산 승인
  □ 결제 알림
  □ 데이터 내보내기
□ 사이드바 정상 (항상 확장)
□ Console 오류 없음
```

---

## 🔄 Step 9: Git 커밋

### A. 변경사항 확인
```bash
cd /root/uvis
git status

# 예상 변경:
# modified: frontend/package.json
# modified: frontend/package-lock.json
# modified: frontend/Dockerfile (선택적)
```

### B. 커밋
```bash
git add frontend/package.json frontend/package-lock.json frontend/Dockerfile

git commit -m "chore: Upgrade Node.js to v20 and fix npm security vulnerabilities

**Node.js Upgrade**:
- Upgraded from v18.x.x to v20.x.x
- Updated npm to v10.x.x
- Installed via NodeSource repository

**npm Security Fixes**:
- Ran npm audit fix
- Fixed X vulnerabilities (Y low, Z moderate, W high)
- Updated outdated packages
- Remaining vulnerabilities: [count] (severity: low)

**Package Updates**:
- Updated critical dependencies
- Maintained compatibility with existing code
- Full rebuild and testing completed

**Docker**:
- Updated Dockerfile to use node:20-alpine (optional)
- Rebuilt frontend image
- Production deployment successful

**Testing**:
✅ Build successful (npm run build)
✅ All pages load correctly
✅ Phase 8 features working
✅ No console errors
✅ Production verified: http://139.150.11.99/

**Before**:
Node.js: v18.x.x
npm: v9.x.x
Vulnerabilities: [count before]

**After**:
Node.js: v20.x.x
npm: v10.x.x
Vulnerabilities: [count after] (reduction: [%]%)

Closes technical debt issue."
```

### C. 푸시
```bash
git push origin phase8-verification
```

---

## 🐛 문제 해결

### 문제 1: 빌드 실패
**증상**: `npm run build` 실패
```bash
Error: Module not found
```

**해결**:
```bash
# 1. node_modules 완전 삭제
rm -rf node_modules

# 2. 캐시 삭제
npm cache clean --force

# 3. 재설치
npm ci

# 4. 재빌드
npm run build
```

---

### 문제 2: 호환성 문제
**증상**: 특정 패키지가 Node.js v20과 호환되지 않음

**해결**:
```bash
# 1. 문제 패키지 확인
npm list <package-name>

# 2. 최신 버전으로 업데이트
npm install <package-name>@latest

# 3. 또는 호환 버전 찾기
npm view <package-name> versions

# 4. 특정 버전 설치
npm install <package-name>@<compatible-version>
```

---

### 문제 3: Docker 빌드 실패
**증상**: Docker 이미지 빌드 중 오류

**해결**:
```bash
# 1. 빌드 캐시 삭제
docker builder prune -a

# 2. 이미지 완전 삭제
docker rmi uvis-frontend

# 3. 재빌드
docker-compose build --no-cache frontend

# 4. 로그 확인
docker-compose logs frontend
```

---

### 문제 4: 프로덕션 배포 후 오류
**증상**: 페이지 로드 실패 또는 기능 오류

**해결**:
```bash
# 1. 롤백 (백업에서 복원)
cd /root
tar -xzf uvis-backup-YYYYMMDD-HHMMSS.tar.gz

# 2. 이전 이미지로 복원
docker load < /root/uvis-frontend-backup.tar

# 3. 컨테이너 재시작
cd /root/uvis
docker-compose restart frontend

# 4. 문제 분석
docker logs uvis-frontend --tail 100
```

---

## 📊 예상 결과

### Before (Node.js v18)
```
Node.js: v18.19.0
npm: v9.8.1
Vulnerabilities: 15 (3 low, 8 moderate, 3 high, 1 critical)
Build time: ~12s
```

### After (Node.js v20)
```
Node.js: v20.11.0
npm: v10.2.4
Vulnerabilities: 2 (2 low, 0 moderate, 0 high, 0 critical)
Build time: ~11s (약간 개선)
```

### 개선 사항
- ✅ Node.js v20 LTS 사용 (장기 지원)
- ✅ 최신 npm (성능 개선)
- ✅ 보안 취약점 87% 감소 (15 → 2)
- ✅ Critical/High 취약점 100% 제거
- ✅ 빌드 성능 약간 개선

---

## 📝 작업 후 보고서 템플릿

```markdown
### Node.js 업그레이드 + npm 보안 수정 완료

**작업 일시**: [YYYY-MM-DD HH:MM]
**소요 시간**: [N]시간

**업그레이드 내역**:
- Node.js: v18.x.x → v20.x.x
- npm: v9.x.x → v10.x.x

**보안 수정**:
- 수정 전 취약점: [N]개 ([low/moderate/high/critical] 분포)
- 수정 후 취약점: [N]개 ([low/moderate/high/critical] 분포)
- 감소율: [%]%

**패키지 업데이트**:
- 업데이트된 패키지: [N]개
- 주요 업데이트:
  - [package-name]: v[old] → v[new]
  - [package-name]: v[old] → v[new]

**테스트 결과**:
- [ ] 빌드 성공: 예/아니오
- [ ] 프로덕션 배포: 성공/실패
- [ ] 기능 테스트: 통과/실패
- [ ] 성능: 개선/유지/저하

**문제 발생**:
- [문제가 있었다면 상세 설명]

**롤백 여부**:
- [ ] 롤백 필요 없음
- [ ] 롤백 실행함

**최종 상태**:
- [ ] ✅ 성공 - 프로덕션 정상 운영
- [ ] ⚠️ 부분 성공 - 일부 이슈 남음
- [ ] ❌ 실패 - 롤백 완료
```

---

## 🎯 체크리스트 요약

### 사전 준비
- [ ] 현재 버전 확인
- [ ] 보안 취약점 확인
- [ ] 백업 생성 (프로젝트 + Docker)

### 업그레이드
- [ ] Node.js v20 설치
- [ ] npm 최신 버전 설치
- [ ] 글로벌 패키지 재설치

### 보안 수정
- [ ] npm audit 실행
- [ ] npm audit fix 실행
- [ ] 남은 취약점 수동 수정

### 테스트
- [ ] 의존성 재설치 (npm ci)
- [ ] 빌드 테스트 (npm run build)
- [ ] Docker 재빌드
- [ ] 프로덕션 배포
- [ ] 기능 테스트

### 마무리
- [ ] 검증 완료
- [ ] Git 커밋 및 푸시
- [ ] 작업 보고서 작성

---

## 🚀 지금 바로 시작하세요!

### 빠른 시작 (한 줄 명령어)
```bash
# 1. 백업
cd /root && tar -czf uvis-backup-$(date +%Y%m%d-%H%M%S).tar.gz uvis/

# 2. Node.js 업그레이드
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash - && sudo yum install -y nodejs

# 3. npm 업데이트 및 보안 수정
cd /root/uvis/frontend && npm install -g npm@latest && npm audit fix

# 4. 빌드 및 배포
npm run build && cd /root/uvis && docker-compose build --no-cache frontend && docker-compose up -d frontend
```

---

**작성일**: 2026-02-07  
**문서**: `NODE_UPGRADE_NPM_SECURITY_FIX.md`  
**예상 소요**: 2-3시간  
**상태**: 즉시 실행 가능 ✅
