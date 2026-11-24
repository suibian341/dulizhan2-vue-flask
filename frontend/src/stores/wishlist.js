import { defineStore } from 'pinia'

function currentOwnerKey() {
  try {
    const user = JSON.parse(localStorage.getItem('misicheng-user') || 'null')
    return user?.id || user?.email ? `user:${user.id || user.email}` : 'guest'
  } catch {
    return 'guest'
  }
}

function storageKey(ownerKey = currentOwnerKey()) {
  return `misicheng-wishlist-items:${ownerKey}`
}

function readItems(ownerKey = currentOwnerKey()) {
  try {
    return JSON.parse(localStorage.getItem(storageKey(ownerKey)) || '[]')
  } catch {
    return []
  }
}

function productSnapshot(product) {
  return {
    id: product.id,
    slug: product.slug,
    sku: product.sku,
    name: product.name,
    image: product.image,
    hoverImage: product.hoverImage,
    images: product.images || [],
    price: product.price,
    compareAtPrice: product.compareAtPrice,
    isNew: product.isNew,
    isFeatured: product.isFeatured,
    rating: product.rating,
    reviewCount: product.reviewCount,
    _count: product._count,
    variants: product.variants || [],
    category: product.category || null
  }
}

export const useWishlistStore = defineStore('wishlist', {
  state: () => ({
    ownerKey: currentOwnerKey(),
    items: readItems()
  }),
  getters: {
    count: state => state.items.length
  },
  actions: {
    syncAccount() {
      const nextOwnerKey = currentOwnerKey()
      if (nextOwnerKey === this.ownerKey) return
      this.ownerKey = nextOwnerKey
      this.items = readItems(nextOwnerKey)
    },
    persist() {
      localStorage.setItem(storageKey(this.ownerKey), JSON.stringify(this.items))
    },
    isSaved(productId) {
      return this.items.some(item => item.id === productId)
    },
    add(product) {
      this.syncAccount()
      if (!product?.id || this.items.some(item => item.id === product.id)) return
      this.items = [productSnapshot(product), ...this.items]
      this.persist()
    },
    remove(productId) {
      this.syncAccount()
      this.items = this.items.filter(item => item.id !== productId)
      this.persist()
    },
    toggle(product) {
      if (!product?.id) return
      if (this.isSaved(product.id)) this.remove(product.id)
      else this.add(product)
    },
    clear() {
      this.syncAccount()
      this.items = []
      this.persist()
    }
  }
})
