// src/stores/quantifyStore.js
import { defineStore } from 'pinia'

export const useQuantifyStore = defineStore('quantify', {
  state: () => ({
    convertedIngredients: []
  }),
  actions: {
    setConvertedIngredients(ingredients) {
      this.convertedIngredients = ingredients
    },
    clearConvertedIngredients() {
      this.convertedIngredients = []
    }
  }
})
