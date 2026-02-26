# 브라우저 줌 레벨 조정 가이드

## 가장 빠른 임시 해결책

### Chrome/Edge:
```
1. Ctrl + 0 (줌 레벨 100%로 리셋)
2. Ctrl + - (줌 아웃, 화면 축소)
3. 원하는 크기까지 반복 (권장: 90% 또는 80%)
```

### 줌 레벨 확인:
- 주소창 오른쪽에 🔍 아이콘 클릭
- 슬라이더로 조정 가능

---

## CSS로 브라우저 줌 적용 (영구적)

```css
/* src/index.css에 추가 */
body {
  zoom: 0.9; /* 90% 크기로 축소 */
}

/* 또는 transform 사용 */
#root {
  transform: scale(0.9);
  transform-origin: top left;
}
```

