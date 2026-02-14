<template>
  <div class="timeline">
    <div v-if="loading && recipes.length === 0" class="loading">
      <i class="fa-solid fa-spinner fa-spin"></i> レシピを読み込み中...
    </div>

    <swiper
      v-else
      ref="mySwiper"
      direction="vertical"
      :slides-per-view="1"
      :observer="true"
      :observe-parents="true"
      :update-on-window-resize="true"
      :speed="500"
      class="timeline-swiper"
      @slideChange="onSlideChange"
      @swiper="onSwiperInit"
    >
      <swiper-slide
        v-for="recipe in recipes"
        :key="recipe.id"
        class="shorts-slide"
      >
        <div class="slide-content">
          <img
            :src="recipe.photo"
            @click="goToRecipeDetail(recipe.id)"
            class="slide-img"
            @load="onImageLoad"
            @error="onImageError(recipe.id)"
          />

      <div class="overlay">
          <div class="caption">
            <h1>{{ recipe.title }}</h1>
          </div>
        <!-- tag表示欄 -->
          <div class="card-footer">
            <span v-for="tag in recipe.tags" :key="tag.id" class="tag-mini">#{{ tag.name }}</span>
          </div>


          <div class="actions">
            <i
              :class="['fa-heart', recipe.liked ? 'fa-solid' : 'fa-regular']"
              @click="toggleLike(recipe)"
            ></i>

            <!-- bookmarkアイコン -->
            <i
              class="fa-bookmark"
              :class="{
                bookmarked: recipe.bookmarked,
                'fa-solid': recipe.bookmarked,
                'fa-regular': !recipe.bookmarked
              }"
              @click="toggleBookmark(recipe)"
            ></i>

            <!-- コメントアイコン -->
            <i
              class="fa-comment"
              :class="recipe.commented ? 'fa-solid commented' : 'fa-regular'"
              @click="toggleComments(recipe)"
            ></i>
          </div>
        </div>

          <transition name="slide-horizontal">
            <div
              v-show="
                activeRecipeForComment &&
                activeRecipeForComment.id === recipe.id
              "
              class="comment-overlay"
            >
              <div class="comment-body">
                <!-- コメント入力欄と投稿ボタン -->
                <div class="comment-input-area">
                  <textarea
                    v-model="newComment"
                    placeholder="コメントを書く..."
                    class="comment-input"
                  ></textarea>
                  <button
                    class="comment-submit-btn"
                    @click="postComment(recipe)"
                  >
                    投稿
                  </button>
                </div>

                <div
                  v-for="comment in recipe.comments || []"
                  :key="comment.id"
                  class="comment-item"
                >
                  <img
                    :src="getAvatarUrl(comment.author?.avatar)"
                    class="avatar"
                    alt="avatar"
                    @error="handleAvatarError"
                  />
                  <span>
                    {{ comment.author?.username || '匿名' }}: {{ comment.text }}
                  </span>

                  <button
                    v-if="
                      loggedInUser &&
                      comment.author?.id === loggedInUser.id
                    "
                    @click="deleteComment(comment, recipe)"
                    class="delete-comment-btn"
                  >
                    <i class="fa-solid fa-trash"></i>
                  </button>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </swiper-slide>

      <swiper-slide
        v-if="fetchingNext"
        key="loading-next-page"
        class="shorts-slide loading-next"
      >
        <div class="loading">
          <i class="fa-solid fa-spinner fa-spin"></i> レシピを連続取得中...
        </div>
      </swiper-slide>
    </swiper>
  </div>
</template>



<script>
import { Swiper, SwiperSlide } from "swiper/vue";
import "swiper/css/bundle";
import axios from "axios";

