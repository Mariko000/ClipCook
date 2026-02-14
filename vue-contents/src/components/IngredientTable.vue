<template>
  <div class="ingredient-table-header">
    <button class="collapse-btn" @click="collapsed = !collapsed">
      {{ collapsed ? '表示する' : '隠す' }}
    </button>
  </div>

  <div v-show="!collapsed" class="table-wrapper">
    <div class="ingredient-table">
      <h3>材料入力画面</h3>

      <!-- ① 倍率スケーリング（プリセット/カスタム） -->
      <div class="button-group">
        <button class="set-base" @click="setAsBaseRecipe">このレシピでセット</button>
        <label>
          プリセット・カスタム入力で、全材料の分量を一括変更:
          <select v-model="selectedOption">
            <option disabled value="">倍率を選択</option>
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
        />


        <button class="sub" @click="applyScaleFactor">倍率を適用</button>
      </div>

      <!-- 基準材料スケーリング -->
      <div class="button-group">
        <label>基準にする材料番号：
          <select v-model.number="baseIndex">
            <option v-for="(ing, idx) in localIngredients" :key="idx" :value="idx">
              {{ idx + 1 }}: {{ ing.name || '---' }}
            </option>
          </select>
        </label>
        <button @click="applyScaling">スケール適用</button>
      </div>
      <small class="description">
        指定した行の材料の量を変えると、他の材料も比率に合わせて自動調整されます。
      </small>

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

      <div class="button-group">
        <button @click="addIngredient">行を追加</button>
        <button class="sub" @click="clearAll">すべてクリア</button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { defineProps, defineEmits } from "vue";

const props = defineProps({
  ingredients: Array,
});
const emit = defineEmits(["update-ingredients"]);
const collapsed = ref(false);

const localIngredients = ref(
  props.ingredients.map(i => ({
    name: i.name || "",
    quantity: i.quantity ?? null,
    unit: i.unit || "",
  }))
);

const originalQuantities = ref(
  props.ingredients.map(i => (i.quantity > 0 ? i.quantity : null))
);

const baseIndex = ref(0);
const selectedOption = ref(2);
const customScaleFactor = ref(1);

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

function handleInput(idx, val) {
  const num = val === "" ? null : Number(val);
  localIngredients.value[idx].quantity = num;
  if ((originalQuantities.value[idx] === null || originalQuantities.value[idx] === undefined) && num !== null && num > 0) {
    originalQuantities.value[idx] = num;
  }
  emitCurrent();
}

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

function emitCurrent() {
  emit("update-ingredients", localIngredients.value.map(i => ({ ...i, quantity: i.quantity ?? 0 })));
}

function applyScaleFactor() {
  let factor = selectedOption.value === "custom" ? parseFloat(customScaleFactor.value) : parseFloat(selectedOption.value);
  if (!factor || factor <= 0) return;
  localIngredients.value.forEach((ing, idx) => {
    const orig = originalQuantities.value[idx];
    if (orig != null) ing.quantity = Math.round(orig * factor * 100) / 100;
  });
  emitCurrent();
}

function setAsBaseRecipe() {
  localIngredients.value.forEach((ing, idx) => {
    originalQuantities.value[idx] = ing.quantity ?? 0;
  });
  emitCurrent();
}

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
select option {
  color: #888; /* 少し濃いめグレー */
}

.ingredient-table {
  padding: 1.5rem;
  max-width: 900px;
  margin: 0 auto;
  font-family: 'Comic Neue', sans-serif;
  color: #333;
}
.ingredient-table h3 {
  color: #333;
  font-size: 1.4rem;
  margin-bottom: 1rem;
  border-bottom: 2px solid #FFD966;
  display: inline-block;
  padding-bottom: 4px;
}
label {
  font-weight: 600;
  margin-right: 8px;
  color: #4E8098;
}
select, input[type="number"], input[type="text"] {
  background: #fff;
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}
select:focus, input:focus {
  outline: none;
  border-color: #FF8C61;
  box-shadow: 0 0 0 2px rgba(255,140,97,0.2);
}
table {
  width: 100%;
  border-collapse: separate; /* separateで丸角を生かす */
  border-spacing: 0;
  margin-top: 1rem;
  background: #fefefe;
  border-radius: 10px;
  overflow: hidden;
  font-family: 'Comic Neue', sans-serif;
}
th {
  background-color: #ffe9b3; /* 柔らかい黄色 */
  color: #333;
  text-align: left;
  padding: 12px 10px;
  font-weight: 600;
  font-size: 0.95rem;
  border-bottom: 1px solid #e0e0e0;
}
td {
  padding: 10px;
  border-bottom: 1px solid #e0e0e0;
}
tr:hover {
  background-color: #FFF5E6;
}

tr:last-child td {
  border-bottom: none;
}

tr:nth-child(even) {
  background-color: #fffaf4; /* 柔らかいオフホワイトで行差し色 */
}

tr:hover {
  background-color: #fff4e6; /* 優しいホバー色 */
}

input[type="text"], input[type="number"] {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 6px 8px;
  background-color: #fff;
  transition: border-color 0.2s;
}

input[type="text"]:focus,
input[type="number"]:focus {
  border-color: #ffb37c; /* 柔らかいオレンジ */
  outline: none;
}
button {
  background-color: #FF8C61;
  border: none;
  color: white;
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.1s ease;
}
button:hover {
  background-color: #ff7a4a;
  transform: translateY(-1px);
}
button:active {
  transform: translateY(0);
}
button.sub {
  background-color: #4E8098;
}
button.sub:hover {
  background-color: #417084;
}
button.set-base {
  background-color: #ff7a4a;
}
button.set-base:hover {
  background-color: #ff7a4a;
  transform: none;
}
.button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 8px;
}
.description {
  display: block;
  font-size: 0.85rem;
  color: #666;
  margin-top: 4px;
}
.ingredient-table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.collapse-btn {
  margin-left: auto;
  background-color: #4E8098;
  color: #fff;
  padding: 6px 12px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s ease;
}
.collapse-btn:hover {
  background-color: #417084;
}
@media (max-width: 600px) {
  .ingredient-table { padding: 1rem; font-size: 0.85rem; }
  .table-wrapper { overflow-x: auto; }
  table { min-width: 500px; }
  .ingredient-table > div { display: flex; flex-direction: column; gap: 8px; }
  select, input[type="number"], input[type="text"], button { width: 100%; box-sizing: border-box; }
  .collapse-btn { width: auto; align-self: flex-end; margin-left: 0; }
}
@media (min-width: 601px) and (max-width: 900px) {
  .ingredient-table { padding: 1.2rem; font-size: 0.9rem; }
  .ingredient-table > div { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
  select, input[type="number"], input[type="text"] { flex: 1 1 120px; }
  button { flex: 0 0 auto; }
  table { font-size: 0.9rem; }
}
@media (min-width: 901px) {
  .ingredient-table { padding: 1.5rem; font-size: 0.95rem; }
  .ingredient-table > div { display: flex; flex-wrap: nowrap; align-items: center; gap: 12px; }
  select, input[type="number"], input[type="text"] { width: auto; }
  table { font-size: 0.95rem; }
}
</style>
