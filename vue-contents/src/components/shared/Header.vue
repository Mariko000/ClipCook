<template>
  <nav class="custom-navbar">
    <div class="custom-container">
      <!-- 左側：ロゴとナビリンク -->
      <div class="left-section">
        <a class="custom-brand" href="http://127.0.0.1:8000/">FitSpin</a>
        <ul class="custom-nav-list">
          <li class="custom-nav-item">
            <router-link class="custom-nav-link" to="/" active-class="active">カスタマイザー</router-link>
          </li>
          <li class="custom-nav-item">
            <router-link class="custom-nav-link" to="/add-recipe" active-class="active">レシピ投稿</router-link>
          </li>
          <li class="custom-nav-item">
            <router-link class="custom-nav-link" to="/timeline" active-class="active">タイムライン</router-link>
          </li>
          <li class="custom-nav-item">
            <router-link class="custom-nav-link" to="/bookmarks" active-class="active">ブックマーク</router-link>
          </li>
          <li class="custom-nav-item">
            <router-link to="/my-album">マイレシピアルバム</router-link>
        </li>
        </ul>
      </div>

      <!-- 右側：ユーザー情報 -->
      <div v-if="currentUser" class="user-info">
        <a v-if="currentUser"
        :href="'http://127.0.0.1:8000/users/profile/'" class="user-info">
        <img
          v-if="currentUser.avatar_url"
          :src="currentUser.avatar_url"
          alt="User Avatar"
          class="user-avatar"
        />
        <span class="username">{{ currentUser.username }}</span>
      </a>
      </div>

      <!-- 未ログイン時 -->
      <div v-else class="user-info">
        <router-link to="/login" class="custom-nav-link">ログイン</router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const currentUser = ref(null)

onMounted(async () => {
  try {
    const res = await fetch('http://127.0.0.1:8000/users/api/current-user/', {
      credentials: 'include'
    })
    if (!res.ok) throw new Error('APIエラー')
    currentUser.value = await res.json()
    console.log('ログイン中ユーザー:', currentUser.value)
  } catch (err) {
    console.error('ユーザー情報取得に失敗:', err)
  }
})
</script>

<style scoped>
.custom-navbar {
  background-color: #5A4DA0;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  position: relative;
  z-index: 1000;
}

.custom-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  height: 70px;
  padding: 0 20px;
}

.left-section {
  display: flex;
  align-items: center;
}

/* ロゴ */
.custom-brand {
  font-family: 'Arial Rounded MT Bold','Helvetica Rounded',sans-serif;
  font-weight: bold;
  font-size: 1.6rem;
  color: #fff;
  text-decoration: none;
  margin-right: 30px;
}

/* ナビリンク */
.custom-nav-list {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 15px;
}

.custom-nav-link {
  color: #fff;
  font-weight: bold;
  text-decoration: none;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
  transition: color 0.3s, text-shadow 0.3s;
}

.custom-nav-link:hover {
  color: #FFD93D;
  text-shadow: 2px 2px 3px rgba(0,0,0,0.6);
}

/* ユーザー情報右端 */
.user-info {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  color: #fff;
  white-space: nowrap;
  text-decoration: none; /* ← 下線を消す */
}

/* a 内の span も下線が付く場合は明示的に消す */
.user-info .username {
  text-decoration: none;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 10px;
}

/* ================================
  レスポンシブ対応
=============================== */

@media (max-width: 768px) {
  .custom-container {
    height: auto;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .custom-brand {
    font-size: 1.4rem;
    margin-right: 0;
  }
  .custom-nav-list {
    flex-wrap: wrap;
    gap: 10px;
  }
  .user-info {
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .custom-container {
    padding: 0 12px;
  }
  .custom-brand {
    font-size: 1.2rem;
  }
  .custom-nav-list {
    flex-direction: column;
    width: 100%;
    gap: 6px;
  }
  .custom-nav-link {
    font-size: 0.9rem;
  }
  .user-info {
    font-size: 0.8rem;
  }
}
</style>
