<template>
  <div ref="pageRef" class="relative mx-auto max-w-7xl px-5 pt-24 pb-40 sm:px-6 md:pb-36 lg:px-8">
    <nav class="mb-8 flex items-center gap-2 text-sm text-muted-foreground">
      <RouterLink :to="localized('/')" class="hover:text-foreground transition-colors">{{ t.common.home }}</RouterLink>
      <ChevronRight class="h-3.5 w-3.5" />
      <span class="text-foreground font-medium">{{ t.shop.breadcrumb }}</span>
    </nav>

    <div class="flex gap-8">
      <aside class="hidden w-60 flex-shrink-0 lg:block">
        <div
          ref="sidebarRef"
          class="max-h-[calc(100vh-7rem)] overflow-y-auto rounded-2xl border border-white/40 bg-white/60 p-5 shadow-[0_8px_32px_rgba(0,0,0,0.08),0_2px_8px_rgba(0,0,0,0.04)] backdrop-blur-xl backdrop-saturate-150 cursor-default select-none"
          @mousemove="handleSidebarMouseMove"
          @mouseleave="handleSidebarMouseLeave"
          @mousedown="setSidebarPressed(true)"
          @mouseup="setSidebarPressed(false)"
          @wheel="handleSidebarWheel"
        >
          <div class="space-y-6 px-2">
            <div>
              <h3 class="mb-3 text-sm font-semibold uppercase tracking-wider">{{ t.shop.categoryFilter }}</h3>
              <div class="space-y-2">
                <label v-for="cat in categories" :key="cat.slug" class="flex cursor-pointer items-center gap-2">
                  <button
                    type="button"
                    class="flex h-4 w-4 items-center justify-center rounded-sm border border-input transition-colors"
                    :class="selectedCategories.includes(cat.slug) ? 'bg-sky-500 text-white border-sky-500' : 'bg-white'"
                    @click="toggleCategory(cat.slug)"
                  >
                    <Check v-if="selectedCategories.includes(cat.slug)" class="h-3 w-3" />
                  </button>
                  <span class="text-sm">{{ cat.name }}</span>
                </label>
              </div>
            </div>

            <div class="h-px bg-border"></div>

            <div>
              <h3 class="mb-3 text-sm font-semibold uppercase tracking-wider">{{ t.shop.priceRange }}</h3>
              <div class="flex items-center gap-2">
                <input
                  v-model="priceRange[0]"
                  type="number"
                  class="h-9 w-full rounded-lg border px-3 text-sm outline-none focus:ring-2 focus:ring-sky-500/30 focus:border-sky-400 transition-all placeholder:text-muted-foreground/40"
                  :placeholder="t.shop.priceMin"
                />
                <span class="text-muted-foreground">-</span>
                <input
                  v-model="priceRange[1]"
                  type="number"
                  class="h-9 w-full rounded-lg border px-3 text-sm outline-none focus:ring-2 focus:ring-sky-500/30 focus:border-sky-400 transition-all placeholder:text-muted-foreground/40"
                  :placeholder="t.shop.priceMax"
                />
              </div>
            </div>

            <div class="h-px bg-border"></div>

            <div>
              <h3 class="mb-3 text-sm font-semibold uppercase tracking-wider">{{ t.shop.productStatus }}</h3>
              <div class="space-y-2">
                <label class="flex cursor-pointer items-center gap-2">
                  <button
                    type="button"
                    class="flex h-4 w-4 items-center justify-center rounded-sm border border-input transition-colors"
                    :class="onSale ? 'bg-sky-500 text-white border-sky-500' : 'bg-white'"
                    @click="onSale = !onSale"
                  >
                    <Check v-if="onSale" class="h-3 w-3" />
                  </button>
                  <span class="text-sm">{{ t.shop.onSale }}</span>
                </label>
                <label class="flex cursor-pointer items-center gap-2">
                  <button
                    type="button"
                    class="flex h-4 w-4 items-center justify-center rounded-sm border border-input transition-colors"
                    :class="newOnly ? 'bg-sky-500 text-white border-sky-500' : 'bg-white'"
                    @click="newOnly = !newOnly"
                  >
                    <Check v-if="newOnly" class="h-3 w-3" />
                  </button>
                  <span class="text-sm">{{ t.shop.newArrival }}</span>
                </label>
                <label class="flex cursor-pointer items-center gap-2">
                  <button
                    type="button"
                    class="flex h-4 w-4 items-center justify-center rounded-sm border border-input transition-colors"
                    :class="inStock ? 'bg-sky-500 text-white border-sky-500' : 'bg-white'"
                    @click="inStock = !inStock"
                  >
                    <Check v-if="inStock" class="h-3 w-3" />
                  </button>
                  <span class="text-sm">{{ t.shop.inStock }}</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <div class="flex-1">
        <div class="mb-6 flex items-center justify-between gap-2 px-1 sm:px-0">
          <div class="flex items-center gap-3">
            <button
              type="button"
              class="inline-flex h-8 items-center justify-center gap-1.5 rounded-md border bg-background px-3 text-sm font-medium shadow-xs transition-all hover:bg-accent hover:text-accent-foreground lg:hidden"
              @click="mobileFiltersOpen = true"
            >
              <SlidersHorizontal class="h-4 w-4" />
              {{ t.shop.filter }}
            </button>
            <p class="text-sm text-muted-foreground">{{ t.shop.totalProducts.replace('{count}', filteredProducts.length) }}</p>
          </div>

          <div class="flex items-center gap-2">
            <select
              v-model="sortBy"
              class="h-9 w-[130px] rounded-md border bg-background px-3 text-sm shadow-xs outline-none transition-all focus:border-sky-400 focus:ring-2 focus:ring-sky-500/30 sm:w-[160px]"
            >
              <option value="recommended">{{ t.shop.sortDefault }}</option>
              <option value="newest">{{ t.shop.sortNewest }}</option>
              <option value="price-asc">{{ t.shop.sortPriceLow }}</option>
              <option value="price-desc">{{ t.shop.sortPriceHigh }}</option>
            </select>

            <div class="hidden gap-1 md:flex">
              <button
                type="button"
                class="inline-flex size-9 items-center justify-center rounded-md text-sm font-medium transition-all"
                :class="viewMode === 'grid' ? 'bg-primary text-primary-foreground hover:bg-primary/90' : 'hover:bg-accent hover:text-accent-foreground'"
                :aria-label="t.shop.gridView"
                @click="viewMode = 'grid'"
              >
                <Grid3X3 class="h-4 w-4" />
              </button>
              <button
                type="button"
                class="inline-flex size-9 items-center justify-center rounded-md text-sm font-medium transition-all"
                :class="viewMode === 'list' ? 'bg-primary text-primary-foreground hover:bg-primary/90' : 'hover:bg-accent hover:text-accent-foreground'"
                :aria-label="t.shop.listView"
                @click="viewMode = 'list'"
              >
                <List class="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        <div v-if="loading" class="grid grid-cols-2 gap-4 md:grid-cols-3 lg:gap-6">
          <div v-for="i in 15" :key="i" class="space-y-3">
            <div class="shimmer aspect-[3/4] w-full rounded-xl"></div>
            <div class="shimmer h-4 w-3/4 rounded-md"></div>
            <div class="shimmer h-4 w-1/2 rounded-md"></div>
          </div>
        </div>

        <div v-else-if="!filteredProducts.length" class="flex flex-col items-center justify-center py-20 text-center">
          <div class="mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-gray-100">
            <SlidersHorizontal class="h-8 w-8 text-gray-400" />
          </div>
          <h3 class="text-lg font-medium">{{ t.shop.noResults }}</h3>
          <p class="mt-1 text-sm text-muted-foreground">{{ t.shop.noResultsHint }}</p>
          <button
            type="button"
            class="mt-4 inline-flex h-9 items-center justify-center rounded-md border bg-background px-4 py-2 text-sm font-medium shadow-xs transition-all hover:bg-accent hover:text-accent-foreground"
            @click="clearFilters"
          >
            {{ t.shop.clearFilters }}
          </button>
        </div>

        <template v-else>
          <div :class="viewMode === 'grid' ? 'grid grid-cols-2 gap-4 md:grid-cols-3 lg:gap-6' : 'flex flex-col gap-3'">
            <ProductCard
              v-for="product in paginatedProducts"
              :key="product.id"
              :product="product"
              :view-mode="viewMode"
            />
          </div>

          <div ref="paginationTriggerRef" class="h-1"></div>

          <div
            v-if="totalPages > 1"
            class="z-40 flex justify-center px-4 pointer-events-none"
            :class="paginationDocked ? 'absolute inset-x-0 bottom-24 md:bottom-8' : 'fixed inset-x-0 bottom-24 md:bottom-8'"
          >
            <div
              ref="paginationRef"
              :class="showPagination ? 'pointer-events-auto' : 'pointer-events-none'"
              @mouseenter="handlePaginationMouseEnter"
              @mousemove="handlePaginationMouseMove"
              @mouseleave="handlePaginationMouseLeave"
            >
              <div
                ref="paginationPanelRef"
                class="pagination-pop inline-flex items-center gap-1.5 rounded-2xl border border-white/40 bg-white/60 px-4 py-2.5 shadow-[0_8px_32px_rgba(0,0,0,0.08),0_2px_8px_rgba(0,0,0,0.04)] backdrop-blur-xl backdrop-saturate-150 cursor-default select-none"
                :class="{ 'pagination-pop--visible': showPagination }"
                :aria-hidden="!showPagination"
              >
                <button
                  type="button"
                  class="flex h-9 w-9 items-center justify-center rounded-xl text-gray-600 transition-all hover:bg-sky-50/80 hover:text-sky-600 disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-gray-600"
                  :disabled="page === 1"
                  @click="handlePageChange(page - 1)"
                >
                  <ChevronLeft class="h-4 w-4" />
                </button>

                <template v-for="(num, idx) in pageNumbers" :key="`${num}-${idx}`">
                  <span v-if="num === '...'" class="px-1 text-gray-400">...</span>
                  <button
                    v-else
                    type="button"
                    class="flex h-9 w-9 items-center justify-center rounded-xl text-sm font-medium transition-all"
                    :class="page === num ? 'bg-sky-500 text-white shadow-sm' : 'text-gray-600 hover:bg-sky-50/80 hover:text-sky-600'"
                    @click="handlePageChange(num)"
                  >
                    {{ num }}
                  </button>
                </template>

                <button
                  type="button"
                  class="flex h-9 w-9 items-center justify-center rounded-xl text-gray-600 transition-all hover:bg-sky-50/80 hover:text-sky-600 disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-gray-600"
                  :disabled="page === totalPages"
                  @click="handlePageChange(page + 1)"
                >
                  <ChevronRight class="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <Transition name="filter-sheet">
      <div v-if="mobileFiltersOpen" class="fixed inset-0 z-50 lg:hidden">
        <button class="absolute inset-0 bg-black/40" type="button" aria-label="Close filters" @click="mobileFiltersOpen = false"></button>
        <aside class="absolute inset-y-0 left-0 w-80 max-w-[86vw] bg-white p-6 shadow-2xl">
          <div class="mb-6 flex items-center justify-between">
            <h2 class="text-lg font-semibold">{{ t.shop.filter }}</h2>
            <button type="button" class="rounded-md p-2 hover:bg-accent" @click="mobileFiltersOpen = false">x</button>
          </div>

          <div class="space-y-6">
            <div>
              <h3 class="mb-3 text-sm font-semibold uppercase tracking-wider">{{ t.shop.categoryFilter }}</h3>
              <div class="space-y-2">
                <label v-for="cat in categories" :key="cat.slug" class="flex cursor-pointer items-center gap-2">
                  <button
                    type="button"
                    class="flex h-4 w-4 items-center justify-center rounded-sm border border-input transition-colors"
                    :class="selectedCategories.includes(cat.slug) ? 'bg-sky-500 text-white border-sky-500' : 'bg-white'"
                    @click="toggleCategory(cat.slug)"
                  >
                    <Check v-if="selectedCategories.includes(cat.slug)" class="h-3 w-3" />
                  </button>
                  <span class="text-sm">{{ cat.name }}</span>
                </label>
              </div>
            </div>

            <div class="h-px bg-border"></div>

            <div>
              <h3 class="mb-3 text-sm font-semibold uppercase tracking-wider">{{ t.shop.priceRange }}</h3>
              <div class="flex items-center gap-2">
                <input v-model="priceRange[0]" type="number" class="h-9 w-full rounded-lg border px-3 text-sm outline-none focus:ring-2 focus:ring-sky-500/30 focus:border-sky-400 transition-all placeholder:text-muted-foreground/40" :placeholder="t.shop.priceMin" />
                <span class="text-muted-foreground">-</span>
                <input v-model="priceRange[1]" type="number" class="h-9 w-full rounded-lg border px-3 text-sm outline-none focus:ring-2 focus:ring-sky-500/30 focus:border-sky-400 transition-all placeholder:text-muted-foreground/40" :placeholder="t.shop.priceMax" />
              </div>
            </div>

            <div class="h-px bg-border"></div>

            <div>
              <h3 class="mb-3 text-sm font-semibold uppercase tracking-wider">{{ t.shop.productStatus }}</h3>
              <div class="space-y-2">
                <label class="flex cursor-pointer items-center gap-2">
                  <button type="button" class="flex h-4 w-4 items-center justify-center rounded-sm border border-input transition-colors" :class="onSale ? 'bg-sky-500 text-white border-sky-500' : 'bg-white'" @click="onSale = !onSale">
                    <Check v-if="onSale" class="h-3 w-3" />
                  </button>
                  <span class="text-sm">{{ t.shop.onSale }}</span>
                </label>
                <label class="flex cursor-pointer items-center gap-2">
                  <button type="button" class="flex h-4 w-4 items-center justify-center rounded-sm border border-input transition-colors" :class="newOnly ? 'bg-sky-500 text-white border-sky-500' : 'bg-white'" @click="newOnly = !newOnly">
                    <Check v-if="newOnly" class="h-3 w-3" />
                  </button>
                  <span class="text-sm">{{ t.shop.newArrival }}</span>
                </label>
                <label class="flex cursor-pointer items-center gap-2">
                  <button type="button" class="flex h-4 w-4 items-center justify-center rounded-sm border border-input transition-colors" :class="inStock ? 'bg-sky-500 text-white border-sky-500' : 'bg-white'" @click="inStock = !inStock">
                    <Check v-if="inStock" class="h-3 w-3" />
                  </button>
                  <span class="text-sm">{{ t.shop.inStock }}</span>
                </label>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { Check, ChevronLeft, ChevronRight, Grid3X3, List, SlidersHorizontal } from 'lucide-vue-next'
