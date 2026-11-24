<template>
  <div class="admin-mode flex h-screen overflow-hidden bg-muted/30">
    <aside class="hidden w-64 shrink-0 flex-col border-r bg-background lg:flex">
      <div class="flex h-14 items-center border-b px-4">
        <RouterLink :to="localized('/admin')" class="flex items-center gap-2">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600">
            <span class="text-sm font-bold text-white">M</span>
          </div>
          <span class="font-semibold">{{ t.appName }}</span>
        </RouterLink>
      </div>

      <nav class="flex-1 overflow-y-auto p-3">
        <ul class="space-y-1">
          <li v-for="item in visibleNavItems" :key="item.href">
            <RouterLink
              :to="localized(item.href)"
              class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
              :class="isActive(item.href) ? 'bg-blue-600 text-white' : 'text-muted-foreground hover:bg-blue-50 hover:text-foreground'"
            >
              <component :is="item.icon" class="h-4 w-4 shrink-0" />
              {{ item.label }}
            </RouterLink>
          </li>
          <li v-if="canManageAdmins">
            <RouterLink
              :to="localized('/admin/admins')"
              class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
              :class="isActive('/admin/admins') ? 'bg-blue-600 text-white' : 'text-muted-foreground hover:bg-blue-50 hover:text-foreground'"
            >
              <Users class="h-4 w-4 shrink-0" />
              {{ locale === 'zh' ? '管理员管理' : 'Admin Management' }}
            </RouterLink>
          </li>
        </ul>
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
        <RouterLink :to="localized('/')" class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground">
          <LogOut class="h-4 w-4" />
          {{ t.backToStorefront }}
        </RouterLink>
      </div>
    </aside>

    <div class="flex min-w-0 flex-1 flex-col overflow-hidden">
      <header class="admin-header flex h-14 shrink-0 items-center justify-between border-b bg-background px-4">
        <button type="button" class="btn btn-ghost h-10 w-10 lg:hidden" aria-label="Open menu" @click="mobileOpen = true">
          <Menu class="h-5 w-5" />
        </button>
        <div class="hidden lg:block" />
        <div class="flex items-center gap-2">
          <span class="text-sm text-muted-foreground">{{ t.fallbackAdmin }}</span>
          <div class="flex h-7 w-7 items-center justify-center rounded-full bg-blue-600 text-[11px] font-bold text-white">M</div>
        </div>
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
          <span class="font-semibold">{{ t.appName }}</span>
          <button type="button" class="btn btn-ghost h-9 w-9" aria-label="Close menu" @click="mobileOpen = false">
            <X class="h-4 w-4" />
          </button>
        </div>
        <nav class="flex-1 overflow-y-auto p-3">
          <RouterLink
            v-for="item in visibleNavItems"
            :key="item.href"
            :to="localized(item.href)"
            class="mb-1 flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
            :class="isActive(item.href) ? 'bg-blue-600 text-white' : 'text-muted-foreground hover:bg-blue-50 hover:text-foreground'"
            @click="mobileOpen = false"
          >
            <component :is="item.icon" class="h-4 w-4 shrink-0" />
            {{ item.label }}
          </RouterLink>
          <RouterLink
            v-if="canManageAdmins"
            :to="localized('/admin/admins')"
            class="mb-1 flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
            :class="isActive('/admin/admins') ? 'bg-blue-600 text-white' : 'text-muted-foreground hover:bg-blue-50 hover:text-foreground'"
            @click="mobileOpen = false"
          >
            <Users class="h-4 w-4 shrink-0" />
            {{ locale === 'zh' ? '管理员管理' : 'Admin Management' }}
          </RouterLink>
        </nav>
      </aside>
    </Transition>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import {
  BarChart3,
  ChevronDown,
  ClipboardCheck,
  ClipboardList,
  FolderTree,
  Globe,
  Image,
  LayoutDashboard,
  LogOut,
  Menu,
  MessageSquare,
  Package,
  Settings,
  Store,
  Tag,
  Truck,
  Users,
  X
} from 'lucide-vue-next'

import { loadLocaleMessages } from '@/i18n'
import { currentUser } from '@/api'

