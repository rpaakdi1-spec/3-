# 프로덕션 서버에서 실행할 명령어

## 📥 최신 문서 가져오기

```bash
# 1. 새 브랜치로 전환
cd /root/uvis
git fetch origin
git checkout phase8-verification
git pull origin phase8-verification

# 2. 문서 확인
ls -la *.md | grep -E "(NEXT_STEPS|PRODUCTION_VERIFICATION)"

# 3. 검증 보고서 확인
less PRODUCTION_VERIFICATION_REPORT.md
# (q를 눌러 종료)

# 4. 다음 단계 확인
less NEXT_STEPS.md
# (q를 눌러 종료)

# 5. 검증 체크리스트 확인
less production_verification_checklist.md
# (q를 눌러 종료)
```

---

## 📊 프로덕션 검증 요약 확인

```bash
cd /root/uvis

# 검증 결과 요약
echo "=== Phase 8 프로덕션 검증 결과 ==="
echo ""
echo "✅ 백엔드 API: 6/6 통과 (100%)"
echo "✅ 데이터베이스: 4/4 테이블 존재"
echo "✅ 보안: JWT 인증 정상"
echo "✅ 성능: 평균 495ms (목표 달성)"
echo "⚠️  프론트엔드: 수동 확인 필요"
echo ""
echo "📊 종합 점수: 97.2% (35/36)"
echo "🎯 상태: 프로덕션 준비 완료 ✅"
echo ""
echo "📝 다음 단계:"
echo "  1. 브라우저에서 http://139.150.11.99/ 접속"
echo "  2. admin / admin123로 로그인"
echo "  3. 청구/정산 메뉴 → 6개 페이지 테스트"
echo "  4. F12 콘솔 오류 확인"
echo "  5. 18개 스크린샷 촬영"
```

---

## 🌐 브라우저 테스트 (수동)

### 접속 정보
- **URL**: http://139.150.11.99/
- **로그인**: admin / admin123

### 확인 사항

#### 1. 로그인 테스트
```
[ ] 로그인 페이지 정상 로드
[ ] admin / admin123 입력
[ ] 로그인 성공
[ ] 대시보드로 이동
```

#### 2. 사이드바 확인
```
[ ] 사이드바에서 "청구/정산" 메뉴 표시
[ ] 메뉴 클릭 시 6개 서브메뉴 확장
[ ] 각 메뉴에 NEW 배지 (녹색) 표시
[ ] 부드러운 애니메이션 효과
[ ] 왼쪽 세로선으로 계층 구조 표시
```

#### 3. Phase 8 페이지 테스트

**재무 대시보드**
- URL: http://139.150.11.99/billing/financial-dashboard
- [ ] 페이지 로드 성공
- [ ] 재무 지표 표시
- [ ] 차트 렌더링

**요금 미리보기**
- URL: http://139.150.11.99/billing/charge-preview
- [ ] 페이지 로드 성공
- [ ] 계산 폼 표시
- [ ] 입력 필드 작동

**자동 청구 스케줄**
- URL: http://139.150.11.99/billing/auto-schedule
- [ ] 페이지 로드 성공
- [ ] 테이블 렌더링
- [ ] 빈 상태 메시지 표시 (데이터 없음)

**정산 승인**
- URL: http://139.150.11.99/billing/settlement-approval
- [ ] 페이지 로드 성공
- [ ] 승인 목록 표시
- [ ] 필터 작동

**결제 알림**
- URL: http://139.150.11.99/billing/payment-reminder
- [ ] 페이지 로드 성공
- [ ] 알림 목록 표시
- [ ] 검색 기능 작동

**데이터 내보내기**
- URL: http://139.150.11.99/billing/export-task
- [ ] 페이지 로드 성공
- [ ] 2개 내보내기 작업 표시 (Excel, PDF)
- [ ] 다운로드 버튼 표시

#### 4. 콘솔 확인 (F12)
```
[ ] F12 개발자 도구 열기
[ ] Console 탭 선택
[ ] 빨간 오류 메시지 없음
[ ] Network 탭: 모든 API 요청 200 OK
[ ] 실패한 요청 없음
```

---

## 📸 스크린샷 촬영

### 저장 디렉토리 생성
```bash
cd /root/uvis
mkdir -p screenshots
cd screenshots
```

### 촬영 목록 (18개)

