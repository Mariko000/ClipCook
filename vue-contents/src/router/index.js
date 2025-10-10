import { createRouter, createWebHistory } from 'vue-router'
import RecipeInput from '../components/RecipeInput.vue'
import '@fortawesome/fontawesome-free/css/all.min.css'


// レシピを保存
import RecipeForm from '../components/RecipeForm.vue'
//投稿
import Timeline from '../components/Timeline.vue'

// ブックマークリスト
import BookmarkList from '../components/BookmarkList.vue'

// レシピ詳細コンポーネント
import RecipeDetail from '../components/RecipeDetail.vue' 
// マイアルバム
import UserAlbum from '../components/Album.vue'

const routes = [
  {
    path: '/',
    name: 'RecipeCustomizer',
    component: RecipeInput
  },
  // 子コンポーネントはルーティング不要

  {
    path: '/add-recipe',
    name: 'RecipeForm',
    component: RecipeForm
  },
  {
    path: '/timeline',
    name: 'Timeline',
    component: Timeline
  },
  // ブックマーク一覧のパス
  {
    path: '/bookmarks',
    name: 'BookmarkList',
    component: BookmarkList
  },
   // レシピ詳細ルート。/recipe/1 や /recipe/2 などに対応
   {
    path: '/recipe/:id',
    name: 'RecipeDetail',
    component: RecipeDetail,
    // IDをuseRoute()で取得
  },
  {
    path: "/my-album",
    name: "UserAlbum",
    component: UserAlbum,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
