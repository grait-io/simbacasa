import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  optimizeDeps: {
    exclude: [
      'vue-demi',
      'chunk-EAUNOWDZ',
      'chunk-YFT6OQ5R'
    ],
    force: true,
    entries: [
      './src/**/*.vue',
      './src/**/*.ts'
    ]
  },
  build: {
    target: 'esnext',
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router', 'pinia']
        }
      }
    }
  }
})
