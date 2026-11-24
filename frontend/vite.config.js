import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// 后端端口：5005（可在启动前设置环境变量 VITE_PROXY_TARGET 覆盖）
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_PROXY_TARGET || 'http://127.0.0.1:5005',
        changeOrigin: true
      }
    }
  }
})
