# 서버 상태 확인 명령어

서버에서 다음 명령어를 실행하여 상태를 확인해주세요:

## 1. 빌드된 파일 확인
```bash
cd /root/uvis/frontend
ls -lh dist/assets/*.css
ls -lh dist/assets/*.js | head -10
```

## 2. 현재 소스 파일 상태 확인
```bash
# App.tsx에서 /orders 라우트 확인
grep -A5 'path="/orders"' src/App.tsx

# OrdersPage에서 Layout import 확인
grep "import Layout" src/pages/OrdersPage.tsx
```

## 3. 브라우저 콘솔 에러 확인
- 브라우저에서 F12를 누르고 Console 탭을 확인
- Network 탭에서 CSS 파일이 제대로 로드되는지 확인
- 스크린샷을 공유해주시면 더 정확한 진단이 가능합니다

## 4. 서버 로그 확인
```bash
docker logs uvis-frontend --tail 50
```

## 5. Git 상태 확인
```bash
cd /root/uvis/frontend
git status
git log --oneline -5
```
