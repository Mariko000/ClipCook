<template>
    <div class="conversion-tool">
      <h2>レシピ単位変換</h2>
  
      <!-- 変換方向切替 -->
      <div class="form-group">
        <label>変換方向:</label>
        <select v-model="direction">
          <option value="to_jp">外国単位 → 日本単位</option>
          <option value="to_foreign">日本単位 → 外国単位</option>
        </select>
      </div>
  
      <!-- 単位系選択（US/UK） -->
      <div v-if="direction === 'to_jp' || direction === 'to_foreign'" class="form-group">
        <label>単位系:</label>
        <select v-model="foreignSystem">
          <option value="us">US（アメリカ）</option>
          <option value="uk">UK（イギリス）</option>
        </select>
      </div>
  
      <!-- レシピ入力 -->
      <textarea v-model="recipeText" placeholder="レシピを貼り付け"></textarea>
      <button @click="convertTextRecipe">変換</button>
  
      <!-- 結果表示 -->
      <div v-if="results.length > 0" class="result">
        <h3>変換結果</h3>
        <ul>
          <li v-for="(res, idx) in results" :key="idx">{{ res }}</li>
        </ul>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from "vue";
  import axios from "axios";
  
  const recipeText = ref("");
  const direction = ref("to_jp");
  const foreignSystem = ref("us");  // デフォルト US
  const results = ref([]);
  
  // 変換実行
  async function convertTextRecipe() {
    try {
      let from_system, to_system;
  
      if (direction.value === "to_jp") {
        from_system = foreignSystem.value; // US or UK
        to_system = "jp";
      } else {
        from_system = "jp";
        to_system = foreignSystem.value; // 日本→外国のときも選択に応じる
      }
  
      const payload = {
        recipe_text: (recipeText.value || "").trim(),
        from_unit_system: from_system,
        to_unit_system: to_system,
      };
  
      const res = await axios.post(
        "http://127.0.0.1:8000/api/foodconversion/convert-recipe/",
        payload,
        { headers: { "Content-Type": "application/json" } }
      );
  
      // 表示用に整形
      results.value = res.data.converted_recipe.map((r) => {
        const hasAmount = r.amount !== null && r.amount !== undefined && r.amount !== "";
        const hasUnit   = r.unit   !== null && r.unit   !== undefined && r.unit   !== "";
  
        if (!hasAmount && !hasUnit) return r.ingredient;
        if (hasAmount && !hasUnit) return `${r.ingredient}: ${r.amount}`;
        return `${r.ingredient}: ${r.amount}${r.unit}`;
      });
  
    } catch (err) {
      console.error("変換エラー:", err);
    }
  }
  </script>
  
  <style scoped>
  textarea { width: 100%; height: 150px; margin-bottom: 8px; }
  button { margin-bottom: 12px; }
  .form-group { margin-bottom: 12px; }
  .result { margin-top: 1rem; }
  </style>
  