<template>
  <div ref="pageRef" class="relative min-h-screen overflow-x-clip bg-gradient-to-b from-teal-50/60 via-cyan-50/30 to-white">
    <section class="relative min-h-screen w-full overflow-hidden bg-gradient-to-br from-teal-50 via-cyan-100/80 to-blue-100/70">
      <div class="pointer-events-none absolute -top-20 -right-20 h-[75%] w-[65%] rounded-full bg-gradient-to-bl from-teal-200/50 via-cyan-100/40 to-transparent blur-3xl"></div>
      <div class="pointer-events-none absolute -bottom-20 -left-20 h-[55%] w-[45%] rounded-full bg-gradient-to-tr from-blue-200/40 via-teal-100/30 to-transparent blur-3xl"></div>

      <Transition :name="direction > 0 ? 'hero-next' : 'hero-prev'" mode="out-in">
        <div :key="slideIndex" class="relative">
          <div class="relative flex min-h-screen items-center pt-[4.5rem] pb-20 md:pt-24 md:pb-24">
            <div class="mx-auto w-full max-w-[1400px] px-6 sm:px-8 lg:px-16">
              <div class="grid items-center gap-8 lg:grid-cols-[1fr_1.618fr] lg:gap-16">
                <div class="max-w-3xl space-y-4 md:space-y-8">
                  <div class="hero-reveal">
                    <span class="inline-block rounded-full bg-teal-100 px-5 py-2.5 text-sm font-semibold tracking-wide text-teal-700">
                      {{ t.bannerTag }}
                    </span>
                  </div>
                  <h1 class="hero-reveal gradient-text-heading text-3xl leading-[1.1] font-bold tracking-tight sm:text-5xl md:text-7xl lg:text-[4.5rem] xl:text-[5rem]">
                    {{ activeSlide?.title }}
                  </h1>
                  <p class="hero-reveal text-lg leading-relaxed font-light text-gray-600 sm:text-xl md:text-2xl">
                    {{ activeSlide?.subtitle }}
                  </p>
                  <div class="hero-reveal flex flex-wrap gap-4 pt-2 sm:gap-5">
                    <div v-for="stat in heroStatsForSlide" :key="stat.label" class="rounded-xl border border-teal-100 bg-white/80 px-6 py-3 shadow-md backdrop-blur-sm sm:px-7 sm:py-4">
                      <div class="gradient-text-heading text-2xl font-bold sm:text-3xl">{{ stat.value }}</div>
                      <div class="mt-0.5 text-sm text-gray-600 sm:text-base">{{ stat.label }}</div>
                    </div>
                  </div>
                  <div class="hero-reveal flex flex-col gap-4 pt-2 sm:flex-row">
                    <RouterLink :to="localized('/shop')">
                      <button class="btn h-12 w-full rounded-xl border-0 bg-gradient-to-r from-teal-500 to-cyan-500 px-8 text-base font-semibold text-white shadow-xl shadow-teal-500/25 transition-all duration-300 hover:-translate-y-1 hover:from-teal-600 hover:to-cyan-600 hover:[box-shadow:0_4px_16px_rgba(20,184,166,0.25),0_0_48px_rgba(20,184,166,0.45)] sm:h-14 sm:w-auto sm:px-10 sm:text-lg md:h-16">
                        <ShoppingBag class="mr-2.5 h-5 w-5 sm:h-6 sm:w-6" />
                        {{ activeSlide?.buttonText || t.shopNow }}
                      </button>
                    </RouterLink>
                    <RouterLink :to="localized('/service')">
                      <button class="btn h-12 w-full rounded-xl border-2 border-gray-300 px-8 text-base font-semibold text-gray-700 transition-all duration-300 hover:-translate-y-1 hover:border-teal-300 hover:bg-white/80 hover:[box-shadow:0_4px_16px_rgba(156,163,175,0.25),0_0_48px_rgba(156,163,175,0.4)] sm:h-14 sm:w-auto sm:px-10 sm:text-lg md:h-16">
                        <Play class="mr-2.5 h-5 w-5 sm:h-6 sm:w-6" />
                        {{ t.learnMore }}
                      </button>
                    </RouterLink>
                  </div>
                </div>

                <div class="hero-image-reveal relative">
                  <div class="relative">
                    <div class="overflow-hidden rounded-2xl lg:rounded-3xl">
                      <img :src="activeSlide?.image" :alt="activeSlide?.title" class="h-[200px] w-full object-cover sm:h-[300px] lg:h-[520px] xl:h-[600px]" />
                    </div>
                    <div class="absolute -inset-8 -z-10 hidden rounded-3xl bg-gradient-to-r from-teal-400 via-cyan-400 to-blue-400 opacity-15 blur-3xl lg:block"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>

      <div v-if="banners.length > 1" class="absolute right-0 bottom-6 left-0 z-20 flex items-center justify-center gap-4 sm:bottom-8 sm:gap-6">
        <button class="rounded-full bg-white/80 p-1.5 text-gray-600 shadow-md backdrop-blur-sm transition hover:text-teal-600 sm:p-2" :aria-label="t.prevSlide" @click="paginate(-1)">
          <ChevronLeft class="h-5 w-5 sm:h-6 sm:w-6" />
        </button>
        <div class="flex gap-2 sm:gap-3">
          <button
            v-for="(_, idx) in banners"
            :key="idx"
            class="h-2 rounded-full transition-all duration-500 sm:h-2.5"
            :class="idx === slideIndex ? 'w-8 bg-gradient-to-r from-teal-500 to-cyan-500 sm:w-10' : 'w-2 bg-gray-300 hover:bg-teal-400 sm:w-2.5'"
            :aria-label="`${t.goToSlide} ${idx + 1}`"
            @click="goTo(idx)"
          ></button>
        </div>
        <button class="rounded-full bg-white/80 p-1.5 text-gray-600 shadow-md backdrop-blur-sm transition hover:text-teal-600 sm:p-2" :aria-label="t.nextSlide" @click="paginate(1)">
          <ChevronRight class="h-5 w-5 sm:h-6 sm:w-6" />
        </button>
      </div>
    </section>

    <div class="mx-auto max-w-[1400px] px-6 sm:px-10 lg:px-16">
      <section class="reveal-section py-12 md:py-24">
        <div class="mb-12 text-center">
          <h2 class="gradient-text-heading text-3xl font-bold md:text-4xl">{{ t.categoryTitle }}</h2>
          <p class="mt-3 text-muted-foreground">{{ t.categorySubtitle }}</p>
        </div>
        <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
          <RouterLink v-for="cp in categoryProducts" :key="cp.category.id" :to="localized(`/shop?category=${cp.category.slug}`)" class="group flex flex-col items-center rounded-xl bg-gradient-to-br from-teal-100 to-cyan-100 p-5 transition-shadow duration-300 hover:shadow-lg">
            <div class="relative aspect-[4/3] w-full overflow-hidden rounded-lg">
              <img :src="cp.category.thumbnailUrl || cp.category.image" :alt="cp.category.name" class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-110" loading="lazy" decoding="async" />
            </div>
            <span class="mt-3 whitespace-normal break-words text-center font-semibold leading-snug text-gray-700 transition-colors group-hover:text-sky-600" :class="fitTextClass(cp.category.name)">
              {{ cp.category.name }}
            </span>
          </RouterLink>
        </div>
        <div class="mt-10 text-center">
          <RouterLink :to="localized('/shop')">
            <button class="btn btn-outline h-11 rounded-full px-8">
              {{ t.viewAllCategories }}
              <ArrowRight class="h-4 w-4" />
            </button>
          </RouterLink>
        </div>
      </section>

      <section class="reveal-section py-12 md:py-24">
        <div class="mb-12 text-center">
          <h2 class="gradient-text-heading text-3xl font-bold md:text-4xl">{{ t.mainProductsTitle }}</h2>
          <p class="mt-3 text-muted-foreground">{{ t.mainProductsSubtitle }}</p>
        </div>
        <div class="flex flex-col gap-6 md:flex-row">
          <div class="hidden w-48 shrink-0 flex-col gap-1 self-start rounded-xl border border-gray-100 bg-white/80 p-3 md:flex">
            <button
              v-for="(cp, idx) in categoryProducts"
              :key="cp.category.id"
              class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium transition-all"
              :class="activeCategory === idx ? 'bg-gradient-to-r from-sky-50 to-cyan-50 text-sky-600 shadow-sm' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'"
              @click="activeCategory = idx"
            >
              <div class="relative h-8 w-8 shrink-0 overflow-hidden rounded-md">
                <img :src="cp.category.thumbnailUrl || cp.category.image" :alt="cp.category.name" class="h-full w-full object-cover" loading="lazy" decoding="async" />
              </div>
              <span class="whitespace-normal break-words leading-snug" :class="fitTextClass(cp.category.name)">{{ cp.category.name }}</span>
            </button>
          </div>
          <div class="min-w-0 flex-1">
            <div class="scrollbar-hide mb-4 flex gap-2 overflow-x-auto pb-3 md:hidden">
              <button
                v-for="(cp, idx) in categoryProducts"
                :key="cp.category.id"
                class="shrink-0 rounded-full px-4 py-2 text-xs font-medium transition-all"
                :class="activeCategory === idx ? 'bg-sky-500 text-white shadow-sm' : 'border border-gray-200 bg-white text-gray-600'"
                @click="activeCategory = idx"
              >
                {{ cp.category.name }}
              </button>
            </div>
            <Transition name="products-tab" mode="out-in">
              <div :key="activeCategory">
                <div class="mb-4 flex items-center justify-between">
                  <h3 class="text-lg font-semibold text-gray-800">{{ currentCategory?.category.name }}</h3>
                  <RouterLink :to="localized(`/shop?category=${currentCategory?.category.slug}`)" class="flex items-center gap-1 text-sm text-sky-600 hover:text-sky-700">
                    {{ t.viewAll }}
                    <ArrowRight class="h-3.5 w-3.5" />
                  </RouterLink>
                </div>
                <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4">
                  <ProductCard v-for="product in currentCategory?.products" :key="product.id" :product="product" />
                  <div v-if="!currentCategory?.products?.length" class="col-span-full py-12 text-center text-sm text-gray-400">{{ t.noProducts }}</div>
                </div>
              </div>
            </Transition>
          </div>
        </div>
      </section>

      <section class="reveal-section py-6 md:py-12">
        <div class="relative mb-12 text-center">
          <h2 class="gradient-text-heading text-3xl font-bold md:text-4xl">{{ t.newArrivalsTitle }}</h2>
          <p class="mt-3 text-muted-foreground">{{ t.newArrivalsSubtitle }}</p>
          <div v-if="newProducts.length" class="mt-5 flex justify-center gap-3 md:absolute md:top-1/2 md:right-0 md:mt-0 md:-translate-y-1/2">
            <button
              type="button"
              class="flex h-10 w-10 items-center justify-center rounded-full border border-gray-200 bg-white text-gray-600 shadow-sm transition-all hover:-translate-y-0.5 hover:border-teal-300 hover:text-teal-600 hover:shadow-md disabled:pointer-events-none disabled:opacity-35"
              :aria-label="t.prevSlide"
              :disabled="railAtStart"
              @click="scrollNewRail(-1)"
            >
              <ChevronLeft class="h-5 w-5" />
            </button>
            <button
              type="button"
              class="flex h-10 w-10 items-center justify-center rounded-full border border-gray-200 bg-white text-gray-600 shadow-sm transition-all hover:-translate-y-0.5 hover:border-teal-300 hover:text-teal-600 hover:shadow-md disabled:pointer-events-none disabled:opacity-35"
              :aria-label="t.nextSlide"
              :disabled="railAtEnd"
              @click="scrollNewRail(1)"
            >
              <ChevronRight class="h-5 w-5" />
            </button>
          </div>
        </div>
        <div ref="newRailRef" class="new-arrivals-rail scrollbar-hide flex gap-4 overflow-x-auto overscroll-x-contain pb-4" style="scroll-snap-type: x mandatory; scroll-behavior: smooth" @scroll="updateRailProgress">
          <div v-for="product in newProducts" :key="product.id" class="w-[260px] flex-shrink-0 md:w-[280px]" style="scroll-snap-align: start">
            <ProductCard :product="{ ...product, isNew: true }" />
          </div>
        </div>
        <div class="mx-auto mt-4 h-1 max-w-xs rounded-full bg-gray-200">
          <div class="h-full rounded-full bg-gradient-to-r from-teal-400 to-cyan-500 transition-[width] duration-150" :style="{ width: `${Math.max(railProgress * 100, 2)}%` }"></div>
        </div>
      </section>

      <section class="reveal-section py-10 md:py-20">
        <div class="mb-12 text-center">
          <h2 class="gradient-text-heading text-3xl font-bold md:text-4xl">{{ t.certTitle }}</h2>
          <p class="mt-3 text-muted-foreground">{{ t.certSubtitle }}</p>
        </div>
        <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
          <button v-for="idx in 12" :key="idx" class="group cursor-pointer text-left" @click="selectedCert = idx">
            <div class="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm transition-all duration-300 group-hover:-translate-y-1 group-hover:shadow-lg">
              <div class="relative aspect-[3/4]">
                <img :src="`/images/certs/cert-${idx}.webp`" :alt="`${t.cert} ${idx}`" class="h-full w-full object-cover" />
              </div>
            </div>
            <p class="mt-2 text-center text-xs font-medium text-gray-600 transition-colors group-hover:text-sky-600">{{ t.cert }} {{ idx }}</p>
          </button>
        </div>
      </section>

      <section id="about" class="reveal-section py-10 md:py-20">
        <div class="mb-6 text-center">
          <h2 class="gradient-text-heading text-3xl font-bold md:text-4xl">{{ t.techTitle }}</h2>
        </div>
        <div class="mx-auto mb-12 max-w-3xl space-y-3 text-center leading-relaxed text-muted-foreground">
          <p>{{ t.techIntro1 }}</p>
          <p>{{ t.techIntro2 }}</p>
        </div>
        <div class="mb-16 grid grid-cols-3 gap-4 rounded-2xl bg-gradient-to-r from-sky-500 to-cyan-500 p-6 text-center text-white md:grid-cols-6">
          <div v-for="stat in techStats" :key="stat.label">
            <div class="text-xl font-bold md:text-2xl">{{ stat.value }}</div>
            <div class="mt-1 text-xs text-white/80">{{ stat.label }}</div>
          </div>
        </div>
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <article v-for="card in techCards" :key="card.title" class="group rounded-2xl border border-gray-100 bg-white p-6 transition-shadow duration-300 hover:shadow-lg">
            <div class="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br" :class="card.color">
              <component :is="card.icon" class="h-5 w-5 text-white" />
            </div>
            <h3 class="mb-2 text-lg font-semibold text-gray-900">{{ card.title }}</h3>
            <p class="text-sm leading-relaxed text-muted-foreground">{{ card.desc }}</p>
          </article>
        </div>
      </section>

      <section class="reveal-section py-12 md:py-24">
        <div class="mb-16 text-center">
          <h2 class="gradient-text-heading mb-4 text-3xl font-bold md:text-4xl">{{ t.serviceTitle }}</h2>
          <p class="mx-auto max-w-2xl text-lg text-gray-500">{{ t.serviceSubtitle }}</p>
        </div>
        <div class="space-y-12 md:space-y-20">
          <div v-for="(step, idx) in serviceSteps" :key="step.title" class="service-row grid grid-cols-1 items-center gap-8 md:grid-cols-[1fr_1.618fr] md:gap-12">
            <div class="relative aspect-[4/3] overflow-hidden rounded-2xl bg-gray-100" :class="idx % 2 === 1 ? 'md:order-2' : 'md:order-1'">
              <img :src="step.image" :alt="step.title" class="h-full w-full object-cover transition-transform duration-500 hover:scale-105" />
            </div>
            <div class="flex flex-col justify-center" :class="idx % 2 === 1 ? 'md:order-1 md:text-right' : 'md:order-2'">
              <span class="gradient-text mb-2 text-5xl font-bold">{{ String(idx + 1).padStart(2, '0') }}</span>
              <h3 class="mb-3 text-2xl font-bold text-gray-900 md:text-3xl">{{ step.title }}</h3>
              <p class="text-lg leading-relaxed text-gray-500">{{ step.desc }}</p>
            </div>
          </div>
        </div>
        <div class="mt-12 text-center md:mt-16">
          <RouterLink :to="localized('/service')">
            <button class="btn gradient-bg h-11 rounded-full px-10 text-white">{{ t.learnMore }}</button>
          </RouterLink>
        </div>
      </section>

      <section class="reveal-section py-10">
        <div class="group relative overflow-hidden rounded-[2rem] shadow-[0_0_50px_rgba(20,184,166,0.35)] transition-shadow duration-500 hover:shadow-[0_0_70px_rgba(20,184,166,0.55)]">
          <div class="relative h-[300px] md:h-[400px]">
            <img src="/images/service/manufacturing.jpg" :alt="t.promoTitle" class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105" />
            <div class="absolute inset-0 bg-gradient-to-r from-black/60 to-transparent"></div>
            <div class="absolute inset-0 flex items-center">
              <div class="px-8 md:px-16">
                <h2 class="promo-reveal mb-3 text-3xl font-bold text-white md:text-5xl">{{ t.promoTitle }}</h2>
                <p class="promo-reveal mb-6 max-w-md text-base text-white/80 md:text-lg">{{ t.promoSubtitle }}</p>
                <RouterLink :to="localized('/shop?filter=sale')" class="promo-reveal inline-flex">
                  <button class="btn rounded-full border-0 bg-gradient-to-r from-teal-500 to-cyan-500 px-8 py-3 font-medium text-white shadow-lg shadow-teal-500/25 hover:from-teal-600 hover:to-cyan-600">{{ t.promoCta }}</button>
                </RouterLink>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <div class="mx-auto max-w-[1400px] px-6 sm:px-10 lg:px-16">
      <section class="reveal-section py-10 md:py-20">
        <div class="mb-12 text-center">
          <h2 class="gradient-text-heading text-3xl font-bold md:text-4xl">{{ t.testimonialTitle }}</h2>
          <p class="mt-3 text-muted-foreground">{{ t.testimonialSubtitle }}</p>
        </div>
        <div class="grid grid-cols-1 gap-5 md:grid-cols-3">
          <article v-for="item in testimonials" :key="item.name" class="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg">
            <div class="mb-3 flex text-amber-400">
              <Star v-for="idx in item.rating" :key="idx" class="h-4 w-4 fill-amber-400" />
            </div>
            <p class="mb-4 text-sm leading-relaxed text-muted-foreground">"{{ item.comment }}"</p>
            <strong class="block text-gray-900">{{ item.name }}</strong>
            <span class="text-xs text-sky-600">{{ item.product }}</span>
          </article>
        </div>
      </section>

      <section class="reveal-section py-10 md:py-20">
        <div class="mb-12 text-center">
          <h2 class="gradient-text-heading text-3xl font-bold md:text-4xl">{{ t.faqTitle }}</h2>
          <p class="mt-3 text-muted-foreground">{{ t.faqSubtitle }}</p>
        </div>
        <div class="mx-auto max-w-3xl space-y-3">
          <details v-for="faq in faqs" :key="faq.q" class="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
            <summary class="cursor-pointer font-semibold text-gray-900">{{ faq.q }}</summary>
            <p class="mt-3 leading-relaxed text-muted-foreground">{{ faq.a }}</p>
          </details>
        </div>
      </section>
    </div>

    <Transition name="fade">
      <div v-if="selectedCert" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm" @click="selectedCert = null">
        <div class="relative max-h-[85vh] w-full max-w-[600px]" @click.stop>
          <button class="absolute -top-3 -right-3 z-10 flex h-8 w-8 items-center justify-center rounded-full bg-white shadow-lg transition-colors hover:bg-gray-100" @click="selectedCert = null">
            <X class="h-4 w-4" />
          </button>
          <div class="overflow-hidden rounded-xl bg-white shadow-2xl">
            <div class="relative aspect-[3/4]">
              <img :src="`/images/certs/cert-${selectedCert}.webp`" :alt="`${t.cert} ${selectedCert}`" class="h-full w-full object-contain" />
            </div>
            <div class="p-3 text-center text-sm font-medium text-gray-700">{{ t.cert }} {{ selectedCert }}</div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import {
  ArrowRight,
  Battery,
  ChevronLeft,
  ChevronRight,
  Cpu,
  Flame,
  Globe,
  Play,
  Shield,
  ShoppingBag,
  Star,
  Wifi,
  Award,
  Zap,
  X
} from 'lucide-vue-next'

