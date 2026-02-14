<template>
  <div class="bookmark-page-container">

   <!-- ヘッダー -->
<header class="header">
  <div class="header-left flex items-center">
    <i class="fa-solid fa-bookmark header-icon"></i>
    <h1>ブックマークしたレシピ</h1>
  </div>



  <!-- 右側に配置 -->
  <router-link
    to="/add-recipe"
    class="create-recipe-btn"
  >
    新規レシピを投稿
  </router-link>
</header>

  <!-- ソート選択 -->
  <select v-model="selectedSort" @change="sortRecipes" class="sort-select">
          <option value="newest">新着順</option>
          <option value="oldest">古い順</option>
          <option value="likes">いいね数順</option>
          <option value="bookmarks">ブックマーク数順</option>
  </select>

    <!-- ローディング -->
    <div v-if="loading" class="loading-message">
      <i class="fa-solid fa-spinner fa-spin"></i> レシピを読み込み中...
    </div>

    <!-- 認証エラー -->
    <div v-else-if="!isAuthenticated" class="empty-message authentication-error">
      <i class="fa-solid fa-lock text-red-500 mb-4 text-3xl"></i>
      <p class="text-xl font-semibold">ログインが必要です</p>
      <p>ブックマークリストを表示するには、サインインしてください。</p>
    </div>

    

    <!-- ブックマーク一覧 -->
    <div v-else-if="recipes.length > 0" class="recipe-grid">
      <div v-for="recipe in recipes" :key="recipe.id" class="recipe-card">
        <router-link :to="{ name: 'RecipeDetail', params: { id: recipe.id } }" class="block hover:opacity-90 transition">
          <img :src="recipe.photo" :alt="recipe.title" class="recipe-image" />
        </router-link>

        <div class="recipe-info">
          <h2 class="recipe-title">{{ getDisplayTitle(recipe) }}</h2>
          <p class="recipe-user">投稿者: {{ recipe.user }}</p>

          <button @click="toggleLike(recipe)" class="likes-info-button">
            <i :class="recipe.liked ? 'fa-solid fa-heart liked' : 'fa-regular fa-heart'"></i>
            <span>{{ recipe.like_count || 0 }}</span>
          </button>

          <button @click="removeBookmark(recipe.id)" class="bookmark-remove-btn">
            ブックマーク解除
          </button>
        </div>
      </div>
    </div>

    <!-- データなし -->
    <div v-else class="empty-message">
      <i class="fa-solid fa-face-sad-cry text-gray-500 mb-4 text-3xl"></i>
      <p class="text-xl font-semibold">ブックマークされたレシピはまだありません</p>
      <p>タイムラインで新しいレシピを見つけて、お気に入りに追加しましょう！</p>
    </div>

    <!-- おすすめレシピ -->
    <section class="recommendation-section mt-12">
  <h2 class="section-title recommendation-title">おすすめレシピ</h2>

  <div v-if="loadingRecommendations" class="loading-message">
    <i class="fa-solid fa-spinner fa-spin"></i> おすすめを読み込み中...
  </div>

  <div v-else-if="recommendedRecipes.length === 0" class="empty-message">
    おすすめがありません。
  </div>

  <div v-else class="recommendation-slider-container">
    <button class="nav-button prev-button" @click="slidePrev">&lt;</button>

    <div class="recommendation-grid">
      <div v-for="recipe in recommendedRecipes" :key="recipe.id" class="recipe-card recommendation-card">
        <router-link :to="{ name: 'RecipeDetail', params: { id: recipe.id } }" class="block hover:opacity-90 transition">
          <img :src="recipe.photo" :alt="recipe.title" class="recipe-image" />
        </router-link>

        <div class="recipe-info">
          <h2 class="recipe-title">{{ getDisplayTitle(recipe) }}</h2>
          <p class="recipe-user">投稿者: {{ recipe.user }}</p>
          <button @click="toggleLike(recipe)" class="likes-info-button">
            <i :class="recipe.liked ? 'fa-solid fa-heart liked' : 'fa-regular fa-heart'"></i>
            <span>{{ recipe.like_count || 0 }}</span>
          </button>
        </div>
      </div>
    </div>

    <button class="nav-button next-button" @click="slideNext">&gt;</button>
  </div>
