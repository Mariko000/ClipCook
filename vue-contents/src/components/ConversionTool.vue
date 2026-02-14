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

    <!-- 単位系選択 -->
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
const foreignSystem = ref("us");
const results = ref([]);

async function convertTextRecipe() {
  try {
    let from_system, to_system;

    if (direction.value === "to_jp") {
      from_system = foreignSystem.value;
      to_system = "jp";
    } else {
      from_system = "jp";
      to_system = foreignSystem.value;
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

    results.value = res.data.converted_recipe.map((r) => {
      const hasAmount = r.amount !== null && r.amount !== undefined && r.amount !== "";
      const hasUnit   = r.unit   !== null && r.unit   !== undefined && r.unit   !== "";

      if (!hasAmount && !hasUnit) return r.ingredient;
      if (hasAmount && !hasUnit) return `${r.ingredient}: ${r.amount}`;
      return `${r.ingredient}: ${r.amount}${r.unit}`.replace(/\s+/g, ' ').trim();
    });

  } catch (err) {
    console.error("変換エラー:", err);
  }
}
</script>

<style scoped>
/* 全体 */
.conversion-tool {
  max-width: 600px;
  margin: 2rem auto;
  padding: 24px;
  background-color: #FFFDF7; /* ベースカラー */
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  font-family: 'Comic Neue', sans-serif;
  color: #333333; /* テキストカラー */
}

/* 見出し */
.conversion-tool h2 {
  background-color: #FFD966; /* メインカラー */
  padding: 12px 16px;
  border-radius: 12px;
  margin-bottom: 24px;
  text-align: center;
  font-size: 1.5rem;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}

/* フォームグループ */
.form-group {
  margin-bottom: 16px;
}
.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
}
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #4E8098; /* サブカラー2 */
  border-radius: 8px;
  background-color: #ffffff;
  font-size: 1rem;
  transition: all 0.2s ease;
}
.form-group select:focus {
  outline: none;
  border-color: #FF8C61; /* サブカラー1 */
  box-shadow: 0 0 0 2px rgba(255,140,97,0.2);
}

/* テキストエリア */
textarea {
  width: 100%;
  height: 150px;
  padding: 12px;
  border: 1px solid #4E8098;
  border-radius: 12px;
  resize: vertical;
  font-size: 1rem;
  margin-bottom: 16px;
  background-color: #fff;
}
textarea:focus {
  outline: none;
  border-color: #FF8C61;
  box-shadow: 0 0 0 2px rgba(255,140,97,0.2);
}

/* ボタン */
button {
  display: block;
  width: 100%;
  padding: 12px;
  background-color: #FF8C61; /* サブカラー1 */
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}
button:hover {
  background-color: #FF7049;
  box-shadow: 0 4px 10px rgba(0,0,0,0.12);
}

/* 結果表示 */
.result {
  margin-top: 24px;
}
.result h3 {
  margin-bottom: 12px;
  font-size: 1.25rem;
  color: #FF8C61;
}
.result ul {
  list-style: none;
  padding: 0;
}
.result li {
  background-color: #FFF;
  border: 1px solid #E0E0E0; /* 枠ボーダー */
  border-radius: 12px;
  padding: 10px 14px;
  margin-bottom: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}

/* -------------------- レスポンシブ -------------------- */

/* スマホ用（最大幅600px） */
@media (max-width: 600px) {
  .conversion-tool {
    margin: 1rem;
    padding: 16px;
    font-size: 0.9rem;
  }

  .conversion-tool h2 {
    font-size: 1.3rem;
    padding: 10px;
  }

  textarea {
    height: 120px;
    font-size: 0.9rem;
  }

  button {
    padding: 10px;
    font-size: 0.95rem;
  }

  .form-group select {
    font-size: 0.95rem;
  }

  .result h3 {
    font-size: 1.1rem;
  }

  .result li {
    padding: 8px 10px;
    font-size: 0.9rem;
  }
}

/* タブレット用（601px～900px） */
@media (min-width: 601px) and (max-width: 900px) {
  .conversion-tool {
    max-width: 500px;
    padding: 20px;
    font-size: 0.95rem;
  }

  .conversion-tool h2 {
    font-size: 1.4rem;
  }

  textarea {
    height: 140px;
  }

  button {
    font-size: 1rem;
    padding: 11px;
  }

  .result h3 {
    font-size: 1.2rem;
  }
}

/* PC用（901px以上） */
@media (min-width: 901px) {
  .conversion-tool {
    max-width: 600px;
    padding: 24px;
    font-size: 1rem;
  }

  .conversion-tool h2 {
    font-size: 1.5rem;
  }

  textarea {
    height: 150px;
  }

  button {
    font-size: 1rem;
    padding: 12px;
  }

  .result h3 {
    font-size: 1.25rem;
  }
}

</style>
