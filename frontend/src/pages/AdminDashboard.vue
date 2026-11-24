<template>
  <div class="mx-auto max-w-7xl px-4 pt-24 py-8 lg:px-8">
    <div class="space-y-6">
      <div class="flex items-start justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold">{{ t.title }}</h1>
          <p class="text-sm text-muted-foreground">{{ t.subtitle }}</p>
        </div>
        <button
          type="button"
          class="inline-flex h-9 items-center justify-center gap-2 rounded-md border bg-background px-4 py-2 text-sm font-medium shadow-xs transition-all hover:bg-accent hover:text-accent-foreground"
          @click="load"
        >
          <RefreshCw class="h-4 w-4" :class="loading ? 'animate-spin' : ''" />
          {{ t.refresh }}
        </button>
      </div>

      <div v-if="loading" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div v-for="i in 4" :key="i" class="shimmer h-[128px] rounded-xl"></div>
      </div>

      <template v-else>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="stat in statCards" :key="stat.title" class="rounded-xl border bg-card text-card-foreground shadow-sm">
            <div class="flex flex-row items-center justify-between p-6 pb-2">
              <h3 class="text-sm font-medium text-muted-foreground">{{ stat.title }}</h3>
              <div class="flex h-8 w-8 items-center justify-center rounded-lg" :class="stat.color">
                <component :is="stat.icon" class="h-4 w-4" />
              </div>
            </div>
            <div class="p-6 pt-0">
              <div class="text-2xl font-bold">{{ stat.value }}</div>
              <div v-if="stat.change" class="flex items-center gap-1 text-xs">
                <TrendingUp v-if="stat.change.startsWith('+')" class="h-3 w-3 text-green-600" />
                <TrendingDown v-else class="h-3 w-3 text-red-600" />
                <span :class="stat.change.startsWith('+') ? 'text-green-600' : 'text-red-600'">{{ stat.change }}</span>
                <span class="text-muted-foreground">{{ t.vsLastMonth }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div class="rounded-xl border bg-card text-card-foreground shadow-sm lg:col-span-2">
            <div class="p-6">
              <h3 class="flex items-center gap-2 text-base font-semibold">
                <TrendingUp class="h-4 w-4 text-blue-600" />
                {{ t.inquiryTrend }}
              </h3>
            </div>
            <div class="p-6 pt-0">
              <div class="flex h-[220px] items-end gap-3 border-b border-l px-3 pb-3">
                <div v-for="row in monthlyData" :key="row.month" class="flex min-w-0 flex-1 flex-col items-center gap-2">
                  <div class="w-full rounded-t-md bg-sky-500 transition-all" :style="{ height: chartHeight(row.inquiries) }"></div>
                  <span class="text-[11px] text-muted-foreground">{{ row.month }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="rounded-xl border bg-card text-card-foreground shadow-sm">
            <div class="p-6">
              <h3 class="text-base font-semibold">{{ t.inquiryStatus }}</h3>
            </div>
            <div class="flex items-center justify-center p-6 pt-0">
              <div v-if="statusData.length" class="relative grid h-[150px] w-[150px] place-items-center rounded-full" :style="{ background: donutBackground(statusData) }">
                <div class="grid h-[92px] w-[92px] place-items-center rounded-full bg-white text-center">
                  <strong>{{ inquiries.length }}</strong>
                  <span class="text-xs text-muted-foreground">{{ t.inquiries }}</span>
                </div>
              </div>
              <p v-else class="text-sm text-muted-foreground">{{ t.noData }}</p>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div class="rounded-xl border bg-card text-card-foreground shadow-sm lg:col-span-2">
            <div class="flex flex-row items-center justify-between p-6">
              <h3 class="flex items-center gap-2 text-base font-semibold">
                <MessageSquare class="h-4 w-4 text-blue-600" />
                {{ t.recentInquiries }}
              </h3>
              <span class="flex items-center gap-1 text-sm text-blue-600">{{ t.viewAll }} <ArrowUpRight class="h-3 w-3" /></span>
            </div>
            <div class="p-6 pt-0">
              <div class="space-y-3">
                <div v-for="inq in inquiries.slice(0, 5)" :key="inq.id" class="flex items-center justify-between rounded-lg border p-3">
                  <div>
                    <p class="text-sm font-medium">{{ inq.contactName }}</p>
                    <p class="text-xs text-muted-foreground">{{ inq.inquiryNumber }} · {{ formatDate(inq.createdAt) }}</p>
                  </div>
                  <span class="rounded-full px-2 py-0.5 text-xs font-medium" :class="statusColors[inq.status] || 'bg-gray-100 text-gray-800'">
                    {{ statusLabels[locale]?.[inq.status] || inq.status }}
                  </span>
                </div>
                <p v-if="!inquiries.length" class="text-sm text-muted-foreground">{{ t.noInquiries }}</p>
              </div>
            </div>
          </div>

          <div class="rounded-xl border bg-card text-card-foreground shadow-sm">
            <div class="flex flex-row items-center justify-between p-6">
              <h3 class="text-base font-semibold">{{ t.topProducts }}</h3>
              <span class="flex items-center gap-1 text-sm text-blue-600">{{ t.viewAll }} <ArrowUpRight class="h-3 w-3" /></span>
            </div>
            <div class="p-6 pt-0">
              <div class="space-y-4">
                <div v-for="(product, index) in topProducts" :key="product.name" class="flex items-center gap-3">
                  <span class="flex h-6 w-6 items-center justify-center rounded-full text-xs font-medium text-white" :style="{ backgroundColor: colors[index % colors.length] }">{{ index + 1 }}</span>
                  <p class="flex-1 whitespace-normal break-words font-medium leading-snug" :class="fitTextClass(product.name)">
                    {{ product.name }}
                  </p>
                  <span class="text-sm text-muted-foreground">{{ product.units }} {{ t.units }}</span>
                </div>
                <p v-if="!topProducts.length" class="text-sm text-muted-foreground">{{ t.noData }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          <div class="rounded-xl border bg-card text-card-foreground shadow-sm">
            <div class="p-6"><h3 class="text-base font-semibold">{{ t.trafficSources }}</h3></div>
            <div class="flex items-center justify-center p-6 pt-0">
              <p class="text-sm text-muted-foreground">{{ t.noData }}</p>
            </div>
          </div>

          <div class="rounded-xl border bg-card text-card-foreground shadow-sm">
            <div class="p-6">
              <h3 class="flex items-center gap-2 text-base font-semibold">
                <Globe class="h-4 w-4 text-blue-600" />
                {{ t.visitorRegions }}
              </h3>
            </div>
            <div class="p-6 pt-0">
              <p class="text-sm text-muted-foreground">{{ t.noData }}</p>
            </div>
          </div>

          <div class="rounded-xl border bg-card text-card-foreground shadow-sm">
            <div class="p-6"><h3 class="text-base font-semibold">{{ t.hotPages }}</h3></div>
            <div class="p-6 pt-0">
              <p class="text-sm text-muted-foreground">{{ t.noData }}</p>
            </div>
          </div>
        </div>

        <p v-if="error" class="text-sm text-destructive">{{ error }}</p>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  ArrowUpRight,
  ClipboardList,
  Eye,
  Globe,
  MessageSquare,
  Package,
  RefreshCw,
  TrendingDown,
  TrendingUp,
  Users
} from 'lucide-vue-next'

import { getAdminAnalytics, getAdminContacts } from '@/api'

const route = useRoute()
const loading = ref(true)
const error = ref('')
const analytics = ref(null)
const contacts = ref([])
const colors = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
const statusColors = {
  SUBMITTED: 'bg-blue-100 text-blue-800',
  REVIEWING: 'bg-yellow-100 text-yellow-800',
  QUOTED: 'bg-purple-100 text-purple-800',
  ACCEPTED: 'bg-green-100 text-green-800',
  REJECTED: 'bg-red-100 text-red-800',
  EXPIRED: 'bg-gray-100 text-gray-800',
  CANCELLED: 'bg-red-100 text-red-800'
}
const statusLabels = {
  en: {
    SUBMITTED: 'Submitted',
    REVIEWING: 'Under Review',
    QUOTED: 'Quoted',
    ACCEPTED: 'Accepted',
    REJECTED: 'Rejected',
    EXPIRED: 'Expired',
    CANCELLED: 'Cancelled'
  },
  zh: {
    SUBMITTED: '已提交',
    REVIEWING: '审核中',
    QUOTED: '已报价',
    ACCEPTED: '已接受',
    REJECTED: '已拒绝',
    EXPIRED: '已过期',
    CANCELLED: '已取消'
  }
}

const locale = computed(() => route.params.locale || 'en')
const t = computed(() => copy[locale.value] || copy.en)
const monthlyData = computed(() => analytics.value?.monthlyData || [])
const topProducts = computed(() => analytics.value?.topProducts || [])
const inquiries = computed(() => contacts.value.map(row => ({
  id: row.id,
  inquiryNumber: row.subject || row.id,
  contactName: row.name,
  email: row.email,
  status: 'SUBMITTED',
  createdAt: row.createdAt,
  items: []
})))
const statCards = computed(() => {
  const s = analytics.value?.stats || {}
  return [
    { title: t.value.pageViews, value: s.pageViews ?? 0, change: s.pageViewsChange, icon: Eye, color: 'text-blue-600 bg-blue-50' },
    { title: t.value.totalInquiries, value: s.totalInquiries ?? s.inquiries ?? inquiries.value.length, change: s.inquiriesChange, icon: ClipboardList, color: 'text-emerald-600 bg-emerald-50' },
    { title: t.value.registeredUsers, value: s.totalUsers ?? 0, change: s.newUsersChange, icon: Users, color: 'text-violet-600 bg-violet-50' },
    { title: t.value.activeProducts, value: `${s.activeProducts ?? 0} / ${s.totalProducts ?? 0}`, icon: Package, color: 'text-amber-600 bg-amber-50' }
  ]
})
const statusData = computed(() => {
  const counts = {}
  for (const row of inquiries.value) counts[row.status] = (counts[row.status] || 0) + 1
  return Object.entries(counts).map(([label, value], index) => ({
    label,
    value,
    color: colors[index % colors.length]
  }))
})

function chartHeight(value) {
  const max = Math.max(...monthlyData.value.map(row => row.inquiries), 1)
  return `${Math.max(4, (Number(value || 0) / max) * 190)}px`
}

function donutBackground(rows) {
  const total = rows.reduce((sum, row) => sum + row.value, 0)
  let current = 0
  const stops = rows.map(row => {
    const start = (current / total) * 100
    current += row.value
    const end = (current / total) * 100
    return `${row.color} ${start}% ${end}%`
  })
  return `conic-gradient(${stops.join(', ')})`
}

function formatDate(value) {
  if (!value) return '-'
  return new Intl.DateTimeFormat(locale.value === 'zh' ? 'zh-CN' : 'en-US', {
    year: 'numeric',
    month: 'short',
    day: '2-digit'
  }).format(new Date(value))
}

function fitTextClass(value) {
  const length = Array.from(String(value || '')).length
  if (length >= 48) return 'text-[10px]'
  if (length >= 32) return 'text-[11px]'
  if (length >= 22) return 'text-xs'
  return 'text-sm'
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [analyticsData, contactData] = await Promise.all([
      getAdminAnalytics(),
      getAdminContacts()
    ])
    analytics.value = analyticsData
    contacts.value = contactData.contacts || []
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.loadFailed
  } finally {
    loading.value = false
  }
}

onMounted(load)

const copy = {
  en: {
    title: 'Dashboard',
    subtitle: 'Store operations overview for the last 30 days',
    refresh: 'Refresh',
    pageViews: 'Page Views',
    totalInquiries: 'Total Inquiries',
    registeredUsers: 'Registered Customers',
    activeProducts: 'Active Products',
    vsLastMonth: 'vs last month',
    inquiryTrend: 'Inquiry Trend (Last 12 Months)',
    inquiryStatus: 'Inquiry Status Distribution',
    inquiries: 'Inquiries',
    recentInquiries: 'Recent Inquiries',
    topProducts: 'Top Products',
    trafficSources: 'Traffic Sources',
    visitorRegions: 'Visitor Regions',
    hotPages: 'Hot Pages',
    viewAll: 'View all',
    units: 'units',
    noData: 'No data',
    noInquiries: 'No inquiries',
    loadFailed: 'Failed to load dashboard data.'
  },
  zh: {
    title: '仪表盘',
    subtitle: '店铺运营数据概览（近 30 天）',
    refresh: '刷新',
    pageViews: '页面浏览',
    totalInquiries: '总询盘数',
    registeredUsers: '注册客户',
    activeProducts: '在售商品',
    vsLastMonth: '较上月',
    inquiryTrend: '询盘趋势（近 12 个月）',
    inquiryStatus: '询盘状态分布',
    inquiries: '询盘',
    recentInquiries: '最近询盘',
    topProducts: '热门商品',
    trafficSources: '流量来源',
    visitorRegions: '访客地区',
    hotPages: '热门页面',
    viewAll: '查看全部',
    units: '件',
    noData: '暂无数据',
    noInquiries: '暂无询盘',
    loadFailed: '后台数据加载失败。'
  }
}
</script>
