<template>
  <div class="recipe-form notebook-bg">
    <div class="recipe-form-inner">
    <h2 class="section-title title-underline">新しいレシピを投稿</h2>
    <form @submit.prevent="submitRecipe">

      <!-- 写真アップロード -->
      <div class="form-section">
        <label class="section-title photo-underline">写真をアップ</label>
         <!-- 非表示のinput -->
  <input type="file" @change="onFileChange" accept="image/*" id="photoInput" class="photo-input"/>
  
  <!-- カスタムボタン -->
  <label for="photoInput" class="photo-button">Choose File</label>

      </div>

      <!-- タイトル -->
      <div class="form-section">
        <label class="section-title title-underline">レシピタイトル</label>
        <input type="text" v-model="title" placeholder="タイトルを入力" class="title-input" required />
      </div>

      <!-- 材料 -->
      <div class="form-section">
        <label class="section-title ingredients-underline">材料</label>
        <ul class="ingredients-list">
          <li v-for="(ingredient, index) in ingredients" :key="index">
            <input
              type="text"
              v-model="ingredients[index]"
              placeholder="材料を入力"
            />
          </li>
        </ul>
        <button type="button" class="add-button" @click="addIngredient">材料を追加</button>
      </div>

      <!-- 作り方（手順） -->
      <div class="form-section">
        <label class="section-title steps-underline">作り方</label>
        <div class="numbered-textarea">
          <div v-for="(step, index) in steps" :key="index" class="step-line">
            <span class="step-number">{{ index + 1 }}.</span>
            <input
              type="text"
              v-model="steps[index]"
              placeholder="手順を入力"
            />
          </div>
        </div>
        <button type="button" class="add-button" @click="addStep">手順を追加</button>
      </div>

      <button type="submit" class="submit-button">投稿</button>
    </form>

    <!-- プレビュー -->
    <div v-if="previewUrl" class="preview">
      <h3>プレビュー:</h3>
      <img :src="previewUrl" alt="preview" style="max-width: 200px;" />
    </div>
  </div>
</div>
</template>

<script>
import { ref } from "vue";
import axios from "axios";

export default {
  name: "RecipeForm",
  setup(_, { emit }) {
    const photo = ref(null);
    const previewUrl = ref(null);
    const title = ref("");
    const ingredients = ref(Array(8).fill(""));
    const steps = ref(Array(10).fill(""));

    const addIngredient = () => ingredients.value.push("");
    const addStep = () => steps.value.push("");

    const onFileChange = (event) => {
      const file = event.target.files[0];
      photo.value = file;
      previewUrl.value = URL.createObjectURL(file);
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

    const submitRecipe = async () => {
      try {
        const formData = new FormData();
        formData.append("photo", photo.value);
        formData.append("title", title.value);
        formData.append("ingredients", JSON.stringify(ingredients.value));
        formData.append("steps", JSON.stringify(steps.value));

        const response = await axios.post(
          "http://127.0.0.1:8000/api/recipes/",
          formData,
          {
            withCredentials: true,
            headers: {
              "Content-Type": "multipart/form-data",
              "X-CSRFToken": getCookie("csrftoken"),
            },
          }
        );

        console.log("投稿成功:", response.data);
        emit("recipe-added", response.data);

        photo.value = null;
        previewUrl.value = null;
        title.value = "";
        ingredients.value = Array(10).fill("");
        steps.value = Array(10).fill("");
      } catch (error) {
        console.error("投稿エラー:", error.response?.data || error.message);
      }
    };

    return {
      photo,
      previewUrl,
      title,
      ingredients,
      steps,
      addIngredient,
      addStep,
      onFileChange,
      submitRecipe,
    };
  },
};
</script>

<style scoped>
/* ページ全体ノート風背景 */
.notebook-bg {
  background-color: #fffbe6;
  background-image:
    linear-gradient(to bottom, #ccc 1px, transparent 1px),
    linear-gradient(to right, #eee 1px, transparent 1px);
  background-size: 100% 1.5em, 20px 100%;
  padding: 20px;
  font-family: 'Comic Neue', 'Yu Gothic', sans-serif;
  display: flex;
  justify-content: center; /* 横中央 */
  align-items: center;     /* 縦中央 */
  min-height: 100vh;       /* 高さ確保 */
  box-sizing: border-box;
}

/* 内側コンテンツ */
.recipe-form-inner {
  width: 80%;               /* 横幅を30%縮小 */
  padding: 10px;
  box-sizing: border-box;
}

/* タイトル入力欄 */
.title-input {
  width: 100%;
  border: none;
  border-bottom: 3px solid #5A4DA0;
  padding: 4px 2px;
  font-size: 1rem;
  outline: none;
}
.section-title {
  color: #000 !important;  /* 黒に固定 */
}


/* 写真アップラベル */
.photo-underline {
  border-bottom: 3px solid #FFB347;
  color: #000; /* 黒に固定 */
  margin-bottom: 6px;
  display: inline-block;
  padding-bottom: 2px;
}

/* 写真アップボタン */
/* input を非表示にする */
.photo-input {
  display: none;
}

/* カスタムボタン */
.photo-button {
  display: inline-block;
  margin-top: 4px;
  margin-right: 10px; /* 横方向に10pxスペース */
  padding: 6px 12px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(90deg,#FFB347,#FFCC33);
  font-weight: 600;
  cursor: pointer;
  color: #000; 
  margin: 10px;  /* ここでラベルとの縦スペースを調整 */
}


/* 材料リスト */
.ingredients-list {
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
  width: 100%;
  font-size: 1rem;
  background-color: transparent;
  color: #000;
  line-height: 1.5em;
  padding: 2px 0;
  font-family: 'Comic Neue', 'Yu Gothic', sans-serif;
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

/* 作り方 */
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
  padding: 6px 8px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  color: #000;
}

/* ボタン */
.add-button {
  margin-top: 5px;
  margin-right: 10px;
  background-color: #FFB347;
  color: #000;
  font-weight: 600;
  padding: 5px 10px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.add-button:hover { background-color: #FFA500; }

.submit-button {
  background-color: #5A4DA0;
  color: white;
  font-weight: 600;
  padding: 10px 15px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 10px; /* 横方向に10pxスペース */
}

.submit-button:hover { background-color: #47368a; }

/* プレビュー */
.preview { margin-top: 20px; }
</style>
