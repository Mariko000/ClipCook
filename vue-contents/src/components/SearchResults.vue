<template>
    <div class="container mt-4">
      <h2 class="mb-3">Search results for "{{ query }}"</h2>
  
      <div v-if="loading">Loading...</div>
  
      <div v-else>
        <div v-if="recipes.length > 0" class="album-grid">
            <div v-for="recipe in recipes" :key="recipe.id" class="recipe-card">
  <div class="image-wrapper" @click="goToRecipe(recipe.id)">
    <img :src="recipe.photo || defaultPhoto" alt="レシピ画像" />
  </div>
  <p class="recipe-title">{{ recipe.title }}</p>
  <div class="mt-2">
    <span v-for="tag in recipe.tags" :key="tag.id" class="badge bg-secondary me-1">
      #{{ tag.name }}
    </span>
  </div>
</div>

        </div>
  
        <div v-else class="text-muted">No recipes found.</div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, watch } from "vue"
  import { useRoute, useRouter } from "vue-router"
  
  const route = useRoute()
  const router = useRouter()
  const query = ref(route.query.q || "")
  const recipes = ref([])
  const loading = ref(true)
  const defaultPhoto = "/default_recipe.png"  // デフォルト画像パス
  
  async function fetchRecipes() {
    if (!query.value) return
    loading.value = true
    try {
      const res = await fetch(
        `/api/search/recipes/?q=${encodeURIComponent(query.value)}`
      )
      if (!res.ok) throw new Error("API error")
      const data = await res.json()
      recipes.value = data
    } catch (err) {
      console.error(err)
    } finally {
      loading.value = false
    }
  }
  
  function goToDetail(recipeId) {
    router.push({ name: "RecipeDetail", params: { id: recipeId } })
  }
  
  onMounted(fetchRecipes)
  watch(() => route.query.q, newQ => {
    query.value = newQ || ""
    fetchRecipes()
  })
  </script>
  
  <style scoped>
  .album-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 16px;
  }
  
  .recipe-card {
    position: relative;
    background: white;
    border-radius: 10px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.05);
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .recipe-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.1);
  }
  
  .image-wrapper img {
    width: 100%;
    height: 120px;
    object-fit: cover;
    border-radius: 10px 10px 0 0;
  }
  
  .recipe-title {
    margin: 8px;
    font-weight: 600;
    font-size: 14px;
    text-align: center;
  }
  
  .tag-list {
    padding: 0 8px 8px;
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
  }
  </style>
  