import { gsap } from 'gsap'

import { getCategories, getProducts } from '@/api'
import ProductCard from '@/components/ProductCard.vue'
import { loadLocaleMessages, translatedCopy } from '@/i18n'
import { productHasFixedPrice, productPriceBounds } from '@/utils'

const route = useRoute()
const pageRef = ref(null)
const sidebarRef = ref(null)
const paginationRef = ref(null)
const paginationPanelRef = ref(null)
const paginationTriggerRef = ref(null)
const categories = ref([])
const products = ref([])
const loading = ref(true)
const sortBy = ref('recommended')
const selectedCategories = ref([])
const priceRange = ref(['', ''])
const onSale = ref(route.query.filter === 'sale')
const newOnly = ref(route.query.filter === 'new')
const inStock = ref(false)
const viewMode = ref('grid')
const page = ref(1)
const mobileFiltersOpen = ref(false)
const pagInListZone = ref(false)
const pagHoverZone = ref(false)
const pagInteracting = ref(false)
const paginationDocked = ref(false)
const sidebarPressed = ref(false)

let paginationObserver
let resetTimer
let lastScrollY = 0
let sidebarMouseX = 0
let sidebarMouseY = 0
let sidebarFollowY = 0
let sidebarScrollY = 0

const SIDEBAR_TOP_OFFSET = 96

