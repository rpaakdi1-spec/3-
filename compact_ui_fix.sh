#!/bin/bash

cat > /tmp/compact_index.css << 'CSS_EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html {
    zoom: 1; /* 100% 고정 */
    font-size: 14px; /* 기본 폰트 크기 줄임 */
  }
  
  body {
    zoom: 1;
    @apply text-sm;
  }
}

@layer components {
  /* 테이블 행 높이 줄이기 */
  table tbody tr {
    @apply text-xs leading-tight;
  }
  
  table th,
  table td {
    @apply py-1.5 px-2; /* 패딩 줄임 (기본: py-4 px-6) */
  }
  
  /* 카드 패딩 줄이기 */
  .card {
    @apply p-3; /* 기본: p-6 */
  }
  
  /* 입력 필드 높이 줄이기 */
  input,
  select,
  textarea {
    @apply py-1 px-2 text-sm; /* 기본: py-2 px-4 */
  }
  
  /* 버튼 높이 줄이기 */
  button {
    @apply py-1 px-3 text-sm; /* 기본: py-2 px-4 */
  }
  
  /* 리스트 항목 간격 줄이기 */
  ul li,
  ol li {
    @apply py-1; /* 기본: py-2 */
  }
  
  /* 섹션 간격 줄이기 */
  section {
    @apply py-4; /* 기본: py-8 */
  }
  
  /* 헤더 높이 줄이기 */
  header {
    @apply py-2; /* 기본: py-4 */
  }
  
  /* 모달 패딩 줄이기 */
  .modal-content {
    @apply p-4; /* 기본: p-6 */
  }
  
  /* 폼 그룹 간격 줄이기 */
  .form-group {
    @apply mb-3; /* 기본: mb-6 */
  }
}

/* 전역 줄 높이 조정 */
@layer utilities {
  .compact-mode {
    @apply leading-tight;
  }
  
  .compact-table {
    @apply text-xs;
  }
  
  .compact-table th,
  .compact-table td {
    @apply py-1 px-2;
  }
}
CSS_EOF

echo "Compact UI CSS 생성 완료"
cat /tmp/compact_index.css
