# 🚀 UVIS 프로덕션 배포 가이드

## ✅ PR 병합 완료!

**Pull Request #1**이 성공적으로 main 브랜치로 병합되었습니다!

- **PR URL**: https://github.com/rpaakdi1-spec/3-/pull/1
- **병합 커밋**: 7780df5 - feat: Complete UVIS transportation management system (#1)
- **변경 사항**: 531 파일, +158,336 줄, -3,460 줄
- **커밋 압축**: 114개 → 1개

---

## 🌡️ 최신 기능: 온도대별 자동 온도 입력

### 구현 내용
프로덕션 환경 **139.150.11.99**에 배포하려면 서버에서 다음 명령어를 실행하세요:

```bash
# 1. 프로젝트 디렉토리로 이동
cd /root/uvis

# 2. 최신 변경사항 가져오기
git fetch origin main
git checkout main
git pull origin main

# 3. 현재 커밋 확인 (7780df5여야 함)
git log --oneline -1

# 4. 서비스 중지
docker-compose -f docker-compose.prod.yml down

# 5. 프론트엔드 재빌드 (온도 자동입력 기능 포함)
docker-compose -f docker-compose.prod.yml build --no-cache frontend

# 6. 백엔드 재빌드
docker-compose -f docker-compose.prod.yml build backend

# 7. 서비스 시작
docker-compose -f docker-compose.prod.yml up -d

# 8. 서비스 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 9. 프론트엔드 로그 확인
docker-compose -f docker-compose.prod.yml logs -f frontend
```

---

## 🧪 배포 후 테스트

### 1. 서비스 접근 확인
- **프론트엔드**: http://139.150.11.99
- **백엔드 API**: http://139.150.11.99:8000
- **API 문서**: http://139.150.11.99:8000/docs

### 2. 온도 자동입력 기능 테스트

#### 테스트 시나리오
1. **주문 관리 페이지 접근**
   - URL: http://139.150.11.99/orders
   - 로그인 필요

2. **신규 주문 등록 모달 열기**
   - "+ 신규 등록" 버튼 클릭

3. **온도대 선택 테스트**

   **냉동 선택 시:**
   ```
   온도대: 냉동 (-30°C ~ -18°C)
   → 최저 온도: -30 (자동 입력)
   → 최고 온도: -18 (자동 입력)
   → 안내: "권장 온도 범위가 자동으로 입력됩니다. 필요시 수정 가능합니다."
   ```

   **냉장 선택 시:**
   ```
   온도대: 냉장 (0°C ~ 6°C)
   → 최저 온도: 0 (자동 입력)
   → 최고 온도: 6 (자동 입력)
   ```

   **상온 선택 시:**
   ```
   온도대: 상온 (-30°C ~ 60°C)
   → 최저 온도: -30 (자동 입력)
   → 최고 온도: 60 (자동 입력)
   ```

4. **온도 수동 수정 테스트**
   - 자동 입력된 값을 변경 가능한지 확인
   - 예: 냉동 -25°C ~ -20°C로 변경

5. **주문 등록 완료**
   - 거래처: 테스트 거래처 선택
   - 출발지: 서울시 강남구
   - 도착지: 경기도 성남시
   - 팔레트 수량: 5
   - 등록 버튼 클릭
   - 등록 성공 메시지 확인

### 3. 예상 결과
- ✅ 온도대 선택 시 즉시 온도 범위 자동 입력
- ✅ 사용자가 값을 수정 가능
- ✅ 안내 메시지 표시
- ✅ 주문 등록 성공

### 4. 오류 대응

#### 422 Unprocessable Entity 오류
**원인**: 브라우저 캐시
**해결**: 
```
Ctrl + Shift + R (Windows/Linux)
Cmd + Shift + R (Mac)
또는 브라우저 캐시 완전 삭제
```

#### 자동 입력이 작동하지 않는 경우
**확인사항**:
1. 브라우저 콘솔(F12) 확인
2. 에러 메시지 확인
3. 프론트엔드 로그 확인:
   ```bash
   docker-compose -f docker-compose.prod.yml logs frontend
   ```

#### 드롭다운이 표시되지 않는 경우
**원인**: 빌드 캐시
**해결**:
```bash
# 프론트엔드만 재빌드
docker-compose -f docker-compose.prod.yml build --no-cache frontend
docker-compose -f docker-compose.prod.yml up -d frontend
```

---

## 📊 배포 확인 체크리스트

### 서비스 상태
- [ ] Frontend 컨테이너 실행 중
- [ ] Backend 컨테이너 실행 중 (healthy)
- [ ] Database 컨테이너 실행 중 (healthy)
- [ ] Redis 컨테이너 실행 중 (healthy)
- [ ] Nginx 컨테이너 실행 중

### 기능 테스트
- [ ] 로그인 성공
- [ ] 주문 목록 조회
- [ ] 온도대 드롭다운 표시
- [ ] 냉동 선택 시 -30 ~ -18 자동 입력
- [ ] 냉장 선택 시 0 ~ 6 자동 입력
- [ ] 상온 선택 시 -30 ~ 60 자동 입력
- [ ] 온도 수동 수정 가능
- [ ] 주문 등록 성공

### 추가 기능 테스트
- [ ] 주문 캘린더 페이지 (http://139.150.11.99/calendar)
- [ ] 드래그앤드롭으로 날짜 변경
- [ ] 실시간 모니터링 (http://139.150.11.99/realtime)
- [ ] GPS 차량 추적
- [ ] 엑셀 업로드/다운로드

---

## 🔧 데이터베이스 마이그레이션

배포 시 자동으로 실행되지만, 수동 실행이 필요한 경우:

```bash
# 백엔드 컨테이너 접속
docker-compose -f docker-compose.prod.yml exec backend bash

# 마이그레이션 실행
alembic upgrade head

# 현재 마이그레이션 버전 확인
alembic current

# 종료
exit
```

### 새로운 마이그레이션
1. `20260129113751_add_has_forklift_to_vehicles.py` - 지게차 운전자 필드
2. `20260129115304_make_weight_optional.py` - 중량 필드 선택사항화
3. `20260129140000_rename_forklift_fields.py` - 지게차 필드 이름 변경
4. `20260129150000_merge_heads.py` - 마이그레이션 헤드 병합
5. `20260129160000_add_calendar_fields_to_orders.py` - 캘린더 필드 추가
   - is_reserved
   - reserved_at
   - confirmed_at
   - recurring_type
   - recurring_end_date

---

## 📈 모니터링

### 로그 확인
```bash
# 모든 서비스 로그
docker-compose -f docker-compose.prod.yml logs -f

# 프론트엔드 로그만
docker-compose -f docker-compose.prod.yml logs -f frontend

# 백엔드 로그만
docker-compose -f docker-compose.prod.yml logs -f backend

# 최근 100줄만 확인
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### 리소스 모니터링
```bash
# 컨테이너 리소스 사용량
docker stats

# 디스크 사용량
df -h

# 메모리 사용량
free -h
```

### Health Check
```bash
# Backend health check
curl http://139.150.11.99:8000/health

# Frontend health check
curl http://139.150.11.99/

# Database connection test
docker-compose -f docker-compose.prod.yml exec backend python -c "from app.core.database import engine; print(engine.url)"
```

---

## 🚨 문제 해결

### 서비스가 시작되지 않는 경우
```bash
# 로그 확인
docker-compose -f docker-compose.prod.yml logs

# 개별 컨테이너 재시작
docker-compose -f docker-compose.prod.yml restart frontend
docker-compose -f docker-compose.prod.yml restart backend

# 전체 재시작
docker-compose -f docker-compose.prod.yml restart
```

### 데이터베이스 연결 오류
```bash
# PostgreSQL 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps db

# PostgreSQL 로그 확인
docker-compose -f docker-compose.prod.yml logs db

# PostgreSQL 재시작
docker-compose -f docker-compose.prod.yml restart db
```

### 빌드 오류
```bash
# 이미지 삭제 후 재빌드
docker-compose -f docker-compose.prod.yml down
docker rmi uvis-frontend uvis-backend
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### 디스크 공간 부족
```bash
# 사용하지 않는 이미지 삭제
docker image prune -a

# 사용하지 않는 컨테이너 삭제
docker container prune

# 사용하지 않는 볼륨 삭제
docker volume prune

# 전체 정리
docker system prune -a
```

---

## 📞 지원

### 문제 발생 시
1. **로그 수집**
   ```bash
   docker-compose -f docker-compose.prod.yml logs > deployment_logs.txt
   ```

2. **스크린샷 캡처**
   - 브라우저 화면
   - 브라우저 콘솔 (F12)
   - 에러 메시지

3. **환경 정보**
   ```bash
   docker --version
   docker-compose --version
   git log --oneline -1
   ```

4. **이슈 생성**
   - GitHub 저장소에 이슈 등록
   - 수집한 정보 첨부

### 긴급 롤백
문제가 심각한 경우 이전 버전으로 롤백:

```bash
# 이전 커밋으로 롤백
cd /root/uvis
git log --oneline -5  # 이전 커밋 확인
git checkout <이전_커밋_해시>

# 재배포
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## ✅ 배포 완료 확인

모든 단계가 완료되면:

1. ✅ PR 병합 완료 (https://github.com/rpaakdi1-spec/3-/pull/1)
2. ✅ 프로덕션 배포 완료
3. ✅ 서비스 정상 작동
4. ✅ 온도 자동입력 기능 작동
5. ✅ 모든 테스트 통과

**배포 완료!** 🎉

---

## 📅 다음 작업

1. **사용자 피드백 수집**
   - 온도 자동입력 기능 사용성
   - 추가 개선사항

2. **성능 모니터링**
   - 응답 시간 측정
   - 에러 발생 추적

3. **추가 기능 개발**
   - PDF 리포트 생성
   - SMS 알림
   - 운전자 평가 시스템

4. **모바일 앱 배포**
   - Google Play Store
   - Apple App Store

---

**문서 작성일**: 2026-01-29  
**버전**: 1.0.0  
**작성자**: GenSpark AI Developer
