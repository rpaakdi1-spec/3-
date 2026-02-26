#!/bin/bash

cat > /tmp/index.css << 'CSS_EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

/* 전역 스케일 조정 */
@layer base {
  html {
    font-size: 14px; /* 기본값 16px → 14px */
  }
  
  body {
    @apply text-sm; /* 기본 텍스트 크기 줄임 */
  }
  
  /* 모든 요소의 크기를 90%로 줄임 */
  * {
    font-size: inherit;
  }
}

/* 컴포넌트별 미세 조정 */
@layer components {
  /* 버튼 크기 조정 */
  .btn {
    @apply px-3 py-1.5 text-sm;
  }
  
  /* 카드 패딩 조정 */
  .card {
    @apply p-4;
  }
  
  /* 입력 필드 크기 조정 */
  input, select, textarea {
    @apply text-sm py-1.5 px-2.5;
  }
}
CSS_EOF

echo "CSS 파일 생성 완료"
cat /tmp/index.css