</section>

    
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      recipes: [],
      loading: true,
      isAuthenticated: true,
      recommendedRecipes: [],
      loadingRecommendations: false,
      selectedSort: "newest",
    };
  },
  methods: {
    getDisplayTitle(recipe) {
      if (recipe.title) return recipe.title;
      if (recipe.memo) {
        const firstLine = recipe.memo.split('\n')[0].replace(/^===\s*/, '').replace(/\s*===$/, '');
        return firstLine || 'タイトルなし';
      }
      return 'タイトルなし';
    },

    async fetchBookmarkedRecipes() {
      this.loading = true;
      try {
        const res = await axios.get("http://127.0.0.1:8000/api/bookmarks/list/", { withCredentials: true });
        this.recipes = res.data;
        this.isAuthenticated = true;
      } catch (error) {
        if (error.response && error.response.status === 401) this.isAuthenticated = false;
        else console.error(error);
      } finally {
        this.loading = false;
      }
    },
    async fetchBookmarkedRecipes() {
      this.loading = true;
      try {
        const res = await axios.get("http://127.0.0.1:8000/api/bookmarks/list/", { withCredentials: true });
        this.recipes = res.data;
        this.sortRecipes(); // 初期表示もソート適用
        this.isAuthenticated = true;
      } catch (error) {
        if (error.response && error.response.status === 401) this.isAuthenticated = false;
        else console.error(error);
      } finally {
        this.loading = false;
      }
    },

    sortRecipes() {
      if (this.selectedSort === "newest") {
        this.recipes.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      } else if (this.selectedSort === "oldest") {
        this.recipes.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
      } else if (this.selectedSort === "likes") {
        this.recipes.sort((a, b) => (b.like_count || 0) - (a.like_count || 0));
      } else if (this.selectedSort === "bookmarks") {
        this.recipes.sort((a, b) => (b.bookmark_count || 0) - (a.bookmark_count || 0));
      }
    },

    async toggleLike(recipe) {
      try {
        const csrfToken = this.getCookie('csrftoken');
        const res = await axios.post(
          "http://127.0.0.1:8000/api/likes/toggle/",
          { model: "recipes.Recipe", object_id: recipe.id },
          { withCredentials: true, headers: { "X-CSRFToken": csrfToken } }
        );
        recipe.liked = res.data.liked;
        recipe.like_count = res.data.like_count;
      } catch (error) {
        if (error.response && error.response.status === 401) this.isAuthenticated = false;
        console.error(error);
      }
    },

    async removeBookmark(recipeId) {
      try {
        const csrfToken = this.getCookie('csrftoken');
        await axios.post(
          "http://127.0.0.1:8000/api/bookmarks/toggle/",
          { model: "recipes.Recipe", object_id: recipeId },
          { withCredentials: true, headers: { "X-CSRFToken": csrfToken } }
        );
        this.recipes = this.recipes.filter(r => r.id !== recipeId);
      } catch (error) {
        console.error(error);
      }
    },

    getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
      return null;
    },

    async fetchRecommendations() {
      this.loadingRecommendations = true;
      try {
        const res = await axios.get("http://127.0.0.1:8000/api/recommendation/recommended/", { withCredentials: true });
        this.recommendedRecipes = res.data;
      } catch (error) {
        console.error(error);
      } finally {
        this.loadingRecommendations = false;
      }
    },
    slidePrev() {
    const container = this.$el.querySelector(".recommendation-grid");
    container.scrollBy({ left: -260, behavior: "smooth" });
  },
  slideNext() {
    const container = this.$el.querySelector(".recommendation-grid");
    container.scrollBy({ left: 260, behavior: "smooth" });
  },
  },
  mounted() {
    this.fetchBookmarkedRecipes();
    this.fetchRecommendations();
  }
};
</script>

<style scoped>
/* BookmarkList.vue 全体スタイル（更新版） */
.bookmark-page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Inter', sans-serif;
  min-height: 100vh;
}

/* ヘッダー */
.header {
  display: flex;
  align-items: center;
  padding: 20px 0;
  margin-bottom: 30px;
  border-bottom: 3px solid #e0e0e0;
  justify-content: space-between; 
}

