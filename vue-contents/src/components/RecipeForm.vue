<template>
  <div class="recipe-form notebook-bg">
    <div class="recipe-form-inner">
      <h2 class="section-title" style="margin:10px;">新しいレシピを投稿</h2>
      <form @submit.prevent="submitRecipe">

        <!-- 写真アップロード -->
        <div class="form-section">
          <label class="section-title" style="margin:10px;">写真をアップ</label>
          <input type="file" @change="onFileChange" accept="image/*" id="photoInput" class="photo-input"/>
          <label for="photoInput" class="photo-button">Choose File</label>
        </div>

        <!-- タイトル -->
        <div class="form-section">
          <label class="section-title" style="margin:10px;">レシピタイトル</label>
          <input type="text" v-model="title" placeholder="タイトルを入力" class="title-input" required @keyup.enter.prevent />
        </div>

        <!-- 材料 -->
        <div class="form-section">
          <label class="section-title" style="margin:10px;">材料</label>
          <ul class="ingredients-list">
            <li v-for="(ingredient, index) in ingredients" :key="index">
              <input type="text" v-model="ingredients[index]" placeholder="材料を入力" @keyup.enter.prevent />
            </li>
          </ul>
          <button type="button" class="add-button" @click="addIngredient">材料を追加</button>
        </div>

        <!-- 作り方 -->
        <div class="form-section">
          <label class="section-title" style="margin:10px;">作り方</label>
          <div class="numbered-textarea">
            <div v-for="(step, index) in steps" :key="index" class="step-line">
              <span class="step-number">{{ index + 1 }}.</span>
              <input type="text" v-model="steps[index]" placeholder="手順を入力" @keyup.enter.prevent />
            </div>
          </div>
          <button type="button" class="add-button" style="margin:10px;" @click="addStep">手順を追加</button>
        </div>

        <!-- タグ -->
        <div class="form-group mt-3">
          <label class="section-title" style="margin:10px;">タグ</label>
          <div class="tag-list-display mb-2">
            <span 
              v-for="(tag, i) in tags" 
              :key="i" 
              class="badge bg-primary tag-item me-1" 
              @click="removeTag(i)"
              title="クリックで削除"
            >
              #{{ tag }}
              <span style="margin-left: 4px; font-weight: bold;">×</span>
            </span>
            <!-- 入力中タグをリアルタイム表示 -->
            <span v-if="liveTag" class="badge live-tag">#{{ liveTag }}</span>
          </div>

          <input
            type="text"
            v-model="tagsInput"
            @keyup.enter.prevent="handleTagEnter"
            placeholder="タグを入力してEnterで確定"
            class="form-control tag-input-field"
          />
        </div>

        <button type="submit" class="submit-button">投稿</button>
        <p v-if="postMessage" class="post-message">{{ postMessage }}</p>
      </form>

      <div v-if="previewUrl" class="preview">
        <h3>プレビュー:</h3>
        <img :src="previewUrl" alt="preview" style="max-width: 200px;" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from "vue";
import axios from "axios";

