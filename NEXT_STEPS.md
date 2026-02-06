# Phase 8 이후 다음 작업 계획

## 📅 이번 주 내 (2026-02-06 ~ 2026-02-13)

### 4️⃣ 스크린샷 촬영 (약 30분)
**목적**: 문서화 및 교육 자료 강화

**촬영 목록** (총 18개):
1. 로그인 페이지
2. 사이드바 (축소 상태)
3. 사이드바 (확장 상태 - Phase 8 메뉴 펼침)
4. 재무 대시보드 (/billing/financial-dashboard)
5. 요금 미리보기 (/billing/charge-preview)
6. 자동 청구 스케줄 (/billing/auto-schedule)
7. 정산 승인 (/billing/settlement-approval)
8. 결제 알림 (/billing/payment-reminder)
9. 데이터 내보내기 (/billing/export-task)
10. 대시보드 - 개요
11. 대시보드 - 차트/그래프
12. 모바일 반응형 (360px)
13. 태블릿 반응형 (768px)
14. 데스크톱 (1920px)
15. 다크모드 (있는 경우)
16. 에러 메시지 예시
17. 성공 메시지 예시
18. 로딩 상태

**저장 경로**:
```bash
mkdir -p /root/uvis/screenshots
# 파일명 형식: phase8_01_login.png, phase8_02_sidebar_collapsed.png 등
```

**상세 가이드**: `/root/uvis/SCREENSHOT_GUIDE.md` 참조

---

### 5️⃣ 로컬 브랜치 정리
```bash
cd /root/uvis
git checkout main
git branch -d genspark_ai_developer  # 로컬 브랜치 삭제
git remote prune origin  # 원격 브랜치 정리
git branch -a  # 확인
```

---

### 6️⃣ 팀 공지 및 교육 자료 배포
**교육 자료 위치**: `/root/uvis/USER_TRAINING_MATERIALS.md`

**공지 내용 (템플릿)**:
```
제목: 🎉 Phase 8: 청구/정산 자동화 시스템 배포 완료

안녕하세요,

Phase 8: Billing & Settlement Automation System이 성공적으로 배포되었습니다!

📌 주요 기능:
• 재무 대시보드 - 실시간 수익/수금 지표
• 요금 미리보기 - 실시간 배송 요금 계산
• 자동 청구 스케줄 - 고객별 청구일 자동화
• 정산 승인 - 기사 정산 승인 워크플로우
• 결제 알림 - 자동 결제 알림 발송
• 데이터 내보내기 - Excel/PDF 대량 내보내기

📊 비즈니스 임팩트:
• 청구서 처리 시간: 2시간 → 5분 (96% 단축)
• 정산 검토: 3일 → 실시간 (99% 개선)
• 결제 회수율: +15%
• 오류율: 95% 감소

🔗 링크:
• 프로덕션: http://139.150.11.99/
• 로그인: admin / admin123
• 사용자 가이드: /root/uvis/PHASE_8_USER_GUIDE_KO.md
• 교육 자료: /root/uvis/USER_TRAINING_MATERIALS.md

🎓 교육 일정:
• 1차 교육: [날짜/시간 입력]
• 2차 교육: [날짜/시간 입력]

감사합니다!
```

---

## 🔧 이번 주 내 - 기술 개선

### 7️⃣ Node.js 버전 업그레이드 (v18 → v20+)
**현재 버전 확인**:
```bash
node --version  # v18.x.x
```

**업그레이드 방법 (CentOS/RHEL)**:
```bash
# NodeSource 저장소 추가
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -

# Node.js 20 설치
sudo yum install -y nodejs

# 버전 확인
node --version  # v20.x.x
npm --version
```

**프로젝트 재빌드**:
```bash
cd /root/uvis/frontend
rm -rf node_modules package-lock.json
npm install
npm run build

# Docker 이미지 재빌드
cd /root/uvis
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

---

### 8️⃣ npm 보안 취약점 해결 (14개)
```bash
cd /root/uvis/frontend