const locale = computed(() => route.params.locale || 'en')
const t = computed(() => translatedCopy(locale.value, copy, source => ({
  common: { home: source.common?.home },
  shop: source.shop
})))
const pageSize = computed(() => (viewMode.value === 'grid' ? 15 : 10))
const showPagination = computed(() => totalPages.value > 1 && (pagInListZone.value || pagHoverZone.value || pagInteracting.value))

function sortableNumber(value, fallback = 0) {
  const number = Number(value)
  return Number.isFinite(number) ? number : fallback
}

function productSortOrder(product) {
  return sortableNumber(product?.sortOrder, Number.MAX_SAFE_INTEGER)
}

function productTimestamp(product) {
  const timestamp = Date.parse(product?.createdAt || product?.updatedAt || '')
  return Number.isFinite(timestamp) ? timestamp : 0
}

function productStableKey(product) {
  return String(product?.id || product?.slug || '')
}

function productSortPrice(product, fallback = 0) {
  if (!productHasFixedPrice(product)) return fallback
  return productPriceBounds(product).min
}

const filteredProducts = computed(() => {
  const min = priceRange.value[0] === '' ? 0 : Number(priceRange.value[0])
  const max = priceRange.value[1] === '' ? Infinity : Number(priceRange.value[1])
  const rows = products.value.filter(product => {
    if (selectedCategories.value.length && !selectedCategories.value.includes(product.category?.slug)) return false
    if (min > 0 || max < Infinity) {
      if (!productHasFixedPrice(product)) return false
      const bounds = productPriceBounds(product)
      if (bounds.max < min || bounds.min > max) return false
    }
    if (onSale.value && !(product.compareAtPrice && product.compareAtPrice > product.price)) return false
    if (newOnly.value && !product.isNew) return false
    if (inStock.value && !(product.variants?.[0]?.stock > 0 || product.stock > 0)) return false
    return true
  })
  const sorted = [...rows]
  if (sortBy.value === 'recommended') {
    sorted.sort((a, b) => {
      const diff = productSortOrder(a) - productSortOrder(b)
      if (diff) return diff
      const createdDiff = productTimestamp(a) - productTimestamp(b)
      return createdDiff || productStableKey(a).localeCompare(productStableKey(b))
    })
  } else if (sortBy.value === 'price-asc') {
    sorted.sort((a, b) => {
      const diff = productSortPrice(a, Number.MAX_SAFE_INTEGER) - productSortPrice(b, Number.MAX_SAFE_INTEGER)
      return diff || productSortOrder(a) - productSortOrder(b) || productStableKey(a).localeCompare(productStableKey(b))
    })
  } else if (sortBy.value === 'price-desc') {
    sorted.sort((a, b) => {
      const diff = productSortPrice(b, -1) - productSortPrice(a, -1)
      return diff || productSortOrder(a) - productSortOrder(b) || productStableKey(a).localeCompare(productStableKey(b))
    })
  } else if (sortBy.value === 'newest') {
    sorted.sort((a, b) => {
      const diff = productTimestamp(b) - productTimestamp(a)
      return diff || productSortOrder(a) - productSortOrder(b) || productStableKey(a).localeCompare(productStableKey(b))
    })
  }
  return sorted
})

