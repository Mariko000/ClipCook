<template>
  <div class="recipe-detail-container app-font">

  <!-- 読み込み中 -->
  <div v-if="loading" class="loading-message">
      <i class="fa-solid fa-spinner fa-spin"></i> レシピを読み込み中...
  </div>

  <!-- レシピ表示 -->
  <div v-else-if="recipe && recipe.id">
      
      <!-- ヘッダーと編集ボタン -->
      <div class="header-section" style="position: relative;">
      <div class="action-buttons">
          <button v-if="isEditing" @click="updateRecipe" class="save-button">
          <i class="fa-solid fa-floppy-disk"></i> 保存
          </button>
          <button v-else @click="toggleEditMode" class="edit-button">
          編集
          </button>
          <button v-if="isEditing" @click="cancelEdit" class="cancel-button">
          <i class="fa-solid fa-xmark"></i> キャンセル
          </button>
      </div>

      

<!-- タイトル＋ブックマーク横並び -->
<div class="title-bookmark-wrapper">
<!-- タイトル編集/表示 -->
<template v-if="isEditing">
    <input
      type="text"
      v-model="editableTitle"
      class="editable-title-input"
      placeholder="レシピタイトルを入力"
    />
</template>
<template v-else>
    <h1 class="recipe-title">{{ displayTitle }}</h1>
</template>

<!-- ブックマークボタン -->
<button
  v-if="recipe && recipe.id"
  class="bookmark-button"
  @click="toggleBookmark"
  title="お気に入りに追加"
>
  <i
    :class="[isBookmarked ? 'fa-solid' : 'fa-regular', 'fa-bookmark']"
    :style="{ color: isBookmarked ? '#ffcc00' : '#555' }"
  ></i>
</button>
</div>
</div>



<button
@click="toggleWakeLock"
class="wake-lock-btn"
title="スリープ防止切替"
>
<i
  :class="[
    wakeLockActive ? 'fa-solid fa-toggle-on wake-lock-on' : 'fa-solid fa-toggle-off wake-lock-off'
  ]"
></i>
<span
  :class="wakeLockActive ? 'wake-lock-on' : 'wake-lock-off'"
>
  {{ wakeLockActive ? 'スリープ防止を有効にする' : 'スリープ防止を解除する' }}
</span>
</button>


      <!-- コンテンツ -->
      <div class="content-wrapper">

      <!-- 画像 -->
      <div class="image-box">
          <img v-if="editablePhoto" :src="editablePhoto" :alt="recipe.memo" class="recipe-image" />
          <div v-else class="no-image">画像なし</div>

          <!-- 編集中なら画像変更UI表示 -->
          <div v-if="isEditing" class="photo-edit-overlay">
          <label for="photo-upload" class="photo-upload-label">
              <i class="fa-solid fa-camera"></i> 画像を変更
              <input type="file" id="photo-upload" @change="onFileChange" accept="image/*" class="photo-upload-input" />
          </label>
          </div>
          

          <!-- 投稿者表示 -->
          <div class="image-overlay">
          <span class="recipe-author">投稿者: {{ recipe.user || '匿名ユーザー' }}</span>
          </div>
      </div>
      

  <!-- 詳細情報 -->
 <div class="detail-box">
    
<!-- 更新メッセージ -->
<div v-if="updateMessage" :class="['message-box', messageType]">{{ updateMessage }}</div>


<div class="recipe-actions">
  <!-- 印刷 -->
  <button @click="printRecipe" class="action-btn print-btn" title="印刷">
      <i class="fa-solid fa-print"></i>
  </button>

  <!-- URLコピー -->
  <button @click="copyUrl" class="action-btn copy-btn" title="URLをコピー">
      <i class="fa-solid fa-copy"></i>
  </button>

  <!-- SNS共有（ドロップダウン） -->
  <div class="share-dropdown">
      <button @click="toggleShareMenu" class="action-btn share-btn" title="共有">
          <i class="fa-solid fa-share-from-square"></i>
      </button>
      <div v-if="showShareMenu" class="share-menu">
          <a :href="xShareUrl" target="_blank" rel="noopener" title="X/Twitter">
              <i class="fa-brands fa-x-twitter"></i>
          </a>
          <a :href="facebookShareUrl" target="_blank" rel="noopener" title="Facebook">
              <i class="fa-brands fa-facebook"></i>
          </a>
          <a :href="pinterestShareUrl" target="_blank" rel="noopener" title="Pinterest">
              <i class="fa-brands fa-pinterest"></i>
          </a>
      </div>
  </div>