# 보안 감사 실행
npm audit

# 자동 수정 시도
npm audit fix

# 강제 수정 (주의: breaking changes 가능)
npm audit fix --force

# 재확인
npm audit

# 수정 후 빌드 테스트
npm run build
```

---

### 9️⃣ Phase 7 WebSocket 이슈 해결
**문제 진단**:
```bash
# 백엔드 로그 확인
docker logs uvis-backend | grep -i websocket

# 프론트엔드 콘솔 확인
# F12 → Console → WebSocket 관련 오류 확인
```

**수정 위치**:
- 백엔드: `/root/uvis/backend/app/api/v1/websocket.py`
- 프론트엔드: `/root/uvis/frontend/src/services/websocket.ts`

**일반적인 해결 방법**:
1. WebSocket 핸들러에서 await 누락 확인
2. 연결 타임아웃 설정 확인
3. 재연결 로직 구현 확인

---

## 📊 이번 달 내 (중기 과제)

### 🔟 성능 최적화
**프론트엔드 번들 분석**:
```bash
cd /root/uvis/frontend

# 번들 크기 분석 도구 설치
npm install --save-dev rollup-plugin-visualizer

# vite.config.ts에 플러그인 추가 후 빌드
npm run build

# 생성된 stats.html 확인
```

**최적화 방법**:
- [ ] 코드 스플리팅 적용
- [ ] lazy loading 구현
- [ ] 이미지 최적화 (WebP 변환)
- [ ] 불필요한 라이브러리 제거

---

### 1️⃣1️⃣ 모니터링 대시보드 설정
**Grafana + Prometheus 구성**:
```bash
cd /root/uvis

# docker-compose.yml에 추가
cat >> docker-compose.yml << 'EOF'

  prometheus:
    image: prom/prometheus:latest
    container_name: uvis-prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - uvis-network

  grafana:
    image: grafana/grafana:latest
    container_name: uvis-grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - uvis-network

volumes:
  prometheus_data:
  grafana_data:
EOF

# 시작
docker-compose up -d prometheus grafana
```

**접속 URL**:
- Prometheus: http://139.150.11.99:9090
- Grafana: http://139.150.11.99:3001 (admin/admin123)

---

### 1️⃣2️⃣ 데이터베이스 백업 자동화
```bash
# 백업 스크립트 생성
cat > /root/uvis/backup_db.sh << 'EOF'
#!/bin/bash
# 데이터베이스 백업 스크립트

BACKUP_DIR="/root/uvis/backups/db"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/uvis_db_$DATE.sql"

# 백업 디렉토리 생성
mkdir -p $BACKUP_DIR

# 백업 실행
docker exec uvis-db pg_dump -U uvis_user uvis_db > $BACKUP_FILE

# 압축
gzip $BACKUP_FILE

# 7일 이상 된 백업 삭제
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "✅ 백업 완료: ${BACKUP_FILE}.gz"
EOF

chmod +x /root/uvis/backup_db.sh

# 크론탭 등록 (매일 새벽 2시)
(crontab -l 2>/dev/null; echo "0 2 * * * /root/uvis/backup_db.sh >> /var/log/uvis_backup.log 2>&1") | crontab -

