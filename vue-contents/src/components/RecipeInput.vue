 <!-- RecipeInput.vue/材料の入力フォーム -->
<!-- ここで IngredientTable、MultiplierSlider、ResultView を子として呼ぶ -->
 <!--OCR/テキストアップロード機能は後で追加するかも -->

 <template>
  <div class="recipe-tool">
    <h2>PortionCustomizer</h2>

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

    <!-- タブの中身 -->
    <div v-if="activeTab === 'scaling'">
      <ScalingTool />
    </div>

    <div v-if="activeTab === 'conversion'">
      <ConversionTool />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ScalingTool from './ScalingTool.vue'
import ConversionTool from './ConversionTool.vue'

const activeTab = ref('scaling') // デフォルトはスケーリング
</script>

<style scoped>
.tabs {
  display: flex;
  margin-bottom: 1rem;
}
.tabs button {
  flex: 1;
  padding: 0.5rem;
  border: none;
  background: #eee;
  cursor: pointer;
}
.tabs button.active {
  background: #ccc;
  font-weight: bold;
}
</style>
