import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  base: '/static/vue/', // Django static 配下
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate', // SW 自動更新
      filename: 'sw.js',           // 出力 SW ファイル名
      includeAssets: [
        'favicon.ico',
        'pwa-192x192.png',
        'pwa-512x512.png',
        'pwa-maskable-512x512.png'
      ],
      manifest: {
        name: 'ClipCook',
        short_name: 'ClipCook',
        description: '家族で使えるレシピアプリ',
        start_url: "/",
        display: 'standalone',
        background_color: '#ffffff',
        theme_color: '#ffffff',
        lang: 'jp',
        scope: "/",
        icons: [
          { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' },
          { src: 'pwa-maskable-512x512.png', sizes: '512x512', type: 'maskable' }
        ]
      },
      workbox: {
        // SW にプリキャッシュする固定ファイル
        globPatterns: ['**/*.{js,css,png,woff2,ico,webmanifest,html}']
      }
    })
  ],

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },

  build: {
    outDir: '../static/vue',  // Django static/vue 配下に出力
    emptyOutDir: true,
    assetsDir: 'assets',      // JS/CSS/フォント用
    cssCodeSplit: true,
    rollupOptions: {
      input: 'index.html',
      output: {
        entryFileNames: `assets/index.js`,
        chunkFileNames: `assets/[name].js`,
        assetFileNames: `assets/[name].[ext]`,
      }
    }
  },

  server: {
    proxy: {
      '/exercise/api': 'http://127.0.0.1:8000',
      '/api': 'http://127.0.0.1:8000'
    },
    fs: {
      allow: [
        path.resolve(__dirname),
        path.resolve(__dirname, '../node_modules')
      ]
    }
  }
})
