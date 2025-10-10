<template>
    <div class="bookmark-page-container">

      
      <header class="header">
        <i class="fa-solid fa-bookmark header-icon"></i>
        <h1>ブックマークしたレシピ</h1>
      </header>
  
      <!-- ローディングメッセージ -->
      <div v-if="loading" class="loading-message">
        <i class="fa-solid fa-spinner fa-spin"></i> レシピを読み込み中...
      </div>
  
      <!-- 認証エラーメッセージ -->
      <div v-else-if="!isAuthenticated" class="empty-message authentication-error">
          <i class="fa-solid fa-lock text-red-500 mb-4 text-3xl"></i>
          <p class="text-xl font-semibold">ログインが必要です</p>
          <p>ブックマークリストを表示するには、サインインしてください。</p>
      </div>

      
  
      <!-- レシピ一覧（データがある場合） -->
<!-- BookmarkList.vue -->
<div v-else-if="recipes.length > 0" class="recipe-grid">
  <div
    v-for="recipe in recipes"
    :key="recipe.id"
    class="recipe-card"
  >
    <!-- クリックで詳細ページへ -->
    <router-link
      :to="{ name: 'RecipeDetail', params: { id: recipe.id } }"
      class="block hover:opacity-90 transition"
    >
      <img :src="recipe.photo" :alt="recipe.title" class="recipe-image" />
    </router-link>

    <div class="recipe-info">
        <h2 class="recipe-title">
            {{ getDisplayTitle(recipe) }}
        </h2>

      <p class="recipe-user">投稿者: {{ recipe.user }}</p>
<!-- いいねボタン -->
<button @click="toggleLike(recipe)" class="likes-info-button">
  <i :class="recipe.liked ? 'fa-solid fa-heart liked' : 'fa-regular fa-heart'"></i>
  <span>{{ recipe.like_count || 0 }}</span>
</button>


        <!-- 追加: ブックマーク削除ボタン -->
    <button
      @click="removeBookmark(recipe.id)"
      class="bookmark-remove-btn"
    >
      ブックマーク解除
    </button>
    </div>
  </div>
</div>

  
      <!-- データがない場合 -->
      <div v-else class="empty-message">
        <i class="fa-solid fa-face-sad-cry text-gray-500 mb-4 text-3xl"></i>
        <p class="text-xl font-semibold">ブックマークされたレシピはまだありません</p>
        <p>タイムラインで新しいレシピを見つけて、お気に入りに追加しましょう！</p>
      </div>
    </div>
  </template>
  
  <script>
  // axiosはプロジェクトで利用可能と仮定します
  import axios from 'axios';
  
  export default {
    data() {
      return {
        recipes: [],
        loading: true,
        isAuthenticated: true, // 初期状態はtrueとして、APIコールで401が返ってきたらfalseにする
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
          // Djangoで設定したAPIエンドポイントを呼び出し
          const res = await axios.get("http://127.0.0.1:8000/api/bookmarks/list/", {
            // 認証情報をサーバーに送るため、withCredentialsが必要です
            withCredentials: true,
          });
  
          // データのフィールド名: RecipeSerializerの fields = ["id", "user", "photo", "memo", ...] に合わせる
          this.recipes = res.data;
          this.isAuthenticated = true;
  
        } catch (error) {
          if (error.response && error.response.status === 401) {
            // 認証エラー (未ログイン)
            console.error("Authentication required. Please log in.");
            this.isAuthenticated = false;
          } else {
            console.error("Failed to fetch bookmarked recipes:", error);
          }
        } finally {
          this.loading = false;
        }
      },
      async toggleLike(recipe) {
  try {
    // GETでもPOSTでもOKですが、今回はPOSTでトグル
    const csrfToken = this.getCookie('csrftoken');
    const res = await axios.post(
      "http://127.0.0.1:8000/api/likes/toggle/",
      {
        model: "recipes.Recipe",
        object_id: recipe.id
      },
      {
        withCredentials: true,
        headers: { "X-CSRFToken": csrfToken }
      }
    );

    // Vueデータを更新
    recipe.liked = res.data.liked;
    recipe.like_count = res.data.like_count;

  } catch (error) {
    console.error("いいね操作に失敗しました:", error);
    if (error.response && error.response.status === 401) {
      this.isAuthenticated = false;
    }
  }
},
      async removeBookmark(recipeId) {
    try {
        const csrfToken = this.getCookie('csrftoken');  // CookieからCSRFトークンを取得
        await axios.post(
        "http://127.0.0.1:8000/api/bookmarks/toggle/",
        {
          model: "recipes.Recipe",
          object_id: recipeId
        },
        { withCredentials: true,
        headers: {
          "X-CSRFToken": csrfToken  // ← ここを追加
        } 
       }
      );
      // 削除後に配列から該当レシピを除外
      this.recipes = this.recipes.filter(r => r.id !== recipeId);
    } catch (error) {
      console.error("ブックマーク解除に失敗しました:", error);
    }
  },

// Cookie取得用ヘルパー
getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}
    },
    mounted() {
      this.fetchBookmarkedRecipes();
    },
  };
  </script>
  
  <!-- Tailwind CSSクラスを使用して美しくスタイリング -->
  <style scoped>
  /* Tailwind CSSがロードされていることを前提に、カスタムスタイルを適用 */
  .bookmark-page-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: 'Inter', sans-serif;
    background-color: #f7f7f7;
    min-height: 100vh;
  }
  
  .header {
    display: flex;
    align-items: center;
    padding: 20px 0;
    margin-bottom: 30px;
    border-bottom: 3px solid #e0e0e0;
  }
  
  .header h1 {
    font-size: 32px;
    font-weight: 900;
    color: #2c3e50;
    margin-left: 15px;
  }
  
  .header-icon {
      font-size: 36px;
      color: #ffd700; /* ゴールドのような色 */
      text-shadow: 0 0 5px rgba(255, 215, 0, 0.5);
  }
  
  .loading-message, .empty-message {
    text-align: center;
    padding: 80px 20px;
    color: #7f8c8d;
    font-size: 20px;
    background: white;
    border-radius: 12px;
    margin-top: 20px;
  }
  
  .loading-message i {
      margin-right: 10px;
      color: #3498db;
  }
  
  .authentication-error {
      background-color: #ffebee;
      border: 1px solid #e74c3c;
      color: #c0392b;
  }
  
  .empty-message p {
      margin: 10px 0;
  }
  
 .recipe-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* PCでは3列 */
  gap: 24px;
  width: 100%;
}

