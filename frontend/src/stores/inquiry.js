import { defineStore } from 'pinia'

import { productHasNegotiablePrice } from '@/utils'

function currentOwnerKey() {
  try {
    const user = JSON.parse(localStorage.getItem('misicheng-user') || 'null')
    return user?.id || user?.email ? `user:${user.id || user.email}` : 'guest'
  } catch {
    return 'guest'
  }
}

function storageKey(ownerKey = currentOwnerKey()) {
  return `misicheng-inquiry-items:${ownerKey}`
}

function readItems(ownerKey = currentOwnerKey()) {
  try {
    return JSON.parse(localStorage.getItem(storageKey(ownerKey)) || '[]')
  } catch {
    return []
  }
}

export const useInquiryStore = defineStore('inquiry', {
  state: () => ({
    ownerKey: currentOwnerKey(),
    items: readItems(),
    drawerOpen: false
  }),
  getters: {
    count: state => state.items.reduce((sum, item) => sum + Number(item.quantity || 0), 0),
    subtotal: state =>
      state.items.reduce((sum, item) => sum + Number(item.price || 0) * Number(item.quantity || 0), 0)
  },
  actions: {
    syncAccount() {
      const nextOwnerKey = currentOwnerKey()
      if (nextOwnerKey === this.ownerKey) return
      this.ownerKey = nextOwnerKey
      this.items = readItems(nextOwnerKey)
      this.drawerOpen = false
    },
    persist() {
      localStorage.setItem(storageKey(this.ownerKey), JSON.stringify(this.items))
    },
    addItem(product, quantity = 1) {
      this.syncAccount()
      const variant = product.variants?.[0] || {}
      const image = product.image || product.images?.[0]?.url
      const id = `${product.id}-${variant.id || 'default'}`
      const existing = this.items.find(item => item.id === id)
      if (existing) {
        existing.quantity += quantity
      } else {
        const itemPrice = Number(variant.price || product.price || 0)
        this.items.push({
          id,
          productId: product.id,
          variantId: variant.id,
          slug: product.slug,
          name: product.name,
          image,
          price: itemPrice,
          priceNegotiable: itemPrice <= 0 && Boolean(variant.priceNegotiable || variant.negotiable || productHasNegotiablePrice(product)),
          maxQuantity: variant.stock || product.stock || 999,
          options: variant.options || {},
          quantity
        })
      }
      this.persist()
      this.drawerOpen = true
    },
    updateQuantity(id, quantity) {
      this.syncAccount()
      const item = this.items.find(row => row.id === id)
      if (!item) return
      item.quantity = Math.max(1, Math.min(Number(quantity), item.maxQuantity || 999))
      this.persist()
    },
    updateNote(id, note) {
      this.syncAccount()
      const item = this.items.find(row => row.id === id)
      if (!item) return
      item.note = note
      this.persist()
    },
    removeItem(id) {
      this.syncAccount()
      this.items = this.items.filter(item => item.id !== id)
      this.persist()
    },
    clear() {
      this.syncAccount()
      this.items = []
      this.persist()
    }
  }
})