const totalPages = computed(() => Math.ceil(filteredProducts.value.length / pageSize.value))
const paginatedProducts = computed(() =>
  filteredProducts.value.slice((page.value - 1) * pageSize.value, page.value * pageSize.value)
)
const pageNumbers = computed(() => {
  const total = totalPages.value
  const current = page.value
  const pages = []
  if (total <= 7) {
    for (let i = 1; i <= total; i += 1) pages.push(i)
  } else {
    pages.push(1)
    if (current > 3) pages.push('...')
    const start = Math.max(2, current - 1)
    const end = Math.min(total - 1, current + 1)
    for (let i = start; i <= end; i += 1) pages.push(i)
    if (current < total - 2) pages.push('...')
    pages.push(total)
  }
  return pages
})

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

function toggleCategory(slug) {
  selectedCategories.value = selectedCategories.value.includes(slug)
    ? selectedCategories.value.filter(item => item !== slug)
    : [...selectedCategories.value, slug]
}

function clearFilters() {
  selectedCategories.value = []
  priceRange.value = ['', '']
  onSale.value = false
  newOnly.value = false
  inStock.value = false
}

function handlePageChange(nextPage) {
  const target = Math.max(1, Math.min(totalPages.value, nextPage))
  if (target === page.value) return
  page.value = target
  const top = Math.max(0, (pageRef.value?.getBoundingClientRect().top || 0) + window.scrollY - 96)
  window.scrollTo({ top, behavior: 'smooth' })
}