export default {
  components: { Swiper, SwiperSlide },

  data() {
    return {
      recipes: [],
      loading: true,
      fetchingNext: false,
      activeRecipeForComment: null,
      newComment: "",
      loggedInUser: null,
      loggedInUserAvatar: null,
      isAuthenticated: false,
      swiper: null,
      injectedAvatarUrl: null, // DOMから取得するHTML用
    };
  },

  methods: {
    async fetchRecipes() {
  try {
    const res = await axios.get("http://127.0.0.1:8000/api/recipes/", {
      withCredentials: true,
    });
    const recipes = res.data;

    // ブックマーク済みリストを取得
    let bookmarkedIds = [];
    if (this.isAuthenticated) {
      const bmRes = await axios.get("http://127.0.0.1:8000/api/bookmarks/list/", {
        withCredentials: true,
      });
      bookmarkedIds = bmRes.data.map(r => r.id);
    }

    // recipe.bookmarked & recipe.commented を反映
    this.recipes = await Promise.all(
      recipes.map(async (r) => {
        const recipe = { ...r, bookmarked: bookmarkedIds.includes(r.id), commented: false };

        if (this.isAuthenticated) {
          try {
            const comRes = await axios.get("http://127.0.0.1:8000/comments/list/", {
              params: { object_id: recipe.id, content_type_id: 9 },
              withCredentials: true,
            });
            recipe.comments = comRes.data.comments || [];
            recipe.commented = recipe.comments.length > 0;
          } catch {
            recipe.comments = [];
          }
        }

        return recipe;
      })
    );

    this.loading = false;
    this.fetchingNext = false;
  } catch (e) {
    console.error("Failed to fetch recipes:", e);
    this.loading = false;
  }
},

    async fetchCurrentUser() {
      try {
        const res = await axios.get(
          "http://127.0.0.1:8000/users/api/current-user/",
          { withCredentials: true }
        );

        this.loggedInUser = res.data;

        // APIからavatarがない場合はHTML側のURLを使う
        this.loggedInUserAvatar =
          res.data.avatar_url && !res.data.avatar_url.includes("default_avatar.svg")
            ? res.data.avatar_url
            : this.injectedAvatarUrl;

        this.isAuthenticated = true;
      } catch {
        // API取得失敗時はHTML側のURLを使う
        this.loggedInUser = null;
        this.loggedInUserAvatar = this.injectedAvatarUrl;
        this.isAuthenticated = !!this.injectedAvatarUrl;
      }
    },

    toggleComments(recipe) {
      if (!this.isAuthenticated) {
        alert("ログインしてください");
        return;
      }
      if (
        this.activeRecipeForComment &&
        this.activeRecipeForComment.id === recipe.id
      ) {
        this.activeRecipeForComment = null;
      } else {
        this.activeRecipeForComment = recipe;
        if (!recipe.comments) this.fetchComments(recipe);
      }
    },

    async fetchComments(recipe) {
      try {
        const res = await axios.get("http://127.0.0.1:8000/comments/list/", {
          params: { object_id: recipe.id, content_type_id: 9 },
          withCredentials: true,
        });
        recipe.comments = (res.data.comments || []).map((comment) => {
          return {
            ...comment,
            author: {
              ...comment.author,
              avatar: comment.author?.avatar
                ? comment.author.avatar.startsWith("http")
                  ? comment.author.avatar
                  : `http://127.0.0.1:8000${comment.author.avatar}`
                : null,
            },
          };
        });
      } catch (e) {
        console.error("コメント取得失敗:", e);
        recipe.comments = [];
      }
    },

    async postComment(recipe) {
  const text = this.newComment.trim();
  if (!text) return;

  const csrftoken = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1];

  try {
    const res = await axios.post(
      "http://127.0.0.1:8000/comments/add/",
      { object_id: recipe.id, content_type_id: 9, text },
      { headers: { "X-CSRFToken": csrftoken }, withCredentials: true }
    );

    recipe.comments = [res.data.comment, ...(recipe.comments || [])];
    recipe.commented = true; // ★コメント済みにする
    this.newComment = "";

    this.$nextTick(() => {
      this.$refs.mySwiper?.swiper?.updateAutoHeight();
    });
  } catch (e) {
    console.error("コメント投稿失敗:", e);
    alert("コメント送信に失敗しました");
  }
},

    async deleteComment(comment, recipe) {
      if (!confirm("このコメントを削除しますか？")) return;

      const csrftoken = document.cookie
        .split("; ")
        .find((r) => r.startsWith("csrftoken="))
        ?.split("=")[1];

      try {
        await axios.post(
          `http://127.0.0.1:8000/comments/delete/${comment.id}/`,
          {},
          { headers: { "X-CSRFToken": csrftoken }, withCredentials: true }
        );
        recipe.comments = recipe.comments.filter((c) => c.id !== comment.id);
        recipe.commented = recipe.comments.length > 0; // ★最後のコメント削除でアイコン更新
      } catch (e) {
        console.error("コメント削除失敗:", e);
      }
    },

    getAvatarUrl(avatarPath) {
      if (avatarPath) {
        if (avatarPath.startsWith("http")) return avatarPath;
        return `http://127.0.0.1:8000${avatarPath}`;
      }
      if (this.loggedInUserAvatar) return this.loggedInUserAvatar;
      return "http://127.0.0.1:8000/static/images/default_avatar.svg";
    },

    handleAvatarError(e) {
      if (e.target.src.includes("default_avatar.svg")) return;
      e.target.src = "http://127.0.0.1:8000/static/images/default_avatar.svg";
    },

    onSwiperInit(swiper) {
      this.swiper = swiper;
    },
    onSlideChange() {},
    onImageLoad() {
      this.$refs.mySwiper?.swiper?.updateAutoHeight();
    },
    onImageError(recipeId) {
      console.warn(`画像読み込み失敗: レシピID ${recipeId}`);
    },

    async toggleLike(recipe) {
      if (!this.isAuthenticated) return alert("ログインしてください");
      const csrftoken = document.cookie
        .split("; ")
        .find((r) => r.startsWith("csrftoken="))
        ?.split("=")[1];

      try {
        const res = await axios.post(
          "http://127.0.0.1:8000/api/likes/toggle/",
          { model: "recipes.Recipe", object_id: recipe.id },
          { headers: { "X-CSRFToken": csrftoken }, withCredentials: true }
        );
        recipe.liked = res.data.liked;
      } catch (e) {
        console.error("Like toggle failed:", e);
      }
    },

    async toggleBookmark(recipe) {
  if (!this.isAuthenticated) return alert("ログインしてください");

  // 即反映
  recipe.bookmarked = !recipe.bookmarked;

  const csrftoken = document.cookie
    .split("; ")
    .find((r) => r.startsWith("csrftoken="))
    ?.split("=")[1];

  try {
    const res = await axios.post(
      "http://127.0.0.1:8000/api/bookmarks/toggle/",
      { model: "recipes.Recipe", object_id: recipe.id },
      { headers: { "X-CSRFToken": csrftoken }, withCredentials: true }
    );
    recipe.bookmarked = res.data.bookmarked; // API反映
  } catch (e) {
    console.error("Bookmark toggle failed:", e);
    // 失敗したら元に戻す
    recipe.bookmarked = !recipe.bookmarked;
  }
},

    goToRecipeDetail(id) {
      this.$router.push(`/recipe/${id}`);
    },
  },

  async mounted() {
    axios.defaults.withCredentials = true;

    // HTMLの隠しタグから avatar URL を取得
    const el = document.getElementById("avatar-url");
    this.injectedAvatarUrl = el?.textContent?.trim() || null;
    this.loggedInUserAvatar = this.injectedAvatarUrl;

    await this.fetchCurrentUser();
    await this.fetchRecipes();

    console.log("Injected avatar URL:", this.injectedAvatarUrl);
    console.log("Fetched user avatar:", this.loggedInUserAvatar);
  },
};
</script>

