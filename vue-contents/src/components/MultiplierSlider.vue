 <!-- 分量倍率を設定するスライダー＋数値入力。 -->
 <template>
  <div>
    <h3>倍率スライダー</h3>
    <div v-for="(item, index) in ingredients" :key="index" style="margin-bottom: 8px;">
      <label>{{ item.name }} の倍率: </label>
      <input
        type="range"
        min="0.1"
        max="5"
        step="0.1"
        :value="1"
        @input="onSlide(index, $event.target.value)"
      />
      <span>{{ (item.quantity * $event.target.value / item.quantity).toFixed(2) }}倍</span>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  ingredients: Array
})
const emit = defineEmits(['scale'])

function onSlide(index, value) {
  const baseQuantity = props.ingredients[index].quantity
  const newQuantity = baseQuantity * value
  emit('scale', { baseIndex: index, newQuantity })
}
</script>
