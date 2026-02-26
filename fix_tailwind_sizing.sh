#!/bin/bash

cat > /tmp/tailwind.config.js << 'TAILWIND_EOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontSize: {
        'xs': '0.75rem',    // 12px
        'sm': '0.875rem',   // 14px
        'base': '0.875rem', // 14px (기본값 줄임)
        'lg': '1rem',       // 16px
        'xl': '1.125rem',   // 18px
      },
      spacing: {
        // 기본 패딩/마진을 약간 줄임
        '1': '0.2rem',
        '2': '0.4rem',
        '3': '0.6rem',
        '4': '0.8rem',
        '5': '1rem',
        '6': '1.2rem',
        '8': '1.6rem',
      },
    },
  },
  plugins: [],
}
TAILWIND_EOF

echo "Tailwind 설정 파일 생성 완료"
cat /tmp/tailwind.config.js