<style scoped>
.timeline { height: 100%; width: 100%; overflow: hidden; background: black; }
.loading { display: flex; justify-content: center; align-items: center; height: 100%; color: white; font-size: 18px; }
.timeline-swiper { height: 100%; }
.timeline-swiper :deep(.swiper-wrapper) { height: 100%; }
.slide-content { 
  position: relative; 
  width: 100%; 
  height: 100%; 
  /* 画像とオーバーレイの位置を制御するために flex を使用 */
  display: flex;
  justify-content: center; /* 横方向中央寄せ */
  align-items: center; /* 縦方向中央寄せ */
}
.shorts-slide {
  display: flex;
  justify-content: center;
  align-items: center;
  background: #333333;
  height: 100% !important;
  padding: 30px 0; /* 上下に余白を追加 */
}


.slide-img {
  width: 55%;            /* 横幅を画面の55%に縮小 */
  height: 50%;           /* 高さも同様に縮小 */
  object-fit: contain;   /* 全体を見せたい場合は contain */
  border-radius: 16px;   /* 角を軽く丸める */
  cursor: pointer;
  display: block;
  /* slide-contentで中央寄せしているので margin: 0 auto; は不要だが、元の構造を維持 */
  margin: 0 auto;
}

.comment-item { display: flex; align-items: center; gap: 10px; margin-top: 10px; }


