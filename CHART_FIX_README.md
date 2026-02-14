# 🚨 재무 대시보드 차트 미표시 문제 - 빠른 해결

## ⚡ 가장 빠른 해결 방법 (한 줄 명령)

서버에서 이 명령만 실행하세요:

```bash
cd /root/uvis && ./fix_charts_all_in_one.sh
```

**소요 시간:** 5-10분  
**이 스크립트가 자동으로 처리하는 것:**
- ✅ API 진단
- ✅ Recharts 설치 확인 및 자동 설치
- ✅ 디버깅 로그 추가
- ✅ 빌드 및 배포
- ✅ 컨테이너 재시작

---

## 📋 실행 후 확인 사항

### 1. 브라우저 접속
```
URL: http://139.150.11.99
로그인: admin / admin123
메뉴: 청구/정산 → 재무 대시보드
```

### 2. 강력 새로고침
- Windows/Linux: `Ctrl + Shift + R`
- macOS: `Cmd + Shift + R`

### 3. 개발자 도구 확인 (F12 키)
- **Console 탭:** 디버그 로그 확인
  ```
  📊 [DEBUG] Fetching financial dashboard data...
  ✅ [DEBUG] API Response received: {...}
  🎨 [DEBUG] Current render state: {...}
  ```
- **Network 탭:** API 호출 상태 확인 (200 OK)
- **Elements 탭:** 차트 DOM 요소 확인

### 4. 디버그 패널 확인
페이지 하단의 "🐛 디버그 정보" 패널을 열어서 API 응답 데이터 확인

---

## 📦 제공된 도구들

| 파일 | 설명 | 사용법 |
|------|------|--------|
| `fix_charts_all_in_one.sh` | ⭐ 올인원 해결 스크립트 | `./fix_charts_all_in_one.sh` |
| `diagnose_charts.sh` | API 및 백엔드 진단 | `./diagnose_charts.sh` |
| `check_dashboard_component.sh` | 프론트엔드 진단 | `./check_dashboard_component.sh` |
| `add_debug_logging.sh` | 디버깅 버전 배포 | `./add_debug_logging.sh` |
| `SOLUTION_PACKAGE_SUMMARY.md` | 📚 전체 솔루션 요약 | 읽기 전용 |
| `CHART_TROUBLESHOOTING_GUIDE.md` | 📚 상세 문제 해결 가이드 | 읽기 전용 |
| `IMMEDIATE_ACTION_PLAN.md` | 📚 즉시 실행 액션 플랜 | 읽기 전용 |

---

## 🎯 예상 결과

모든 것이 정상 작동하면 화면에 표시되는 것:

### ✅ 요약 카드 (3개)
```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ 총 매출      │  │ 수금액       │  │ 미수금       │
│ ₩1,234,567   │  │ ₩987,654     │  │ ₩246,913     │
└──────────────┘  └──────────────┘  └──────────────┘
```

### ✅ 월별 추이 차트
Line 차트 (파란색 선: 총 매출, 초록색 선: 수금액)

### ✅ 상위 고객 TOP 10
Bar 차트 (파란색 막대)

---

## 🆘 문제가 계속되면?

### 진단 보고서 생성
```bash
cd /root/uvis
./diagnose_charts.sh > diagnosis_report.txt
./check_dashboard_component.sh >> diagnosis_report.txt
cat diagnosis_report.txt
```

### 스크린샷 제공
1. 브라우저 Console 탭 (F12)
2. 브라우저 Network 탭
3. 재무 대시보드 현재 화면

### 추가 정보
- 백엔드 로그: `docker logs --tail 100 uvis-backend`
- 컨테이너 상태: `docker ps | grep uvis`

---

## 💡 문서 읽는 순서

1. **이 파일 (README)** - 빠른 시작 ⭐
2. **SOLUTION_PACKAGE_SUMMARY.md** - 전체 솔루션 개요
3. **IMMEDIATE_ACTION_PLAN.md** - 단계별 액션 플랜
4. **CHART_TROUBLESHOOTING_GUIDE.md** - 상세 문제 해결

---

## 🔧 수동 해결 (올인원 스크립트가 실패할 경우)

### 1단계: Recharts 설치
```bash
cd /root/uvis/frontend
npm install recharts --save
```

### 2단계: 빌드
```bash
npm run build
```

### 3단계: 배포
```bash
cd /root/uvis
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/
docker-compose restart frontend
```

### 4단계: 검증
```bash
sleep 15
docker ps | grep frontend
```

---

## ✅ 체크리스트

스크립트 실행 전:
- [ ] 서버 접속 확인
- [ ] `/root/uvis` 디렉토리에 있음
- [ ] Docker 컨테이너 실행 중

스크립트 실행 후:
- [ ] 빌드 성공 메시지 확인
- [ ] 컨테이너 재시작 완료
- [ ] 브라우저에서 강력 새로고침 (Ctrl+Shift+R)
- [ ] Console에 디버그 로그 표시
- [ ] 요약 카드 표시
- [ ] 월별 추이 차트 표시
- [ ] 상위 고객 TOP 10 표시

---

**버전:** 1.0  
**최종 업데이트:** 2026-02-12  
**상태:** ✅ 즉시 사용 가능

---

**🚀 지금 바로 시작하세요:**

```bash
cd /root/uvis && ./fix_charts_all_in_one.sh
```
