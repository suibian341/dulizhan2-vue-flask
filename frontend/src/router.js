import { createRouter, createWebHistory } from 'vue-router'

const localePattern = 'en|zh|ja|ko|fr|de|es|ar'
const localeCodes = new Set(localePattern.split('|'))

function storedLocale() {
  const locale = localStorage.getItem('misicheng-locale') || 'en'
  return localeCodes.has(locale) ? locale : 'en'
}

function redirectToStoredLocale(base) {
  return to => {
    const rawMatch = to.params.pathMatch
    const suffix = Array.isArray(rawMatch) ? rawMatch.join('/') : rawMatch
    return {
      path: `/${storedLocale()}${base}${suffix ? `/${suffix}` : ''}`,
      query: to.query,
      hash: to.hash
    }
  }
}

const routes = [
  { path: '/', redirect: () => `/${storedLocale()}` },
  { path: '/admin', redirect: redirectToStoredLocale('/admin') },
  { path: '/admin/:pathMatch(.*)*', redirect: redirectToStoredLocale('/admin') },
  { path: '/vendor', redirect: redirectToStoredLocale('/vendor') },
  { path: '/vendor/:pathMatch(.*)*', redirect: redirectToStoredLocale('/vendor') },
  { path: `/:locale(${localePattern})`, name: 'home', component: () => import('@/pages/HomePage.vue') },
  { path: `/:locale(${localePattern})/shop`, name: 'shop', component: () => import('@/pages/ShopPage.vue') },
  {
    path: `/:locale(${localePattern})/product/:slug`,
    name: 'product',
    component: () => import('@/pages/ProductDetailPage.vue')
  },
  { path: `/:locale(${localePattern})/inquiry`, name: 'inquiry', component: () => import('@/pages/InquiryPage.vue') },
  { path: `/:locale(${localePattern})/about`, name: 'about', component: () => import('@/pages/AboutPage.vue') },
  { path: `/:locale(${localePattern})/contact`, name: 'contact', component: () => import('@/pages/ContactPage.vue') },
  { path: `/:locale(${localePattern})/service`, name: 'service', component: () => import('@/pages/ServicePage.vue') },
  { path: `/:locale(${localePattern})/faq`, name: 'faq', component: () => import('@/pages/FaqPage.vue') },
  { path: `/:locale(${localePattern})/shipping`, name: 'shipping', component: () => import('@/pages/PolicyPage.vue') },
  { path: `/:locale(${localePattern})/returns`, name: 'returns', component: () => import('@/pages/PolicyPage.vue') },
  { path: `/:locale(${localePattern})/privacy`, name: 'privacy', component: () => import('@/pages/PolicyPage.vue') },
  { path: `/:locale(${localePattern})/terms`, name: 'terms', component: () => import('@/pages/PolicyPage.vue') },
  { path: `/:locale(${localePattern})/blog`, name: 'blog', component: () => import('@/pages/BlogPage.vue') },
  { path: `/:locale(${localePattern})/login`, name: 'login', component: () => import('@/pages/AuthPage.vue'), meta: { authMode: 'user' } },
  { path: `/:locale(${localePattern})/forgot-password`, name: 'forgot-password', component: () => import('@/pages/ForgotPasswordPage.vue') },
  { path: `/:locale(${localePattern})/register`, name: 'register', component: () => import('@/pages/AuthPage.vue'), meta: { authMode: 'user' } },
  { path: `/:locale(${localePattern})/account`, name: 'account', component: () => import('@/pages/AccountPage.vue') },
  { path: `/:locale(${localePattern})/account/orders`, name: 'account-orders', component: () => import('@/pages/AccountOrdersPage.vue') },
  { path: `/:locale(${localePattern})/account/inquiries/:id`, name: 'account-inquiry-detail', component: () => import('@/pages/InquiryDetailPage.vue') },
  { path: `/:locale(${localePattern})/account/wishlist`, name: 'wishlist', component: () => import('@/pages/WishlistPage.vue') },
  { path: `/:locale(${localePattern})/admin/login`, name: 'admin-login', component: () => import('@/pages/AuthPage.vue'), meta: { authMode: 'admin' } },
  { path: `/:locale(${localePattern})/admin`, name: 'admin', component: () => import('@/pages/AdminPage.vue') },
  { path: `/:locale(${localePattern})/admin/products`, name: 'admin-products', component: () => import('@/pages/AdminPage.vue') },
  { path: `/:locale(${localePattern})/admin/products/new`, name: 'admin-product-new', component: () => import('@/pages/AdminPage.vue') },
  { path: `/:locale(${localePattern})/admin/products/:id/edit`, name: 'admin-product-edit', component: () => import('@/pages/AdminPage.vue') },
  { path: `/:locale(${localePattern})/admin/spec-template`, name: 'admin-spec-template', component: () => import('@/pages/AdminPage.vue') },
  { path: `/:locale(${localePattern})/admin/vendors`, name: 'admin-vendors', component: () => import('@/pages/AdminPage.vue') },
  { path: `/:locale(${localePattern})/admin/banners`, name: 'admin-banners', component: () => import('@/pages/AdminPage.vue') },
  { path: `/:locale(${localePattern})/admin/categories`, name: 'admin-categories', component: () => import('@/pages/AdminPage.vue') },
  { path: `/:locale(${localePattern})/admin/orders`, name: 'admin-orders', component: () => import('@/pages/AdminPage.vue') },
  { path: `/:locale(${localePattern})/admin/orders/:id`, name: 'admin-order-detail', component: () => import('@/pages/AdminPage.vue') },
  { path: `/:locale(${localePattern})/admin/customers`, name: 'admin-customers', component: () => import('@/pages/AdminPage.vue') },
  { path: `/:locale(${localePattern})/admin/admins`, name: 'admin-admins', component: () => import('@/pages/AdminPage.vue') },
  { path: `/:locale(${localePattern})/admin/media`, name: 'admin-media', component: () => import('@/pages/AdminPage.vue') },
  { path: `/:locale(${localePattern})/admin/coupons`, name: 'admin-coupons', component: () => import('@/pages/AdminPage.vue') },
  { path: `/:locale(${localePattern})/admin/shipping`, name: 'admin-shipping', component: () => import('@/pages/AdminPage.vue') },
  { path: `/:locale(${localePattern})/admin/analytics`, name: 'admin-analytics', component: () => import('@/pages/AdminPage.vue') },
  { path: `/:locale(${localePattern})/admin/i18n`, name: 'admin-i18n', component: () => import('@/pages/AdminPage.vue') },
  { path: `/:locale(${localePattern})/admin/contacts`, name: 'admin-contacts', component: () => import('@/pages/AdminPage.vue') },
  { path: `/:locale(${localePattern})/admin/password`, name: 'admin-password', component: () => import('@/pages/AdminPage.vue') },
  { path: `/:locale(${localePattern})/vendor`, name: 'vendor', component: () => import('@/pages/VendorWorkspacePage.vue') },
  { path: `/:locale(${localePattern})/vendor/application`, name: 'vendor-application', component: () => import('@/pages/VendorWorkspacePage.vue') },
  { path: `/:locale(${localePattern})/vendor/products`, name: 'vendor-products', component: () => import('@/pages/VendorWorkspacePage.vue') },
  { path: `/:locale(${localePattern})/vendor/products/new`, name: 'vendor-product-new', component: () => import('@/pages/VendorWorkspacePage.vue') },
  { path: `/:locale(${localePattern})/vendor/products/:id/edit`, name: 'vendor-product-edit', component: () => import('@/pages/VendorWorkspacePage.vue') },
  { path: `/:locale(${localePattern})/vendor/media`, name: 'vendor-media', component: () => import('@/pages/VendorWorkspacePage.vue') },
  { path: `/:locale(${localePattern})/vendor/password`, name: 'vendor-password', component: () => import('@/pages/VendorWorkspacePage.vue') },
  { path: `/:locale(${localePattern})/vendor/login`, name: 'vendor-login', component: () => import('@/pages/AuthPage.vue'), meta: { authMode: 'vendor' } },
  { path: `/:locale(${localePattern})/vendor/register`, name: 'vendor-register', component: () => import('@/pages/AuthPage.vue'), meta: { authMode: 'vendor' } },
  { path: '/:pathMatch(.*)*', redirect: '/en' }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach((to, from, next) => {
  const locale = to.params.locale
  if (locale) {
    localStorage.setItem('misicheng-locale', locale)
    document.documentElement.lang = locale
    document.documentElement.dir = locale === 'ar' ? 'rtl' : 'ltr'
  }
  next()
})

export default router