.delete-comment-btn { margin-left: auto; background: transparent; border: none; color: #ff4b5c; cursor: pointer; font-size: 16px; }
.delete-comment-btn:hover { color: #ff0000; }

/*
=====================================================
 .overlay の幅を画像(.slide-img)に合わせる
=====================================================
*/
.overlay {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 55%;
  height: 25%; /* 下部25%を覆う */
  background: rgba(0, 0, 0, 0.4);
  pointer-events: none;
  /* 下側だけ丸める */
   border-bottom-left-radius: 16px;
  border-bottom-right-radius: 16px;

  /* 上側は丸めない */
  border-top-left-radius: 0;
  border-top-right-radius: 0;
}

.overlay .caption {
  position: absolute;
  bottom: 20px;   /* 半透明の中の下端にタイトル */
  left: 50%;
  transform: translateX(-50%);
  width: 90%;     /* 少し余白を持たせる */
  color: #fff;
  font-weight: 700;
  font-size: 1.4rem;
  text-align: center;
  line-height: 1.2;
}

/* アイコン群の位置を修正 (画像の右端の外側に配置) */
.overlay .actions {
  position: absolute;
  /* 画像の右端から外側に配置 */
  right: -70px; /* 適切なオフセット値に調整してください */
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  pointer-events: auto; /* アイコンをクリック可能に戻す */
}

/* 各アイコンのスタイル */
.overlay .actions i {
  font-size: 2rem;
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  transition: transform 0.2s ease, color 0.2s ease;
}

.overlay .actions i:hover {
  transform: scale(1.2);
  color: #ff7b7b; /* hover時に柔らかく赤系ハイライト */
}

/* 状態別カラー */
.overlay .actions .fa-heart.fa-solid {
  color: #ff6b81;
}
.overlay .actions .fa-bookmark.fa-solid {
  color: #ffd166;
}
.overlay .actions .fa-comment.fa-solid {
  color: #6ecbff;
}

/* solid（コメント済み） */
.fa-comment.fa-solid.commented {
  color: #5bc0eb; /* 水色 */
  transition: color 0.3s;
}

.comment-input-area {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
  width: 100%;
}

/* 入力欄を広く、モダンな見た目に */
.comment-input {
  flex: 1;
  padding: 10px 14px;
  border: 2px solid #5bc0eb; /* 水色の縁 */
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  resize: none;
  height: 60px; /* 高さを少し広げる */
  font-size: 14px;
  line-height: 1.5;
  transition: border-color 0.3s, background 0.3s;
}

.comment-input::placeholder {
  color: #bbb;
}
/* コメント入力欄 */
.comment-input:focus {
  outline: none;
  border-color: #00bfff; /* フォーカス時の青色 */
  background: rgba(255, 255, 255, 0.2);
}

/* 投稿ボタンを強調 */
.comment-submit-btn {
  padding: 10px 18px;
  background: #5bc0eb;
  border: none;
  color: white;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s, transform 0.2s;
}

.comment-submit-btn:hover {
  background: #48a8d9;
  transform: scale(1.05);
}


.comment-overlay { position: absolute; right: 120px; bottom: 60px; width: 60%; height: 80%; background: rgba(0,0,0,0.9); color: white; border-radius: 12px; padding: 20px; overflow-y: auto; }
.avatar { width: 35px; height: 35px; border-radius: 50%; }

 /*タグのスタイル */
.tag-mini {
  display: inline-block;   /* 横並びのまま、paddingやmarginを有効 */
  background-color: #4E8098; /* 背景色 */
  color: #fff;              /* 文字色を白に */
  padding: 4px 8px;         /* 上下左右に空白を追加 */
  border-radius: 12px;      /* 角を少し丸くする */
  margin: 6px;              /* タグ同士の間に余白 */
  font-size: 0.85rem;       /* 少し小さめの文字サイズ */
}

@keyframes pop { 0% { transform: scale(1); } 50% { transform: scale(1.6); } 100% { transform: scale(1); } }

/*スマホでタイトルとアイコンが重なって見えないように調整 */
@media (max-width: 600px) {
  /* スマホでの画像幅に合わせたオーバーレイとアクションの位置調整 */
  .slide-img {
    width: 85%; /* スマホに合わせて画像を広く表示 */
  }
  .overlay {
    width: 85%; /* オーバーレイの幅も画像に合わせる */
  }
  
  .overlay .caption h1 {
    font-size: 0.9rem;
  }
  .overlay .actions {
    right: 3%; /* アイコンを画面の右端に近づける */
    transform: translateY(-70%); /* 中央寄せを元の値に戻す */
    gap: 10px;
  }
}

</style>