</div>

          <!-- 材料セクション -->
          <div class="ingredients-section">
              <h3 class="section-title ingredients-underline">材料</h3>
              <!-- 編集モード -->
              <template v-if="isEditing">
                  <div v-for="(ingredient, index) in ingredients" :key="index" class="list-item-row">
                      <input
                          v-model="ingredients[index]"
                          type="text"
                          class="form-control ingredient-input"
                          placeholder="例: 小麦粉 200g"
                      />
                      <button type="button" @click="removeIngredient(index)" class="btn-remove">−</button>
                  </div>
                  <button type="button" @click="addIngredient" class="btn-add">＋ 材料を追加</button>
              </template>
              <!-- 表示モード -->
              <template v-else>
                  <ul class="list-display">
                      <li v-for="(ingredient, index) in recipeIngredients" :key="index">
                          <span class="list-index">•</span> {{ ingredient }}
                      </li>
                  </ul>
                  <p v-if="!recipeIngredients.length" class="empty-list-message">材料の記述がありません。</p>
              </template>
          </div>
           <!-- タグ入力欄 -->

<!-- タグセクション -->
<div class="recipe-tags-section">
<h3 class="section-title tags-underline">タグ</h3>

<!-- 編集モード -->
<template v-if="isEditing">
  <div class="tag-inputs">
    <span
      v-for="(tag, index) in editableTags"
      :key="index"
      class="tag-badge editable"
    >
      #{{ tag }}
      <button type="button" @click="removeTag(index)" class="btn-remove-tag">×</button>
    </span>
  </div>
  <div class="add-tag-row">
    <input
      v-model="newTagName"
      type="text"
      placeholder="タグを入力してEnter"
      @keyup.enter="addTag"
      class="form-control tag-input"
    />
    <button type="button" @click="addTag" class="btn-add-tag">＋</button>
  </div>
</template>

<!-- 表示モード -->
<template v-else>
  <span v-for="tag in recipe.tags" :key="tag.id" class="tag-badge">
    #{{ tag.name }}
  </span>
</template>
</div>


          <!-- 作り方セクション -->
          <div class="steps-section">
              <h3 class="section-title steps-underline">作り方</h3>
              <!-- 編集モード -->
              <template v-if="isEditing">
                  <div v-for="(step, index) in steps" :key="index" class="list-item-row">
                      <span class="step-index">{{ index + 1 }}.</span>
                      <textarea
                          v-model="steps[index]"
                          class="form-control step-input"
                          placeholder="例: ボウルに材料を入れて混ぜる"
                          rows="2"
                      ></textarea>
                      <button type="button" @click="removeStep(index)" class="btn-remove">−</button>
                  </div>
                  <button type="button" @click="addStep" class="btn-add">＋ 手順を追加</button>
              </template>
              <!-- 表示モード -->
              <template v-else>
                  <ol class="list-display">
                      <li v-for="(step, index) in recipeSteps" :key="index">
                          {{ step }}
                      </li>
                  </ol>
                  <p v-if="!recipeSteps.length" class="empty-list-message">作り方の記述がありません。</p>
              </template>
          </div>
          
          

          <!-- メモ（非推奨/予備として残す場合はここに表示ロジックを組み込む） -->
          <!-- 今回は材料と作り方に置き換えるため、一旦非表示とします -->
          


      </div>
      </div>
  </div>
  

  <!-- レシピ未取得/エラー -->
  <div v-else class="error-message">
      <i class="fa-solid fa-triangle-exclamation"></i> レシピが見つかりませんでした。
  </div>

  <!-- 戻るボタン -->
  <button @click="goBack" class="back-button">
     戻る
  </button>

  </div>
</template>

<script>
import axios from "axios";


// Cookie から CSRF トークンを取得
function getCookie(name) {
let cookieValue = null;
if (document.cookie && document.cookie !== "") {
  const cookies = document.cookie.split(";");
  for (let i = 0; i < cookies.length; i++) {
    const cookie = cookies[i].trim();
    if (cookie.startsWith(name + "=")) {
      cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
      break;
    }
  }
}
return cookieValue;
}

// 材料・作り方の区切り
const INGREDIENTS_SEPARATOR = "=== 材料 ===";
const STEPS_SEPARATOR = "=== 作り方 ===";

