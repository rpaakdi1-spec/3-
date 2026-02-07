import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // 청크 크기 경고 제한 상향 (KB)
    chunkSizeWarningLimit: 1000,
    
    // 롤업 옵션
    rollupOptions: {
      output: {
        // 수동 청크 분할 전략
        manualChunks: {
          // React 핵심 라이브러리
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          
          // 차트 라이브러리들
          'chart-vendor': ['chart.js', 'react-chartjs-2', 'recharts'],
          
          // 지도 관련 라이브러리
          'map-vendor': ['leaflet', 'react-leaflet'],
          
          // UI 유틸리티
          'ui-vendor': ['lucide-react', 'react-hot-toast', 'clsx'],
          
          // 상태 관리 및 데이터
          'data-vendor': ['zustand', 'axios'],
          
          // 날짜 처리
          'date-vendor': ['date-fns', 'moment', 'react-big-calendar'],
          
          // 기타 유틸리티
          'utils-vendor': ['i18next', 'react-i18next', 'qrcode.react'],
        },
        
        // 에셋 파일명 패턴
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.')
          let extType = info[info.length - 1]
          
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(extType)) {
            extType = 'images'
          } else if (/woff|woff2|eot|ttf|otf/i.test(extType)) {
            extType = 'fonts'
          }
          
          return `assets/${extType}/[name]-[hash][extname]`
        },
        
        // 청크 파일명 패턴
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
      },
    },
    
    // 소스맵 생성 (프로덕션에서는 비활성화 가능)
    sourcemap: false,
    
    // CSS 코드 스플리팅
    cssCodeSplit: true,
    
    // Minification 설정
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // console.log 제거
        drop_debugger: true, // debugger 제거
      },
    },
  },
  
  // 최적화 옵션
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'zustand',
      'axios',
    ],
  },
})
