<template>
  <div class="ingredient-table">
    <h3>材料テーブル</h3>

    <!-- ① 倍率スケーリング（プリセット/カスタム） -->
    <div style="margin-top: 12px;">
      <label>
        倍率を選択:
        <select v-model="selectedOption">
          <option :value="0.5">0.5倍（半量）</option>
          <option :value="1">1倍（元の分量）</option>
          <option :value="2">2倍</option>
          <option :value="3">3倍</option>
          <option :value="4">4倍</option>
          <option value="custom">カスタム入力</option>
        </select>
      </label>

      <input
        v-if="selectedOption === 'custom'"
        type="number"
        step="0.1"
        v-model.number="customScaleFactor"
        placeholder="倍率を入力（例: 1.25）"
        style="margin-left:8px; width:120px;"
      />

      <button @click="applyScaleFactor">倍率を適用</button>
      <button @click="setAsBaseRecipe">このレシピでセット</button>
    </div>

    <!-- 材料テーブル -->
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>材料名</th>
          <th>分量</th>
          <th>単位</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(ingredient, index) in localIngredients" :key="index">
          <td>{{ index + 1 }}</td>
          <td><input v-model="ingredient.name" placeholder="材料名" /></td>
          <td>
            <input
              type="number"
              :value="ingredient.quantity ?? ''"
              @input="handleInput(index, $event.target.value)"
              placeholder="分量"
              min="0"
            />
          </td>
          <td><input v-model="ingredient.unit" placeholder="単位" /></td>
          <td><button @click="removeIngredient(index)">削除</button></td>
        </tr>
      </tbody>
    </table>

    <div style="margin-top: 8px;">
      <button @click="addIngredient">行を追加</button>
      <button @click="clearAll">すべてクリア</button>
    </div>

    <!-- 基準材料スケーリング -->
    <div style="margin-top: 8px;">
      <label>基準にする材料番号：
        <select v-model.number="baseIndex">
          <option v-for="(ing, idx) in localIngredients" :key="idx" :value="idx">
            {{ idx + 1 }}: {{ ing.name || '---' }}
          </option>
        </select>
      </label>
      <button @click="applyScaling">スケール適用</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { defineProps, defineEmits } from "vue";

const props = defineProps({
  ingredients: Array, // 親から渡される材料リスト
});
const emit = defineEmits(["update-ingredients"]);

const localIngredients = ref(
  props.ingredients.map(i => ({
    name: i.name || "",
    quantity: i.quantity ?? null,
    unit: i.unit || "",
  }))
);

// 🔹 元の分量を保持
const originalQuantities = ref(
  props.ingredients.map(i => (i.quantity > 0 ? i.quantity : null))
);

// 基準材料用
const baseIndex = ref(0);

// 倍率スケーリング用
const selectedOption = ref(1);
const customScaleFactor = ref(1);

// 親から ingredients が変わったら localIngredients 更新
watch(
  () => props.ingredients,
  newVal => {
    localIngredients.value = newVal.map(i => ({
      name: i.name || "",
      quantity: i.quantity ?? null,
      unit: i.unit || "",
    }));

    if (originalQuantities.value.length < newVal.length) {
      const extra = newVal.slice(originalQuantities.value.length).map(i => i.quantity ?? null);
      originalQuantities.value.push(...extra);
    }
  },
  { deep: true }
);

// 🔹 入力ハンドラ
function handleInput(idx, val) {
  const num = val === "" ? null : Number(val);
  localIngredients.value[idx].quantity = num;

  if ((originalQuantities.value[idx] === null || originalQuantities.value[idx] === undefined) && num !== null && num > 0) {
    originalQuantities.value[idx] = num;
  }
  emitCurrent();
}

// 🔹 行追加・削除・クリア
function addIngredient() {
  localIngredients.value.push({ name: "", quantity: null, unit: "" });
  originalQuantities.value.push(null);
  emitCurrent();
}
function removeIngredient(idx) {
  localIngredients.value.splice(idx, 1);
  originalQuantities.value.splice(idx, 1);
  if (baseIndex.value >= localIngredients.value.length) baseIndex.value = Math.max(0, localIngredients.value.length - 1);
  emitCurrent();
}
function clearAll() {
  localIngredients.value.forEach((i, idx) => {
    i.name = "";
    i.quantity = null;
    i.unit = "";
    originalQuantities.value[idx] = null;
  });
  emitCurrent();
}

// 🔹 現在の ingredients を親に反映
function emitCurrent() {
  emit("update-ingredients", localIngredients.value.map(i => ({ ...i, quantity: i.quantity ?? 0 })));
}

// -----------------------------
// ① 倍率スケーリング
// -----------------------------
function applyScaleFactor() {
  let factor;
  if (selectedOption.value === "custom") {
    factor = parseFloat(customScaleFactor.value);
  } else {
    factor = parseFloat(selectedOption.value);
  }
  if (!factor || factor <= 0) return;

  localIngredients.value.forEach((ing, idx) => {
    const orig = originalQuantities.value[idx];
    if (orig != null) {
      ing.quantity = Math.round(orig * factor * 100) / 100;
    }
  });
  emitCurrent();
}

// 🔹 「このレシピでセット」ボタン
function setAsBaseRecipe() {
  localIngredients.value.forEach((ing, idx) => {
    originalQuantities.value[idx] = ing.quantity ?? 0;
  });
  emitCurrent();
}

// -----------------------------
// ② 基準材料スケーリング
// -----------------------------
function applyScaling() {
  if (!localIngredients.value.length) return;
  const baseOrig = originalQuantities.value[baseIndex.value];
  const baseCur = localIngredients.value[baseIndex.value].quantity;

  if (!baseOrig || !baseCur) {
    alert("基準材料の元の量または希望量を入力してください");
    return;
  }
  const ratio = baseCur / baseOrig;

  localIngredients.value.forEach((ing, idx) => {
    if (idx === baseIndex.value) return;
    const orig = originalQuantities.value[idx] ?? 0;
    ing.quantity = Math.round(orig * ratio * 100) / 100;
  });
  emitCurrent();
}
</script>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
}

th, td {
  border: 1px solid #ccc;
  padding: 6px 8px;
}

input {
  width: 100%;
  box-sizing: border-box;
  padding: 4px;
}

button {
  padding: 4px 8px;
  margin: 4px;
}
</style>