export default {
name: "RecipeDetail",
data() {
  return {
    recipe: null,
    loading: true,
    error: null,
    isEditing: false,
    editableTitle: "",
    editablePhoto: null,
    newPhotoFile: null,
    ingredients: [],
    steps: [],
    updateMessage: "",
    messageType: "info",
    isBookmarked: false,
    showShareMenu: false,

    // タグ関連
    editableTags: [], // 編集用タグ文字列配列
    newTagName: "",   // 新規タグ入力
    tagIdMap: {},     // { tagName: tagId } 既存タグID保持

    // Wake Lock関連
    wakeLock: null,
    wakeLockActive: false,
  };
},
computed: {
  recipeId() {
    return this.$route.params.id;
  },
  /**
   * @description レシピのタイトルを表示。this.recipeがnullの場合は読み込み中メッセージを返すことで、
   * nullアクセスによるエラーを防ぐ。
   */
  displayTitle() {
    // ★修正: this.recipe が null の場合に早期リターン
    if (!this.recipe) return "レシピを読み込み中..."; 

    if (this.recipe.title) return this.recipe.title;
    if (this.recipe.memo) {
      const firstLine = this.recipe.memo
        .split("\n")[0]
        .replace(/^===\s*/, "")
        .replace(/\s*===$/, "");
      return firstLine || this.recipe.memo.substring(0, 30) + "...";
    }
    return "無題のレシピ";
  },
  /**
   * @description レシピの材料リストを計算。
   * this.recipe が null の場合に備え、nullアクセスによるエラーを防ぐガードを強化。
   */
  recipeIngredients() {
    // ★修正: this.recipe が null の場合に早期リターンすることで、後のthis.recipe.ingredientsへのアクセスを防ぐ
    if (!this.recipe) return []; 

    // APIからingredients配列が直接提供されている場合
    if (Array.isArray(this.recipe.ingredients) && this.recipe.ingredients.length)
      return this.recipe.ingredients;
      
    // memoからパースするロジック (this.recipeが存在することが保証されている)
    if (!this.recipe.memo) return [];
    const memo = this.recipe.memo;
    const start = memo.indexOf(INGREDIENTS_SEPARATOR);
    const end = memo.indexOf(STEPS_SEPARATOR);
    if (start === -1 || end === -1 || start > end) return [];
    return memo
      .substring(start + INGREDIENTS_SEPARATOR.length, end)
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0);
  },
  /**
   * @description レシピの作り方リストを計算。
   * this.recipe が null の場合に備え、nullアクセスによるエラーを防ぐガードを強化。
   */
  recipeSteps() {
    // ★修正: this.recipe が null の場合に早期リターン
    if (!this.recipe) return [];

    // APIからsteps配列が直接提供されている場合
    if (Array.isArray(this.recipe.steps) && this.recipe.steps.length) return this.recipe.steps;
    
    // memoからパースするロジック
    if (!this.recipe.memo) return [];
    const memo = this.recipe.memo;
    const start = memo.indexOf(STEPS_SEPARATOR);
    if (start === -1) return [];
    return memo
      .substring(start + STEPS_SEPARATOR.length)
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0);
  },
  xShareUrl() {
    return `https://twitter.com/intent/tweet?url=${encodeURIComponent(window.location.href)}`;
  },
  facebookShareUrl() {
    return `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(window.location.href)}`;
  },
  pinterestShareUrl() {
    return `https://www.pinterest.com/pin/create/button/?url=${encodeURIComponent(window.location.href)}`;
  },
},
methods: {
  // ========================
  // Wake Lock制御
  // ========================
  async requestWakeLock() {
    try {
      if ("wakeLock" in navigator) {
        this.wakeLock = await navigator.wakeLock.request("screen");
        this.wakeLockActive = true;
        console.log("✅ Wake Lock 有効化");
        this.wakeLock.addEventListener("release", () => {
          this.wakeLockActive = false;
          console.log("⚠️ Wake Lockが解除されました");
        });
      } else {
        // alertの代わりにconsole.errorを使用
        console.error("このブラウザはWake Lock APIに対応していません。");
      }
    } catch (err) {
      console.error("Wake Lock取得失敗:", err);
      this.wakeLockActive = false;
    }
  },
  async releaseWakeLock() {
    if (this.wakeLock) {
      try {
        await this.wakeLock.release();
        this.wakeLock = null;
        this.wakeLockActive = false;
        console.log("🔓 Wake Lock解除");
      } catch (err) {
        console.error("Wake Lock解除失敗:", err);
      }
    }
  },
  async toggleWakeLock() {
    if (this.wakeLockActive) {
      await this.releaseWakeLock();
    } else {
      await this.requestWakeLock();
    }
  },

  parseMemoToArrays(memoText) {
    if (!memoText) return { ingredients: [""], steps: [""] };
    const ingredients = [];
    const steps = [];
    const startIng = memoText.indexOf(INGREDIENTS_SEPARATOR);
    const startSteps = memoText.indexOf(STEPS_SEPARATOR);
    if (startIng !== -1 && startSteps !== -1 && startIng < startSteps) {
      const ingText = memoText.substring(startIng + INGREDIENTS_SEPARATOR.length, startSteps).trim();
      if (ingText) ingredients.push(...ingText.split("\n").map((l) => l.trim()).filter((l) => l.length > 0));
      const stepText = memoText.substring(startSteps + STEPS_SEPARATOR.length).trim();
      if (stepText) steps.push(...stepText.split("\n").map((l) => l.trim()).filter((l) => l.length > 0));
    } else {
      steps.push(...memoText.split("\n").map((l) => l.trim()).filter((l) => l.length > 0));
    }
    if (ingredients.length === 0) ingredients.push("");
    if (steps.length === 0) steps.push("");
    return { ingredients, steps };
  },

  toggleEditMode() {
    // this.recipe が存在しない場合は編集モードに移行しない
    if (!this.recipe) return;

    this.isEditing = true;
    this.editableTitle = this.recipe.title || "";
    this.editablePhoto = this.recipe.photo;
    this.newPhotoFile = null;
    this.updateMessage = "";
    
    // 既にAPIからingredients/stepsが配列で来ていればそれを使う、なければmemoからパースしたものを使う
    const initialIngredients = Array.isArray(this.recipe.ingredients) 
      ? this.recipe.ingredients.filter(l => l.trim() !== '') : [];
    const initialSteps = Array.isArray(this.recipe.steps) 
      ? this.recipe.steps.filter(l => l.trim() !== '') : [];
    
    // APIデータが空の場合はmemoをパース
    if (initialIngredients.length === 0 || initialSteps.length === 0) {
      const parsed = this.parseMemoToArrays(this.recipe.memo || "");
      this.ingredients = parsed.ingredients;
      this.steps = parsed.steps;
    } else {
      this.ingredients = initialIngredients.length === 0 ? [''] : initialIngredients;
      this.steps = initialSteps.length === 0 ? [''] : initialSteps;
    }
  },
  cancelEdit() {
    this.isEditing = false;
    this.editableTitle = this.recipe.title || "";
    this.editablePhoto = this.recipe.photo;
    this.newPhotoFile = null;
    this.updateMessage = "";
    this.fetchRecipeDetail();
  },
  onFileChange(event) {
    const file = event.target.files[0];
    if (file) {
      this.newPhotoFile = file;
      this.editablePhoto = URL.createObjectURL(file);
    }
  },
  addIngredient() {
    this.ingredients.push("");
  },
  removeIngredient(index) {
    this.ingredients.splice(index, 1);
    if (this.ingredients.length === 0) this.ingredients.push("");
  },
  addStep() {
    this.steps.push("");
  },
  removeStep(index) {
    this.steps.splice(index, 1);
    if (this.steps.length === 0) this.steps.push("");
  },

  // ========================
  // タグ操作
  // ========================
  addTag() {
    const tag = this.newTagName.trim();
    if (!tag) return;
    if (!this.editableTags.includes(tag)) {
      this.editableTags.push(tag);
    }
    this.newTagName = "";
  },
  removeTag(index) {
    this.editableTags.splice(index, 1);
  },

  printRecipe() {
    window.print();
  },
  async copyUrl() {
  try {
    await navigator.clipboard.writeText(window.location.href);
    // 成功したら画面上にメッセージを表示
    this.updateMessage = "✅ URLをコピーしました！";
    this.messageType = "success";
    // 3秒後に自動で消える
    setTimeout(() => (this.updateMessage = ""), 3000);
  } catch (err) {
    console.error("コピーに失敗:", err);
    this.updateMessage = "❌ URLのコピーに失敗しました";
    this.messageType = "error";
    setTimeout(() => (this.updateMessage = ""), 3000);
  }
},

  toggleShareMenu() {
    this.showShareMenu = !this.showShareMenu;
  },

  async fetchRecipeDetail() {
    this.loading = true;
    this.isEditing = false;
    this.updateMessage = "";
    this.error = null;
    // エラー時に備え、初期値を設定
    this.recipe = null;
    this.ingredients = []; 
    this.steps = []; 
    this.editableTags = []; 
    this.tagIdMap = {};

    try {
      const res = await axios.get(`http://127.0.0.1:8000/api/recipes/${this.recipeId}/`, {
        withCredentials: true,
      });

      // 成功したらデータを設定
      this.recipe = res.data || {};
      this.editableTitle = this.recipe.title || "";
      this.editablePhoto = this.recipe.photo || null;

      // memo 解析して必ず配列を返す
      const parsed = this.parseMemoToArrays(this.recipe.memo || "");
      this.ingredients = Array.isArray(this.recipe.ingredients) 
        ? this.recipe.ingredients.filter(l => l.trim() !== '') : parsed.ingredients;
      this.steps = Array.isArray(this.recipe.steps) 
        ? this.recipe.steps.filter(l => l.trim() !== '') : parsed.steps;
      
      // 編集用配列が空の場合の初期値を設定
      if (this.ingredients.length === 0) this.ingredients.push('');
      if (this.steps.length === 0) this.steps.push('');


      // タグセット（編集用配列 + IDマップ）
      this.editableTags = Array.isArray(this.recipe.tags)
        ? this.recipe.tags.map((t) => t.name)
        : [];
      this.tagIdMap = {};
      if (Array.isArray(this.recipe.tags)) {
        this.recipe.tags.forEach((t) => {
          if (t.id && t.name) this.tagIdMap[t.name] = t.id;
        });
      }

    } catch (err) {
      console.error("Recipe detail fetch error:", err.response?.data || err.message);
      this.error = "レシピの取得に失敗しました。";
      // エラー時は recipe を null のままにして、テンプレートの v-else が処理するようにする
      this.recipe = null; 
      
    } finally {
      this.loading = false;
    }
  },


  async updateRecipe() {
    this.updateMessage = "保存中...";
    this.messageType = "info";

    try {
      const ingredientsArray = this.ingredients.map(l => l.trim()).filter(l => l !== "");
      const stepsArray = this.steps.map(l => l.trim()).filter(l => l !== "");

      // タグID配列作成（既存タグはID、新規タグは名前）
      const tagIds = [];
      const newTags = [];
      this.editableTags.forEach(tag => {
        if (!tag || tag.trim() === "") return; // 空文字を除外
        const id = this.tagIdMap[tag];
        if (id) tagIds.push(id);
        else newTags.push(tag.trim());
      });

      let response;
      if (this.newPhotoFile) {
        const formData = new FormData();
        formData.append("title", this.editableTitle);
        formData.append("ingredients", JSON.stringify(ingredientsArray));
        formData.append("steps", JSON.stringify(stepsArray));
        formData.append("tag_ids", JSON.stringify(tagIds));
        formData.append("new_tags", JSON.stringify(newTags));
        formData.append("photo", this.newPhotoFile);

        response = await axios.patch(
          `http://127.0.0.1:8000/api/recipes/${this.recipeId}/`,
          formData,
          {
            withCredentials: true,
            headers: {
              "Content-Type": "multipart/form-data",
              "X-CSRFToken": getCookie("csrftoken"),
            },
          }
        );
      } else {
        response = await axios.patch(
          `http://127.0.0.1:8000/api/recipes/${this.recipeId}/`,
          {
            title: this.editableTitle,
            ingredients: ingredientsArray,
            steps: stepsArray,
            tag_ids: tagIds,
            new_tags: newTags,
          },
          {
            withCredentials: true,
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCookie("csrftoken"),
            },
          }
        );
      }

      this.recipe = response.data;
      this.isEditing = false;
      this.newPhotoFile = null;
      this.updateMessage = "✅ レシピが正常に更新されました！";
      this.messageType = "success";

      setTimeout(() => (this.updateMessage = ""), 5000);
    } catch (err) {
      console.error("更新エラー:", err.response?.data || err.message);
      this.updateMessage = "更新に失敗しました。入力データを確認してください。";
      this.messageType = "error";
      setTimeout(() => (this.updateMessage = ""), 8000);
    }
  },

  async checkBookmarkStatus() {
    try {
      const res = await axios.get(
        `http://127.0.0.1:8000/api/bookmarks/toggle/?model=recipes.Recipe&object_id=${this.recipeId}`,
        { withCredentials: true }
      );
      this.isBookmarked = res.data.bookmarked;
    } catch (err) {
      console.warn("ブックマーク状態の取得に失敗:", err);
    }
  },
  async toggleBookmark() {
    try {
      const res = await axios.post(
        `http://127.0.0.1:8000/api/bookmarks/toggle/`,
        { model: "recipes.Recipe", object_id: this.recipeId },
        {
          withCredentials: true,
          headers: { "Content-Type": "application/json", "X-CSRFToken": getCookie("csrftoken") },
        }
      );
      this.isBookmarked = res.data.bookmarked;
    } catch (err) {
      console.error("ブックマーク切替に失敗:", err);
    }
  },
  goBack() {
    this.$router.back();
  },
},
mounted() {
  if (this.recipeId) {
    this.fetchRecipeDetail().then(() => {
      // レシピ取得後にブックマーク状態を確認（recipeがnullでない場合のみ）
      if (this.recipe && this.recipe.id) {
        this.checkBookmarkStatus();
      }
    });
  }
  document.addEventListener("visibilitychange", async () => {
    if (document.visibilityState === "visible" && this.wakeLockActive) {
      await this.requestWakeLock();
    }
  });
},
beforeUnmount() {
  this.releaseWakeLock();
},
watch: {
  recipeId(newId) {
    if (newId) this.fetchRecipeDetail();
  },
},
};
</script>