const route = useRoute()
const router = useRouter()
const mobileOpen = ref(false)
const localeOpen = ref(false)
const locale = computed(() => route.params.locale || 'en')
const adminUser = ref(currentUser())
const isSuperAdmin = computed(() => adminUser.value?.role === 'SUPER_ADMIN' || adminUser.value?.email === 'baomiai@126.com')
const isElevatedAdmin = computed(() => isSuperAdmin.value || adminUser.value?.role === 'SENIOR_ADMIN')
const canManageAdmins = computed(() => isElevatedAdmin.value)
const basicAdminNav = new Set([
  '/admin',
  '/admin/products',
  '/admin/products?status=PENDING_REVIEW',
  '/admin/vendors',
  '/admin/media',
  '/admin/orders',
  '/admin/contacts',
  '/admin/password'
])

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
const navItems = computed(() => [
  { href: '/admin', icon: LayoutDashboard, label: t.value.nav.dashboard },
  { href: '/admin/products', icon: Package, label: t.value.nav.products },
  { href: '/admin/products?status=PENDING_REVIEW', icon: ClipboardCheck, label: t.value.nav.productReview },
  { href: '/admin/spec-template', icon: Settings, label: t.value.nav.specTemplate || (locale.value === 'zh' ? '模板设置' : 'Template Settings') },
  { href: '/admin/vendors', icon: Store, label: t.value.nav.vendorReview },
  { href: '/admin/banners', icon: Image, label: t.value.nav.banners || (locale.value === 'zh' ? '\u6a2a\u5e45' : 'Banners') },
  { href: '/admin/categories', icon: FolderTree, label: t.value.nav.categories },
  { href: '/admin/orders', icon: ClipboardList, label: t.value.nav.orders },
  { href: '/admin/customers', icon: Users, label: t.value.nav.customers },
  { href: '/admin/media', icon: Image, label: t.value.nav.media },
  { href: '/admin/coupons', icon: Tag, label: t.value.nav.coupons },
  { href: '/admin/shipping', icon: Truck, label: t.value.nav.shipping },
  { href: '/admin/analytics', icon: BarChart3, label: t.value.nav.analytics },
  { href: '/admin/i18n', icon: Globe, label: t.value.nav.translations },
  { href: '/admin/contacts', icon: MessageSquare, label: t.value.nav.contacts },
  { href: '/admin/password', icon: Settings, label: locale.value === 'zh' ? '修改密码' : 'Change Password' }
])

const visibleNavItems = computed(() => {
  if (isElevatedAdmin.value) return navItems.value
  return navItems.value.filter(item => basicAdminNav.has(item.href))
})

function localized(path) {
  if (path === '/') return `/${locale.value}`
  return `/${locale.value}${path}`
}

function pathWithoutLocale() {
  return route.path.replace(/^\/(en|zh|ja|ko|fr|de|es|ar)(?=\/|$)/, '') || '/'
}

function isActive(href) {
  const [hrefPath, hrefQuery] = href.split('?')
  const currentPath = pathWithoutLocale()
  if (hrefPath === '/admin') return currentPath === '/admin'
  if (!currentPath.startsWith(hrefPath)) return false
  if (hrefQuery) {
    const expected = new URLSearchParams(hrefQuery).get('status')
    return route.query.status === expected
  }
  if (hrefPath === '/admin/products') return !route.query.status && (currentPath === '/admin/products' || currentPath.startsWith('/admin/products/'))
  return true
}

