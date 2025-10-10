<!--スケーリング専用に切り出し-->
<template>
    <div class="scaling-tool">
      <ingredient-table
        :ingredients="ingredients"
        @update-ingredients="updateIngredients"
      />
      <result-view :ingredients="ingredients" />
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import IngredientTable from './IngredientTable.vue'
  import ResultView from './ResultView.vue'
  
  
const ingredients = ref([
  { name: '', quantity: 0, unit: '' },
  { name: '', quantity: 0, unit: '' },
  { name: '', quantity: 0, unit: '' },
  { name: '', quantity: 0, unit: '' },
  { name: '', quantity: 0, unit: '' },
  { name: '', quantity: 0, unit: '' },
])

const newIngredientName = ref('')
const newIngredientQuantity = ref(0)
const newIngredientUnit = ref('')

function addIngredient() {
  if (!newIngredientName.value || !newIngredientQuantity.value) return
  ingredients.value.push({
    name: newIngredientName.value,
    quantity: newIngredientQuantity.value,
    unit: newIngredientUnit.value || ''
  })
  newIngredientName.value = ''
  newIngredientQuantity.value = 0
  newIngredientUnit.value = ''
}

// IngredientTable.vue から ingredients の更新を受け取る
function updateIngredients(updatedIngredients) {
  ingredients.value = updatedIngredients
}
  </script>
  