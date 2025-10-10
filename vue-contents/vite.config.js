// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  base: '/',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    cssCodeSplit: true,
    rollupOptions: {
      input: 'index.html',
      output: {
        entryFileNames: `assets/[name]-[hash].js`,
        chunkFileNames: `assets/[name]-[hash].js`,
        assetFileNames: `assets/[name]-[hash].[ext]`,
      },
    },
  },
  server: {
    proxy: {
      // Django 側に飛ばしたいパスを書いておく
      //開発サーバー（http://127.0.0.1:5173）→ Vite の proxy 機能 → Django サーバー（http://127.0.0.1:8000）に転送
      '/exercise/api': 'http://127.0.0.1:8000',
      '/api': 'http://127.0.0.1:8000',
    },
    fs: {
      // 親ディレクトリの node_modules も許可
      allow: [
        path.resolve(__dirname),              // vue-contents
        path.resolve(__dirname, '../node_modules')  // PortionCustomizer/node_modules
      ]
    }
  },
})
