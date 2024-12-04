import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  optimizeDeps: {
    exclude: [
      'chunk-EAUNOWDZ',
      'chunk-YFT6OQ5R'
    ],
    force: true,
    entries: [
      './src/**/*.vue',
      './src/**/*.ts'
    ],
    include: ['vue-demi']
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
  },
  resolve: {
    dedupe: ['vue-demi', 'vue'],
    alias: {
      'vue-demi': path.resolve(__dirname, 'node_modules/vue-demi/lib/index.mjs')
    }
  }
})
