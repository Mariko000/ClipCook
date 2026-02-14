<template>
  <div class="result-wrapper">
    <div class="result-card" aria-live="polite">
      <div class="result-header">
        <h3 class="title">計算結果</h3>

        <div class="actions">
          <button class="copy-btn" @click="copyResults" :disabled="!hasAny">
            コピー
          </button>
          <button class="toggle-btn" @click="toggleExpanded" :disabled="!hasAny">
            {{ expanded ? '閉じる' : 'もっと見る' }}
          </button>
        </div>
      </div>

      <transition name="fade">
        <div>
          <div v-if="expanded" class="result-body">
            <ul>
              <li v-for="(ing, idx) in ingredients" :key="idx" class="result-item">
                <span class="name">{{ ing.name || '---' }}</span>
                <span class="sep">：</span>
                <span class="value"><strong>{{ ing.quantity }}</strong> {{ ing.unit }}</span>
              </li>
            </ul>
          </div>

          <div v-else class="result-preview">
            <ul>
              <li v-for="(ing, idx) in previewIngredients" :key="idx" class="result-item">
                <span class="name">{{ ing.name || '---' }}</span>
                <span class="sep">：</span>
                <span class="value"><strong>{{ ing.quantity }}</strong> {{ ing.unit }}</span>
              </li>
            </ul>

            <div v-if="!hasAny" class="empty-note">まだ計算結果がありません</div>
          </div>
        </div>
      </transition>

      <div v-if="copyStatus" class="copy-toast">{{ copyStatus }}</div>

    </div>
  </div>
</template>

<script setup>
import { defineProps, ref, computed } from 'vue'

const props = defineProps({
  ingredients: {
    type: Array,
    required: true
  }
})

const expanded = ref(false)
const copyStatus = ref('')

const toggleExpanded = () => {
  expanded.value = !expanded.value
}

const previewIngredients = computed(() => props.ingredients.slice(0, 3))
const hasAny = computed(() => Array.isArray(props.ingredients) && props.ingredients.length > 0)

const copyResults = async () => {
  if (!hasAny.value) return

  const text = props.ingredients
    .map(ing => `${ing.name || '---'}：${ing.quantity} ${ing.unit}`)
    .join('\n')

  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
    } else {
      const ta = document.createElement('textarea')
      ta.value = text
      ta.setAttribute('readonly', '')
      ta.style.position = 'absolute'
      ta.style.left = '-9999px'
      document.body.appendChild(ta)
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
    }
    copyStatus.value = '計算結果をコピーしました'
  } catch {
    copyStatus.value = 'コピーに失敗しました'
  }

  setTimeout(() => (copyStatus.value = ''), 2000)
}
</script>

<style scoped>
/* ===== レイアウト全体 ===== */
.result-wrapper {
  display: flex;
  justify-content: center; /* 💡中央寄せ */
  margin: 0 auto;
  width: 100%;
}

/* ===== カード ===== */
.result-card {
  width: 100%;
  max-width: 540px;
  background: #fff;
  border-radius: 12px;
  padding: 0.8rem 1rem;
  margin-top: 0.8rem;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
  color: #333;
  font-family: 'Comic Neue', sans-serif;
  box-sizing: border-box;
}

/* ===== ヘッダ ===== */
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 0.4rem;
}

.title {
  font-size: 1rem;
  margin: 0;
  padding-bottom: 2px;
  border-bottom: 2px solid #FFD966;
  color: #333;
}

/* ===== アクションボタン ===== */
.actions {
  display: flex;
  gap: 8px;
}

.copy-btn,
.toggle-btn {
  background: #4E8098;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 6px 8px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.15s ease, transform 0.06s ease;
}

.copy-btn[disabled],
.toggle-btn[disabled] {
  opacity: 0.5;
  cursor: default;
}

.copy-btn:hover:not([disabled]),
.toggle-btn:hover:not([disabled]) {
  background: #FF8C61;
  transform: translateY(-1px);
}

/* ===== リスト部分 ===== */
.result-preview ul,
.result-body ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.result-item {
  display: flex;
  gap: 6px;
  align-items: baseline;
  padding: 4px 0;
  font-size: 0.92rem;
  border-bottom: 1px dashed #E0E0E0;
}

.result-item:last-child {
  border-bottom: none;
}

.name {
  color: #4E8098;
  min-width: 120px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.value {
  color: #333;
}

.empty-note {
  color: #888;
  font-size: 0.9rem;
  padding: 6px 0;
  text-align: center;
}

/* ===== コピー完了トースト ===== */
.copy-toast {
  margin-top: 8px;
  padding: 6px 8px;
  font-size: 0.85rem;
  color: #fff;
  background: rgba(78,128,152,0.95);
  border-radius: 8px;
  width: fit-content;
}

/* ===== フェード ===== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease, transform 0.18s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* ===== スマホ対応 ===== */
@media (max-width: 600px) {
  .result-card {
    max-width: 95%;
    padding: 0.7rem;
  }
  .name {
    min-width: 100px;
  }
}
</style>