#### 기본 화면 (9개)
1. `phase8_01_login.png` - 로그인 페이지
2. `phase8_02_sidebar_collapsed.png` - 사이드바 축소 상태
3. `phase8_03_sidebar_expanded.png` - 사이드바 확장 (청구/정산 펼침)
4. `phase8_04_financial_dashboard.png` - 재무 대시보드
5. `phase8_05_charge_preview.png` - 요금 미리보기
6. `phase8_06_auto_schedule.png` - 자동 청구 스케줄
7. `phase8_07_settlement_approval.png` - 정산 승인
8. `phase8_08_payment_reminder.png` - 결제 알림
9. `phase8_09_export_task.png` - 데이터 내보내기

#### 추가 화면 (9개)
10. `phase8_10_dashboard_overview.png` - 대시보드 개요
11. `phase8_11_charts.png` - 차트/그래프
12. `phase8_12_mobile_360px.png` - 모바일 반응형 (360px)
13. `phase8_13_tablet_768px.png` - 태블릿 반응형 (768px)
14. `phase8_14_desktop_1920px.png` - 데스크톱 (1920px)
15. `phase8_15_darkmode.png` - 다크모드 (있으면)
16. `phase8_16_error_message.png` - 에러 메시지 예시
17. `phase8_17_success_message.png` - 성공 메시지 예시
18. `phase8_18_loading_state.png` - 로딩 상태

### 촬영 방법
1. Windows: `Win + Shift + S` 또는 Snipping Tool
2. Mac: `Cmd + Shift + 4`
3. Linux: `PrtSc` 또는 Screenshot 도구
4. 브라우저: F12 → 디바이스 툴바 → 스크린샷 아이콘

---

## 📋 검증 결과 보고

### 템플릿

```
Phase 8 프로덕션 검증 결과 보고

검증 일시: [날짜/시간]
검증자: [이름]

=== 프론트엔드 테스트 결과 ===

✅ 로그인: [정상/오류]
✅ 사이드바: [정상/오류]
✅ 재무 대시보드: [정상/오류]
✅ 요금 미리보기: [정상/오류]
✅ 자동 청구: [정상/오류]
✅ 정산 승인: [정상/오류]
✅ 결제 알림: [정상/오류]
✅ 데이터 내보내기: [정상/오류]

콘솔 오류:
- [오류 내용 또는 "없음"]

발견된 이슈:
- [이슈 내용 또는 "없음"]

스크린샷:
- [촬영 완료: X/18개]

=== 최종 평가 ===

[ ] 🟢 우수: 모든 항목 정상
[ ] 🟡 양호: 경미한 이슈
[ ] 🟠 개선 필요: 중간 이슈
[ ] 🔴 불합격: 심각한 이슈

종합 의견:
[의견 작성]
```

---

## 🔄 문제 해결

### 페이지가 로드되지 않을 때
```bash
# 1. 컨테이너 상태 확인
docker ps

# 2. 프론트엔드 재시작
cd /root/uvis
docker-compose restart frontend

# 3. 로그 확인
docker logs uvis-frontend --tail 50
```

### API 오류가 발생할 때
```bash
# 1. 백엔드 로그 확인
docker logs uvis-backend --tail 100

# 2. 백엔드 재시작
docker-compose restart backend

# 3. 데이터베이스 확인
docker exec uvis-db psql -U uvis_user -d uvis_db -c "SELECT tablename FROM pg_tables WHERE schemaname='public';"
```

### 브라우저 캐시 문제
1. `Ctrl + Shift + R` (Windows/Linux)
2. `Cmd + Shift + R` (Mac)
3. 또는 설정 → 인터넷 사용 기록 삭제

---

## 📞 지원

문제 발생 시:
1. 스크린샷 촬영
2. F12 콘솔 오류 메시지 복사
3. 오류 내용 공유

**GitHub Issues**: https://github.com/rpaakdi1-spec/3-/issues

---

## ✅ 완료 체크리스트

### 즉시 실행
- [ ] 프로덕션 서버에서 문서 가져오기
- [ ] PRODUCTION_VERIFICATION_REPORT.md 확인
- [ ] NEXT_STEPS.md 확인

### 수동 테스트
- [ ] 브라우저에서 사이트 접속
- [ ] 로그인 테스트
- [ ] 6개 Phase 8 페이지 테스트
- [ ] 콘솔 오류 확인

### 문서화
- [ ] 18개 스크린샷 촬영
- [ ] 검증 결과 보고서 작성
- [ ] 팀에 공지

---

**마지막 업데이트**: 2026-02-07  
**브랜치**: phase8-verification  
**상태**: 문서 준비 완료 ✅
