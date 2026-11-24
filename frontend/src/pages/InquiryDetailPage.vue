<template>
  <div class="mx-auto max-w-3xl px-4 pt-24 py-8 lg:px-8">
    <div class="mb-6 flex items-center gap-3">
      <RouterLink :to="localized('/account/orders')" class="btn btn-ghost h-9 w-9">
        <ChevronLeft class="h-5 w-5" />
      </RouterLink>
      <h1 class="text-2xl font-bold">{{ t.title }}</h1>
    </div>

    <div v-if="!user" class="rounded-xl border bg-background p-8 text-center">
      <User class="mx-auto mb-3 h-10 w-10 text-sky-500" />
      <h2 class="text-lg font-semibold">{{ t.loginRequired }}</h2>
      <RouterLink :to="localized('/login')" class="btn mt-4 h-10 bg-primary px-5 text-primary-foreground">{{ t.login }}</RouterLink>
    </div>

    <div v-else-if="loading" class="flex min-h-[50vh] items-center justify-center">
      <div class="h-8 w-8 animate-spin rounded-full border-2 border-foreground border-t-transparent"></div>
    </div>

    <div v-else-if="error || !inquiry" class="rounded-xl border bg-background p-10 text-center">
      <Package class="mx-auto mb-3 h-12 w-12 text-muted-foreground/40" />
      <h2 class="text-lg font-semibold">{{ t.notFound }}</h2>
      <p class="mt-1 text-sm text-muted-foreground">{{ error || t.notFoundDesc }}</p>
      <RouterLink :to="localized('/account/orders')" class="btn btn-outline mt-5 h-10 px-5">{{ t.backToList }}</RouterLink>
    </div>

    <template v-else>
      <div class="mb-6 rounded-xl border bg-background p-4">
        <div class="flex items-center justify-between gap-3">
          <div>
            <p class="text-lg font-semibold">{{ inquiry.inquiryNumber }}</p>
            <p class="text-sm text-muted-foreground">{{ t.submitDate }} {{ formatDate(inquiry.createdAt) }}</p>
          </div>
          <span class="rounded-full px-3 py-1 text-xs font-medium" :class="statusClass(inquiry.status)">
            {{ statusLabel(inquiry.status) }}
          </span>
        </div>
        <div v-if="inquiry.message" class="mt-3 border-t pt-3">
          <p class="text-sm text-muted-foreground">{{ t.messageLabel }}</p>
          <p class="break-words text-sm">{{ inquiry.message }}</p>
        </div>
      </div>

      <div class="mb-6 rounded-xl border bg-background p-4">
        <h3 class="mb-3 font-semibold">{{ t.productList }}</h3>
        <div class="max-h-[300px] space-y-3 overflow-y-auto">
          <div v-for="item in inquiry.items" :key="item.id" class="flex items-center gap-3 rounded-lg border p-3">
            <img v-if="item.image" :src="item.image" :alt="item.name" class="h-16 w-16 rounded-lg bg-muted object-contain p-1" />
            <div class="min-w-0 flex-1">
              <p class="break-words font-medium">{{ item.name }}</p>
              <p v-if="formatOptions(item.options)" class="mt-1 text-xs text-muted-foreground">{{ formatOptions(item.options) }}</p>
              <p class="text-sm text-muted-foreground">{{ t.quantity.replace('{count}', item.quantity) }}</p>
              <p v-if="item.note" class="break-words text-sm text-muted-foreground">{{ t.note.replace('{text}', item.note) }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="mb-6 rounded-xl border bg-background p-4">
        <h3 class="mb-3 font-semibold">{{ t.contactInfo }}</h3>
        <div class="space-y-2">
          <div class="flex items-center gap-2">
            <User class="h-4 w-4 text-muted-foreground" />
            <span class="text-sm">{{ inquiry.contactName }}</span>
          </div>
          <p v-if="inquiry.companyName" class="text-sm text-muted-foreground">{{ t.company.replace('{name}', inquiry.companyName) }}</p>
          <p class="text-sm text-muted-foreground">{{ t.email.replace('{email}', inquiry.email) }}</p>
          <p v-if="inquiry.phone" class="text-sm text-muted-foreground">{{ t.phone.replace('{phone}', inquiry.phone) }}</p>
        </div>
      </div>

      <div v-if="inquiry.quotes?.length" class="mb-6 space-y-4">
        <h3 class="font-semibold">{{ t.quoteInfo }}</h3>
        <QuoteCard
          v-for="quote in inquiry.quotes"
          :key="quote.id"
          :quote="quote"
          :inquiry-status="inquiry.status"
          :locale="locale"
          @accept="respondToQuote('ACCEPTED')"
          @reject="respondToQuote('REJECTED')"
        />
      </div>

      <div class="mb-6">
        <MessagePanel
          :inquiry-id="inquiry.id"
          :current-user-id="user.id"
          current-user-role="USER"
          :initial-messages="inquiry.messages || []"
          :locale="locale"
        />
      </div>

      <RouterLink :to="localized('/account/orders')" class="btn btn-outline h-10 w-full">{{ t.backToList }}</RouterLink>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { ChevronLeft, Package, User } from 'lucide-vue-next'
import { currentUser, getInquiry, updateInquiry } from '@/api'
import MessagePanel from '@/components/MessagePanel.vue'
import QuoteCard from '@/components/QuoteCard.vue'
import { formatVariantOptions } from '@/variantOptions'

const route = useRoute()
const locale = computed(() => route.params.locale || 'en')
const user = ref(currentUser())
const inquiry = ref(null)
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
    const data = await getInquiry(route.params.id)
    inquiry.value = data.data || data.inquiry
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.loadFailed
  } finally {
    loading.value = false
  }
}

async function respondToQuote(status) {
  if (!inquiry.value) return
  const data = await updateInquiry(inquiry.value.id, { status })
  inquiry.value = data.data || data.inquiry || { ...inquiry.value, status }
}

function formatDate(value) {
  if (!value) return '-'
  return new Intl.DateTimeFormat(locale.value === 'zh' ? 'zh-CN' : 'en-US', {
    year: 'numeric',
    month: 'short',
    day: '2-digit'
  }).format(new Date(value))
}

function formatOptions(options) {
  return formatVariantOptions(options, [], locale.value === 'zh' ? 'zh' : 'en')
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
    title: 'Inquiry Detail',
    loginRequired: 'Please log in first',
    login: 'Log In',
    notFound: 'Inquiry not found',
    notFoundDesc: 'This inquiry record does not exist or has been deleted.',
    submitDate: 'Submitted:',
    messageLabel: 'Message:',
    productList: 'Product List',
    quantity: 'Quantity: {count}',
    note: 'Note: {text}',
    contactInfo: 'Contact Information',
    company: 'Company: {name}',
    email: 'Email: {email}',
    phone: 'Phone: {phone}',
    quoteInfo: 'Quote Information',
    backToList: 'Back to list',
    loadFailed: 'Failed to load inquiry.'
  },
  zh: {
    title: '询价详情',
    loginRequired: '请先登录',
    login: '登录',
    notFound: '未找到询价',
    notFoundDesc: '该询价记录不存在或已被删除。',
    submitDate: '提交日期:',
    messageLabel: '留言:',
    productList: '产品列表',
    quantity: '数量: {count}',
    note: '备注: {text}',
    contactInfo: '联系信息',
    company: '公司: {name}',
    email: '邮箱: {email}',
    phone: '电话: {phone}',
    quoteInfo: '报价信息',
    backToList: '返回列表',
    loadFailed: '询价详情加载失败。'
  }
}
</script>