<style>

:deep(body) {
background-color: #fafafa;
margin: 0;
padding: 0;
}
:deep(#app) {
display: flex;
justify-content: center;
align-items: flex-start;
min-height: 100vh;
padding-top: 60px;
padding-bottom: 60px;
box-sizing: border-box;
}
.recipe-detail-container {
max-width: 720px;
width: 100%;
background-color: #fff;
border-radius: 16px;
box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
padding: 50px 40px;
margin: 0 auto;
}
.recipe-detail-container {
/* 表示領域を2回り小さく */
max-width: 720px; /* 900px → 720pxに縮小 */
margin: 60px auto; /* 上下にも余白を多めに */
padding: 50px 40px; /* 内側余白を少し増やす */
background-color: #ffffff;
border-radius: 16px;
box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
font-family: 'Comic Neue', 'Yu Gothic', sans-serif;
color: #222; /* 全体のテキストもやや濃く */
}

/* ============================
フォーム以外の全体フォント
============================ */


.back-button {
    background: none;
    border: none;
    color: #4E8098;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    padding: 8px 15px;
    border-radius: 8px;
    transition: background-color 0.2s;
    display: flex;
    align-items: center;
    gap: 5px;
    /* 編集ボタンと重ならないように左寄せを維持 */
    order: -1; 
}