import { getHomeData } from '@/api'
import ProductCard from '@/components/ProductCard.vue'
import { loadLocaleMessages, translatedCopy } from '@/i18n'

gsap.registerPlugin(ScrollTrigger)

const route = useRoute()
const pageRef = ref(null)
const newRailRef = ref(null)
const banners = ref([])
const categoryProducts = ref([])
const newProducts = ref([])
const slideIndex = ref(0)
const direction = ref(1)
const activeCategory = ref(0)
const railProgress = ref(0)
const railAtStart = ref(true)
const railAtEnd = ref(true)
const selectedCert = ref(null)
let timer
let ctx
let railProgressRaf = 0

const locale = computed(() => route.params.locale || 'en')
const t = computed(() => translatedCopy(locale.value, copy, source => source.home || {}))
const activeSlide = computed(() => banners.value[slideIndex.value] || fallbackBanners.value[0])
const currentCategory = computed(() => categoryProducts.value[activeCategory.value])
const fallbackBanners = computed(() => [
  { title: t.value.bannerTitle1, subtitle: t.value.bannerSubtitle1, buttonText: t.value.bannerCta1, image: '/images/hero-banner.png' },
  { title: t.value.bannerTitle2, subtitle: t.value.bannerSubtitle2, buttonText: t.value.bannerCta2, image: '/images/banner-1.png' },
  { title: t.value.bannerTitle3, subtitle: t.value.bannerSubtitle3, buttonText: t.value.bannerCta3, image: '/images/banner-2.png' }
])
const heroStatsForSlide = computed(() => statsSet.value[slideIndex.value % statsSet.value.length])
const statsSet = computed(() => [
  [
    { value: '30+', label: t.value.statYears },
    { value: '500+', label: t.value.statModels }
  ],
  [
    { value: '50+', label: t.value.statCountries },
    { value: '24h', label: t.value.statResponse }
  ],
  [
    { value: '12', label: t.value.statCerts },
    { value: '100%', label: t.value.statQc }
  ]
])
const techStats = computed(() => [
  { value: '30+', label: t.value.statYears },
  { value: '500+', label: t.value.statModels },
  { value: '50+', label: t.value.statCountries },
  { value: '24h', label: t.value.statResponse },
  { value: '12', label: t.value.statCerts },
  { value: '100%', label: t.value.statQc }
])
const techCards = computed(() => [
  { icon: Zap, color: 'from-amber-400 to-orange-500', title: t.value.tech1, desc: t.value.tech1Desc },
  { icon: Shield, color: 'from-blue-400 to-indigo-500', title: t.value.tech2, desc: t.value.tech2Desc },
  { icon: Globe, color: 'from-teal-400 to-cyan-500', title: t.value.tech3, desc: t.value.tech3Desc },
  { icon: Cpu, color: 'from-violet-400 to-purple-500', title: t.value.tech4, desc: t.value.tech4Desc },
  { icon: Wifi, color: 'from-sky-400 to-blue-500', title: t.value.tech5, desc: t.value.tech5Desc },
  { icon: Battery, color: 'from-green-400 to-emerald-500', title: t.value.tech6, desc: t.value.tech6Desc },
  { icon: Flame, color: 'from-red-400 to-rose-500', title: t.value.tech7, desc: t.value.tech7Desc },
  { icon: Award, color: 'from-pink-400 to-fuchsia-500', title: t.value.tech8, desc: t.value.tech8Desc }
])
const serviceSteps = computed(() => [
  { title: t.value.serviceStep1Title, desc: t.value.serviceStep1Desc, image: '/images/service/customer-service.jpg' },
  { title: t.value.serviceStep2Title, desc: t.value.serviceStep2Desc, image: '/images/service/pricing-quote.jpg' },
  { title: t.value.serviceStep3Title, desc: t.value.serviceStep3Desc, image: '/images/service/manufacturing.jpg' },
  { title: t.value.serviceStep4Title, desc: t.value.serviceStep4Desc, image: '/images/service/logistics.jpg' },
  { title: t.value.serviceStep5Title, desc: t.value.serviceStep5Desc, image: '/images/service/aftersales.jpg' }
])
const testimonials = computed(() => [
  { name: 'Sarah Johnson', rating: 5, product: 'Industrial Drum Fan', comment: t.value.testimonial1 },
  { name: 'Michael Chen', rating: 5, product: 'Portable Air Conditioner', comment: t.value.testimonial2 },
  { name: 'Amina Roberts', rating: 4, product: 'Air Curtain', comment: t.value.testimonial3 }
])
const faqs = computed(() => [
  { q: t.value.faq1Q, a: t.value.faq1A },
  { q: t.value.faq2Q, a: t.value.faq2A },
  { q: t.value.faq3Q, a: t.value.faq3A },
  { q: t.value.faq4Q, a: t.value.faq4A }
])

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

