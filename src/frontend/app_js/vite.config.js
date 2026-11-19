import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
//
// The Vite dev server proxies the webinput backend's API paths to
// localhost:5279, which `dev_webinput.py` keeps headless for exactly this
// reason (see .clinerules/skills/webinput-backend).
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/schema': { target: 'http://localhost:5279', changeOrigin: true },
      '/submit': { target: 'http://localhost:5279', changeOrigin: true },
      '/health': { target: 'http://localhost:5279', changeOrigin: true },
      '/assets': { target: 'http://localhost:5279', changeOrigin: true },
    }
  },
  resolve: {
    alias: {
      vue: 'vue/dist/vue.esm-bundler.js',
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    }
  },
})