@media (max-width: 1024px) {
  .recipe-grid {
    grid-template-columns: repeat(2, 1fr); /* タブレットは2列 */
  }
}

@media (max-width: 768px) {
  .recipe-grid {
    grid-template-columns: 1fr; /* スマホは1列 */
    gap: 15px;
  }
}


  
  .recipe-card {
    background: white;
    border-radius: 16px;
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.05);
    overflow: hidden;
    transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
  }
  
  .recipe-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 25px rgba(0, 0, 0, 0.1);
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

  .likes-info-button ::v-deep(.fa-solid) {
  color: #e74c3c;
}

  
  .likes-info-button {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 16px;
  background: none;
  border: none;
  cursor: pointer;
}

.likes-info-button i {
  font-size: 18px;
  color: #e74c3c; /* liked なら赤に */
  transition: transform 0.2s ease;
}

.likes-info-button i.liked {
  color: #e74c3c; /* 赤 */
  transform: scale(1.2); /* ちょっと大きくしてアニメーション感 */
}

.likes-info-button span {
  color: #e74c3c;
  font-weight: 600;
}


  .bookmark-remove-btn {
   
    /* デザイン: 画像と同じオレンジ〜黄色のグラデーション */
    background: linear-gradient(135deg, #FFD75B 0%, #FF9933 100%); 
    color: #4a4a4a; /* 文字色は濃い色に */
    
    /* サイズを固定 */
    width: auto; 
    padding: 8px 12px;
    height: auto; 
    
    border-radius: 12px; /* 角丸を深くする */
    box-shadow: 0 4px 10px rgba(255, 175, 76, 0.6); /* 影で浮き上がらせる */
    border: 2px solid rgba(255, 255, 255, 0.8); /* 白い縁を追加 */
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 16px;
    font-weight: 700; /* 文字を太く */

 
  }
  
  
  /* モバイル対応 */
  @media (max-width: 768px) {
      .recipe-grid {
          grid-template-columns: 1fr;
          gap: 15px;
      }
      .bookmark-page-container {
          padding: 10px;
      }
      .header h1 {
          font-size: 24px;
      }
  }
  </style>
  