function fitTextClass(value) {
  const length = Array.from(value || '').length
  if (length >= 12) return 'text-[10px]'
  if (length >= 8) return 'text-[11px]'
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

watch(() => route.fullPath, () => {
  adminUser.value = currentUser()
}, { immediate: true })

const copy = {
  en: {
    appName: 'Misicheng Admin',
    backToStorefront: 'Back to storefront',
    fallbackAdmin: 'Admin',
    nav: {
      dashboard: 'Dashboard',
      products: 'Products',
      productReview: 'Product Review',
      specTemplate: 'Template Settings',
      vendorReview: 'Vendor Review',
      banners: 'Banners',
      categories: 'Categories',
      orders: 'Inquiries',
      customers: 'Customers',
      media: 'Media',
      coupons: 'Coupons',
      shipping: 'Shipping',
      analytics: 'Analytics',
      translations: 'Translations',
      contacts: 'Contact Messages'
    }
  },
  zh: {
    appName: 'Misicheng 后台',
    backToStorefront: '返回前台',
    fallbackAdmin: '管理员',
    nav: {
      dashboard: '仪表盘',
      products: '商品',
      productReview: '商品审核',
      specTemplate: '模板设置',
      vendorReview: '商家审核',
      banners: '横幅',
      categories: '分类',
      orders: '询盘',
      customers: '客户',
      media: '媒体库',
      coupons: '优惠券',
      shipping: '物流',
      analytics: '分析',
      translations: '翻译',
      contacts: '联系消息'
    }
  },
  ja: {
    appName: 'Misicheng 管理',
    backToStorefront: 'ストアに戻る',
    fallbackAdmin: '管理者',
    nav: {
      dashboard: 'ダッシュボード',
      products: '商品',
      productReview: '商品審査',
      specTemplate: 'テンプレート設定',
      vendorReview: '出店審査',
      banners: 'バナー',
      categories: 'カテゴリ',
      orders: '問い合わせ',
      customers: '顧客',
      media: 'メディア',
      coupons: 'クーポン',
      shipping: '配送',
      analytics: '分析',
      translations: '翻訳',
      contacts: '連絡メッセージ'
    }
  },
  ko: {
    appName: 'Misicheng 관리자',
    backToStorefront: '스토어로 돌아가기',
    fallbackAdmin: '관리자',
    nav: {
      dashboard: '대시보드',
      products: '상품',
      productReview: '상품 검토',
      specTemplate: '템플릿 설정',
      vendorReview: '입점 심사',
      banners: '배너',
      categories: '카테고리',
      orders: '문의',
      customers: '고객',
      media: '미디어',
      coupons: '쿠폰',
      shipping: '배송',
      analytics: '분석',
      translations: '번역',
      contacts: '문의 메시지'
    }
  },
  fr: {
    appName: 'Administration Misicheng',
    backToStorefront: 'Retour à la boutique',
    fallbackAdmin: 'Administrateur',
    nav: {
      dashboard: 'Tableau de bord',
      products: 'Produits',
      productReview: 'Validation produits',
      specTemplate: 'Paramètres du modèle',
      vendorReview: 'Validation vendeurs',
      banners: 'Bannières',
      categories: 'Catégories',
      orders: 'Demandes',
      customers: 'Clients',
      media: 'Médias',
      coupons: 'Coupons',
      shipping: 'Livraison',
      analytics: 'Analyses',
      translations: 'Traductions',
      contacts: 'Messages'
    }
  },
  de: {
    appName: 'Misicheng Admin',
    backToStorefront: 'Zurück zum Shop',
    fallbackAdmin: 'Admin',
    nav: {
      dashboard: 'Dashboard',
      products: 'Produkte',
      productReview: 'Produktprüfung',
      specTemplate: 'Vorlageneinstellungen',
      vendorReview: 'Händlerprüfung',
      banners: 'Banner',
      categories: 'Kategorien',
      orders: 'Anfragen',
      customers: 'Kunden',
      media: 'Medien',
      coupons: 'Gutscheine',
      shipping: 'Versand',
      analytics: 'Analysen',
      translations: 'Übersetzungen',
      contacts: 'Nachrichten'
    }
  },
  es: {
    appName: 'Administración Misicheng',
    backToStorefront: 'Volver a la tienda',
    fallbackAdmin: 'Administrador',
    nav: {
      dashboard: 'Panel',
      products: 'Productos',
      productReview: 'Revisión de productos',
      specTemplate: 'Configuración de plantilla',
      vendorReview: 'Revisión de vendedores',
      banners: 'Banners',
      categories: 'Categorías',
      orders: 'Consultas',
      customers: 'Clientes',
      media: 'Medios',
      coupons: 'Cupones',
      shipping: 'Envíos',
      analytics: 'Analítica',
      translations: 'Traducciones',
      contacts: 'Mensajes'
    }
  },
  ar: {
    appName: 'إدارة Misicheng',
    backToStorefront: 'العودة إلى المتجر',
    fallbackAdmin: 'المسؤول',
    nav: {
      dashboard: 'لوحة التحكم',
      products: 'المنتجات',
      productReview: 'مراجعة المنتجات',
      specTemplate: 'إعدادات القالب',
      vendorReview: 'مراجعة التجار',
      banners: 'اللافتات',
      categories: 'الفئات',
      orders: 'الاستفسارات',
      customers: 'العملاء',
      media: 'الوسائط',
      coupons: 'القسائم',
      shipping: 'الشحن',
      analytics: 'التحليلات',
      translations: 'الترجمات',
      contacts: 'الرسائل'
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