function updatePaginationDock() {
  const rect = pageRef.value?.getBoundingClientRect()
  paginationDocked.value = !!rect && rect.bottom <= window.innerHeight
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value))
}

function getSidebarFollowMetrics() {
  const sidebar = sidebarRef.value
  const container = sidebar?.parentElement
  if (!sidebar || !container) return null
  const containerTop = container.getBoundingClientRect().top + window.scrollY
  const maxFollowY = Math.max(0, container.offsetHeight - sidebar.offsetHeight)
  return { containerTop, maxFollowY }
}

function updateSidebarFollow(currentY = window.scrollY) {
  const metrics = getSidebarFollowMetrics()
  if (!metrics) return { followY: 0, maxFollowY: 0 }
  sidebarFollowY = clamp(currentY - metrics.containerTop + SIDEBAR_TOP_OFFSET, 0, metrics.maxFollowY)
  animateSidebar()
  return { followY: sidebarFollowY, maxFollowY: metrics.maxFollowY }
}

function initSidebarMotion() {
  if (!sidebarRef.value) return
  gsap.set(sidebarRef.value, {
    willChange: 'transform',
    transformOrigin: 'center center'
  })
  animateSidebar()
}

function animateSidebar() {
  if (!sidebarRef.value) return
  const scale = sidebarPressed.value ? 0.97 : 1
  const y = sidebarFollowY + sidebarMouseY + sidebarScrollY
  gsap.to(sidebarRef.value, { x: sidebarMouseX, y, scale, duration: 0.42, ease: 'power3.out', overwrite: 'auto' })
}

