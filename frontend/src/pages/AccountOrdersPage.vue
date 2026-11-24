<template>
  <div class="mx-auto max-w-5xl px-4 pt-24 py-8 lg:px-8">
    <div class="mb-6 flex items-center gap-3">
      <RouterLink :to="localized('/account')" class="btn btn-ghost h-9 w-9">
        <ChevronLeft class="h-5 w-5" />
      </RouterLink>
      <div>
        <h1 class="text-2xl font-bold">{{ t.title }}</h1>
        <p class="text-sm text-muted-foreground">{{ t.subtitle }}</p>
      </div>
    </div>

    <div v-if="!user" class="rounded-xl border bg-background p-8 text-center">
      <User class="mx-auto mb-3 h-10 w-10 text-sky-500" />
      <h2 class="text-lg font-semibold">{{ t.loginRequired }}</h2>
      <RouterLink :to="localized('/login?redirect=/account/orders')" class="btn mt-4 h-10 bg-primary px-5 text-primary-foreground">
        {{ t.login }}
      </RouterLink>
    </div>

    <div v-else-if="loading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="shimmer h-24 rounded-xl"></div>
    </div>

    <div v-else-if="error" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
      {{ error }}
    </div>

    <div v-else-if="!inquiries.length" class="rounded-xl border bg-background p-10 text-center">
      <ClipboardList class="mx-auto mb-3 h-12 w-12 text-muted-foreground/40" />
      <h2 class="text-lg font-semibold">{{ t.empty }}</h2>
      <p class="mt-1 text-sm text-muted-foreground">{{ t.emptyDesc }}</p>
      <RouterLink :to="localized('/shop')" class="gradient-bg mt-5 inline-flex h-10 items-center rounded-md px-5 text-sm font-medium text-white">
        {{ t.browse }}
      </RouterLink>
    </div>

    <div v-else class="space-y-3">
      <RouterLink
        v-for="inquiry in inquiries"
        :key="inquiry.id"
        :to="localized(`/account/inquiries/${inquiry.id}`)"
        class="block rounded-xl border bg-background p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
      >
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div class="min-w-0">
            <p class="font-semibold">{{ inquiry.inquiryNumber }}</p>
            <p class="mt-1 text-sm text-muted-foreground">{{ t.totalItems.replace('{count}', inquiry.items?.length || 0).replace('{name}', inquiry.contactName || '-') }}</p>
          </div>
          <div class="flex items-center gap-3">
            <span class="rounded-full px-3 py-1 text-xs font-medium" :class="statusClass(inquiry.status)">
              {{ statusLabel(inquiry.status) }}
            </span>
            <span class="text-sm text-muted-foreground">{{ formatDate(inquiry.createdAt) }}</span>
          </div>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { ChevronLeft, ClipboardList, User } from 'lucide-vue-next'
import { currentUser, getInquiries } from '@/api'

const route = useRoute()
const locale = computed(() => route.params.locale || 'en')
const user = ref(currentUser())
const inquiries = ref([])
const loading = ref(false)
const error = ref('')
const t = computed(() => locale.value === 'zh' ? copy.zh : copy.en)

onMounted(load)

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

async function load() {
  if (!user.value) return
  loading.value = true
  error.value = ''
  try {
    const data = await getInquiries()
    inquiries.value = data.data || data.inquiries || []
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.loadFailed
  } finally {
    loading.value = false
  }
}

function formatDate(value) {
  if (!value) return '-'
  return new Intl.DateTimeFormat(locale.value === 'zh' ? 'zh-CN' : 'en-US', {
    year: 'numeric',
    month: 'short',
    day: '2-digit'
  }).format(new Date(value))
}

function statusClass(status) {
  return {
    SUBMITTED: 'bg-blue-100 text-blue-800',
    REVIEWING: 'bg-yellow-100 text-yellow-800',
    QUOTED: 'bg-purple-100 text-purple-800',
    ACCEPTED: 'bg-green-100 text-green-800',
    REJECTED: 'bg-red-100 text-red-800',
    EXPIRED: 'bg-gray-100 text-gray-800',
    CANCELLED: 'bg-red-100 text-red-800'
  }[status] || 'bg-gray-100 text-gray-800'
}

function statusLabel(status) {
  const map = locale.value === 'zh' ? {
    SUBMITTED: '已提交',
    REVIEWING: '审核中',
    QUOTED: '已报价',
    ACCEPTED: '已接受',
    REJECTED: '已拒绝',
    EXPIRED: '已过期',
    CANCELLED: '已取消'
  } : {
    SUBMITTED: 'Submitted',
    REVIEWING: 'Under Review',
    QUOTED: 'Quoted',
    ACCEPTED: 'Accepted',
    REJECTED: 'Rejected',
    EXPIRED: 'Expired',
    CANCELLED: 'Cancelled'
  }
  return map[status] || status
}

const copy = {
  en: {
    title: 'My Inquiries',
    subtitle: 'View and manage submitted quotation requests',
    loginRequired: 'Please log in first',
    login: 'Log In',
    empty: 'No inquiry records',
    emptyDesc: 'Your inquiry records will appear here after submission.',
    browse: 'Browse Products',
    totalItems: '{count} products, contact: {name}',
    loadFailed: 'Failed to load inquiries.'
  },
  zh: {
    title: '我的询价',
    subtitle: '查看和管理已提交的报价请求',
    loginRequired: '请先登录',
    login: '登录',
    empty: '暂无询价记录',
    emptyDesc: '提交询价后，记录会显示在这里。',
    browse: '浏览产品',
    totalItems: '{count} 个产品，联系人: {name}',
    loadFailed: '询价记录加载失败。'
  }
}
</script>