.back-button:hover { background-color: #f0f0f0; }

/* ★追加: 編集/保存ボタンのスタイル */
.action-buttons {
    display: flex;
    gap: 10px;
    position: absolute;
    right: 0;
}
.edit-button, .save-button, .cancel-button {
    padding: 10px 15px;
    border-radius: 8px;
    font-weight: 700;
    cursor: pointer;
    transition: background-color 0.2s, transform 0.1s;
    display: flex;
    align-items: center;
    gap: 5px;
    border: none;
}
.edit-button {
    background-color: #4E8098;
    color: white;
}
.save-button {
    background-color: #27ae60;
    color: white;
}
.cancel-button {
    background-color: #ecf0f1;
    color: #333;
    border: 1px solid #ccc;
}
.edit-button:hover { background-color: #483d8b; }
.save-button:hover { background-color: #2ecc71; }
.cancel-button:hover { background-color: #dfe6e9; }


.title-bookmark-wrapper {
  display: flex;
  align-items: center; /* 縦位置を中央揃え */
  gap: 10px;           /* タイトルとボタンの間隔 */
}

.recipe-title {
  margin: 0;
  font-size: 1.5rem;
}

/* ★追加: 編集フィールドのスタイル */
.editable-title-input {
max-width: 40%;
width: auto; 
font-size: 2.2rem;
font-weight: 800;
color: #333;
border: none;
border-bottom: 3px solid #ff9ff3; /* ポップなピンク下線 */
background-color: transparent;
margin-bottom: 50px;
outline: none;
transition: border-color 0.3s, transform 0.1s;
font-family: 'Comic Neue', 'Yu Gothic', sans-serif;
}
.editable-title-input:focus {
border-bottom-color: #54a0ff; /* フォーカス時は明るいブルー */

}

.bookmark-button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.6rem;
  transition: transform 0.2s;
}

/* ブックマークアイコンの色を状態で切替 */
.bookmark-button i {
  color: #555; /* デフォルト: グレー */
  transition: color 0.2s;
}

.bookmark-button.bookmarked i {
  color: #ffb700; /* ブックマーク済み: オレンジ色 */
}



.bookmark-button:hover {
  transform: scale(1.1);
}

.content-wrapper {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 25px;
}

/* 画像ボックス */
.image-box {
  flex: 0 0 45%; /* 全体の45%まで */
  aspect-ratio: 4 / 5; /* 縦長比率を維持（例: 4:5） */
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

/* 画像本体 */
.recipe-image {
  width: 100%;
  height: 100%;
  object-fit: cover; /* 比率を維持しつつ切り抜き */
  display: block;
}

/* 半透明黒帯＋投稿者 */
.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.4);
  text-align: right;
}

.recipe-author {
  color: #fff;
  font-size: 0.9rem;
  font-weight: 500;
}




.no-image {
    width: 100%;
    height: 300px;
    background-color: #e0e0e0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #666;
    font-weight: bold;
}

/* 画像変更UIのスタイル */
.photo-edit-overlay {
    position: absolute;
    bottom: 10px;
    right: 10px;
    padding: 8px 12px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 5; /* 画像ラベルより前面に表示してボタンだけにクリック可能範囲を限定 */
    transition: background 0.25s;
}


.photo-upload-label {
background-color: #ffeaa7; /* 柔らかいイエロー */
padding: 12px 24px;
border-radius: 10px;
font-weight: bold;
cursor: pointer;
transition: background-color 0.25s, transform 0.1s;
display: inline-flex;
align-items: center;
gap: 10px;
margin-top: 15px;
margin-left: 10px;

}
.photo-upload-label:hover {
background-color: #fdcb6e; /* 濃いめの黄色に変化 */
transform: translateY(-2px);
}
/* 「Choose File」ボタンのブラウザ標準デザインを隠したい*/
.photo-upload-input {
display: none;
}
/* ============================
フォーム部品の基本スタイル
============================ */
/* input[type="text"]はタイトル入力用として残す */


input[type="text"] {
width: 80%;
border-radius: 0;
border: none;/*デフォルトの角丸をなくすことで跳ね上げ0 */
border-bottom:4px solid #FFB6C1;
outline: none;
font-size: 1.1rem;
background: transparent;
}
input[type="text"]:focus {
border-bottom-color: #4DB6AC;
}




/* ============================
リスト形式の編集UI
============================ */
.ingredients-section, .steps-section {
    margin-bottom: 30px;

}
.list-item-row {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;

}



.step-index {
    font-weight: bold;
    color: #333333;
    width: 20px; /* 番号の幅を固定 */
    flex-shrink: 0;
}


textarea.form-control {
width: 100%;
height: 30%;
padding: 8px;
border: solid #ccc;
border-radius: 4px;
font-size: 1rem;
resize: vertical;
min-height: 40px; /* 最小の高さ */
transition: border-color 0.2s;
box-sizing: border-box;
}

.btn-add {
    background-color: #d4f7e2; /* 淡いグリーン */
    color: #1a7e43;
    border: 1px solid #7edc99;
    padding: 8px 15px;
    border-radius: 20px;
    font-size: 0.9rem;
    cursor: pointer;
    transition: background-color 0.2s;
    margin-top: 10px;
    display: inline-block;
}
.btn-add:hover {
    background-color: #aae0bb;
}

.btn-remove {
    background-color: #ffcccc; /* 淡いレッド */
    color: #c0392b;
    border: none;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    font-weight: bold;
    font-size: 1.2rem;
    line-height: 1;
    cursor: pointer;
    transition: background-color 0.2s;
    flex-shrink: 0;
}
.btn-remove:hover {
    background-color: #ff9999;
}

/* ============================
リスト形式の表示UI
============================ */
.list-display {
    list-style: none;
    padding: 0;
    margin-top: 10px;
}
.list-display li {
    margin-bottom: 8px;
    padding: 5px 0;
    line-height: 1.6;
    color: #444;
}

/* 材料リストのスタイル */
.ingredients-section .list-display li {
    display: flex;
    gap: 10px;
    border-bottom: 1px dashed #eee;
}
.ingredients-section .list-display li:last-child {
    border-bottom: none;
}
.list-index {
    color: #4E8098; /* 強調色 */
    font-weight: bold;
}

/* 作り方リストのスタイル */
.steps-section .list-display {
    list-style-type: decimal; /* 番号付きリスト */
    padding-left: 20px;
}
.steps-section .list-display li {
    font-size: 1rem;
    padding-left: 5px;
    counter-increment: step-counter;
}

.empty-list-message {
    color: #999;
    font-style: italic;
    margin-top: 15px;
}


.image-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(0, 0, 0, 0.5);
    padding: 10px;
    color: white;
    font-size: 1rem;
    font-weight: 500;
}

.recipe-author {
    font-style: italic;
}

.detail-box {
    flex: 1;
    padding-top: 10px;
}

.detail-box h2 {
    font-size: 1.5rem;
    color: #4E8098;
    border-bottom: 2px solid #4E8098;
    padding-bottom: 5px;
    margin-bottom: 20px;
}

.section-title {
    font-size: 1.2rem;
    color: #333;
    margin-bottom: 10px;
    font-weight: 700;
    display: block;
}

.metadata {
    display: flex;
    gap: 20px;
    margin-bottom: 30px;
}

.meta-item {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #e74c3c;
    font-weight: 600;
}

.loading-message, .error-message {
    text-align: center;
    padding: 50px;
    font-size: 1.2rem;
    color: #888;
    border: 2px dashed #ccc;
    border-radius: 10px;
}

.error-message i {
    color: #e74c3c;
    margin-right: 10px;
}

/* ★追加: メッセージボックスのスタイル */
.message-box {
    padding: 10px 15px;
    border-radius: 8px;
    margin-top: 20px;
    font-weight: 600;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
.info {
    background-color: #e7f3ff;
    color: #004085;
    border: 1px solid #b8daff;
}
.success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}
.error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}


