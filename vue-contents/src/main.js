// vue-contents/src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router/index.js'
import axios from 'axios'
import './assets/css/main.css'
import UserProfile from './components/UserProfile.vue'
import { useQuantifyStore } from '@/stores/quantifyStore'
import { registerSW } from 'virtual:pwa-register'

// Django の HTML 側で埋め込まれた avatar-url を取得
const avatarUrlElement = document.getElementById('avatar-url')
const avatarUrl = avatarUrlElement ? avatarUrlElement.textContent.trim() : null
console.log('Avatar URL provided to Vue:', avatarUrl)

// Vue アプリを作成（app を最初に作る）
const app = createApp(App)

// Pinia ストア登録
const pinia = createPinia()
app.use(pinia)

// Axios 設定
axios.defaults.withCredentials = true
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

//  グローバル登録
app.component('UserProfile', UserProfile)

// provide で全体に注入
app.provide('avatarUrl', avatarUrl)

// Router 有効化
app.use(router)

// マウント
app.mount('#app')


//  Service Worker はここで登録
const updateSW = registerSW({
  onNeedRefresh() {},
  onOfflineReady() {}
})

