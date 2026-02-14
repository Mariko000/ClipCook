 <!-- RecipeInput.vue/材料の入力フォーム -->
<!-- ここで IngredientTable、MultiplierSlider、ResultView を子として呼ぶ -->
 <!--OCR/テキストアップロード機能は後で追加するかも -->
 <template>
  <div class="recipe-tool">
    <h2>Quantify</h2>

    <!-- ℹ️アイコン（画面左上固定） -->
    <div class="info-container">
      <button class="info-btn" @click.stop="togglePopover" title="主な単位換算表">
        ℹ️
      </button>

      <!-- ポップオーバ（中央寄り・広く表示） -->
      <div v-if="showPopover" class="popover" ref="popover">
        <ConversionReference />
      </div>
    </div>

    <!-- タブ切り替え -->
    <div class="tabs">
      <button 
        :class="{ active: activeTab === 'scaling' }" 
        @click="activeTab = 'scaling'"
      >
        分量スケーリング
      </button>
      <button 
        :class="{ active: activeTab === 'conversion' }" 
        @click="activeTab = 'conversion'"
      >
        単位変換
      </button>
    </div>

    <!-- タブ内容 -->
    <div v-if="activeTab === 'scaling'">
      <ScalingTool />
    </div>
    <div v-if="activeTab === 'conversion'">
      <ConversionTool />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import ScalingTool from './ScalingTool.vue'
import ConversionTool from './ConversionTool.vue'
import ConversionReference from './ConversionReference.vue'

const activeTab = ref('scaling')
const showPopover = ref(false)
const popover = ref(null)

function togglePopover() {
  showPopover.value = !showPopover.value
}

function handleClickOutside(event) {
  if (popover.value && !popover.value.contains(event.target)) {
    showPopover.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})
onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style>
.recipe-tool {
  padding: 3rem;
  position: relative;
  box-sizing: border-box;
}

/* ℹ️ アイコンを画面左上に固定 */
.info-container {
  position: fixed;
  top: 7rem; 
  right: 5rem;
  z-index: 300;
}
.info-btn {
  font-size: 1.4rem;
  background: #f5f7fa;
  border: 1px solid #ccc;
  border-radius: 50%;
  width: 2.4rem;
  height: 2.4rem;
  color: #4E8098;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  transition: all 0.2s;
}
.info-btn:hover {
  transform: scale(1.15);
  color: #FF8C61;
}

/* ポップオーバ：画面中央寄りに大きく展開 */
.popover {
  position: fixed;
  top: 7rem;
  left: 50%;
  transform: translateX(-50%);
  width: 75%; /* ←広めに変更 */
  max-width: 90vw;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
  padding: 1.6rem 2rem;
  z-index: 400;
  max-height: 80vh;
  overflow-y: auto;
  animation: fadeIn 0.2s ease-in-out;
}

/* 開閉アニメーション */
@keyframes fadeIn {
  from { opacity: 0; transform: translate(-50%, -10px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}

/* タブ */
.tabs {
  display: flex;
  margin-top: 1rem;
  margin-bottom: 1rem;
}
.tabs button {
  flex: 1;
  padding: 0.6rem;
  border: none;
  background: #eee;
  cursor: pointer;
  transition: 0.3s;
}
.tabs button.active {
  background: #ccc;
  font-weight: bold;
}
</style>
