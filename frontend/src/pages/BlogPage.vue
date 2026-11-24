<template>
  <div class="mx-auto max-w-7xl px-4 pt-24 py-12 lg:px-8">
    <nav class="mb-8 flex items-center gap-2 text-sm text-muted-foreground">
      <RouterLink :to="localized('/')" class="transition-colors hover:text-foreground">{{ t.home }}</RouterLink>
      <ChevronRight class="h-3.5 w-3.5" />
      <span class="font-medium text-foreground">{{ t.breadcrumb }}</span>
    </nav>

    <div class="mb-12 text-center">
      <h1 class="text-4xl font-bold tracking-tight">{{ t.title }}</h1>
      <p class="mt-4 text-lg text-muted-foreground">{{ t.subtitle }}</p>
    </div>

    <div class="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
      <article
        v-for="post in posts"
        :key="post.title"
        class="group flex flex-col overflow-hidden rounded-xl border transition-shadow hover:shadow-lg"
      >
        <div class="flex h-48 items-center justify-center overflow-hidden bg-gray-50">
          <img
            :src="post.image"
            :alt="post.title"
            class="h-full w-full object-contain p-4 transition-transform duration-300 group-hover:scale-105"
          />
        </div>
        <div class="flex flex-1 flex-col p-6">
          <div class="mb-3 flex items-center gap-3">
            <span class="inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium" :class="post.badgeClass">
              {{ post.category }}
            </span>
          </div>
          <h2 class="mb-2 text-lg font-semibold leading-tight group-hover:text-primary">{{ post.title }}</h2>
          <p class="mb-4 flex-1 whitespace-normal break-words text-sm leading-6 text-muted-foreground">{{ post.excerpt }}</p>
          <div class="flex items-center justify-between text-xs text-muted-foreground">
            <div class="flex items-center gap-1">
              <CalendarDays class="h-3.5 w-3.5" />
              <span>{{ post.date }}</span>
            </div>
            <div class="flex items-center gap-1">
              <Clock class="h-3.5 w-3.5" />
              <span>{{ post.readTime }}</span>
            </div>
          </div>
        </div>
      </article>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { CalendarDays, ChevronRight, Clock } from 'lucide-vue-next'

import { translatedCopy } from '@/i18n'

const route = useRoute()
const locale = computed(() => route.params.locale || 'en')
const t = computed(() => translatedCopy(locale.value, {}, source => ({
  home: source.common?.home || 'Home',
  ...(source.blog || {})
})))

const postMeta = [
  { image: '/images/products/product-1.png', date: '2026-07-15', categoryKey: 'categoryGuide', badgeClass: 'bg-blue-100 text-blue-800' },
  { image: '/images/products/product-2.png', date: '2026-07-03', categoryKey: 'categoryTech', badgeClass: 'bg-purple-100 text-purple-800' },
  { image: '/images/products/product-3.png', date: '2026-06-20', categoryKey: 'categorySafety', badgeClass: 'bg-red-100 text-red-800' },
  { image: '/images/products/product-4.png', date: '2026-06-08', categoryKey: 'categoryTech', badgeClass: 'bg-purple-100 text-purple-800' },
  { image: '/images/products/product-5.png', date: '2026-05-26', categoryKey: 'categoryTips', badgeClass: 'bg-green-100 text-green-800' },
  { image: '/images/products/product-6.png', date: '2026-05-12', categoryKey: 'categoryGuide', badgeClass: 'bg-blue-100 text-blue-800' }
]

const posts = computed(() => postMeta.map((meta, index) => {
  const number = index + 1
  return {
    ...meta,
    title: t.value[`post${number}Title`],
    excerpt: t.value[`post${number}Excerpt`],
    category: t.value[meta.categoryKey],
    readTime: t.value[`readTime${number}`]
  }
}))

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}
</script>
