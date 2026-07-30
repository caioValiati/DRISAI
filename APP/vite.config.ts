import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'

// O proxy mantém front e API na mesma origem em desenvolvimento, o que faz o
// cookie httpOnly de refresh funcionar sem depender de CORS com credenciais.
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
})
