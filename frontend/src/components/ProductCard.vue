<template>
  <article
    ref="cardRef"
    class="group self-start overflow-hidden rounded-xl border border-gray-100 bg-white transition-all hover:-translate-y-1 hover:shadow-lg hover:shadow-sky-500/10"
    :class="[
      viewMode === 'list' ? 'list-card duration-300' : 'duration-[400ms]',
      visible ? 'translate-y-0 opacity-100' : viewMode === 'list' ? 'translate-y-2.5 opacity-0' : 'translate-y-5 opacity-0'
    ]"
  >
    <RouterLink
      v-if="viewMode !== 'list'"
      :to="localized(`/product/${product.slug}`)"
      class="group/card block"
      @mouseenter="hovered = true"
      @mouseleave="hovered = false"
    >
      <div class="relative overflow-hidden rounded-xl bg-gray-100">
        <img
          :src="image"
          :alt="product.name"
          class="block h-auto w-full object-contain transition-opacity duration-500"
          :class="hovered ? 'opacity-95' : 'opacity-100'"
          loading="lazy"
          decoding="async"
        />
        <img
          v-if="hoverImage"
          :src="hoverImage"
          :alt="product.name"
          class="absolute inset-0 h-full w-full object-contain transition-opacity duration-500"
          :class="hovered ? 'opacity-100' : 'opacity-0'"
          loading="lazy"
          decoding="async"
        />

        <div class="absolute left-3 top-3 flex flex-col gap-1.5">
          <span v-if="product.isNew" class="gradient-bg rounded-md px-2 py-1 text-xs font-semibold text-white">{{ t.newArrival }}</span>
          <span v-if="isSale && discount > 0" class="rounded-md bg-red-500 px-2 py-1 text-xs font-semibold text-white">-{{ discount }}%</span>
          <span v-if="product.isFeatured && !product.isNew" class="rounded-md bg-amber-500 px-2 py-1 text-xs font-semibold text-white">{{ t.featured }}</span>
        </div>

        <button
          class="absolute right-3 top-3 flex h-9 w-9 items-center justify-center rounded-full bg-white/80 backdrop-blur-sm transition-all hover:scale-110 hover:bg-white"
          @click.prevent.stop="toggleWishlist"
          aria-label="Wishlist"
        >
          <Heart class="h-4 w-4" :class="wishlisted ? 'fill-red-500 text-red-500' : 'text-gray-600'" />
        </button>

      </div>

      <div class="flex h-[104px] flex-col justify-between bg-white px-3 py-3 sm:h-[108px]">
        <h3 class="product-card-title whitespace-normal break-words font-medium leading-snug text-gray-900 group-hover/card:text-gray-700" :class="productNameTextClass">
          {{ product.name }}
        </h3>
        <div class="flex min-h-[42px] flex-col items-start justify-end gap-0.5">
          <span class="text-base font-semibold leading-tight text-gray-900">{{ displayPrice }}</span>
          <span v-if="displayComparePrice" class="text-sm leading-tight text-muted-foreground line-through">
            {{ displayComparePrice }}
          </span>
        </div>
      </div>
    </RouterLink>

    <RouterLink v-else :to="localized(`/product/${product.slug}`)" class="group flex gap-4 p-3">
      <div class="relative w-[120px] shrink-0 overflow-hidden rounded-lg bg-gray-100 sm:w-[200px]">
        <img :src="image" :alt="product.name" class="block h-auto w-full object-contain transition-opacity duration-500 group-hover:opacity-95" loading="lazy" decoding="async" />
        <div class="absolute left-1.5 top-1.5 flex flex-col gap-1">
          <span v-if="product.isNew" class="gradient-bg rounded-md px-1.5 py-0 text-[10px] text-white">{{ t.newArrival }}</span>
          <span v-if="isSale && discount > 0" class="rounded-md bg-red-500 px-1.5 py-0 text-[10px] text-white">-{{ discount }}%</span>
        </div>
      </div>
      <div class="flex min-w-0 flex-1 flex-col justify-center">
        <div>
          <h3 class="product-card-title whitespace-normal break-words font-medium leading-snug text-gray-900 transition-colors group-hover:text-sky-600" :class="productNameTextClass">
            {{ product.name }}
          </h3>
          <div class="mt-2 flex flex-col items-start gap-0.5">
            <span class="text-base font-semibold leading-tight text-gray-900">{{ displayPrice }}</span>
            <span v-if="displayComparePrice" class="text-xs leading-tight text-muted-foreground line-through">{{ displayComparePrice }}</span>
          </div>
        </div>
      </div>
    </RouterLink>
  </article>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { Heart } from 'lucide-vue-next'

import { translatedCopy } from '@/i18n'
import { useUiStore } from '@/stores/ui'
import { useWishlistStore } from '@/stores/wishlist'
import { productComparePriceRange, productPriceRange, salePercent } from '@/utils'

const props = defineProps({
  product: { type: Object, required: true },
  viewMode: { type: String, default: 'grid' }
})

const route = useRoute()
const ui = useUiStore()
const wishlist = useWishlistStore()
const cardRef = ref(null)
const hovered = ref(false)
const visible = ref(false)
let observer
const locale = computed(() => route.params.locale || 'en')
const t = computed(() => translatedCopy(locale.value, copy, source => ({
  newArrival: source.product?.newArrival,
  featured: source.product?.featured
})))
const image = computed(() => props.product.imageThumb || props.product.images?.[0]?.thumbnailUrl || props.product.image || props.product.images?.[0]?.url || '/images/products/product-1.png')
const hoverImage = computed(() => props.product.hoverImageThumb || props.product.images?.[1]?.thumbnailUrl || props.product.hoverImage || props.product.images?.[1]?.url)
const discount = computed(() => salePercent(props.product))
const displayPrice = computed(() => productPriceRange(props.product, ui.currency, { negotiableText: t.value.negotiable }))
const displayComparePrice = computed(() => productComparePriceRange(props.product, ui.currency))
const isSale = computed(() => !!displayComparePrice.value)
const productNameTextClass = computed(() => fitTextClass(props.product.name))
const wishlisted = computed(() => wishlist.isSaved(props.product.id))

function fitTextClass(value) {
  const length = Array.from(String(value || '')).length
  if (length >= 48) return 'text-sm sm:text-[11px]'
  if (length >= 34) return 'text-sm sm:text-xs'
  if (length >= 24) return 'text-sm sm:text-[13px]'
  return 'text-sm'
}

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

function toggleWishlist() {
  wishlist.toggle(props.product)
}

onMounted(() => {
  if (!cardRef.value || !('IntersectionObserver' in window)) {
    visible.value = true
    return
  }
  observer = new IntersectionObserver(([entry]) => {
    if (!entry.isIntersecting) return
    visible.value = true
    observer?.disconnect()
  }, { threshold: 0.1 })
  observer.observe(cardRef.value)
})

onUnmounted(() => {
  observer?.disconnect()
})

const copy = {
  en: {
    newArrival: 'New Arrival',
    featured: 'Featured',
    negotiable: 'Negotiable'
  },
  zh: {
    newArrival: '新品',
    featured: '精选',
    negotiable: '面议'
  }
}
</script>

<style scoped>
.product-card-title {
  display: -webkit-box;
  min-height: 2.35em;
  overflow: hidden;
  text-overflow: ellipsis;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}
</style>
