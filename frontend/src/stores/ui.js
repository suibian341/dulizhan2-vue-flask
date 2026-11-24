import { defineStore } from 'pinia'

export const useUiStore = defineStore('ui', {
  state: () => ({
    locale: localStorage.getItem('misicheng-locale') || 'en',
    currency: localStorage.getItem('misicheng-currency') || 'USD',
    searchOpen: false
  }),
  actions: {
    setLocale(locale) {
      this.locale = locale
      localStorage.setItem('misicheng-locale', locale)
    },
    setCurrency(currency) {
      this.currency = currency
      localStorage.setItem('misicheng-currency', currency)
    }
  }
})