.create-recipe-btn {
  background: linear-gradient(135deg, #FFD75B 0%, #FF9933 100%);
  color: #4a4a4a;
  padding: 8px 14px;
  border-radius: 12px;
  font-weight: 700;
  text-decoration: none;
  box-shadow: 0 4px 10px rgba(255,175,76,0.6);
  transition: transform 0.2s, box-shadow 0.2s;
}
.create-recipe-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(255,175,76,0.8);
}
.header h1 {
  font-size: 32px;
  font-weight: 900;
  color: #2c3e50;
  margin-left: 15px;
}
.header-icon {
  font-size: 36px;
  color: #ffd700;
  text-shadow: 0 0 5px rgba(255, 215, 0, 0.5);
}

/* ローディング / 空メッセージ */
.loading-message, .empty-message {
  text-align: center;
  padding: 80px 20px;
  color: #7f8c8d;
  font-size: 20px;
  background: white;
  border-radius: 12px;
  margin-top: 20px;
}
.authentication-error {
  background-color: #ffebee;
  border: 1px solid #e74c3c;
  color: #c0392b;
}
.empty-message p {
  margin: 10px 0;
}

/* ブックマーク一覧グリッド */
.recipe-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  width: 100%;
  margin-top: 20px;
}
@media (max-width: 1024px) { .recipe-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .recipe-grid { grid-template-columns: 1fr; gap: 15px; } }

/* カード */
.recipe-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 15px rgba(0,0,0,0.05);
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
}
.recipe-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 25px rgba(0,0,0,0.1);
}
.recipe-image {
  width: 100%;
  height: 250px;
  object-fit: cover;
  display: block;
}
.recipe-info {
  padding: 18px;
}
.recipe-title {
  font-size: 22px;
  font-weight: 700;
  color: #34495e;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.recipe-user {
  font-size: 14px;
  color: #95a5a6;
  margin-bottom: 12px;
}

/* いいねボタン */
.likes-info-button {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 16px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 0;
}
.likes-info-button i {
  font-size: 18px;
  color: #e74c3c;
  transition: transform 0.2s ease;
}
.likes-info-button i.liked {
  color: #e74c3c;
  transform: scale(1.2);
}
.likes-info-button span {
  color: #e74c3c;
  font-weight: 600;
}

/* ブックマーク解除ボタン */
.bookmark-remove-btn {
  margin-top: 10px;
  background: linear-gradient(135deg, #FFD75B 0%, #FF9933 100%);
  color: #4a4a4a;
  padding: 8px 12px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(255, 175, 76, 0.6);
  border: 2px solid rgba(255,255,255,0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.bookmark-remove-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(255,175,76,0.8);
}

/* おすすめセクションのタイトル */
.recommendation-title {
  color: #da7e0d; /* ハイコントラスト文字色 */
  font-size: 26px;
  font-weight: 800;
  margin-bottom: 15px;
}

/* おすすめセクション */
.recommendation-section {
  margin-top: 60px;
  background-color: #dcecfc; /* 控えめな背景色 */
  padding: 20px;
  border-radius: 12px;
}


/* おすすめレシピ横スライドグリッド（最大4枚） */
.recommendation-grid {
  display: flex;
  gap: 20px;
  overflow-x: auto;
  padding-bottom: 10px;
}
.recommendation-card {
  min-width: 250px;
  flex: 0 0 auto;
}

.recommendation-slider-container {
  position: relative;
}

.nav-button {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  background-color: rgba(255, 255, 255, 0.8);
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
}

.prev-button {
  left: -10px; /* 左端より少し外に */
}

.next-button {
  right: -10px; /* 右端より少し外に */
}

/* ソートセレクト */
.sort-select {
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-weight: 600;
  background-color: white;
  cursor: pointer;
}

/* モバイル対応 */
@media (max-width: 768px) {
  .bookmark-page-container { padding: 10px; }
  .header h1 { font-size: 24px; }
  .recipe-title { font-size: 18px; }
  .recipe-user { font-size: 12px; }
  .bookmark-remove-btn { font-size: 14px; padding: 6px 10px; }
  .recommendation-section .section-title { font-size: 20px; }
  .recommendation-card { min-width: 200px; }
}

</style>
