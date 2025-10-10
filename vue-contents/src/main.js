// vue-contents/src/main.js
import { createApp } from 'vue'
import App from './App.vue'           // ルートはApp.vueにする
import router from './router/index.js'         // ルーターをインポート
import axios from 'axios'
import './assets/css/main.css'
import UserProfile from './components/UserProfile.vue'


// ✅ Django の HTML 側で埋め込まれた avatar-url を取得
const avatarUrlElement = document.getElementById('avatar-url')
const avatarUrl = avatarUrlElement ? avatarUrlElement.textContent.trim() : null
console.log('✅ Avatar URL provided to Vue:', avatarUrl)


axios.defaults.withCredentials = true
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

const app = createApp(App)            // App.vueをベースにアプリ生成
app.component('UserProfile', UserProfile) // ここでグローバル登録
// ✅ provide で Vue 全体に注入
app.provide('avatarUrl', avatarUrl)
app.use(router)                       // ルーターを有効化
app.mount('#app')                     // マウント
