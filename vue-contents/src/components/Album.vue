<template>
    <div class="user-album">
      <h2>マイレシピアルバム</h2>
      <div class="album-grid">
        <div
          v-for="recipe in recipes"
          :key="recipe.id"
          class="recipe-card"
        >
          <div class="image-wrapper" @click="goToRecipe(recipe.id)">
            <img :src="recipe.photo || defaultPhoto" alt="レシピ画像" />
          </div>
          <p>{{ recipe.title }}</p>
          <button
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
  
  export default {
    name: "UserAlbum",
    data() {
      return {
        recipes: [],
        defaultPhoto: "/default_recipe.png",
      };
    },
    methods: {
      async fetchUserRecipes() {
        try {
          const res = await axios.get(
            "http://127.0.0.1:8000/api/recipes/?my=true",
            { withCredentials: true }
          );
          this.recipes = res.data;
        } catch (err) {
          console.error("ユーザーレシピ取得エラー:", err);
        }
      },
      goToRecipe(recipeId) {
        this.$router.push({ name: "RecipeDetail", params: { id: recipeId } });
      },
      async deleteRecipe(recipeId) {
        if (!confirm("本当にこのレシピを削除しますか？")) return;
  
        try {
          await axios.delete(
            `http://127.0.0.1:8000/api/recipes/${recipeId}/`,
            {
              withCredentials: true,
              headers: {
                "X-CSRFToken": getCookie("csrftoken"),
              },
            }
          );
          // 削除成功 → recipes 配列から除外
          this.recipes = this.recipes.filter(r => r.id !== recipeId);
          alert("レシピを削除しました");
        } catch (err) {
          console.error("レシピ削除エラー:", err);
          alert("削除に失敗しました。権限や接続を確認してください");
        }
      },
    },
    mounted() {
      this.fetchUserRecipes();
    },
  };
  </script>
  
  <style scoped>
  .album-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 12px;
  }
  
  .recipe-card {
    position: relative;
    text-align: center;
    cursor: pointer;
  }
  
  .image-wrapper img {
    width: 100%;
    height: 100px;
    object-fit: cover;
    border-radius: 6px;
  }
  
  .delete-btn {
    position: absolute;
    top: 4px;
    right: 4px;
    background: rgba(255, 255, 255, 0.8);
    border: none;
    border-radius: 50%;
    padding: 4px;
    cursor: pointer;
    font-size: 14px;
    color: #d00;
  }
  
  .delete-btn:hover {
    background: rgba(255, 255, 255, 1);
  }
  </style>
  