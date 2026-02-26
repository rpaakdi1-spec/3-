# 🚀 빠른 수정 가이드

## ⚡ 한 줄 명령어 (서버에서 실행)

```bash
cd /root/uvis/frontend && bash FIX_UI_ISSUES.sh
```

스크립트가 없으면 아래 전체 명령어를 복사하여 실행:

---

## 📋 전체 수정 명령어 (복사하여 한 번에 실행)

```bash
cd /root/uvis/frontend

# 백업
cp src/pages/OrdersPage.tsx src/pages/OrdersPage.tsx.backup_$(date +%Y%m%d_%H%M%S)
cp src/App.tsx src/App.tsx.backup_$(date +%Y%m%d_%H%M%S)

# OrdersPage.tsx 복원 및 수정
git checkout HEAD -- src/pages/OrdersPage.tsx
sed -i '/^import Layout from/d' src/pages/OrdersPage.tsx

# Layout 태그 제거
python3 << 'EOF'
with open("src/pages/OrdersPage.tsx", "r") as f:
    lines = f.readlines()
filtered = [line for line in lines if line.strip() not in ["<Layout>", "</Layout>"]]
with open("src/pages/OrdersPage.tsx", "w") as f:
    f.writelines(filtered)
print("✅ Layout 태그 제거 완료")
EOF

# 검증
echo -e "\n=== 검증 ==="
echo "Layout import: $(grep -c '^import Layout from' src/pages/OrdersPage.tsx || echo '0')개 (0이어야 함)"
echo "<Layout> 태그: $(grep -c '<Layout>' src/pages/OrdersPage.tsx || echo '0')개 (0이어야 함)"

# 빌드
echo -e "\n=== 빌드 시작 ==="
npm run build 2>&1 | tail -30

# 결과 확인
if [ $? -eq 0 ]; then
    echo -e "\n✅ 빌드 성공!"
    echo -e "\n다음 명령어로 Docker 재배포:"
    echo "cd /root/uvis"
    echo "docker-compose stop frontend && docker-compose rm -f frontend"
    echo "docker rmi uvis-frontend"
    echo "docker-compose build --no-cache frontend"
    echo "docker-compose up -d frontend"
else
    echo -e "\n❌ 빌드 실패"
fi
```

---

## 🔄 Docker 재배포 명령어 (빌드 성공 후 실행)

```bash
cd /root/uvis
docker-compose stop frontend
docker-compose rm -f frontend
docker rmi uvis-frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend

# 확인
sleep 10
docker ps | grep frontend
docker logs uvis-frontend --tail 20
```

---

## 🌐 브라우저 확인 (배포 후)

1. **캐시 완전 삭제:**
   - `Ctrl + Shift + Delete`
   - "전체 기간" 선택
   - "캐시된 이미지 및 파일" 체크
   - 삭제

2. **Service Worker 제거:**
   - `F12` → Application 탭
   - Service Workers → Unregister

3. **강제 새로고침:**
   - `Ctrl + F5`

4. **시크릿 모드로 테스트:**
   - `Ctrl + Shift + N`

---

## 🔍 문제 진단 (문제가 계속되면)

```bash
cd /root/uvis/frontend

# 현재 상태 확인
echo "=== 파일 상태 ==="
grep "import Layout" src/pages/OrdersPage.tsx || echo "✅ Layout import 없음"
grep "<Layout>" src/pages/OrdersPage.tsx || echo "✅ Layout 태그 없음"

echo -e "\n=== /orders 라우트 ==="
grep -A3 'path="/orders"' src/App.tsx

echo -e "\n=== 빌드 파일 ==="
ls -lh dist/assets/*.css
echo "JS 파일 개수: $(ls -1 dist/assets/*.js 2>/dev/null | wc -l)개"

echo -e "\n=== Git 상태 ==="
git status --short

echo -e "\n=== Docker 상태 ==="
docker ps | grep frontend
```

---

## 📸 스크린샷 공유 (문제 지속 시)

다음을 캡처하여 공유:
1. 로그인 페이지 화면
2. F12 Console 탭
3. F12 Network 탭 (index-*.css 파일)
4. 위 진단 명령어 출력 결과

---

## ✅ 정상 상태 확인

- [ ] 로그인 페이지에 **파란색 gradient 배경** 표시
- [ ] 로그인 폼 (사용자 이름, 비밀번호, 로그인 버튼) 정상 표시
- [ ] 로그인 성공 후 대시보드로 이동
- [ ] 사이드바 메뉴 정상 표시
- [ ] 주문 관리(/orders) 페이지 정상 표시
- [ ] Layout 중복 없음

---

## 📞 추가 도움

문제가 해결되지 않으면:
1. 위의 **진단 명령어** 출력 결과
2. **스크린샷** (로그인 페이지, F12 Console, Network)
3. `npm run build` **전체 출력**

을 공유해주세요.
