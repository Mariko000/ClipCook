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

          <div class="caption">
            <h3>{{ recipe.title }}</h3>
            <p>{{ recipe.memo || 'No description.' }}</p>
          </div>

          <div class="actions">
            <i
              :class="['fa-heart', recipe.liked ? 'fa-solid' : 'fa-regular']"
              @click="toggleLike(recipe)"
            ></i>
            <i
              :class="['fa-bookmark', recipe.bookmarked ? 'fa-solid' : 'fa-regular']"
              @click="toggleBookmark(recipe)"
            ></i>
            <i class="fa-regular fa-comment" @click="toggleComments(recipe)"></i>
          </div>

          <transition name="slide-horizontal">
            <div
              v-show="activeRecipeForComment && activeRecipeForComment.id === recipe.id"
              class="comment-overlay"
            >
              <div class="comment-body">
                <h4>コメント</h4>
                <textarea v-model="newComment" placeholder="コメントを書く..."></textarea>
                <button @click="postComment(recipe)">投稿</button>

                <div
                  v-for="comment in recipe.comments || []"
                  :key="comment.id"
                  class="comment-item"
                >
                <img
  :key="comment.id"
  :src="getAvatarUrl(comment.author?.avatar)"
  class="avatar"
  alt="avatar"
  @error="handleAvatarError"
/>


                  <span>{{ comment.author?.username || '匿名' }}: {{ comment.text }}</span>

                  <button
                    v-if="loggedInUser && comment.author?.id === loggedInUser.id"
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

      <swiper-slide v-if="fetchingNext" key="loading-next-page" class="shorts-slide loading-next">
        <div class="loading">
          <i class="fa-solid fa-spinner fa-spin"></i> レシピを連続取得中...
        </div>
      </swiper-slide>
    </swiper>
  </div>
</template>

<script>
import { inject } from "vue"; // ✅ 追加
import { Swiper, SwiperSlide } from "swiper/vue";
import "swiper/css/bundle";
import axios from "axios";

export default {
  components: { Swiper, SwiperSlide },

  setup() {
     // HTML側で埋め込まれたアバターURLを取得
    const avatarUrl = inject("avatarUrl", null);
    return { avatarUrl };
  },

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
    };
  },

  methods: {
    async fetchRecipes() {
      try {
        const res = await axios.get("http://127.0.0.1:8000/api/recipes/", {
          withCredentials: true,
        });
        this.recipes = res.data;
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
         //  APIからavatar_urlがない場合のみ、HTML側injectを使う
         this.loggedInUserAvatar =
          res.data.avatar_url && !res.data.avatar_url.includes("default_avatar.svg")
            ? res.data.avatar_url
            : this.injectedAvatarUrl;

        this.isAuthenticated = true;
      } catch {
        // APIが失敗してもHTML側からinjectしたURLを利用
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
      } catch (e) {
        console.error("コメント削除失敗:", e);
      }
    },

    // ✅ injectされた avatarUrl を優先して使うよう修正
    getAvatarUrl(avatarPath) {
      if (avatarPath) {
        if (avatarPath.startsWith("http")) return avatarPath;
        return `http://127.0.0.1:8000${avatarPath}`;
      }
      // injectされたavatarUrlを優先
      if (this.avatarUrl) return this.avatarUrl;
      // fallback
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
        recipe.bookmarked = res.data.bookmarked;
      } catch (e) {
        console.error("Bookmark toggle failed:", e);
      }
    },

    goToRecipeDetail(id) {
      this.$router.push(`/recipe/${id}`);
    },
  },

  async mounted() {
    axios.defaults.withCredentials = true;
    await this.fetchCurrentUser();
    await this.fetchRecipes();
    console.log("Injected avatar URL:", this.injectedAvatarUrl)
     console.log("Fetched user avatar:", this.loggedInUserAvatar)

  },
};
</script>


<style scoped>
.timeline { height: 100%; width: 100%; overflow: hidden; background: black; }
.loading { display: flex; justify-content: center; align-items: center; height: 100%; color: white; font-size: 18px; }
.timeline-swiper { height: 100%; }
.timeline-swiper :deep(.swiper-wrapper) { height: 100%; }
.shorts-slide { display: flex; justify-content: center; align-items: center; background: black; height: 100% !important; }
.slide-content { position: relative; width: 100%; height: 100%; }
.slide-img { width: 100%; height: 100%; object-fit: cover; cursor: pointer; }
.comment-item { display: flex; align-items: center; gap: 10px; margin-top: 10px; }
.delete-comment-btn { margin-left: auto; background: transparent; border: none; color: #ff4b5c; cursor: pointer; font-size: 16px; }
.delete-comment-btn:hover { color: #ff0000; }
.caption { position: absolute; bottom: 30px; left: 20px; color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.6); }
.actions { position: absolute; right: 20px; bottom: 100px; display: flex; flex-direction: column; gap: 15px; color: white; font-size: 24px; }
.fa-heart.fa-solid { color: #ff4b5c; animation: pop 0.3s ease; }
.fa-bookmark.fa-solid { color: #ffd700; }
.comment-overlay { position: absolute; right: 120px; bottom: 60px; width: 60%; height: 80%; background: rgba(0,0,0,0.9); color: white; border-radius: 12px; padding: 20px; overflow-y: auto; }
.avatar { width: 35px; height: 35px; border-radius: 50%; }
@keyframes pop { 0% { transform: scale(1); } 50% { transform: scale(1.6); } 100% { transform: scale(1); } }
</style>
