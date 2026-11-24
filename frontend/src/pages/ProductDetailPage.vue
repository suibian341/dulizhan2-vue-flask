<template>
  <div class="mx-auto max-w-[1440px] px-4 pt-24 pb-10 lg:px-8" :class="product ? 'pb-40 lg:pb-10' : ''">
    <template v-if="loading">
      <div class="shimmer mb-8 h-4 w-72 rounded-md"></div>
      <div class="grid gap-5 lg:grid-cols-[minmax(420px,0.95fr)_minmax(0,1.05fr)_300px]">
        <div class="shimmer h-[520px] rounded-2xl"></div>
        <div class="shimmer h-[520px] rounded-2xl"></div>
        <div class="shimmer h-[520px] rounded-2xl"></div>
      </div>
    </template>

    <div v-else-if="!product" class="py-20 text-center">
      <h1 class="text-2xl font-bold">{{ t.detail.notFound }}</h1>
      <p class="mt-2 text-muted-foreground">{{ t.detail.notFoundDesc }}</p>
      <RouterLink :to="localized('/shop')" class="mt-6 inline-flex h-10 items-center justify-center rounded-md bg-primary px-5 text-sm font-medium text-primary-foreground hover:bg-primary/90">
        {{ t.detail.backToShop }}
      </RouterLink>
    </div>

    <template v-else>
      <nav class="mb-5 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
        <RouterLink :to="localized('/')" class="transition-colors hover:text-foreground">{{ t.common.home }}</RouterLink>
        <ChevronRight class="h-3.5 w-3.5" />
        <RouterLink :to="localized('/shop')" class="transition-colors hover:text-foreground">{{ t.shop.breadcrumb }}</RouterLink>
        <ChevronRight class="h-3.5 w-3.5" />
        <RouterLink v-if="product.category" :to="localized(`/shop?category=${product.category.slug}`)" class="transition-colors hover:text-foreground">
          {{ product.category.name }}
        </RouterLink>
        <ChevronRight v-if="product.category" class="h-3.5 w-3.5" />
        <span class="min-w-0 max-w-full truncate font-medium text-foreground">{{ product.name }}</span>
      </nav>

      <section class="grid gap-5 lg:grid-cols-[minmax(420px,0.95fr)_minmax(0,1.05fr)_300px] xl:grid-cols-[minmax(500px,0.98fr)_minmax(0,1.08fr)_320px]">
        <div class="space-y-4">
          <div class="grid gap-3 sm:grid-cols-[72px_minmax(0,1fr)]">
            <div class="order-2 flex gap-3 overflow-x-auto scrollbar-hide sm:order-1 sm:max-h-[520px] sm:flex-col sm:overflow-y-auto sm:overflow-x-hidden">
              <button
                v-for="(image, idx) in displayImages"
                :key="image.id || image.url || idx"
                type="button"
                class="relative aspect-square w-16 shrink-0 overflow-hidden rounded-lg border bg-white transition sm:w-full"
                :class="selectedImage === idx ? 'border-primary shadow-sm' : 'border-border hover:border-primary/60'"
                @click="selectedImage = idx"
              >
                <img :src="image.thumbnailUrl || image.url" :alt="image.alt || product.name" class="h-full w-full object-contain p-1" loading="lazy" decoding="async" />
              </button>
            </div>

            <div class="order-1 sm:order-2">
              <div class="relative overflow-hidden rounded-xl bg-muted p-2">
                <Transition name="image-fade" mode="out-in">
                  <img
                    :key="selectedImage"
                    :src="mainImage?.url"
                    :alt="mainImage?.alt || product.name"
                    class="mx-auto block max-h-[72vh] w-auto max-w-full object-contain"
                  />
                </Transition>
                <div class="absolute left-4 top-4 flex flex-col gap-2">
                  <span v-if="product.isNew" class="gradient-bg rounded-md px-2 py-1 text-xs font-semibold text-white">{{ t.detail.newBadge }}</span>
                  <span v-if="discount > 0" class="rounded-md bg-destructive px-2 py-1 text-xs font-semibold text-white">-{{ discount }}%</span>
                </div>
                <button type="button" class="absolute right-4 top-4 flex h-10 w-10 items-center justify-center rounded-full bg-white/90 shadow-sm backdrop-blur-sm transition hover:bg-white" :aria-label="t.detail.favorite" @click="toggleWishlist">
                  <Heart class="h-5 w-5" :class="wishlisted ? 'fill-red-500 text-red-500' : ''" />
                </button>
                <button type="button" class="absolute right-4 top-1/2 flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded-full bg-white/90 shadow-sm backdrop-blur-sm transition hover:bg-white" :aria-label="t.detail.nextImage" @click="selectImage(selectedImage + 1)">
                  <ChevronRight class="h-5 w-5" />
                </button>
                <button type="button" class="absolute left-4 top-1/2 flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded-full bg-white/90 shadow-sm backdrop-blur-sm transition hover:bg-white" :aria-label="t.detail.prevImage" @click="selectImage(selectedImage - 1)">
                  <ChevronLeft class="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>

        </div>

        <div class="self-start rounded-xl border bg-background p-5 shadow-sm">
          <div class="space-y-3">
            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-primary">{{ product.category?.name || t.detail.readyToQuote }}</p>
              <h1 class="mt-2 text-2xl font-bold leading-tight lg:text-3xl">{{ product.name }}</h1>
              <p v-if="product.shortDescription" class="mt-2 text-sm leading-relaxed text-muted-foreground">{{ product.shortDescription }}</p>
            </div>
            <p v-if="product.sku" class="text-sm text-muted-foreground">SKU: {{ product.sku }}</p>
          </div>

          <div v-if="priceTiers.length" class="mt-5 overflow-hidden rounded-xl border bg-background">
            <div class="border-b bg-muted/50 px-4 py-3 text-sm font-semibold">{{ t.detail.tierPricing }}</div>
            <div class="tier-pricing-grid bg-border" :style="tierGridStyle">
              <div
                v-for="(tier, index) in priceTiers"
                :key="`${tier.minQty}-${tier.maxQty}-${index}`"
                class="bg-background px-4 py-4 text-center transition"
                :class="index === priceTiers.length - 1 && priceTiers.length > 1 ? 'bg-primary/5' : ''"
              >
                <p class="text-sm font-semibold text-muted-foreground">{{ formatTierRange(tier) }}</p>
                <div class="mt-2 flex flex-col items-center gap-1">
                  <p class="text-2xl font-bold leading-tight text-primary">{{ tier.price }}</p>
                  <p v-if="tier.compareAtPrice" class="text-sm leading-tight text-muted-foreground line-through">{{ tier.compareAtPrice }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-4 flex items-center justify-between gap-3 rounded-xl bg-muted/50 p-3 text-sm">
            <div class="flex min-w-0 items-center gap-2">
              <Package class="h-4 w-4 shrink-0 text-primary" />
              <span class="font-medium">{{ t.detail.getSample }}</span>
            </div>
            <a :href="whatsappUrl" target="_blank" rel="noopener noreferrer" class="btn btn-outline h-9 rounded-full px-4 text-xs">{{ t.detail.getSample }}</a>
          </div>

          <div class="mt-5 space-y-5">
            <div v-for="type in variantOptionTypes" :key="type.key">
              <div class="mb-3 flex items-center justify-between gap-3">
                <h3 class="font-semibold">{{ variantTypeLabel(type) }}</h3>
                <button type="button" class="text-xs text-muted-foreground underline hover:text-foreground" @click="openInquiryModal()">{{ t.detail.chooseNow }}</button>
              </div>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="value in optionValuesForType(type)"
                  :key="`${type.key}-${value.en}-${value.zh}`"
                  type="button"
                  class="rounded-lg border px-4 py-2 text-sm transition"
                  :class="optionButtonClass(type, value)"
                  :disabled="!isOptionAvailable(type, value)"
                  @click="selectVariantOption(type, value, true)"
                >
                  {{ variantValueLabel(value) }}
                </button>
              </div>
            </div>

          </div>
        </div>

        <aside class="space-y-4 lg:self-start">
          <div class="rounded-xl border bg-background p-5 shadow-sm">
            <button type="button" class="flex w-full items-center justify-between gap-3 text-left font-bold">
              <span>{{ t.detail.tradeAssurance }}</span>
              <ChevronRight class="h-4 w-4" />
            </button>
            <div class="mt-4 space-y-4 text-sm">
              <div class="flex gap-3">
                <ShieldCheck class="mt-0.5 h-5 w-5 shrink-0 text-emerald-600" />
                <div>
                  <p class="font-semibold">{{ t.detail.securePayment }}</p>
                  <p class="mt-1 text-muted-foreground">{{ t.detail.securePaymentDesc }}</p>
                </div>
              </div>
              <div class="flex gap-3">
                <RotateCcw class="mt-0.5 h-5 w-5 shrink-0 text-emerald-600" />
                <div>
                  <p class="font-semibold">{{ t.detail.refundPolicy }}</p>
                  <p class="mt-1 text-muted-foreground">{{ t.detail.refundPolicyDesc }}</p>
                </div>
              </div>
            </div>
            <div class="my-5 h-px bg-border"></div>
            <div class="space-y-3">
              <button type="button" class="btn h-12 w-full rounded-full bg-primary text-primary-foreground hover:bg-primary/90" :disabled="!inStockNow" @click="openInquiryModal()">
                <ShoppingCart class="h-5 w-5" />
                {{ inStockNow ? t.product.addToInquiry : t.product.outOfStock }}
              </button>
              <a :href="whatsappUrl" target="_blank" rel="noopener noreferrer" class="btn h-12 w-full rounded-full border bg-background hover:bg-muted">
                <MessageSquare class="h-5 w-5" />
                {{ t.detail.sendInquiry }}
              </a>
            </div>
            <p class="mt-4 text-xs leading-relaxed text-muted-foreground">{{ t.detail.tradeAssuranceDesc }}</p>
          </div>
        </aside>
      </section>

      <section class="mt-8">
        <div class="min-w-0">
          <div class="sticky top-16 z-20 border-b bg-background/95 backdrop-blur">
            <div class="flex gap-8 overflow-x-auto text-sm font-semibold">
              <button type="button" class="border-b-4 px-1 py-4 transition" :class="activeTab === 'attributes' ? 'border-foreground text-foreground' : 'border-transparent text-muted-foreground'" @click="activeTab = 'attributes'">{{ t.detail.attributes }}</button>
              <button type="button" class="border-b-4 px-1 py-4 transition" :class="activeTab === 'supplier' ? 'border-foreground text-foreground' : 'border-transparent text-muted-foreground'" @click="activeTab = 'supplier'">{{ t.detail.supplier }}</button>
              <button type="button" class="border-b-4 px-1 py-4 transition" :class="activeTab === 'description' ? 'border-foreground text-foreground' : 'border-transparent text-muted-foreground'" @click="activeTab = 'description'">{{ t.product.description }}</button>
            </div>
          </div>

          <div class="py-8">
            <section v-if="activeTab === 'attributes'" class="space-y-8">
              <div>
                <h2 class="text-2xl font-bold">{{ specTableCopy.title }}</h2>
                <div class="mt-5 space-y-7">
                  <div v-for="group in specGroups" :key="group.title" class="space-y-2">
                    <h3 class="text-base font-semibold">{{ group.title }}</h3>
                    <div class="overflow-hidden border-y border-border bg-background">
                      <div
                        v-for="(pair, pairIndex) in pairRows(group.rows)"
                        :key="`${group.title}-${pairIndex}`"
                        class="grid gap-0 lg:grid-cols-[minmax(108px,0.85fr)_minmax(0,1.55fr)_minmax(108px,0.85fr)_minmax(0,1.55fr)]"
                        :class="pairIndex ? 'border-t border-border' : ''"
                      >
                        <div
                          v-for="row in pair"
                          :key="`${group.title}-${pairIndex}-${row.label}`"
                          class="grid grid-cols-[minmax(88px,0.72fr)_minmax(0,1fr)] lg:contents"
                        >
                          <div class="border-b border-border bg-muted/55 px-3 py-2 text-xs font-medium text-foreground lg:border-b-0 lg:border-r lg:px-3 lg:py-2.5">
                            {{ row.label }}
                          </div>
                          <div class="min-w-0 break-words border-b border-border px-3 py-2 text-xs leading-5 text-foreground lg:border-b-0 lg:px-3 lg:py-2.5">
                            {{ row.value }}
                          </div>
                        </div>
                        <template v-if="pair.length === 1">
                          <div class="hidden border-r border-border bg-muted/55 lg:block"></div>
                          <div class="hidden lg:block"></div>
                        </template>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <section v-else-if="activeTab === 'supplier'" class="space-y-4">
              <h2 class="text-2xl font-bold">{{ t.detail.supplier }}</h2>
              <div class="rounded-xl border bg-background p-5">
                <p class="font-semibold">{{ supplierName }}</p>
                <p class="mt-2 text-sm text-muted-foreground">{{ t.detail.supplierDescription }}</p>
              </div>
            </section>

            <section v-else class="space-y-8">
              <div>
                <h2 class="text-2xl font-bold">{{ t.product.description }}</h2>
                <p class="mt-4 leading-relaxed text-muted-foreground">{{ product.description || product.shortDescription }}</p>
              </div>
              <div v-if="posterImages.length > 0" class="space-y-4">
                <div v-for="image in posterImages" :key="image.id || image.url" class="mx-auto w-full max-w-5xl overflow-hidden rounded-xl">
                  <img :src="image.url" :alt="image.alt || product.name" class="h-auto w-full object-contain" />
                </div>
              </div>
            </section>
          </div>
        </div>

      </section>

      <section v-if="relatedProducts.length > 0" class="mt-12">
        <h2 class="mb-6 text-2xl font-bold">{{ t.product.relatedProducts }}</h2>
        <div class="grid grid-cols-2 gap-4 md:grid-cols-4 lg:gap-6">
          <ProductCard v-for="item in relatedProducts" :key="item.id" :product="item" />
        </div>
      </section>

      <div class="fixed bottom-16 left-0 right-0 z-40 border-t bg-white p-3 shadow-lg lg:hidden">
        <div class="flex items-center justify-between gap-3">
          <div>
            <span class="block text-xl font-bold leading-tight text-primary">{{ displayPriceRange }}</span>
            <span v-if="displayComparePriceRange" class="block text-sm leading-tight text-muted-foreground line-through">{{ displayComparePriceRange }}</span>
          </div>
          <button type="button" class="btn h-10 rounded-full bg-primary px-5 text-sm font-medium text-primary-foreground disabled:pointer-events-none disabled:opacity-50" :disabled="!inStockNow" @click="openInquiryModal()">
            <ShoppingCart class="h-4 w-4" />
            {{ inStockNow ? t.detail.addToInquiryMobile : t.detail.outOfStockMobile }}
          </button>
        </div>
      </div>

      <Teleport to="body">
        <Transition name="modal-fade">
          <div v-if="inquiryModalOpen" class="fixed inset-0 z-[80] flex items-center justify-center bg-black/45 px-4 py-6" @click.self="closeInquiryModal">
            <div class="max-h-[92vh] w-full max-w-2xl overflow-y-auto rounded-2xl bg-background p-5 shadow-2xl">
              <div class="flex items-start justify-between gap-4">
                <div>
                  <p class="text-xs font-medium uppercase tracking-wide text-primary">{{ t.detail.selectSpecsToQuote }}</p>
                  <h2 class="mt-1 text-xl font-bold">{{ product.name }}</h2>
                </div>
                <button type="button" class="btn btn-ghost h-9 w-9" :aria-label="t.detail.close" @click="closeInquiryModal">
                  <X class="h-5 w-5" />
                </button>
              </div>

              <div class="mt-5 space-y-5">
                <div v-for="type in variantOptionTypes" :key="`modal-${type.key}`">
                  <h3 class="mb-3 text-sm font-semibold">{{ variantTypeLabel(type) }}</h3>
                  <div class="flex flex-wrap gap-2">
                    <button
                      v-for="value in optionValuesForType(type)"
                      :key="`modal-${type.key}-${value.en}-${value.zh}`"
                      type="button"
                      class="inline-flex min-h-11 flex-col items-start justify-center rounded-lg border px-4 py-2 text-sm transition"
                      :class="optionButtonClass(type, value)"
                      :disabled="!isOptionAvailable(type, value)"
                      @click="selectVariantOption(type, value)"
                    >
                      <span>{{ variantValueLabel(value) }}</span>
                      <span v-if="variantOptionPriceText(type, value)" class="mt-0.5 text-xs font-semibold text-primary">{{ variantOptionPriceText(type, value) }}</span>
                    </button>
                  </div>
                </div>

                <div class="grid gap-3 rounded-xl border bg-muted/40 p-4 text-sm sm:grid-cols-4">
                  <div>
                    <p class="text-xs text-muted-foreground">{{ t.detail.selectedOptions }}</p>
                    <p class="mt-1 font-semibold">{{ selectedVariantText || t.detail.toBeConfirmed }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-muted-foreground">SKU</p>
                    <p class="mt-1 font-semibold">{{ selectedVariantSku || product.sku }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-muted-foreground">{{ t.detail.price }}</p>
                    <p class="mt-1 font-semibold text-primary">{{ selectedVariantPriceText }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-muted-foreground">{{ t.detail.stock }}</p>
                    <p class="mt-1 font-semibold" :class="selectedVariantStock > 0 ? 'text-emerald-600' : 'text-destructive'">
                      {{ selectedVariantStock > 0 ? `${selectedVariantStock} ${t.detail.piecesUnit}` : t.product.outOfStock }}
                    </p>
                  </div>
                </div>

                <div>
                  <h3 class="mb-3 text-sm font-semibold">{{ t.detail.quantity }}</h3>
                  <div class="flex w-44 items-center rounded-lg border">
                    <button type="button" class="flex h-10 w-10 items-center justify-center transition hover:bg-muted" :aria-label="t.detail.decreaseQuantity" @click="quantity = Math.max(1, quantity - 1)">
                      <Minus class="h-4 w-4" />
                    </button>
                    <span class="flex-1 text-center font-medium">{{ quantity }}</span>
                    <button type="button" class="flex h-10 w-10 items-center justify-center transition hover:bg-muted" :aria-label="t.detail.increaseQuantity" @click="increaseQuantity">
                      <Plus class="h-4 w-4" />
                    </button>
                  </div>
                  <p v-if="!hasCompleteVariantSelection" class="mt-2 text-sm text-amber-700">{{ t.detail.chooseAllSpecs }}</p>
                  <p v-else-if="variantUnavailable" class="mt-2 text-sm text-destructive">{{ t.detail.variantUnavailable }}</p>
                </div>
              </div>

              <div class="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
                <button type="button" class="btn btn-outline h-11 px-5" @click="closeInquiryModal">{{ t.detail.cancel }}</button>
                <button type="button" class="btn h-11 bg-primary px-6 text-primary-foreground" :disabled="!canConfirmInquiry" @click="confirmInquiry">
                  <ShoppingCart class="h-4 w-4" />
                  {{ t.detail.confirmInquiry }}
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import {
  ChevronLeft,
  ChevronRight,
  Heart,
  MessageSquare,
  Minus,
  Package,
  Plus,
  RotateCcw,
  ShoppingCart,
  ShieldCheck,
  X
} from 'lucide-vue-next'

import { currentUser, getProduct } from '@/api'
import ProductCard from '@/components/ProductCard.vue'
import { loadLocaleMessages, translatedCopy } from '@/i18n'
import { createDefaultPowerStripSpecs, isCustomizationSpec } from '@/specTemplates'
import { useInquiryStore } from '@/stores/inquiry'
import { useUiStore } from '@/stores/ui'
import { useWishlistStore } from '@/stores/wishlist'
import { price, productComparePriceRange, productHasNegotiablePrice, productPriceRange, productPricingMode, salePercent } from '@/utils'
import {
  formatVariantOptions,
  localizedOptionName,
  localizedOptionValue,
  normalizeVariantOptionTypes,
  optionPairsForType
} from '@/variantOptions'

const route = useRoute()
const router = useRouter()
const inquiry = useInquiryStore()
const ui = useUiStore()
const wishlist = useWishlistStore()
const loading = ref(true)
const product = ref(null)
const relatedProducts = ref([])
const selectedImage = ref(0)
const selectedVariantOptions = reactive({})
const inquiryModalOpen = ref(false)
const quantity = ref(1)
const activeTab = ref('attributes')
const whatsappUrl = 'https://wa.me/8613247309378'

const locale = computed(() => route.params.locale || 'en')
const t = computed(() => translatedCopy(locale.value, copy, source => ({
  common: { home: source.common?.home },
  shop: { breadcrumb: source.shop?.breadcrumb },
  product: {
    addToInquiry: source.product?.addToInquiry,
    outOfStock: source.product?.outOfStock,
    sizeGuide: source.product?.sizeGuide,
    color: source.product?.color,
    size: source.product?.size,
    description: source.product?.description,
    specifications: source.product?.specifications,
    reviews: source.product?.reviews,
    relatedProducts: source.product?.relatedProducts
  },
  detail: source.productDetail
})))

const usesPowerStripSpecs = computed(() => {
  const haystack = [
    product.value?.sku,
    product.value?.slug,
    product.value?.name,
    product.value?.category?.name,
    product.value?.category?.slug
  ].join(' ').toLowerCase()
  return /203ms|power strip|extension socket|socket|plug|adapter|charging station|charging strip|surge protector|power hub|排插|插线板|延长插座|插头|转换器|快充|电源|浪涌|无线充电/.test(haystack)
})
const displayImages = computed(() => {
  const rows = (product.value?.images || []).filter(image => (image.sortOrder ?? 0) < 100)
  return rows.length ? rows : (product.value?.images || [])
})
const mainImage = computed(() => displayImages.value[selectedImage.value] || displayImages.value[0] || null)
const posterImages = computed(() => (product.value?.images || []).filter(image => (image.sortOrder ?? 0) >= 100))
const tradeInfo = computed(() => product.value?.tradeInfo || {})
const variantOptionTypes = computed(() => {
  const savedTypes = Array.isArray(tradeInfo.value.variantOptionTypes) ? tradeInfo.value.variantOptionTypes : []
  const variants = product.value?.variants || []
  const hasVariantOptions = variants.some(variant => Object.keys(variant.options || {}).length)
  if (!savedTypes.length && !hasVariantOptions) return []
  return normalizeVariantOptionTypes(savedTypes, variants)
})
const rawSpecs = computed(() => {
  const saved = Array.isArray(product.value?.specifications) ? product.value.specifications : []
  if (saved.length) return saved.filter(spec => !isCustomizationSpec(spec))
  return usesPowerStripSpecs.value ? createDefaultPowerStripSpecs() : []
})
const normalizedSpecs = computed(() => {
  const rows = rawSpecs.value.map(item => ({
    label: localizedTradeText(item.label || item.name || item.key || { en: item.labelEn, zh: item.labelZh }, ''),
    value: localizedTradeText(item.value || item.details || item.content || { en: item.valueEn, zh: item.valueZh }, ''),
    note: localizedTradeText(item.note || item.notes || item.remark || item.section || { en: item.noteEn, zh: item.noteZh }, '')
  })).filter(item => item.label && item.value)
  return rows
})
const specTableCopy = computed(() => locale.value === 'zh'
  ? { title: '产品规格', defaultGroup: '产品规格' }
  : { title: 'Product Specifications', defaultGroup: 'Product Specifications' }
)
const specGroups = computed(() => {
  const groups = []
  const byTitle = new Map()
  for (const row of normalizedSpecs.value) {
    const title = row.note || specTableCopy.value.defaultGroup
    if (!byTitle.has(title)) {
      const group = { title, rows: [] }
      byTitle.set(title, group)
      groups.push(group)
    }
    byTitle.get(title).rows.push(row)
  }
  return groups
})
const currentVariant = computed(() => {
  const variants = product.value?.variants || []
  if (!variants.length) return null
  if (!variantOptionTypes.value.length) return variants[0]
  if (!hasCompleteVariantSelection.value) return null
  return variants.find(variant => variantMatchesSelection(variant, selectedVariantOptions)) || null
})
const selectedVariantOptionsPayload = computed(() => {
  const options = {}
  for (const type of variantOptionTypes.value) {
    const selected = selectedVariantOptions[type.key]
    if (!selected) continue
    const pair = optionPairsForType(type).find(item => optionKey(item) === selected || item.zh === selected)
    options[type.key] = {
      name: {
        en: type.nameEn || type.name?.en || type.key,
        zh: type.nameZh || type.name?.zh || type.nameEn || type.key
      },
      value: {
        en: pair?.en || selected,
        zh: pair?.zh || pair?.en || selected
      }
    }
  }
  return options
})
const selectedVariantText = computed(() => formatSelectedVariantOptions(selectedVariantOptionsPayload.value))
const selectedVariantSku = computed(() => currentVariant.value?.sku || '')
const hasCompleteVariantSelection = computed(() => variantOptionTypes.value.every(type => selectedVariantOptions[type.key]))
const totalStock = computed(() => {
  if (tradeInfo.value.stock !== undefined && tradeInfo.value.stock !== null && tradeInfo.value.stock !== '') {
    return Number(tradeInfo.value.stock || 0)
  }
  return (product.value?.variants || []).reduce((sum, variant) => sum + Number(variant.stock || 0), 0)
})
const selectedVariantStock = computed(() => {
  if (currentVariant.value) return Number(currentVariant.value.stock || 0)
  if ((product.value?.variants || []).length) return 0
  return Number(totalStock.value || 999)
})
const selectedVariantPriceText = computed(() => {
  if (!hasCompleteVariantSelection.value) return t.value.detail.toBeConfirmed
  return variantPriceText(currentVariant.value) || displayPriceRange.value
})
const variantUnavailable = computed(() => {
  if (!product.value) return false
  if (!hasCompleteVariantSelection.value) return false
  if (!(product.value.variants || []).length) return false
  return !currentVariant.value || selectedVariantStock.value <= 0
})
const canConfirmInquiry = computed(() => {
  if (!product.value) return false
  if (!hasCompleteVariantSelection.value) return false
  return !variantUnavailable.value
})
const inStockNow = computed(() => totalStock.value > 0 || !currentVariant.value || currentVariant.value.stock > 0)
const discount = computed(() => salePercent(product.value))
const wishlisted = computed(() => product.value ? wishlist.isSaved(product.value.id) : false)
const supplierName = computed(() => product.value?.brandName ? `${product.value.brandName} Supplier` : 'Misicheng Supplier')
const pricingMode = computed(() => productPricingMode(product.value))
const displayPriceRange = computed(() => productPriceRange(product.value, ui.currency, { negotiableText: t.value.detail.negotiable }))
const displayComparePriceRange = computed(() => productComparePriceRange(product.value, ui.currency))
const priceTiers = computed(() => {
  if (pricingMode.value !== 'tier') return []
  const base = Number(product.value?.price || 0)
  const saved = Array.isArray(tradeInfo.value.priceTiers) ? tradeInfo.value.priceTiers : []
  const rows = saved
    .map(row => ({
      minQty: Number(row.minQty || 0),
      maxQty: row.maxQty === '' || row.maxQty === null || row.maxQty === undefined ? null : Number(row.maxQty),
      amount: Number(row.price || 0),
      compareAtAmount: Number(row.compareAtPrice || row.comparePrice || row.originalPrice || 0),
      negotiable: !!(row.negotiable || row.priceNegotiable)
    }))
    .filter(row => row.minQty > 0 && (row.negotiable || row.amount > 0))
  const fallback = base > 0
    ? [{ minQty: 0, maxQty: null, amount: base, compareAtAmount: Number(product.value?.compareAtPrice || 0), negotiable: false, isBase: true }]
    : []
  return (rows.length ? rows : fallback).map(row => ({
    ...row,
    price: row.negotiable ? t.value.detail.negotiable : price(row.amount, ui.currency),
    compareAtPrice: row.negotiable || !row.compareAtAmount ? '' : price(row.compareAtAmount, ui.currency)
  }))
})
const tierGridStyle = computed(() => {
  const count = priceTiers.value.length
  return { '--tier-columns': String(Math.max(1, Math.min(count, 4))) }
})
function localizedTradeText(value, fallback = '') {
  if (value && typeof value === 'object') {
    return value[locale.value === 'zh' ? 'zh' : 'en'] || value.en || value.zh || fallback
  }
  return value || fallback
}

function optionKey(value) {
  if (!value) return ''
  if (typeof value === 'object' && value.value !== undefined) return optionKey(value.value)
  if (typeof value === 'object') return value.en || value.zh || ''
  return String(value)
}

function optionMatches(value, selected) {
  if (!selected) return true
  if (!value) return false
  if (typeof value === 'object') return value.en === selected || value.zh === selected
  return String(value) === selected
}

function variantMatchesSelection(variant, selection) {
  return variantOptionTypes.value.every(type => {
    const selected = selection[type.key]
    return !selected || optionMatches(variant.options?.[type.key], selected)
  })
}

function variantTypeLabel(type) {
  return localizedOptionName(type, locale.value === 'zh' ? 'zh' : 'en')
}

function optionValuesForType(type) {
  return optionPairsForType(type)
}

function variantValueLabel(value) {
  return localizedOptionValue(value, locale.value === 'zh' ? 'zh' : 'en')
}

function isOptionSelected(type, value) {
  return selectedVariantOptions[type.key] === optionKey(value)
}

function isOptionAvailable(type, value) {
  const variants = product.value?.variants || []
  if (!variants.length) return true
  const selection = { ...selectedVariantOptions, [type.key]: optionKey(value) }
  return variants.some(variant => variantMatchesSelection(variant, selection) && Number(variant.stock || 0) > 0)
}

function optionButtonClass(type, value) {
  if (isOptionSelected(type, value)) return 'border-primary bg-primary/10 text-primary'
  if (isOptionAvailable(type, value)) return 'border-border hover:border-primary/50'
  return 'cursor-not-allowed border-gray-100 text-gray-300 line-through'
}

function positiveAmount(value) {
  const number = Number(value)
  return Number.isFinite(number) && number > 0 ? number : null
}

function variantPriceText(variant) {
  if (pricingMode.value !== 'variant') return ''
  const amount = positiveAmount(variant?.price)
  if (amount !== null) return price(amount, ui.currency)
  return productHasNegotiablePrice(product.value) ? t.value.detail.negotiable : ''
}

function candidateVariantForOption(type, value) {
  const variants = product.value?.variants || []
  if (!variants.length) return null
  const selection = { ...selectedVariantOptions, [type.key]: optionKey(value) }
  const matches = variants.filter(variant => variantMatchesSelection(variant, selection) && Number(variant.stock || 0) > 0)
  if (!matches.length) return null
  const complete = variantOptionTypes.value.every(item => selection[item.key])
  if (complete || matches.length === 1) return matches[0]
  const pricedMatches = matches.filter(variant => positiveAmount(variant.price) !== null)
  const uniquePrices = new Set(pricedMatches.map(variant => String(positiveAmount(variant.price))))
  return uniquePrices.size === 1 ? pricedMatches[0] : null
}

function variantOptionPriceText(type, value) {
  if (pricingMode.value !== 'variant') return ''
  const variant = candidateVariantForOption(type, value)
  return variant ? variantPriceText(variant) : ''
}

function selectVariantOption(type, value, openModal = false) {
  if (!isOptionAvailable(type, value)) return
  selectedVariantOptions[type.key] = optionKey(value)
  if (openModal) inquiryModalOpen.value = true
}

function formatSelectedVariantOptions(options) {
  return formatVariantOptions(options, variantOptionTypes.value, locale.value === 'zh' ? 'zh' : 'en')
}

function resetVariantSelection() {
  Object.keys(selectedVariantOptions).forEach(key => delete selectedVariantOptions[key])
  const firstAvailableVariant = (product.value?.variants || []).find(variant => Number(variant.stock || 0) > 0) || product.value?.variants?.[0]
  for (const type of variantOptionTypes.value) {
    const firstVariantValue = firstAvailableVariant?.options?.[type.key]
    const firstOption = optionPairsForType(type)[0]
    selectedVariantOptions[type.key] = optionKey(firstVariantValue) || optionKey(firstOption)
  }
}

function openInquiryModal(type = null, value = null) {
  if (type && value) selectVariantOption(type, value)
  inquiryModalOpen.value = true
}

function closeInquiryModal() {
  inquiryModalOpen.value = false
}

function increaseQuantity() {
  quantity.value = Math.min(selectedVariantStock.value || 999, quantity.value + 1)
}

function shortHash(value) {
  let hash = 0
  for (let index = 0; index < value.length; index += 1) {
    hash = ((hash << 5) - hash) + value.charCodeAt(index)
    hash |= 0
  }
  return Math.abs(hash).toString(36)
}

function pairRows(rows) {
  const pairs = []
  for (let index = 0; index < rows.length; index += 2) {
    pairs.push(rows.slice(index, index + 2))
  }
  return pairs
}

function qtyUnit() {
  return locale.value === 'zh' ? t.value.detail.piecesUnit : 'pcs'
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString(locale.value === 'zh' ? 'zh-CN' : 'en-US')
}

function formatQty(value) {
  return `${formatNumber(value)} ${qtyUnit()}`
}

function formatTierRange(tier) {
  if (tier.isBase) return locale.value === 'zh' ? '\u4ef7\u683c' : 'Price'
  if (!tier.maxQty) return `${formatNumber(tier.minQty)}+ ${qtyUnit()}`
  return `${formatNumber(tier.minQty)}-${formatNumber(tier.maxQty)} ${qtyUnit()}`
}

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

function selectImage(idx) {
  if (!displayImages.value.length) return
  selectedImage.value = (idx + displayImages.value.length) % displayImages.value.length
}

function showSizeGuide() {
  window.alert(t.value.detail.sizeGuideText)
}

function confirmInquiry() {
  if (!product.value || !canConfirmInquiry.value) return
  const user = currentUser()
  if (!user) {
    router.push(localized(`/login?redirect=${encodeURIComponent(route.fullPath)}`))
    return
  }
  const optionSignature = Object.entries(selectedVariantOptionsPayload.value)
    .map(([key, value]) => `${key}-${optionKey(value)}`)
    .join('_') || 'default'
  const variantPrice = positiveAmount(currentVariant.value?.price) ?? positiveAmount(product.value.price) ?? 0
  const variant = {
    ...(currentVariant.value || {}),
    id: currentVariant.value?.id || `opt-${shortHash(optionSignature)}`,
    sku: currentVariant.value?.sku || product.value.sku,
    price: variantPrice,
    priceNegotiable: variantPrice <= 0 && productHasNegotiablePrice(product.value),
    stock: currentVariant.value?.stock ?? selectedVariantStock.value ?? 999,
    options: selectedVariantOptionsPayload.value
  }
  inquiry.addItem({ ...product.value, variants: [variant] }, quantity.value)
  inquiryModalOpen.value = false
}

function toggleWishlist() {
  if (!product.value) return
  wishlist.toggle(product.value)
}

async function load() {
  const targetLocale = locale.value
  loading.value = true
  try {
    const data = await getProduct(route.params.slug, targetLocale)
    if (targetLocale !== locale.value) return
    product.value = data.product
    relatedProducts.value = data.relatedProducts || []
    resetVariantSelection()
    selectedImage.value = 0
    quantity.value = 1
    activeTab.value = 'attributes'
  } catch {
    if (targetLocale !== locale.value) return
    product.value = null
  } finally {
    if (targetLocale === locale.value) loading.value = false
  }
}

watch(() => route.params.slug, load)
watch(locale, async target => {
  await loadLocaleMessages(target).catch(() => {})
  await load()
})
onMounted(async () => {
  await loadLocaleMessages(locale.value).catch(() => {})
  await load()
})

const copy = {
  en: {
    common: { home: 'Home' },
    shop: { breadcrumb: 'All Products' },
    product: {
      addToInquiry: 'Add to Cart',
      outOfStock: 'Out of Stock',
      sizeGuide: 'Size Guide',
      color: 'Color',
      size: 'Size',
      description: 'Description',
      specifications: 'Specifications',
      reviews: 'Reviews',
      relatedProducts: 'Related Products'
    },
    detail: {
      notFound: 'Product Not Found',
      notFoundDesc: "This product may have been removed or doesn't exist",
      backToShop: 'Back to Shop',
      newBadge: 'New',
      favorite: 'Favorite',
      prevImage: 'Previous image',
      nextImage: 'Next image',
      readyToQuote: 'Ready to Quote',
      samplePrice: 'Sample price',
      negotiable: 'Negotiable',
      getSample: 'Contact for Sample',
      chooseNow: 'Choose now',
      tierPricing: 'Tier Pricing',
      price: 'Price',
      minimumOrderShort: 'MOQ',
      cartonSpec: 'Carton',
      stock: 'Stock',
      shipFrom: 'Ship from',
      defaultShipFrom: 'Shenzhen / Yiwu',
      piecesUnit: 'pcs',
      cartonUnit: 'sets/carton',
      inStockLabel: 'in stock',
      plugStandard: 'Plug Standard',
      coreAttributes: 'Core Industry Attributes',
      logistics: 'Logistics',
      shippingNotice: 'Shipping solution will be confirmed after quantity and destination are selected.',
      tradeAssurance: 'Trade Assurance',
      securePayment: 'Secure payment',
      securePaymentDesc: 'Payments and order details are protected for B2B purchasing.',
      refundPolicy: 'Refund policy',
      refundPolicyDesc: 'Request support if goods are not shipped, missing, or have quality issues.',
      contactSupplier: 'Contact Supplier',
      tradeAssuranceDesc: 'Quote-based order support is available after submitting an inquiry.',
      sendInquiry: 'Send Inquiry',
      quantity: 'Quantity',
      decreaseQuantity: 'Decrease quantity',
      increaseQuantity: 'Increase quantity',
      onlyLeft: 'Only {count} left, order now.',
      inStockShip: 'In stock, ships after quotation confirmation.',
      attributes: 'Attributes',
      supplier: 'Supplier',
      productSpecs: 'Product Specifications',
      specCategory: 'Category',
      specFields: 'Fields',
      importantAttributes: 'Important Attributes',
      parameter: 'Parameter',
      details: 'Details',
      notes: 'Notes / Recommendation',
      packagingAndDelivery: 'Packaging and Delivery Information',
      viewDetails: 'View details',
      noReviews: 'No reviews yet.',
      supplierDescription: 'Professional air movement and electrical products supplier supporting OEM, project and distributor sourcing.',
      responseTime: 'Response time',
      onTimeDelivery: 'On-time delivery rate',
      supplierMeta: 'CN · OEM / ODM · Project sourcing',
      sizeGuideText: 'Confirm plug standard, outlet count, cable length, voltage, certification and target market before bulk orders.',
      sellingUnit: 'Selling Unit',
      singleItem: 'Single item',
      packageSize: 'Package Size',
      grossWeight: 'Gross Weight',
      toBeConfirmed: 'To be confirmed',
      minimumOrderLabel: 'Minimum Order',
      selectSpecsToQuote: 'Select specifications',
      selectedOptions: 'Selected specifications',
      chooseAllSpecs: 'Please select all specifications before adding to cart.',
      variantUnavailable: 'This specification combination is out of stock.',
      confirmInquiry: 'Add to Cart',
      cancel: 'Cancel',
      close: 'Close',
      addToInquiryMobile: 'Add to Cart',
      outOfStockMobile: 'Out of Stock'
    }
  },
  zh: {
    common: { home: '首页' },
    shop: { breadcrumb: '全部商品' },
    product: {
      addToInquiry: '加入购物车',
      outOfStock: '缺货',
      sizeGuide: '规格指南',
      color: '颜色',
      size: '规格',
      description: '描述',
      specifications: '规格参数',
      reviews: '评价',
      relatedProducts: '相关商品'
    },
    detail: {
      notFound: '未找到商品',
      notFoundDesc: '该商品可能已下架或不存在',
      backToShop: '返回商品列表',
      newBadge: '新品',
      favorite: '收藏',
      prevImage: '上一张图片',
      nextImage: '下一张图片',
      readyToQuote: '可快速报价',
      samplePrice: '样品价格',
      negotiable: '面议',
      getSample: '联系取样',
      chooseNow: '立即选择',
      tierPricing: '阶梯价格',
      price: '价格',
      minimumOrderShort: '起订量',
      cartonSpec: '箱规',
      stock: '库存',
      shipFrom: '发货地',
      defaultShipFrom: '深圳 / 义乌',
      piecesUnit: '件',
      cartonUnit: '套/箱',
      inStockLabel: '现货',
      plugStandard: '插头标准分类',
      coreAttributes: '核心行业属性',
      logistics: '物流',
      shippingNotice: '所选数量暂无运输解决方案，提交询盘后确认。',
      tradeAssurance: '交易保障',
      securePayment: '安全支付',
      securePaymentDesc: 'B2B 采购订单和支付信息将受到保护。',
      refundPolicy: '退款保障',
      refundPolicyDesc: '若订单未发货、丢失或收货后发现问题，可申请支持。',
      contactSupplier: '联系商家',
      tradeAssuranceDesc: '通过提交询盘确认数量、规格和物流方案。',
      sendInquiry: '发送询盘',
      quantity: '数量',
      decreaseQuantity: '减少数量',
      increaseQuantity: '增加数量',
      onlyLeft: '仅剩 {count} 件，尽快下单。',
      inStockShip: '现货，报价确认后发货。',
      attributes: '属性',
      supplier: '供应商',
      importantAttributes: '重要属性',
      parameter: '参数',
      details: '参数内容',
      notes: '备注 / 建议',
      packagingAndDelivery: '包装和发货信息',
      viewDetails: '查看详情',
      noReviews: '暂无评价。',
      supplierDescription: '专业排插、转换器与电气产品供应商，支持 OEM、工程项目和经销采购。',
      responseTime: '响应时间',
      onTimeDelivery: '准时发货率',
      supplierMeta: 'CN · OEM / ODM · 工程采购',
      sizeGuideText: '批量下单前请确认插头标准、插座位数、线长、电压、认证和目标市场。',
      sellingUnit: '销售单位',
      singleItem: '单一商品',
      packageSize: '包装尺寸',
      grossWeight: '单个产品毛重',
      toBeConfirmed: '待确认',
      minimumOrderLabel: '最小订单',
      selectSpecsToQuote: '选择规格',
      selectedOptions: '已选规格',
      chooseAllSpecs: '请先选择完整规格再加入购物车。',
      variantUnavailable: '当前规格组合暂无库存。',
      confirmInquiry: '加入购物车',
      cancel: '取消',
      close: '关闭',
      addToInquiryMobile: '加入购物车',
      outOfStockMobile: '缺货'
    }
  }
}
</script>

<style scoped>
.image-fade-enter-active,
.image-fade-leave-active {
  transition: opacity 0.3s ease;
}

.image-fade-enter-from,
.image-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.22s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.tier-pricing-grid {
  display: grid;
  gap: 1px;
  grid-template-columns: 1fr;
}

@media (min-width: 640px) {
  .tier-pricing-grid {
    grid-template-columns: repeat(var(--tier-columns), minmax(0, 1fr));
  }
}
</style>