function fitTextClass(value) {
  const length = Array.from(String(value || '')).length
  if (length >= 40) return 'text-[10px]'
  if (length >= 28) return 'text-[11px]'
  if (length >= 18) return 'text-xs'
  return 'text-sm'
}

function paginate(delta) {
  if (banners.value.length <= 1) return
  direction.value = delta
  slideIndex.value = (slideIndex.value + delta + banners.value.length) % banners.value.length
}

function goTo(index) {
  direction.value = index > slideIndex.value ? 1 : -1
  slideIndex.value = index
}

function updateRailProgress() {
  if (railProgressRaf) return
  railProgressRaf = window.requestAnimationFrame(() => {
    railProgressRaf = 0
    const el = newRailRef.value
    if (!el) return
    const max = el.scrollWidth - el.clientWidth
    const current = Math.max(0, Math.min(max, el.scrollLeft))
    railProgress.value = max > 0 ? current / max : 0
    railAtStart.value = max <= 0 || current <= 2
    railAtEnd.value = max <= 0 || current >= max - 2
  })
}

function scrollNewRail(delta) {
  const el = newRailRef.value
  if (!el) return
  const max = Math.max(0, el.scrollWidth - el.clientWidth)
  if (max <= 0) return
  const step = Math.max(260, el.clientWidth * 0.85)
  const nextLeft = Math.max(0, Math.min(max, el.scrollLeft + step * delta))
  el.scrollTo({ left: nextLeft, behavior: 'smooth' })
  window.setTimeout(updateRailProgress, 320)
}