function setSidebarScrollInertia(value, hold = 60) {
  sidebarScrollY = clamp(value, -10, 10)
  animateSidebar()
  if (resetTimer) clearTimeout(resetTimer)
  resetTimer = setTimeout(() => {
    sidebarScrollY = 0
    animateSidebar()
  }, hold)
}

function setSidebarPressed(value) {
  sidebarPressed.value = value
  animateSidebar()
}

function handleSidebarMouseMove(event) {
  if (!sidebarRef.value) return
  const rect = sidebarRef.value.getBoundingClientRect()
  sidebarMouseX = clamp(((event.clientX - (rect.left + rect.width / 2)) / 300) * 4, -4, 4)
  sidebarMouseY = clamp(((event.clientY - (rect.top + rect.height / 2)) / 400) * 4, -4, 4)
  animateSidebar()
}

function handleSidebarMouseLeave() {
  sidebarMouseX = 0
  sidebarMouseY = 0
  animateSidebar()
}

function handleSidebarWheel(event) {
  const el = sidebarRef.value
  if (!el) return
  const maxScroll = el.scrollHeight - el.clientHeight
  if (maxScroll <= 0) return
  const atTop = el.scrollTop <= 1 && event.deltaY < 0
  const atBottom = el.scrollTop >= maxScroll - 1 && event.deltaY > 0
  if (atTop) setSidebarScrollInertia(-10, 80)
  else if (atBottom) setSidebarScrollInertia(10, 80)
}

