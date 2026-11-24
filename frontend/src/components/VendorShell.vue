<template>
  <div class="flex h-screen overflow-hidden bg-muted/30">
    <aside class="hidden w-64 shrink-0 flex-col border-r bg-background lg:flex">
      <div class="flex h-14 items-center border-b px-4 font-semibold">{{ t.portalTitle }}</div>
      <nav class="flex-1 overflow-y-auto p-3">
        <RouterLink
          v-for="item in navItems"
          :key="item.href"
          :to="localized(item.href)"
          class="mb-1 flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
          :class="isActive(item.href) ? 'bg-blue-600 text-white' : 'text-muted-foreground hover:bg-blue-50 hover:text-foreground'"
        >
          <component :is="item.icon" class="h-4 w-4 shrink-0" />
          {{ item.label }}
        </RouterLink>
      </nav>
      <div class="space-y-1 border-t p-3">
        <div class="relative">
          <button
            type="button"
            class="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            @click="localeOpen = !localeOpen"
          >
            <Globe class="h-4 w-4 shrink-0" />
            <span class="flex-1 min-w-0 whitespace-nowrap text-left" :class="fitTextClass(currentLocale.name)">{{ currentLocale.flag }} {{ currentLocale.name }}</span>
            <ChevronDown class="h-3 w-3" />
          </button>
          <div v-if="localeOpen" class="absolute bottom-full left-0 mb-2 w-52 rounded-xl border bg-background p-1 shadow-lg">
            <button
              v-for="item in localeOptions"
              :key="item.code"
              type="button"
              class="flex w-full items-center rounded-lg px-3 py-2 text-left text-sm transition-colors"
              :class="item.code === locale ? 'bg-blue-50 text-blue-700' : 'hover:bg-muted'"
              @click="switchLocale(item.code)"
            >
              <span class="mr-2">{{ item.flag }}</span>{{ item.name }}
            </button>
          </div>
        </div>
        <button type="button" class="btn btn-ghost h-10 w-full justify-start px-3 text-muted-foreground" @click="$emit('signout')">
          <LogOut class="h-4 w-4" />
          {{ t.signOut }}
        </button>
      </div>
    </aside>

    <div class="flex min-w-0 flex-1 flex-col overflow-hidden">
      <header class="admin-header flex h-14 shrink-0 items-center justify-between border-b bg-background px-4">
        <button type="button" class="btn btn-ghost h-10 w-10 lg:hidden" aria-label="Open menu" @click="mobileOpen = true">
          <Menu class="h-5 w-5" />
        </button>
        <div class="hidden lg:block" />
        <span class="max-w-[60vw] whitespace-nowrap text-muted-foreground" :class="fitTextClass(userLabel)">{{ userLabel }}</span>
      </header>
      <main class="flex-1 overflow-y-auto p-4 lg:p-6">
        <slot />
      </main>
    </div>

    <Transition name="fade">
      <div v-if="mobileOpen" class="fixed inset-0 z-[90] bg-black/40 lg:hidden" @click="mobileOpen = false"></div>
    </Transition>
    <Transition name="slide">
      <aside v-if="mobileOpen" class="fixed inset-y-0 left-0 z-[100] flex w-72 flex-col border-r bg-background shadow-xl lg:hidden">
        <div class="flex h-14 items-center justify-between border-b px-4">
          <span class="font-semibold">{{ t.portalTitle }}</span>
          <button type="button" class="btn btn-ghost h-9 w-9" aria-label="Close menu" @click="mobileOpen = false">
            <X class="h-4 w-4" />
          </button>
        </div>
        <nav class="flex-1 overflow-y-auto p-3">
          <RouterLink
            v-for="item in navItems"
            :key="item.href"
            :to="localized(item.href)"
            class="mb-1 flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
            :class="isActive(item.href) ? 'bg-blue-600 text-white' : 'text-muted-foreground hover:bg-blue-50 hover:text-foreground'"
            @click="mobileOpen = false"
          >
            <component :is="item.icon" class="h-4 w-4 shrink-0" />
            {{ item.label }}
          </RouterLink>
        </nav>
      </aside>
    </Transition>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { ChevronDown, ClipboardCheck, Globe, Image, LayoutDashboard, LogOut, Menu, Package, Plus, X } from 'lucide-vue-next'

import { loadLocaleMessages } from '@/i18n'

const props = defineProps({
  user: { type: Object, default: null }
})
defineEmits(['signout'])

const route = useRoute()
const router = useRouter()
const mobileOpen = ref(false)
const localeOpen = ref(false)
const locale = computed(() => route.params.locale || 'en')

