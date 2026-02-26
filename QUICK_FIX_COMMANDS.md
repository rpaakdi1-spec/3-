# 🚀 서버에서 바로 실행할 명령어

## 📋 복사해서 서버에 붙여넣기

```bash
cd /root/uvis && python3 << 'PYEOF'
file_path = 'frontend/src/pages/OrdersPage.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('       </>\n  );', '      )}\n    </>\n  );')
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("✅ OrdersPage.tsx 수정 완료")
PYEOF
```

그 다음:

```bash
cd /root/uvis/frontend && npm run build && cd .. && docker-compose build --no-cache frontend && docker-compose up -d frontend && sleep 15 && docker ps && docker logs uvis-frontend --tail 10
```

## 또는 전체 스크립트 다운로드

```bash
# 서버에서
cd /root/uvis
curl -o deploy_fix.sh http://139.150.11.99/DEPLOY_LAYOUT_FIX.sh
chmod +x deploy_fix.sh
./deploy_fix.sh
```

---

## ✅ 수정 내용

**파일**: `frontend/src/pages/OrdersPage.tsx`

**변경**:
```diff
          </div>
        </div>
-      )}
-       </>
+      )}\n    </>
  );
```

**이유**: Voice modal의 닫는 괄호 `)}` 후에 Fragment 닫기 태그 `</>`가 와야 함.

---

## 🎯 예상 결과

1. ✅ 빌드 성공 (약 15-20초)
2. ✅ Docker 이미지 생성 성공
3. ✅ Frontend 컨테이너 재시작
4. ✅ 브라우저에서 모든 페이지 사이드바 1개만 표시

---

**생성일**: 2026-02-25  
**작성자**: AI Assistant  
**위치**: Sandbox
