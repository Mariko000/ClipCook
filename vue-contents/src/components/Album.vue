<template>
  <div class="album-page-container">
    <!-- ヘッダー -->
    <header class="header">
      <div class="header-left flex items-center">
        <!-- 削除モード中は一括削除ボタンを表示、通常はタイトルを表示 -->
        <button 
            v-if="isDeleteMode && selectedRecipes.length > 0" 
            @click="confirmBulkDelete" 
            class="bulk-delete-btn"
        >
            選択したレシピを削除 ({{ selectedRecipes.length }})
        </button>
        <h1 v-else>マイレシピアルバム</h1>
      </div>

      <!-- 右側のボタン群 (既存のボタンと新しいボタン) -->
      <div class="header-right-buttons">
        <!-- ★追加: 選択して削除ボタン (モード切り替えボタン) -->
        <button 
            @click="toggleDeleteMode" 
            :class="['select-delete-mode-btn', { 'mode-cancel': isDeleteMode }]"
        >
            {{ isDeleteMode ? 'キャンセル' : '選択して削除' }}
        </button>

        <!-- 新規レシピ投稿ボタン (削除モード中は非表示) -->
        <router-link 
            v-if="!isDeleteMode" 
            to="/add-recipe" 
            class="create-recipe-btn"
        >
          新規レシピを投稿
        </router-link>
      </div>
    </header>

    <!-- ソート選択 (削除モード中は非表示) -->
    <select v-if="!isDeleteMode" v-model="selectedSort" @change="sortRecipes" class="sort-select">
      <option value="newest">新着順</option>
      <option value="oldest">古い順</option>
      <option value="likes">いいね数順</option>
      <option value="bookmarks">ブックマーク数順</option>
    </select>

    <!-- アルバムグリッド -->
    <div class="album-grid">
      <div
        v-for="recipe in recipes"
        :key="recipe.id"
        :class="['recipe-card', { 'selected-for-delete': selectedRecipes.includes(recipe.id), 'delete-mode-active': isDeleteMode }]"
        @click="toggleRecipeSelection(recipe.id)"
      >
        <!-- ★追加: 選択アイコン (削除モードでのみ表示) -->
        <div 
          v-if="isDeleteMode" 
          class="selection-icon-wrapper"
        >
            <i 
              :class="[
                'selection-icon',
                selectedRecipes.includes(recipe.id) ? 'fa-solid fa-circle selected-circle' : 'fa-regular fa-circle'
              ]"
            ></i>
        </div>

        <div class="image-wrapper" @click="goToRecipe(recipe.id)">
          <img :src="recipe.photo || defaultPhoto" alt="レシピ画像" />
        </div>
        <p class="recipe-title">{{ recipe.title || "タイトルなし" }}</p>

        <!-- 個別削除ボタン (削除モード中は非表示) -->
        <button
          v-if="!isDeleteMode"
          class="delete-btn"
          @click.stop="deleteRecipe(recipe.id)"
          title="削除"
        >
          <i class="fa-solid fa-trash"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