const localeOptions = [
  { code: 'en', name: 'English', flag: 'EN' },
  { code: 'zh', name: '中文', flag: 'ZH' },
  { code: 'ja', name: '日本語', flag: 'JA' },
  { code: 'ko', name: '한국어', flag: 'KO' },
  { code: 'fr', name: 'Français', flag: 'FR' },
  { code: 'de', name: 'Deutsch', flag: 'DE' },
  { code: 'es', name: 'Español', flag: 'ES' },
  { code: 'ar', name: 'العربية', flag: 'AR' }
]

const t = computed(() => copy[locale.value] || copy.en)
const currentLocale = computed(() => localeOptions.find(item => item.code === locale.value) || localeOptions[0])
const userLabel = computed(() => props.user?.name || props.user?.email || t.value.vendor)
const navItems = computed(() => [
  { href: '/vendor', icon: LayoutDashboard, label: t.value.nav.overview },
  { href: '/vendor/application', icon: ClipboardCheck, label: t.value.nav.application },
  { href: '/vendor/products', icon: Package, label: t.value.nav.products },
  { href: '/vendor/products/new', icon: Plus, label: t.value.nav.newProduct },
  { href: '/vendor/media', icon: Image, label: t.value.nav.media },
  { href: '/vendor/password', icon: ClipboardCheck, label: locale.value === 'zh' ? '修改密码' : 'Change Password' }
])

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

function pathWithoutLocale() {
  return route.path.replace(/^\/(en|zh|ja|ko|fr|de|es|ar)(?=\/|$)/, '') || '/'
}

function isActive(href) {
  const current = pathWithoutLocale()
  if (href === '/vendor') return current === '/vendor'
  return current === href || current.startsWith(`${href}/`)
}

function fitTextClass(value) {
  const length = Array.from(value || '').length
  if (length >= 34) return 'text-[10px]'
  if (length >= 24) return 'text-[11px]'
  return 'text-sm'
}

function switchLocale(target) {
  const rest = route.fullPath.replace(/^\/(en|zh|ja|ko|fr|de|es|ar)(?=\/|$)/, '') || ''
  localeOpen.value = false
  router.push(`/${target}${rest}`)
}

watch(locale, target => {
  loadLocaleMessages(target).catch(() => {})
}, { immediate: true })

const copy = {
  en: {
    portalTitle: 'Vendor Portal',
    vendor: 'Vendor',
    signOut: 'Sign out',
    nav: {
      overview: 'Overview',
      application: 'Application',
      products: 'Products',
      newProduct: 'New Product',
      media: 'Media'
    }
  },
  zh: {
    portalTitle: '商家中心',
    vendor: '商家',
    signOut: '退出登录',
    nav: {
      overview: '概览',
      application: '入驻申请',
      products: '商品管理',
      newProduct: '发布商品',
      media: '媒体库'
    }
  },
  ja: {
    portalTitle: '出店者ポータル',
    vendor: '出店者',
    signOut: 'ログアウト',
    nav: {
      overview: '概要',
      application: '出店申請',
      products: '商品',
      newProduct: '新規商品',
      media: 'メディア'
    }
  },
  ko: {
    portalTitle: '판매자 포털',
    vendor: '판매자',
    signOut: '로그아웃',
    nav: {
      overview: '개요',
      application: '입점 신청',
      products: '상품',
      newProduct: '새 상품',
      media: '미디어'
    }
  },
  fr: {
    portalTitle: 'Portail vendeur',
    vendor: 'Vendeur',
    signOut: 'Déconnexion',
    nav: {
      overview: 'Aperçu',
      application: 'Candidature',
      products: 'Produits',
      newProduct: 'Nouveau produit',
      media: 'Médias'
    }
  },
  de: {
    portalTitle: 'Händlerportal',
    vendor: 'Händler',
    signOut: 'Abmelden',
    nav: {
      overview: 'Übersicht',
      application: 'Bewerbung',
      products: 'Produkte',
      newProduct: 'Neues Produkt',
      media: 'Medien'
    }
  },
  es: {
    portalTitle: 'Portal de vendedor',
    vendor: 'Vendedor',
    signOut: 'Cerrar sesión',
    nav: {
      overview: 'Resumen',
      application: 'Solicitud',
      products: 'Productos',
      newProduct: 'Nuevo producto',
      media: 'Medios'
    }
  },
  ar: {
    portalTitle: 'بوابة التاجر',
    vendor: 'تاجر',
    signOut: 'تسجيل الخروج',
    nav: {
      overview: 'نظرة عامة',
      application: 'طلب الانضمام',
      products: 'المنتجات',
      newProduct: 'منتج جديد',
      media: 'الوسائط'
    }
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active,
.slide-enter-active,
.slide-leave-active {
  transition: all 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
}
</style>