function localizedBannerCopy(banner, index, targetLocale) {
  const fallback = fallbackBanners.value[index % fallbackBanners.value.length]
  const rows = Array.isArray(banner.translations) ? banner.translations : null
  const row = rows?.find(item => item.locale === targetLocale)
  const englishRow = rows?.find(item => item.locale === 'en')
  const source = row || englishRow
  const fallbackTitle = englishRow?.title || banner.title || fallback.title
  const fallbackSubtitle = englishRow?.subtitle || banner.subtitle || fallback.subtitle
  const fallbackButton = englishRow?.buttonText || banner.buttonText || fallback.buttonText
  if (source && (source.title || source.subtitle || source.buttonText)) {
    return {
      title: source.title || fallbackTitle,
      subtitle: source.subtitle || fallbackSubtitle,
      buttonText: source.buttonText || fallbackButton
    }
  }
  return {
    title: fallbackTitle,
    subtitle: fallbackSubtitle,
    buttonText: fallbackButton
  }
}

function runAnimations() {
  ctx?.revert()
  ctx = gsap.context(() => {
    gsap.utils.toArray('.reveal-section').forEach(section => {
      gsap.from(section, {
        autoAlpha: 0,
        y: 24,
        duration: 0.45,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: section,
          start: 'top 86%',
          once: true
        }
      })
    })
    gsap.utils.toArray('.service-row').forEach((row, index) => {
      gsap.from(row, {
        autoAlpha: 0,
        x: index % 2 ? 36 : -36,
        duration: 0.45,
        ease: 'power2.out',
        scrollTrigger: { trigger: row, start: 'top 82%', once: true }
      })
    })
  }, pageRef.value)
}