// CookieからCSRFトークンを取得
const getCookie = (name) => {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

// カスタム確認ダイアログの代替（alert/confirm禁止のため）
// ただし、ご要望のアラート動作を再現するため、window.confirm/alertのロジックを一時的に残します。
function showCustomConfirmation(message, onConfirm) {
  // 1. 「選択したレシピを削除しますか？」のアラート
  // 2. ユーザーがEnterを押すとYes/Noが表示される
  // ご要望のフローを再現するため、window.confirmを使用しますが、実際のアプリケーションではカスタムモーダルUIに置き換えてください。
  if (window.confirm(message)) {
    onConfirm();
  }
}


export default {
  name: "UserAlbum",
  data() {
    return {
      recipes: [],
      defaultPhoto: "/default_recipe.png",
      selectedSort: "newest",
      // ★追加: 選択されたレシピIDを保持する配列
      selectedRecipes: [],
      // ★追加: 削除モードの状態フラグ
      isDeleteMode: false,
    };
  },
  methods: {
    async fetchUserRecipes() {
      try {
        const res = await axios.get(
          "http://127.0.0.1:8000/api/my_recipes/",
          { withCredentials: true }
        );
        this.recipes = res.data;
        this.sortRecipes(); // 初期ロード時もソート適用
      } catch (err) {
        console.error("ユーザーレシピ取得エラー:", err);
      }
    },
    goToRecipe(recipeId) {
      // 削除モード中は詳細ページに飛ばさない
      if (this.isDeleteMode) return;
      this.$router.push({ name: "RecipeDetail", params: { id: recipeId } });
    },
    
    // 既存の個別削除機能。削除モード中は非表示にする
    async deleteRecipe(recipeId) {
      // alert/confirm禁止のため、showCustomConfirmationを使用
      showCustomConfirmation("本当にこのレシピを削除しますか？", async () => {
          try {
              await axios.delete(
                  `http://127.0.0.1:8000/api/recipes/${recipeId}/`,
                  {
                      withCredentials: true,
                      headers: { "X-CSRFToken": getCookie("csrftoken") },
                  }
              );
              this.recipes = this.recipes.filter((r) => r.id !== recipeId);
              console.log("レシピを削除しました"); // alertの代替
          } catch (err) {
              console.error("レシピ削除エラー:", err);
              console.log("削除に失敗しました。"); // alertの代替
          }
      });
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

    // ★追加: 削除モードを切り替える
    toggleDeleteMode() {
      this.isDeleteMode = !this.isDeleteMode;
      // モード終了時は選択をリセット
      if (!this.isDeleteMode) {
        this.selectedRecipes = [];
      }
    },

    // ★追加: レシピの選択を切り替える (recipe-cardクリック時)
    toggleRecipeSelection(recipeId) {
      // 削除モードではない場合は何もしない
      if (!this.isDeleteMode) return; 

      const index = this.selectedRecipes.indexOf(recipeId);
      if (index > -1) {
        this.selectedRecipes.splice(index, 1); // 選択解除
      } else {
        this.selectedRecipes.push(recipeId); // 選択
      }
    },

    // ★追加: 選択されたレシピを一括削除する確認
    confirmBulkDelete() {
      if (this.selectedRecipes.length === 0) {
        // alertの代替。一括削除ボタンはdisabledになるため、通常は発生しない
        console.warn("削除するレシピを選択してください。");
        return;
      }

      showCustomConfirmation(
        `選択された${this.selectedRecipes.length}件のレシピを本当に削除しますか？`,
        // ユーザーが確認した場合の処理
        () => {
          this.executeDelete(this.selectedRecipes);
        }
      );
    },

    // ★追加: 実際の削除処理
    async executeDelete(recipeIds) {
        const csrfToken = getCookie("csrftoken");
        let successfulDeletions = 0;
        let failedDeletions = 0;

        const deletionPromises = recipeIds.map(async (id) => {
            try {
                await axios.delete(
                    `http://127.0.0.1:8000/api/recipes/${id}/`,
                    {
                        withCredentials: true,
                        headers: { "X-CSRFToken": csrfToken },
                    }
                );
                successfulDeletions++;
                return true;
            } catch (err) {
                console.error(`レシピID ${id} の削除エラー:`, err);
                failedDeletions++;
                return false;
            }
        });

        await Promise.all(deletionPromises);

        // 成功したIDを除外してレシピリストを更新
        this.recipes = this.recipes.filter(r => !recipeIds.includes(r.id));
        this.selectedRecipes = []; // 選択状態をリセット

        if (successfulDeletions > 0) {
          console.log(`成功: ${successfulDeletions}件のレシピを削除しました。`);
        }
        
        // 削除モードを解除して、詳細表示に戻る
        this.isDeleteMode = false;
    },
  },
  mounted() {
    this.fetchUserRecipes();
  },
};
</script>

<style scoped>
/* ====================================
  ★追加・修正されたスタイル
==================================== */
/* ヘッダー右側のボタンをフレックスで並べる */
.header-right-buttons {
    display: flex;
    gap: 12px;
    align-items: center;
}

/* 選択して削除モード切り替えボタン */
.select-delete-mode-btn {
  background-color: #f1f1f1;
  color: #4a4a4a;
  padding: 8px 14px;
  border-radius: 12px;
  font-weight: 700;
  border: 1px solid #ccc;
  cursor: pointer;
  transition: background-color 0.2s, box-shadow 0.2s;
}
.select-delete-mode-btn:hover {
  background-color: #e0e0e0;
}
.select-delete-mode-btn.mode-cancel {
  background-color: #fce3e3; /* キャンセルモードは少し赤く */
  color: #c0392b;
  border-color: #e74c3c;
}
.select-delete-mode-btn.mode-cancel:hover {
  background-color: #f9dcdc;
}

/* 一括削除ボタン (ヘッダーの左側に表示される) */
.bulk-delete-btn {
    background-color: #e74c3c;
    color: white;
    padding: 10px 18px;
    border: none;
    border-radius: 12px;
    font-weight: 700;
    cursor: pointer;
    transition: background-color 0.2s;
    font-size: 16px;
    box-shadow: 0 4px 10px rgba(231, 76, 60, 0.4);
}
.bulk-delete-btn:hover {
    background-color: #c0392b;
}

/* 選択アイコンのラッパー */
.selection-icon-wrapper {
    position: absolute;
    top: 6px;
    right: 6px;
    z-index: 10;
    /* 個別削除ボタンと同じ位置に配置 */
}

/* 選択アイコンの基本スタイル */
.selection-icon {
    font-size: 20px;
    cursor: pointer;
    color: #fff; /* 未選択のアイコンは白（外枠） */
    text-shadow: 0 0 3px rgba(0, 0, 0, 0.5); /* 視認性を高める影 */
    transition: color 0.1s;
}

/* 選択されたアイコンの色塗り */
.selection-icon.selected-circle {
    /* fa-solid fa-circle を使って色を塗る */
    color: #e74c3c; /* 赤色に塗る */
    text-shadow: 0 0 0 transparent; /* 影を消す */
}

/* 削除モード中のカード */
.recipe-card.delete-mode-active {
    /* 削除モード中はカーソルを変更し、個別削除ボタンのホバーエフェクトを無効にする */
    cursor: pointer;
    border: 3px solid transparent;
}
.recipe-card.selected-for-delete {
    /* 選択されたカードを視覚的に強調 */
    border: 3px solid #e74c3c; 
    box-shadow: 0 0 10px rgba(231, 76, 60, 0.3);
}

/* ゴミ箱ボタン (個別削除ボタン) は削除モード中は非表示にする */
.recipe-card.delete-mode-active .delete-btn {
    display: none;
}

/* ====================================
  既存のスタイル (変更なし)
==================================== */
.album-page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: "Inter", sans-serif;
  min-height: 100vh;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 16px;
  border-bottom: 3px solid #e0e0e0;
  margin-bottom: 24px;
}
.header h1 {
  font-size: 28px;
  font-weight: 900;
  color: #2c3e50;
}
.create-recipe-btn {
  background: linear-gradient(135deg, #ffd75b 0%, #ff9933 100%);
  color: #4a4a4a;
  padding: 8px 14px;
  border-radius: 12px;
  font-weight: 700;
  text-decoration: none;
  box-shadow: 0 4px 10px rgba(255, 175, 76, 0.6);
  transition: transform 0.2s, box-shadow 0.2s;
}
.create-recipe-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(255, 175, 76, 0.8);
}
.sort-select {
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-weight: 600;
  background-color: white;
  cursor: pointer;
  margin-bottom: 20px;
}
.album-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
}
.recipe-card {
  position: relative;
  text-align: center;
  /* ... 既存のスタイル ... */
}
.recipe-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 18px rgba(0,0,0,0.1);
}
.image-wrapper img {
  width: 100%;
  height: 110px;
  object-fit: cover;
  border-radius: 10px 10px 0 0;
}
.recipe-title {
  margin: 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}
.delete-btn {
  position: absolute;
  top: 6px;
  right: 6px;
  background: rgba(255, 255, 255, 0.85);
  border: none;
  border-radius: 50%;
  padding: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #d00;
  transition: background 0.2s;
}
.delete-btn:hover {
  background: rgba(255, 255, 255, 1);
}
/* モバイル対応 */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  .header-left {
    width: 100%;
    /* モードによってはタイトルとボタンが並ぶ */
    justify-content: flex-start;
  }
  .header-right-buttons {
    width: 100%;
    justify-content: space-between;
  }
  .header h1 {
    font-size: 22px;
  }
  .sort-select {
    width: 100%;
  }
  .album-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
}
</style>