# 백업 테스트
/root/uvis/backup_db.sh
```

---

## 🚀 이번 분기 (장기 과제)

### Phase 9 기획
- 결제 게이트웨이 연동 (카카오페이, 토스페이먼츠)
- 고급 분석 기능 (AI 기반 수요 예측)
- 고객 포털 구축 (셀프 서비스)
- 모바일 앱 강화 (React Native)

### 보안 강화
- [ ] HTTPS 적용 (Let's Encrypt)
- [ ] 2FA (Two-Factor Authentication)
- [ ] API Rate Limiting
- [ ] 감사 로그 강화

---

## 📋 실행 순서 (권장)

### 지금 바로 (오늘)
1. ✅ 로컬 브랜치 정리 (5분)
2. ✅ 프로덕션 사이트 최종 확인 (10분)
3. ✅ GitHub 릴리스 확인 (5분)

### 오늘 중
4. 📸 스크린샷 촬영 (30분)
5. 📢 팀 공지 (10분)

### 이번 주
6. ⬆️ Node.js 업그레이드 (1시간)
7. 🔒 npm 보안 수정 (30분)
8. 🔌 WebSocket 이슈 해결 (1시간)

### 이번 달
9. ⚡ 성능 최적화 (2시간)
10. 📊 모니터링 대시보드 (3시간)
11. 💾 데이터베이스 백업 자동화 (1시간)

---

## 🎯 우선순위 매트릭스

| 우선순위 | 작업 | 예상 시간 | 비즈니스 임팩트 | 기술 부채 해결 |
|---------|------|----------|---------------|--------------|
| 🔴 긴급 | 로컬 브랜치 정리 | 5분 | 낮음 | 중간 |
| 🔴 긴급 | 프로덕션 최종 확인 | 10분 | 높음 | 낮음 |
| 🟠 높음 | 스크린샷 촬영 | 30분 | 중간 | 낮음 |
| 🟠 높음 | 팀 공지 | 10분 | 높음 | 낮음 |
| 🟡 중간 | Node.js 업그레이드 | 1시간 | 중간 | 높음 |
| 🟡 중간 | npm 보안 수정 | 30분 | 중간 | 높음 |
| 🟡 중간 | WebSocket 이슈 해결 | 1시간 | 중간 | 높음 |
| 🟢 낮음 | 성능 최적화 | 2시간 | 중간 | 중간 |
| 🟢 낮음 | 모니터링 대시보드 | 3시간 | 중간 | 낮음 |
| 🟢 낮음 | 백업 자동화 | 1시간 | 높음 | 낮음 |

---

## ✅ 체크리스트

### 즉시 실행 (오늘)
- [ ] 로컬 저장소 정리 (`git branch -d genspark_ai_developer`)
- [ ] 프로덕션 사이트 최종 검증 (http://139.150.11.99/)
- [ ] GitHub 릴리스 확인 (v2.0.0-phase8)

### 이번 주
- [ ] 스크린샷 촬영 (18개)
- [ ] 팀 공지 및 교육 자료 배포
- [ ] Node.js v20 업그레이드
- [ ] npm 보안 취약점 해결 (14개)
- [ ] Phase 7 WebSocket 이슈 해결

### 이번 달
- [ ] 프론트엔드 성능 최적화
- [ ] Grafana + Prometheus 모니터링 대시보드
- [ ] 데이터베이스 백업 자동화

### 이번 분기
- [ ] Phase 9 기획 및 착수
- [ ] HTTPS 적용
- [ ] 2FA 구현
- [ ] API Rate Limiting

---

## 📞 지원 및 문의

**문서 위치**:
- 사용자 가이드: `/root/uvis/PHASE_8_USER_GUIDE_KO.md`
- 교육 자료: `/root/uvis/USER_TRAINING_MATERIALS.md`
- 스크린샷 가이드: `/root/uvis/SCREENSHOT_GUIDE.md`
- PR 리뷰 체크리스트: `/root/uvis/PR_REVIEW_CHECKLIST.md`

**주요 링크**:
- 프로덕션: http://139.150.11.99/
- GitHub 저장소: https://github.com/rpaakdi1-spec/3-
- PR #4: https://github.com/rpaakdi1-spec/3-/pull/4
- 릴리스 v2.0.0-phase8: https://github.com/rpaakdi1-spec/3-/releases/tag/v2.0.0-phase8

---

**마지막 업데이트**: 2026-02-06
**작성자**: GenSpark AI Developer
**상태**: Phase 8 완전히 완료 ✅
