import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../aesconnect/dist',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/auth': 'http://localhost:5000',
      '/posts': 'http://localhost:5000',
      '/groups': 'http://localhost:5000',
      '/messages': 'http://localhost:5000',
      '/utils': 'http://localhost:5000',
      '/notifications': 'http://localhost:5000',
    }
  }
})
