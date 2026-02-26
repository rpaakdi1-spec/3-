# 🚀 Frontend Sonner Import Error 수정 - 서버 재배포

## 📌 문제
Frontend에서 "Failed to resolve module specifier 'sonner'" 오류 발생:
- Phase 16 파일들이 `sonner` 패키지를 import하려고 시도
- `sonner`가 `package.json`에 없음
- 프로젝트는 이미 `react-hot-toast`를 사용 중

## ✅ 수정 완료
- **커밋:** `c43df1b`
- **수정 파일:** 8개 (모든 Phase 16 파일)
- **변경:** `import { toast } from 'sonner'` → `import toast from 'react-hot-toast'`

---

## 🎯 서버 재배포 명령어 (최종)

```bash
cd /root/uvis

# 1. 최신 코드 가져오기
git fetch origin
git reset --hard origin/main

# 2. 최신 커밋 확인 (c43df1b 확인)
git log --oneline -3

# 예상 출력:
# c43df1b (HEAD -> main, origin/main) fix(frontend): Replace sonner with react-hot-toast
# 16575b7 docs: Add second FCM import fix deployment guide
# 78c4c99 fix(backend): Fix fcm_service import in notification_service.py

# 3. Frontend 재빌드 및 재시작
docker-compose stop frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend

# 4. 60초 대기
sleep 60

# 5. 상태 확인
docker-compose ps

# 6. Frontend 접속 테스트
curl -I http://localhost/

# 예상 응답: HTTP/1.1 200 OK
```

---

## 🌐 브라우저 테스트

### **반드시 캐시 클리어!**
1. **개발자 도구 방법 (가장 확실):**
   - `F12` 키로 개발자 도구 열기
   - 새로고침 버튼 **마우스 오른쪽 클릭**
   - **"캐시 비우기 및 강력 새로고침"** 선택

2. **시크릿 모드:**
   - `Ctrl + Shift + N`
   - http://139.150.11.99 접속

### **테스트 페이지**
- **메인:** http://139.150.11.99
- **로그인:** http://139.150.11.99/login
- **대시보드:** http://139.150.11.99/dashboard
- **채팅 (Phase 16.3):** http://139.150.11.99/chat ⭐
- **파일 (Phase 16.2):** http://139.150.11.99/files ⭐
- **API 문서:** http://139.150.11.99:8000/docs

---

## ✅ 예상 결과

### **컨테이너 상태**
```
NAME            STATUS
uvis-frontend   Up (healthy)  ✅
uvis-backend    Up (healthy)  ✅
uvis-minio      Up (healthy)  ✅
uvis-db         Up (healthy)  ✅
uvis-redis      Up (healthy)  ✅
```

### **브라우저 콘솔**
- ❌ ~~"Failed to resolve module specifier 'sonner'"~~ (사라짐)
- ✅ 오류 없음
- ✅ 정상 작동

---

## 📊 수정 요약

| 파일 | 변경 전 | 변경 후 |
|------|---------|---------|
| NotificationSettings.tsx | `import { toast } from 'sonner'` | `import toast from 'react-hot-toast'` |
| FileUpload.tsx | `import { toast } from 'sonner'` | `import toast from 'react-hot-toast'` |
| FileManager.tsx | `import { toast } from 'sonner'` | `import toast from 'react-hot-toast'` |
| ChatRoomList.tsx | `import { toast } from 'sonner'` | `import toast from 'react-hot-toast'` |
| MessageInput.tsx | `import { toast } from 'sonner'` | `import toast from 'react-hot-toast'` |
| useFCM.ts | `import { toast } from 'sonner'` | `import toast from 'react-hot-toast'` |
| useChatWebSocket.ts | `import { toast } from 'sonner'` | `import toast from 'react-hot-toast'` |
| ChatPage.tsx | `import { toast } from 'sonner'` | `import toast from 'react-hot-toast'` |

**총 8개 파일 수정 완료** ✅

---

## 🎉 배포 후 확인

1. ✅ Backend 정상 작동 (import error 없음)
2. ✅ Frontend 빌드 성공
3. ✅ 브라우저에서 오류 없음
4. ✅ Phase 16 기능 정상 작동:
   - FCM 푸시 알림
   - 파일 업로드/다운로드
   - 실시간 채팅

---

**작성:** 2026-02-27  
**최신 커밋:** c43df1b  
**상태:** ✅ 수정 완료, 재배포 준비
