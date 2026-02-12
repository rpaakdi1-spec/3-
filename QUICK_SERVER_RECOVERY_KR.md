# 🚨 서버 접속 불가 - 긴급 복구 절차

**현재 상황**: PuTTY로 서버 접속 불가 (과부하 추정)

---

## ⚡ 즉시 실행할 절차 (5분 이내)

### 1단계: Hetzner 웹 콘솔 접속 ⏱️ 1분

```
1. 브라우저에서 열기: https://console.hetzner.cloud/
2. 로그인
3. 서버 목록에서 "139.150.11.99" 서버 클릭
```

### 2단계: 웹 콘솔 열기 ⏱️ 30초

```
1. 서버 상세 페이지에서
2. 우측 상단 "Console" 버튼 클릭
3. 브라우저에서 콘솔 터미널이 열림
```

### 3단계: 서버 재시작 ⏱️ 3분

#### 옵션 A: 소프트 재시작 (권장)
```bash
# 웹 콘솔에서 실행
reboot
```

#### 옵션 B: 웹 인터페이스에서 재시작
```
1. 서버 상세 페이지
2. 우측 상단 "Power" 버튼 클릭
3. "Reboot" 선택
4. 확인
```

### 4단계: 재시작 대기 ⏱️ 2-3분

```
서버가 재시작되는 동안 대기...
```

### 5단계: SSH 재접속 ⏱️ 30초

```bash
# PuTTY 또는 터미널에서
ssh root@139.150.11.99

# 또는 Hetzner 웹 콘솔 사용
```

---

## 🔍 복구 후 확인 명령어

### 서버 접속 후 즉시 실행

```bash
# 1. 작업 디렉토리로 이동
cd /root/uvis

# 2. 자동 점검 스크립트 다운로드 및 실행
curl -O https://raw.githubusercontent.com/rpaakdi1-spec/3-/main/server_recovery_check.sh
chmod +x server_recovery_check.sh
./server_recovery_check.sh
```

### 또는 수동 확인

```bash
# Docker 상태 확인
docker ps

# 서비스 재시작 (필요 시)
cd /root/uvis
docker-compose restart

# 헬스 체크
curl http://localhost:8000/health
```

---

## 📊 정상 작동 확인

### 확인 사항
- ✅ SSH 접속 가능
- ✅ Docker 컨테이너 7개 실행 중
- ✅ 백엔드 응답: http://localhost:8000/health
- ✅ 프론트엔드 접속: http://139.150.11.99/
- ✅ 메모리 사용량 < 80%

---

## 🆘 여전히 문제가 있다면?

### 완전 재시작 (최후의 수단)

```bash
# 1. 모든 Docker 컨테이너 중지
cd /root/uvis
docker-compose down

# 2. 5초 대기
sleep 5

# 3. 다시 시작
docker-compose up -d

# 4. 10초 대기
sleep 10

# 5. 상태 확인
docker-compose ps
```

---

## 📞 추가 지원

### Hetzner 지원팀
- 웹사이트: https://www.hetzner.com/support
- 티켓: https://console.hetzner.cloud/support

### 자동 복구 스크립트 위치
- GitHub: https://github.com/rpaakdi1-spec/3-
- 파일: `server_recovery_check.sh`
- 가이드: `SERVER_OVERLOAD_RECOVERY_GUIDE.md`

---

## 💡 예방 조치 (복구 후 실행)

```bash
# 로그 정리
docker system prune -af

# 메모리 캐시 정리
sync && echo 3 > /proc/sys/vm/drop_caches

# 모니터링 스크립트 설정
# (상세 내용은 SERVER_OVERLOAD_RECOVERY_GUIDE.md 참조)
```

---

## ✅ 체크리스트

- [ ] Hetzner 웹 콘솔 접속 완료
- [ ] 서버 재시작 완료
- [ ] SSH 재접속 성공
- [ ] Docker 컨테이너 정상 작동
- [ ] 웹사이트 접속 확인
- [ ] 자동 점검 스크립트 실행
- [ ] 로그 에러 없음

---

**작성**: 2026-02-08  
**최종 업데이트**: AI Assistant

**중요**: 이 가이드는 GitHub에 커밋되어 있으므로 서버 접속 후 언제든지 참조 가능합니다.