/* Font Awesomeのfont-weight競合対策 (新規追加) */
.fa-solid {
    /* グローバルリセット(* { font-weight: normal; })に勝つために強制的に900を適用 */
    font-weight: 900 !important;
}

/* アクションボタン */
.recipe-actions {
    display: flex;
    gap: 10px;
    margin-top: 15px;
    margin-bottom: 15px;
}
.action-btn {
    background: #f0f0f0;
    border: none;
    padding: 8px 10px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1.2rem;
    transition: background-color 0.2s;
}
.action-btn:hover { background-color: #e0e0e0; }

/* Wake Lock 専用スタイル */
.wake-lock-btn {
  background: none;
  border: none;
  color: #049c71;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}


.wake-lock-on {
  color: green;
}
.wake-lock-off {
  color: rgb(102, 105, 102);
}

/* SNSドロップダウン */
.share-dropdown { position: relative; display: inline-block; }
.share-menu {
    position: absolute;
    top: 40px;
    right: 0;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 8px 12px;
    display: flex;
    gap: 10px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.15);
    z-index: 100;
}
.share-menu a { font-size: 1.2rem; color: #333; }
.share-menu a:hover { color: #5A4DA0; }

.tag-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background-color: #f0f0f0;
  padding: 5px 10px;
  border-radius: 12px;
  font-size: 0.9rem;
  margin-right: 5px;
  margin-bottom: 5px;
}
.tag-badge.editable {
  background-color: #ffeaa7;
}
.btn-remove-tag {
  background: transparent;
  border: none;
  color: #c0392b;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}
.add-tag-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}
.tag-input {
  flex-grow: 1;
  padding: 6px 10px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
}
.btn-add-tag {
  background-color: #d4f7e2;
  color: #1a7e43;
  border: 1px solid #7edc99;
  padding: 6px 12px;
  border-radius: 20px;
  cursor: pointer;
}
.btn-add-tag:hover {
  background-color: #aae0bb;
}


/* タグ */
.recipe-tags-section {
    margin-bottom: 25px;
}

.tag-badge {
    display: inline-flex;
    align-items: center;
    background: #ffeaa7;
    color: #2d3436;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.9rem;
    margin: 4px 4px 0 0;
}

.tag-badge:hover {
  background-color: #ff922b;
}
.tag-badge.editable {
    background: #dfe6e9;
    color: #333;
}

.btn-remove-tag {
    background: transparent;
    border: none;
    font-size: 0.9rem;
    margin-left: 4px;
    cursor: pointer;
}

.add-tag-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 8px;
}

.message-box {
  padding: 12px 16px;
  border-radius: 8px;
  margin-top: 20px;
  font-weight: 600;
  font-size: 14px;
  text-align: center;
  transition: opacity 0.3s;
}

/* 状態別カラー */
.message-box.info {
  background-color: #d0e6ff;
  color: #0056b3;
}
.message-box.success {
  background-color: #d4edda;
  color: #155724;
}
.message-box.error {
  background-color: #f8d7da;
  color: #721c24;
}


/* 印刷用レイアウト */
@media print {
    body * { visibility: hidden; }
    .recipe-detail-container, .recipe-detail-container * { visibility: visible; }
    .recipe-detail-container { width: 100%; padding: 0; margin: 0; box-shadow: none; }
    .recipe-actions, .back-button, .edit-button, .save-button, .cancel-button, .bookmark-button { display: none; }
}


/* レスポンシブ対応 */
@media (max-width: 768px) {
    .recipe-detail-container {
    padding: 15px;
    margin: 10px auto;
    }
    .content-wrapper {
    flex-direction: column;
    gap: 20px;
    }
    .image-box {
    min-width: 100%;
    aspect-ratio: auto; /* 画像を自然比率で表示 */
    }
    .recipe-title {
    font-size: 1.8rem;
    }
    .action-buttons {
    /* モバイルではボタンを右上に固定 */
    position: static;
    justify-content: flex-end;
    margin-top: -10px;
    margin-bottom: 10px;
    width: 100%;
    }
    .header-section {
    flex-wrap: wrap;
    justify-content: space-between;
    }
    .back-button {
    margin-bottom: 10px;
    order: 1;
    }
}
</style>