function handleScroll() {
  const currentY = window.scrollY
  const delta = currentY - lastScrollY
  lastScrollY = currentY
  const { followY, maxFollowY } = updateSidebarFollow(currentY)
  if (Math.abs(delta) > 0.2) {
    let inertiaOffset = clamp(delta * 0.6, -10, 10)
    if (followY <= 0 && delta < 0) inertiaOffset = -10
    else if (maxFollowY > 0 && followY >= maxFollowY - 1 && delta > 0) inertiaOffset = 10
    setSidebarScrollInertia(inertiaOffset)
  }
  updatePaginationDock()
}

function handleWindowWheel(event) {
  const maxScroll = Math.max(0, document.documentElement.scrollHeight - window.innerHeight)
  const { followY, maxFollowY } = updateSidebarFollow()
  if ((window.scrollY <= 0 || followY <= 0) && event.deltaY < 0) setSidebarScrollInertia(-10, 80)
  else if ((window.scrollY >= maxScroll - 2 || (maxFollowY > 0 && followY >= maxFollowY - 1)) && event.deltaY > 0) setSidebarScrollInertia(10, 80)
}

function handleResize() {
  updatePaginationDock()
  updateSidebarFollow()
}

function handleMouseZone(event) {
  updatePaginationDock()
  const nearBottom = event.clientY > window.innerHeight - 140
  if (nearBottom) {
    pagHoverZone.value = true
  } else if (pagHoverZone.value) {
    pagHoverZone.value = false
  }
}

function handlePaginationMouseEnter() {
  pagInteracting.value = true
}

function handlePaginationMouseMove(event) {
  if (!paginationRef.value) return
  const rect = paginationRef.value.getBoundingClientRect()
  const x = Math.max(-5, Math.min(5, ((event.clientX - (rect.left + rect.width / 2)) / 300) * 5))
  const y = Math.max(-3, Math.min(3, ((event.clientY - (rect.top + rect.height / 2)) / 100) * 3))
  gsap.to(paginationRef.value, { x, y, duration: 0.35, ease: 'power3.out' })
}

function handlePaginationMouseLeave() {
  pagInteracting.value = false
  if (!paginationRef.value) return
  gsap.to(paginationRef.value, { x: 0, y: 0, duration: 0.35, ease: 'power3.out' })
}

async function loadShopContent(targetLocale = locale.value) {
  loading.value = true
  try {
    const [productData, categoryData] = await Promise.all([
      getProducts({ limit: 500 }, targetLocale),
      getCategories(targetLocale)
    ])
    if (targetLocale !== locale.value) return
    products.value = productData.products || []
    categories.value = categoryData || []
  } finally {
    if (targetLocale === locale.value) {
      loading.value = false
      await nextTick()
      updatePaginationDock()
      updateSidebarFollow()
    }
  }
}

watch([selectedCategories, priceRange, onSale, newOnly, inStock, sortBy, viewMode], () => {
  page.value = 1
  nextTick(() => {
    updatePaginationDock()
    updateSidebarFollow()
  })
}, { deep: true })

