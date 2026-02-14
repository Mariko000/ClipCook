<!-- UserProfile.vue -->
<!-- 使用中止 -->
<template>
    <img :src="avatarUrl" class="avatar" />
  </template>
  
  <script setup>
  import { inject } from 'vue'
  const avatarUrl = inject('avatarUrl')  // HTML から渡された URL を受け取る
  </script>
  
  <style>
  .avatar {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    object-fit: cover;
  }
  </style>
  