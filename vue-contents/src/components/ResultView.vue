 <!-- 計算済みのリストを表示 -->
 <template>
  <div class="result-view">
    <h3>計算結果</h3>
    <ul>
      <li v-for="(ing, idx) in ingredients" :key="idx">
        {{ ing.name || '---' }}: {{ ing.quantity }} {{ ing.unit }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  ingredients: {
    type: Array,
    required: true
  }
})
</script>

<style scoped>
.result-view {
  margin-top: 16px;
}
</style>