export default {
  name: "RecipeForm",
  setup() {
    const photo = ref(null);
    const previewUrl = ref(null);
    const title = ref("");
    const initialIngredientsCount = 8;
    const initialStepsCount = 8;
    const ingredients = ref(Array(initialIngredientsCount).fill(""));
    const steps = ref(Array(initialStepsCount).fill(""));
    const tags = ref([]);
    const tagIds = ref([]);
    const tagsInput = ref("");
    const liveTag = ref("");
    const postMessage = ref("");

    const addIngredient = () => ingredients.value.push("");
    const addStep = () => steps.value.push("");

    const onFileChange = (event) => {
      const file = event.target.files?.[0];
      if (file) {
        photo.value = file;
        previewUrl.value = URL.createObjectURL(file);
      } else {
        photo.value = null;
        previewUrl.value = null;
      }
    };

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

    watch(tagsInput, (val) => {
      liveTag.value = val.trim();
    });

    const addTag = (tagName) => {
      tagName = tagName.trim();
      if (!tagName) return;
      if (!tags.value.includes(tagName)) {
        tags.value.push(tagName);
      }
      tagsInput.value = "";
      liveTag.value = "";
    };

    const handleTagEnter = () => {
      addTag(tagsInput.value);
    };

    const removeTag = (index) => {
      tags.value.splice(index, 1);
    };

    const resetForm = () => {
      title.value = "";
      ingredients.value = Array(initialIngredientsCount).fill("");
      steps.value = Array(initialStepsCount).fill("");
      tags.value = [];
      tagIds.value = [];
      photo.value = null;
      previewUrl.value = null;
      tagsInput.value = "";
      liveTag.value = "";
      const photoInput = document.getElementById('photoInput');
      if (photoInput) photoInput.value = '';
    };

    const submitRecipe = async () => {
      if (tagsInput.value.trim()) addTag(tagsInput.value);
      const cleanedIngredients = ingredients.value.filter(i => i.trim() !== "");
      const cleanedSteps = steps.value.filter(s => s.trim() !== "");
      const csrfToken = getCookie("csrftoken");
      if (!csrfToken) return;

      tagIds.value = [];
      const tagsToCreate = [];

      for (let tagName of tags.value) {
        tagName = tagName.trim();
        if (!tagName) continue;
        try {
          const res = await axios.get(`http://127.0.0.1:8000/api/tags/?search=${encodeURIComponent(tagName)}`, { withCredentials: true });
          if (res.data.length > 0) tagIds.value.push(res.data[0].id);
          else tagsToCreate.push(tagName);
        } catch (err) {
          console.error("タグ検索エラー:", tagName, err);
        }
      }

      const newTagNames = [];
      for (const tagName of tagsToCreate) {
        try {
          const createRes = await axios.post(
            "http://127.0.0.1:8000/api/tags/",
            { name: tagName },
            { withCredentials: true, headers: { "X-CSRFToken": csrfToken } }
          );
          tagIds.value.push(createRes.data.id);
          newTagNames.push(tagName);
        } catch (err) {
          console.error("新規タグ作成エラー:", tagName, err);
        }
      }

      const formData = new FormData();
      if (photo.value instanceof File) formData.append("photo", photo.value);
      formData.append("title", title.value);
      formData.append("ingredients", JSON.stringify(cleanedIngredients));
      formData.append("steps", JSON.stringify(cleanedSteps));
      formData.append("tag_ids", JSON.stringify(tagIds.value));
      formData.append("new_tags", JSON.stringify(newTagNames));

      try {
        await axios.post("http://127.0.0.1:8000/api/recipes/", formData, {
          withCredentials: true,
          headers: { "X-CSRFToken": csrfToken },
        });
        resetForm();
        postMessage.value = "レシピを投稿しました！";
        setTimeout(() => (postMessage.value = ""), 3000);
      } catch (err) {
        console.error("レシピ投稿エラー:", err);
      }
    };

    return {
      photo, previewUrl, title, ingredients, steps,
      tags, tagsInput, liveTag,
      addIngredient, addStep, onFileChange,
      handleTagEnter, submitRecipe, removeTag,
      postMessage,
    };
  }
};
</script>