watch(totalPages, value => {
  if (page.value > value) page.value = Math.max(1, value)
  if (value <= 1) {
    pagInListZone.value = false
    pagHoverZone.value = false
    pagInteracting.value = false
  }
})

watch(locale, async target => {
  await loadLocaleMessages(target).catch(() => {})
  await loadShopContent(target)
})

onMounted(async () => {
  selectedCategories.value = route.query.category ? [route.query.category] : []
  await loadLocaleMessages(locale.value).catch(() => {})
  await loadShopContent(locale.value)
  if (paginationTriggerRef.value) {
    paginationObserver = new IntersectionObserver(([entry]) => {
      pagInListZone.value = entry.isIntersecting
    }, {
      root: null,
      threshold: 0,
      rootMargin: '0px 0px -12% 0px'
    })
    paginationObserver.observe(paginationTriggerRef.value)
  }
  lastScrollY = window.scrollY
  initSidebarMotion()
  updateSidebarFollow()
  window.addEventListener('mousemove', handleMouseZone, { passive: true })
  window.addEventListener('scroll', handleScroll, { passive: true })
  window.addEventListener('wheel', handleWindowWheel, { passive: true })
  window.addEventListener('resize', handleResize, { passive: true })
})

onUnmounted(() => {
  paginationObserver?.disconnect()
  window.removeEventListener('mousemove', handleMouseZone)
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('wheel', handleWindowWheel)
  window.removeEventListener('resize', handleResize)
  if (resetTimer) clearTimeout(resetTimer)
  if (sidebarRef.value) gsap.killTweensOf(sidebarRef.value)
})

const copy = {
  en: {
    common: { home: 'Home' },
    shop: {
      breadcrumb: 'All Products',
      categoryFilter: 'Categories',
      priceRange: 'Price Range',
      priceMin: 'Min',
      priceMax: 'Max',
      productStatus: 'Product Status',
      onSale: 'On Sale',
      newArrival: 'New Arrivals',
      inStock: 'In Stock',
      filter: 'Filter',
      sortDefault: 'Recommended',
      sortNewest: 'Newest',
      sortPriceLow: 'Price: Low to High',
      sortPriceHigh: 'Price: High to Low',
      totalProducts: '{count} products',
      noResults: 'No products match your criteria',
      noResultsHint: 'Try adjusting your filters',
      clearFilters: 'Clear Filters',
      gridView: 'Grid view',
      listView: 'List view'
    }
  },
  zh: {
    common: { home: '首页' },
    shop: {
      breadcrumb: '全部产品',
      categoryFilter: '分类',
      priceRange: '价格范围',
      priceMin: '最低',
      priceMax: '最高',
      productStatus: '产品状态',
      onSale: '促销',
      newArrival: '新品',
      inStock: '有库存',
      filter: '筛选',
      sortDefault: '推荐',
      sortNewest: '最新',
      sortPriceLow: '价格：从低到高',
      sortPriceHigh: '价格：从高到低',
      totalProducts: '{count} 件产品',
      noResults: '没有符合条件的产品',
      noResultsHint: '请尝试调整筛选条件',
      clearFilters: '清除筛选',
      gridView: '网格视图',
      listView: '列表视图'
    }
  }
}
</script>

<style scoped>
.pagination-pop {
  opacity: 0;
  filter: blur(8px);
  transform: translateY(72px) scale(0.82);
  transform-origin: bottom center;
  transition:
    opacity 0.5s ease,
    filter 0.5s ease,
    transform 0.5s ease;
  will-change: opacity, filter, transform;
}

.pagination-pop--visible {
  opacity: 1;
  filter: blur(0);
  transform: translateY(0) scale(1);
}

.filter-sheet-enter-active,
.filter-sheet-leave-active {
  transition: opacity 0.2s ease;
}

.filter-sheet-enter-from,
.filter-sheet-leave-to {
  opacity: 0;
}
</style>