async function loadHomeContent(targetLocale = locale.value) {
  try {
    const data = await getHomeData(targetLocale)
    if (targetLocale !== locale.value) return
    banners.value = (data.banners || []).map((banner, idx) => ({
      ...banner,
      ...localizedBannerCopy(banner, idx, targetLocale)
    }))
    categoryProducts.value = data.categoryProducts || []
    newProducts.value = data.newProducts || []
  } catch {
    if (targetLocale !== locale.value) return
    banners.value = fallbackBanners.value
    categoryProducts.value = []
    newProducts.value = []
  }
  if (!banners.value.length) banners.value = fallbackBanners.value
  slideIndex.value = Math.min(slideIndex.value, Math.max(0, banners.value.length - 1))
  activeCategory.value = Math.min(activeCategory.value, Math.max(0, categoryProducts.value.length - 1))
  await nextTick()
  if (newRailRef.value) newRailRef.value.scrollLeft = 0
  updateRailProgress()
  ScrollTrigger.refresh()
}

watch(slideIndex, () => {
  nextTick(() => {
    if (window.scrollY > window.innerHeight * 0.8) return
    gsap.fromTo(
      pageRef.value?.querySelectorAll('.hero-reveal'),
      { autoAlpha: 0, y: 24 },
      { autoAlpha: 1, y: 0, stagger: 0.12, duration: 0.55, ease: 'power2.out' }
    )
    gsap.fromTo(
      pageRef.value?.querySelector('.hero-image-reveal'),
      { autoAlpha: 0, scale: 0.9 },
      { autoAlpha: 1, scale: 1, duration: 0.7, ease: 'power2.out' }
    )
  })
})