<style scoped>
/* ページ全体ノート風背景 */
.notebook-bg {
  background-color: #fffbe6;
  background-image: linear-gradient(to bottom, #ccc 1px, transparent 1px);
  background-size: 100% 1.5em;
  padding: 20px;
  font-family: 'Comic Neue', 'Yu Gothic', sans-serif;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  box-sizing: border-box;
}


/* 内側コンテンツ */
.recipe-form-inner {
  width: 80%;               /* 横幅を30%縮小 */
  padding: 10px;
  box-sizing: border-box;
}

/* セクションタイトル */
.section-title {
  color: #000 !important;  
  font-weight: bold;
}

/* タイトル入力欄 */
.title-input {
  width: 60%;
  border: none;
  border-bottom: 4px solid #FF4B5C; /* 赤*/
  padding: 4px 2px;
  font-size: 1rem;
  outline: none;
  margin:10px;
}

/* --- 見出しの装飾（下線）--- */
.title-underline {
  border-bottom: 3px solid #FF4B5C; /* 赤 */
  display: inline-block;
  padding-bottom: 2px;
}
.ingredients-underline {
  border-bottom: 3px solid #3AA1BF; /* 青 */
  display: inline-block;
  padding-bottom: 2px;
}
.steps-underline {
  border-bottom: 3px solid #059b32; /* 緑 */
  display: inline-block;
  padding-bottom: 2px;
}
.photo-underline {
  border-bottom: 3px solid #FFB347; /* オレンジ */
  display: inline-block;
  padding-bottom: 2px;
}

/* --- 写真アップロード --- */
.photo-input {
  display: none;
}
.photo-button {
  display: inline-block;
  margin-top: 4px;
  padding: 6px 12px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(90deg,#FFB347,#FFCC33);
  font-weight: 600;
  cursor: pointer;
  color: #000; 
  margin: 10px;
  box-shadow: 0 4px #e09600;
  transition: all 0.1s ease;
}
.photo-button:active {
  box-shadow: 0 0 #e09600;
  transform: translateY(4px);
}


/* --- 材料リスト --- */
.ingredients-list {
  margin:10px;
  list-style-type: disc;
  padding-left: 25px; /* bulletの位置 */
  margin: 5px 0;
}
.ingredients-list li {
  margin-bottom: 4px;
  position: relative;
}
.ingredients-list li input {
  border: none;
  outline: none;
  width: calc(100% - 20px); /* bullet分だけ余白を残す */
  font-size: 1rem;
  background-color: transparent;
  color: #000;
  line-height: 1.5em;
  padding: 2px 0;
  font-family: 'Comic Neue', 'Yu Gothic', sans-serif;
  margin-left: 20px; /* bulletを避ける */
}

/* --- 作り方 (手順) --- */
.numbered-textarea {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.step-line {
  display: flex;
  align-items: center;
}
.step-number {
  width: 20px;
  text-align: right;
  margin-right: 10px;
  font-weight: 600;
  color: #3AA1BF;
}
.step-line input {
  flex: 1;
  padding: 8px 10px;
  font-size: 1rem;
  border: 2px solid #001F5B;
  border-radius: 6px;
  color: #001F5B;
  font-weight: 600;
  background-color: transparent;
  outline: none;
}

/* --- タグ表示/入力 --- */
.tag-list-display {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 10px 0;
  padding: 10px;
  border: 1px dashed #888; 
  border-radius: 6px;
  background-color: #fcfcfc;
  min-height: 40px;
  margin-left: 10px;
}
.tag-item {
  /* 確定済みタグのデザイン */
  background-color: #3AA1BF !important; 
  color: white !important;
  padding: 4px 12px;
  border-radius: 20px; 
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background-color 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.tag-item:hover {
    background-color: #001F5B !important;
}
.live-tag {
  /* 入力中タグのデザイン */
  background-color: #ddd !important;
  color: #000 !important;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  opacity: 0.7;
}

.tag-input-field {
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 8px;
    margin-left: 10px;
    width: calc(100% - 20px);
    background-color: #fff;
    font-family: 'Comic Neue', 'Yu Gothic', sans-serif;
}


/* --- 共通ボタン --- */
.add-button {
  margin-top: 5px;
  margin-right: 10px;
  background-color: #FFB347;
  color: #000;
  font-weight: 600;
  padding: 5px 12px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 3px #e09600;
  transition: all 0.1s ease;
}
.add-button:active {
  box-shadow: 0 0 #e09600;
  transform: translateY(3px);
}

.submit-button {
  background-color: #059b32;
  color: white;
  font-weight: 600;
  padding: 12px 20px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  margin-top: 20px; 
  box-shadow: 0 4px #037526;
  transition: all 0.1s ease;
}
.submit-button:active {
  box-shadow: 0 0 #037526;
  transform: translateY(4px);
}
/* プレビュー */
.preview { margin-top: 20px; }

.live-tag {
  background-color: rgba(200, 200, 200, 0.3) !important;
  color: #000 !important;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  opacity: 0.8;
  border: none;
}

.post-message {
  color: red;
  font-weight: bold;
  margin-top: 10px;
}

</style>
