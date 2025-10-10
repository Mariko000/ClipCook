<!-- src/App.vue -->
<template>
  <Header />
  <!-- ★修正点: router-viewをmain-content-wrapperで囲む★ -->
  <main class="main-content-wrapper"> 
    <router-view />   <!-- ここに各ページがレンダリングされる (Timelineを含む) -->
  </main>
</template>

<script setup>
import Header from './components/shared/Header.vue'
import './assets/css/main.css'
import { onMounted, provide } from 'vue'

// HTML の data-avatar-url から取得
const avatarUrl = document.getElementById('app').dataset.avatarUrl
provide('avatarUrl', avatarUrl)

onMounted(() => {
  console.log('App mounted!')
})


</script>

<style>
/* App.vue内またはグローバルCSSで設定 */

/* body の設定は base.css (min-height: 100vh) で十分なため、ここではシンプルに */
body {
  padding:0;
  margin:0;
  width: 100%;
}

/* ★修正点: #appをFlexコンテナ化し、Headerとmainを縦に配置する★ */
#app {
  display: flex;
  flex-direction: column; /* ←縦に積む */
  min-height: 100vh;      /* 画面の高さを確保 */
  padding:0;
  margin:0;
  width: 100%;
}

/* ★修正点: main-content-wrapper が残りの高さを全て占有する★ */
.main-content-wrapper {
  flex-grow: 1; /* Headerが占有した残りの高さを全て取得する */
  overflow: hidden; /* スクロールはTimeline内部のSwiperに任せる */
  width: 100%;
}

/* もし body に flex が当たっている場合はリセット */
body {
  display: block; /* もしくは flex-direction:column; */
}
</style>