watch(locale, async target => {
  await loadLocaleMessages(target).catch(() => {})
  await loadHomeContent(target)
})

onMounted(async () => {
  await loadLocaleMessages(locale.value).catch(() => {})
  await loadHomeContent(locale.value)
  timer = window.setInterval(() => paginate(1), 6000)
  await nextTick()
  runAnimations()
  window.addEventListener('resize', updateRailProgress, { passive: true })
})

onUnmounted(() => {
  window.clearInterval(timer)
  window.removeEventListener('resize', updateRailProgress)
  ctx?.revert()
  if (railProgressRaf) window.cancelAnimationFrame(railProgressRaf)
})

const copy = {
  en: {
    bannerTag: 'MISICHENG Professional Smart Power Solutions',
    bannerTitle1: 'Whole-Home Power, All at Once',
    bannerSubtitle1: 'Smart power strips, USB-C fast charging, independent controls and remote connectivity for a cleaner, more efficient home and office.',
    bannerCta1: 'Shop Now',
    bannerTitle2: 'Fast Charging & Safety, No Compromise',
    bannerSubtitle2: 'GaN high-efficiency fast charging with multi-layer protection for phones, tablets, laptops and small appliances.',
    bannerCta2: 'Explore Now',
    bannerTitle3: 'Professional Power Protection',
    bannerSubtitle3: 'Surge defense, overload protection, and flame-retardant housing safeguard valuable devices around the clock.',
    bannerCta3: 'View Solutions',
    shopNow: 'Shop Now',
    learnMore: 'Learn More',
    prevSlide: 'Previous slide',
    nextSlide: 'Next slide',
    goToSlide: 'Go to slide',
    categoryTitle: 'Shop by Product Category',
    categorySubtitle: 'Choose EU, UK, US, AU, China, India and other plug standards for your target market.',
    viewAllCategories: 'View all categories',
    mainProductsTitle: 'Our Main Products',
    mainProductsSubtitle: 'Browse smart power strips, GaN charging stations, surge protectors, travel adapters, and desktop power hubs.',
    viewAll: 'View all',
    noProducts: 'No products yet',
    newArrivalsTitle: 'New Arrivals',
    newArrivalsSubtitle: 'Latest smart power, fast charging, surge protection and travel adapter products.',
    certTitle: 'Certified Quality',
    certSubtitle: 'Inspection, compliance, and export-ready documentation for global buyers.',
    cert: 'Certificate',
    techTitle: 'Built for Safer Power',
    techIntro1: 'Misicheng focuses on smart power strips, USB-C fast charging, travel adapters and surge protection for global markets.',
    techIntro2: 'Each product family is designed around electrical safety, durable materials, efficient sourcing, and B2B customization needs.',
    statYears: 'Years',
    statModels: 'Models',
    statCountries: 'Countries',
    statResponse: 'Response',
    statCerts: 'Certs',
    statQc: 'QC',
    tech1: 'Fast Charging',
    tech1Desc: 'USB-C PD and GaN charging options for phones, tablets, laptops and desktop devices.',
    tech2: 'Safety Protection',
    tech2Desc: 'Surge, overload, grounding, flame-retardant material and child-safety options by model.',
    tech3: 'Category Coverage',
    tech3Desc: 'Regional plug standards, smart strips, travel adapters, desktop hubs and surge protectors.',
    tech4: 'Control Options',
    tech4Desc: 'Master switch, individual switch, WiFi app control and OEM functional options by model.',
    tech5: 'Use Scenarios',
    tech5Desc: 'Designed for homes, offices, desks, travel, retail shelves and distributor product lines.',
    tech6: 'Stable Output',
    tech6Desc: 'Stable conductive parts, cable choices and shell structure for repeated daily use.',
    tech7: 'Market Matching',
    tech7Desc: 'EU, UK, US, AU, China, India, Brazil and Argentina standards for regional demand.',
    tech8: 'Documentation',
    tech8Desc: 'Export-ready documentation and certification support.',
    serviceTitle: 'One-stop B2B Service',
    serviceSubtitle: 'From sample consultation to after-sales support, every step has a clear owner.',
    serviceStep1Title: 'Customer Consultation',
    serviceStep1Desc: 'Confirm market, product category, sample quantity, certification, and packaging needs.',
    serviceStep2Title: 'Pricing Quote',
    serviceStep2Desc: 'Prepare product, customization, carton packing, and shipping quotation.',
    serviceStep3Title: 'Manufacturing',
    serviceStep3Desc: 'Track production progress and key quality checkpoints before shipment.',
    serviceStep4Title: 'Logistics',
    serviceStep4Desc: 'Compare express, air, sea, and consolidated freight by timeline and cost.',
    serviceStep5Title: 'After-sales',
    serviceStep5Desc: 'Keep order records, feedback, and replacement follow-up traceable.',
    promoTitle: 'B2B Smart Power Products Ready to Quote',
    promoSubtitle: 'Browse power strips, adapters, GaN charging and surge protection products, then submit a combined inquiry for fast quotation.',
    promoCta: 'View Offers',
    testimonialTitle: 'Trusted by Global Buyers',
    testimonialSubtitle: 'Real purchasing scenarios from smart power and charging product buyers.',
    testimonial1: 'The samples matched our target category mix and packaging requirements.',
    testimonial2: 'Quotation was clear and the production updates were easy to follow.',
    testimonial3: 'Good fit for power strip and adapter sourcing across multiple markets.',
    faqTitle: 'Frequently Asked Questions',
    faqSubtitle: 'Common details buyers ask before sample orders and bulk purchasing.',
    faq1Q: 'Can I request samples before bulk purchase?',
    faq1A: 'Yes. Submit an inquiry with target models and quantity, and sales will confirm sample terms.',
    faq2Q: 'Do products support custom packaging?',
    faq2A: 'Yes. OEM packaging and labeling can be quoted after artwork and order volume are confirmed.',
    faq3Q: 'Which certifications are available?',
    faq3A: 'Common documentation includes CE, RoHS, and product-specific test reports depending on model.',
    faq4Q: 'How fast do you respond to inquiries?',
    faq4A: 'Most inquiries receive a first response within one business day.'
  },
  zh: {
    bannerTag: 'MISICHENG 专业智能电力方案',
    bannerTitle1: '全屋供电，一次到位',
    bannerSubtitle1: '智能排插、USB-C 快充、独立分控与远程联动，让家庭与办公桌面更整洁、更高效。',
    bannerCta1: '立即选购',
    bannerTitle2: '快充与安全，不再二选一',
    bannerSubtitle2: 'GaN 高效快充搭配多重防护设计，为手机、平板、笔记本和小家电提供稳定电力支持。',
    bannerCta2: '立即探索',
    bannerTitle3: '专业级用电保护',
    bannerSubtitle3: '从浪涌防护到过载保护，从阻燃外壳到精密结构，为关键设备提供持续稳定的电力保障。',
    bannerCta3: '查看方案',
    shopNow: '立即选购',
    learnMore: '了解更多',
    prevSlide: '上一张',
    nextSlide: '下一张',
    goToSlide: '跳转到轮播',
    categoryTitle: '按产品分类选购',
    categorySubtitle: '按目标市场选择欧规、英规、美规、澳规、中规、印度规等插头标准。',
    viewAllCategories: '查看全部分类',
    mainProductsTitle: '主要产品',
    mainProductsSubtitle: '浏览智能排插、GaN 快充站、浪涌保护排插、旅行转换器和桌面电源集线器。',
    viewAll: '查看全部',
    noProducts: '暂无商品',
    newArrivalsTitle: '新品上市',
    newArrivalsSubtitle: '最新智能供电、快充、浪涌保护和旅行转换产品。',
    certTitle: '认证品质',
    certSubtitle: '为全球买家准备检验、合规和出口资料。',
    cert: '证书',
    techTitle: '为安全供电而设计',
    techIntro1: 'Misicheng 聚焦全球市场所需的智能排插、USB-C 快充、旅行转换器和浪涌保护产品。',
    techIntro2: '每个产品系列都围绕用电安全、耐用材料、高效采购和 B2B 定制需求设计。',
    statYears: '行业经验',
    statModels: '产品型号',
    statCountries: '覆盖国家',
    statResponse: '响应时间',
    statCerts: '认证资料',
    statQc: '质检覆盖',
    tech1: '快充方案',
    tech1Desc: 'USB-C PD 与 GaN 快充选项，适配手机、平板、笔记本和桌面设备。',
    tech2: '安全防护',
    tech2Desc: '按型号提供浪涌、过载、接地、阻燃材料和儿童保护门选项。',
    tech3: '品类覆盖',
    tech3Desc: '覆盖区域插头标准、智能排插、旅行转换器、桌面电源和浪涌保护产品。',
    tech4: '控制方式',
    tech4Desc: '按型号提供总控、单控、WiFi APP 控制和 OEM 功能定制。',
    tech5: '使用场景',
    tech5Desc: '适合家庭、办公室、桌面、出差旅行、零售货架和经销商产品线。',
    tech6: '稳定输出',
    tech6Desc: '稳定导电件、线材选择和外壳结构，适合日常重复使用。',
    tech7: '市场匹配',
    tech7Desc: '欧规、英规、美规、澳规、中规、印度规、巴西规和阿根廷规匹配区域需求。',
    tech8: '资料支持',
    tech8Desc: '提供出口资料和认证支持。',
    serviceTitle: '一站式 B2B 服务',
    serviceSubtitle: '从样品咨询到售后支持，每一步都有清晰负责人。',
    serviceStep1Title: '客户咨询',
    serviceStep1Desc: '确认市场、产品分类、样品数量、认证和包装需求。',
    serviceStep2Title: '价格报价',
    serviceStep2Desc: '整理产品、定制、外箱包装和物流报价。',
    serviceStep3Title: '生产制造',
    serviceStep3Desc: '发货前跟进生产进度和关键质检节点。',
    serviceStep4Title: '物流交付',
    serviceStep4Desc: '按时间和成本对比快递、空运、海运和集货。',
    serviceStep5Title: '售后支持',
    serviceStep5Desc: '保留订单、反馈和补件跟进记录。',
    promoTitle: 'B2B 智能电力产品可快速报价',
    promoSubtitle: '浏览排插、转换器、GaN 快充和浪涌保护产品，提交组合询盘快速报价。',
    promoCta: '查看优惠',
    testimonialTitle: '全球买家信赖',
    testimonialSubtitle: '来自智能电力与充电产品采购场景的真实反馈。',
    testimonial1: '样品符合目标品类组合和包装要求。',
    testimonial2: '报价清晰，生产进度更新也很容易跟进。',
    testimonial3: '适合多个市场的排插和转换器采购。',
    faqTitle: '常见问题',
    faqSubtitle: '样品和批量采购前，客户经常确认的细节。',
    faq1Q: '批量采购前可以申请样品吗？',
    faq1A: '可以。提交目标型号和数量后，销售会确认样品条款。',
    faq2Q: '是否支持定制包装？',
    faq2A: '支持。确认设计稿和订单量后可提供 OEM 包装报价。',
    faq3Q: '可以提供哪些认证资料？',
    faq3A: '常见资料包括 CE、RoHS 和对应产品测试报告，具体按型号确认。',
    faq4Q: '询盘多久回复？',
    faq4A: '大多数询盘会在一个工作日内收到首次回复。'
  }
}
</script>

<style scoped>
.new-arrivals-rail {
  overscroll-behavior-x: contain;
  overscroll-behavior-y: auto;
  touch-action: pan-y;
  will-change: scroll-position;
}

.hero-next-enter-active,
.hero-next-leave-active,
.hero-prev-enter-active,
.hero-prev-leave-active {
  transition: all 0.55s ease;
}

.hero-next-enter-from {
  opacity: 0;
  transform: translateX(300px) scale(0.92);
  filter: blur(8px);
}

.hero-next-leave-to {
  opacity: 0;
  transform: translateX(-300px) scale(0.95);
  filter: blur(4px);
}

.hero-prev-enter-from {
  opacity: 0;
  transform: translateX(-300px) scale(0.92);
  filter: blur(8px);
}

.hero-prev-leave-to {
  opacity: 0;
  transform: translateX(300px) scale(0.95);
  filter: blur(4px);
}

.products-tab-enter-active,
.products-tab-leave-active {
  transition: all 0.2s ease;
}

.products-tab-enter-from {
  opacity: 0;
  transform: translateX(10px);
}

.products-tab-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
