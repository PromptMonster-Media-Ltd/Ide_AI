/**
 * vite.config.ts — Vite configuration for Ide/AI frontend.
 * Uses @tailwindcss/vite plugin and proxies /api to the FastAPI backend.
 */
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true }
    }
  }
})
