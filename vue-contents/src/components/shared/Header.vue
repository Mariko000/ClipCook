<template>
  <nav class="navbar navbar-expand-lg" style="background-color: #FFFDF7; position: relative;">
    <div class="container-fluid">

      <!-- トグルボタン（常に左） -->
      <button class="navbar-toggler" type="button" @click="collapsed = !collapsed">
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- 小画面中央ロゴ -->
      <a class="navbar-brand mx-auto d-lg-none position-absolute start-50 translate-middle-x"
         href="http://127.0.0.1:8000/">ClipCook</a>

      <!-- collapse 内 -->
      <div :class="['collapse navbar-collapse', collapsed ? 'show' : '']">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <!-- PC・タブレット用ロゴ -->
          <li class="nav-item d-none d-lg-block">
            <a class="navbar-brand" href="http://127.0.0.1:8000/">ClipCook</a>
          </li>

          <!-- ナビリンク -->
          <li class="nav-item">
            <router-link class="nav-link" to="/" active-class="active">Quantify</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/add-recipe" active-class="active">Post Recipe</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/timeline" active-class="active">Timeline</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/bookmarks" active-class="active">Bookmarks</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/my-album">My Recipe Album</router-link>
          </li>
        </ul>

        <!-- 右端ユーザー情報 -->
  <div class="search-and-user">
  <form class="custom-search-form" @submit.prevent="handleSearch">
    <input
      v-model="query"
      class="form-control custom-search-input"
      type="search"
      placeholder="Search recipes or tags..."
    />
    <button class="btn btn-outline-secondary" type="submit">Search</button>
  </form>

        <div v-if="currentUser">
          <a :href="'http://127.0.0.1:8000/users/profile/'" class="text-decoration-none">
            <img v-if="currentUser.avatar_url" :src="currentUser.avatar_url" class="user-avatar" />
            <span class="username">{{ currentUser.username }}</span>
          </a>
        </div>
        <div v-else>
          <router-link to="/login" class="nav-link">ログイン</router-link>
        </div>
      </div>
    </div>

    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()               // routerインスタンスを取得

const collapsed = ref(false)
const currentUser = ref(null)

const query = ref("")
function handleSearch() {
  router.push(`/search?q=${encodeURIComponent(query.value)}`)
}


onMounted(async () => {
  try {
    const res = await fetch('http://127.0.0.1:8000/users/api/current-user/', {
      credentials: 'include'
    })
    if (!res.ok) throw new Error('APIエラー')
    currentUser.value = await res.json()
  } catch (err) {
    console.error(err)
  }
})
</script>

<style scoped>

.navbar-brand {
  font-family: 'Arial Rounded MT Bold', 'Helvetica Rounded', sans-serif;
  font-weight: bold;
  font-size: 2rem;
  color: #333333;
  letter-spacing: 0.5px;
  text-decoration: none;
}

/* ================================
  ナビゲーションリンク
=============================== */

.nav-link {
  font-family: 'Quicksand', sans-serif;
  font-weight: bold;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 8px;
  object-fit: cover;
}

.username {
  color: #333333;
  font-weight: bold;
  text-decoration: none;
}

/* フォーム全体を左寄せ（ロゴ側に近づける） */
.custom-search-form {
  margin-left: 0;  /* 必要に応じて px で微調整 */
}

/* 入力欄の右側マージン */
.custom-search-input {
  margin-right: 8px; /* ボタンとの間隔 */
}

/* 検索ボタンとユーザーアバターの間に余白 */
.search-and-user {
  display: flex;
  align-items: center;
  gap: 24px; /* ボタンとアバターの間隔を広めに設定 */
}

/* アバターと名前の間の余白 */
.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  margin-right: 8px;
}


/* 小画面のとき中央タイトルを固定 */
@media (max-width: 991.98px) {
  .navbar .navbar-brand.mx-auto {
    top: 0.5rem; /* 高さを調整 */
  }
}

/* タブレット以下の画面サイズでは縦並びにする */
@media (max-width: 991.98px) {
  .search-and-user {
    flex-direction: column;  /* 縦並び */
    align-items: flex-start; /* 左寄せ、中央寄せしたければ center */
    gap: 8px;                /* 上下の間隔 */
  }

  .custom-search-form {
    width: 100%;             /* 検索バーを横幅いっぱいに */
  }

  /* ユーザー情報を横並びにしたい場合のみ */
  .search-and-user > div {
    display: flex;
    align-items: center;
    width: 100%;             /* 必要に応じて横幅いっぱい */
    justify-content: flex-start; /* 左寄せ */
  }
}

</style>
