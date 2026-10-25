import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// modulepreload를 초기 필수 청크만 제한하는 플러그인
function selectiveModulePreload() {
  // 초기 로딩에 반드시 필요한 청크만 preload
  const PRELOAD_WHITELIST = [
    'vendor-react',
    'vendor-http',
    'vendor-state',
    'vendor-ui',
    'vendor-date',
  ];
  return {
    name: 'selective-modulepreload',
    transformIndexHtml(html: string) {
      // vendor-charts, vendor-map, 개별 페이지 청크의 modulepreload 제거
      return html.replace(
        /<link rel="modulepreload"[^>]+href="\/assets\/(vendor-charts|vendor-map|[A-Z][^"]*|Order[^"]*|Dispatch[^"]*|Vehicle[^"]*|Driver[^"]*|Client[^"]*|Analytics[^"]*|Billing[^"]*|Financial[^"]*|ML[^"]*|Tracking[^"]*|Settings[^"]*|Reports[^"]*|More[^"]*|Notification[^"]*)[^"]*\.js"[^>]*>\n?/g,
        ''
      );
    },
  };
}

export default defineConfig({
  plugins: [react(), selectiveModulePreload()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    allowedHosts: ['.sandbox.novita.ai'],
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/uploads': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    chunkSizeWarningLimit: 1500,
    sourcemap: false,
    minify: 'esbuild',
    cssCodeSplit: true,
    modulePreload: {
      // 초기 엔트리 청크만 preload, 동적 import 청크는 제외
      polyfill: false,
      resolveDependencies: (filename, deps) => {
        // 무거운 lazy 청크는 preload에서 제외
        const HEAVY_CHUNKS = ['vendor-charts', 'vendor-map'];
        return deps.filter(dep =>
          !HEAVY_CHUNKS.some(chunk => dep.includes(chunk))
        );
      }
    },
    rollupOptions: {
      onwarn(warning, warn) {
        if (warning.code === 'UNUSED_EXTERNAL_IMPORT') return
        if (warning.code === 'UNRESOLVED_IMPORT') return
        warn(warning)
      },
      output: {
        manualChunks: {
          // ── 초기 로딩 필수 청크 (preload O) ──
          // React 핵심
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          // HTTP + 상태관리
          'vendor-http': ['axios'],
          'vendor-state': ['zustand'],
          // 아이콘/UI 유틸
          'vendor-ui': ['lucide-react', 'react-icons', 'clsx'],
          // 날짜 (date-fns만)
          'vendor-date': ['date-fns'],

          // ── 지연 로딩 청크 (preload X) ──
          // 차트/시각화 (DashboardPage lazy import)
          'vendor-charts': ['recharts', 'chart.js', 'react-chartjs-2'],
          // 지도 (TrackingPage lazy import)
          'vendor-map': ['leaflet', 'react-leaflet'],
        }
      }
    }
  }
})
