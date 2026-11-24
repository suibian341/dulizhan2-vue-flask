<template>
  <div class="mx-auto max-w-7xl px-4 pt-24 py-12 lg:px-8">
    <nav class="mb-8 flex items-center gap-2 text-sm text-muted-foreground">
      <RouterLink :to="localized('/')" class="hover:text-foreground transition-colors">{{ t.home }}</RouterLink>
      <ChevronRight class="h-3.5 w-3.5" />
      <RouterLink :to="localized('/account')" class="hover:text-foreground transition-colors">{{ t.account }}</RouterLink>
      <ChevronRight class="h-3.5 w-3.5" />
      <span class="font-medium text-foreground">{{ t.wishlist }}</span>
    </nav>

    <div class="mb-8 text-center">
      <h1 class="text-3xl font-bold">{{ t.wishlist }}</h1>
      <p class="mt-2 text-muted-foreground">{{ t.subtitle }}</p>
    </div>

    <div v-if="!user" class="flex flex-col items-center justify-center py-20 text-center">
      <Heart class="mb-4 h-14 w-14 text-muted-foreground/40" />
      <h2 class="text-xl font-semibold">{{ t.signInRequired }}</h2>
      <p class="mt-2 text-muted-foreground">{{ t.signInDesc }}</p>
      <RouterLink :to="localized('/login?redirect=/account/wishlist')" class="btn gradient-bg mt-6 h-10 rounded-md px-6 text-white">{{ t.signIn }}</RouterLink>
    </div>

    <div v-else-if="loading" class="grid grid-cols-2 gap-4 md:grid-cols-4 lg:gap-6">
      <div v-for="i in 4" :key="i" class="space-y-3">
        <div class="shimmer aspect-[3/4] rounded-xl"></div>
        <div class="shimmer h-4 w-3/4 rounded-md"></div>
        <div class="shimmer h-4 w-1/2 rounded-md"></div>
      </div>
    </div>

    <div v-else-if="!products.length" class="flex flex-col items-center justify-center py-20 text-center">
      <Heart class="mb-4 h-14 w-14 text-muted-foreground/40" />
      <h2 class="text-xl font-semibold">{{ t.emptyTitle }}</h2>
      <p class="mt-2 text-muted-foreground">{{ t.emptyDesc }}</p>
      <RouterLink :to="localized('/shop')" class="btn gradient-bg mt-6 h-10 rounded-md px-6 text-white">{{ t.browse }}</RouterLink>
    </div>

    <div v-else class="grid grid-cols-2 gap-4 md:grid-cols-4 lg:gap-6">
      <ProductCard v-for="product in products" :key="product.id" :product="product" />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { ChevronRight, Heart } from 'lucide-vue-next'

import ProductCard from '@/components/ProductCard.vue'
import { useWishlistStore } from '@/stores/wishlist'

const route = useRoute()
const wishlist = useWishlistStore()
const loading = ref(true)
const user = ref(readUser())
const products = computed(() => user.value ? wishlist.items : [])
const locale = computed(() => route.params.locale || 'en')
const t = computed(() => copy[locale.value] || copy.en)

function readUser() {
  try {
    return JSON.parse(localStorage.getItem('misicheng-user') || 'null')
  } catch {
    return null
  }
}

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

onMounted(() => {
  user.value = readUser()
  wishlist.syncAccount()
  loading.value = false
})

const copy = {
  en: {
    home: 'Home',
    account: 'My Account',
    wishlist: 'Wishlist',
    subtitle: 'Products saved for quick comparison and inquiry.',
    signInRequired: 'Sign in required',
    signInDesc: 'Log in to view products saved to your account.',
    signIn: 'Log In',
    emptyTitle: 'Your wishlist is empty',
    emptyDesc: 'Browse products and save items you want to compare.',
    browse: 'Browse Products'
  },
  zh: {
    home: '首页',
    account: '我的账户',
    wishlist: '收藏夹',
    subtitle: '保存商品，便于快速对比和询盘。',
    emptyTitle: '收藏夹为空',
    emptyDesc: '浏览产品并保存想要对比的商品。',
    browse: '浏览产品',
    signInRequired: '需要登录',
    signInDesc: '登录后查看当前账号收藏的商品。',
    signIn: '登录'
  }
}
</script>
