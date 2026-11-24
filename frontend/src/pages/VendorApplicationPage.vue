<template>
  <div class="mx-auto max-w-7xl px-4 pt-24 py-8 lg:px-8">
    <div v-if="loading" class="space-y-6">
      <div class="shimmer h-24 rounded-2xl"></div>
      <div class="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <div class="shimmer h-[360px] rounded-2xl"></div>
        <div class="shimmer h-[360px] rounded-2xl"></div>
      </div>
    </div>

    <div v-else-if="error" class="rounded-2xl border bg-background p-6">
      <p class="text-sm text-destructive">{{ error }}</p>
    </div>

    <div v-else-if="!application" class="rounded-2xl border bg-background p-6">
      <h1 class="text-2xl font-bold">{{ t.title }}</h1>
      <p class="mt-2 text-sm text-muted-foreground">{{ t.empty }}</p>
      <RouterLink :to="localized('/vendor/register')" class="btn gradient-bg mt-6 h-10 px-6 text-white">
        {{ t.apply }}
      </RouterLink>
    </div>

    <div v-else class="space-y-6">
      <div class="rounded-2xl border bg-background p-6 shadow-sm">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div class="flex items-start gap-4">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-blue-700">
              <ClipboardCheck class="h-6 w-6" />
            </div>
            <div class="space-y-2">
              <div class="flex items-center gap-3">
                <h1 class="text-2xl font-semibold tracking-tight">{{ t.title }}</h1>
                <span class="rounded-full px-3 py-1 text-xs font-medium" :class="statusClass">
                  {{ statusLabel }}
                </span>
              </div>
              <p class="max-w-2xl text-sm leading-6 text-muted-foreground">{{ statusDescription }}</p>
            </div>
          </div>
          <div class="space-y-1 text-sm text-muted-foreground">
            <p>{{ t.submittedAt }}: {{ formatDate(application.submittedAt) }}</p>
            <p v-if="application.reviewedAt">{{ t.reviewedAt }}: {{ formatDate(application.reviewedAt) }}</p>
          </div>
        </div>
        <div v-if="application.reviewNote" class="mt-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          <p class="font-medium">{{ t.reviewNote }}</p>
          <p class="mt-1">{{ application.reviewNote }}</p>
        </div>
      </div>

      <div class="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <div class="rounded-2xl border bg-background p-6 shadow-sm">
          <h2 class="mb-4 text-lg font-semibold">{{ t.companyDetails }}</h2>
          <div class="grid gap-4 sm:grid-cols-2">
            <Info :label="t.companyName" :value="application.companyName" />
            <Info :label="t.contactPerson" :value="application.contactPerson || '-'" />
            <Info :label="t.email" :value="application.email" />
            <Info :label="t.phone" :value="application.phone || '-'" />
            <Info :label="t.country" :value="application.country || '-'" />
            <Info :label="t.address" :value="application.address || '-'" />
          </div>
          <div class="mt-4 space-y-2">
            <p class="text-sm font-medium text-foreground">{{ t.companyProfile }}</p>
            <p class="rounded-xl bg-muted/40 px-4 py-3 text-sm leading-6 text-muted-foreground">
              {{ application.description || t.noDescription }}
            </p>
          </div>
        </div>

        <div class="rounded-2xl border bg-background p-6 shadow-sm">
          <h2 class="mb-4 text-lg font-semibold">{{ t.files }}</h2>
          <div class="space-y-3">
            <div v-for="file in application.certificationFiles" :key="file" class="flex items-center justify-between rounded-xl border px-4 py-3">
              <div class="flex min-w-0 items-center gap-3">
                <FileText class="h-4 w-4 shrink-0 text-muted-foreground" />
                <span class="whitespace-normal break-all leading-snug" :class="fitTextClass(file)">
                  {{ file.split('/').pop() || file }}
                </span>
              </div>
              <a :href="file" target="_blank" rel="noreferrer" class="btn btn-outline h-8 px-3 text-xs">{{ t.open }}</a>
            </div>
            <p v-if="!application.certificationFiles.length" class="rounded-xl border border-dashed px-4 py-6 text-sm text-muted-foreground">
              {{ t.noFiles }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { ClipboardCheck, FileText, CheckCircle2, Clock3, ShieldX, XCircle } from 'lucide-vue-next'

import { getVendorApplication } from '@/api'

const route = useRoute()
const locale = computed(() => route.params.locale || 'en')
const application = ref(null)
const loading = ref(true)
const error = ref('')

const t = computed(() => copy[locale.value] || copy.en)
const statusMeta = computed(() => {
  const status = application.value?.status || 'PENDING'
  const isZh = locale.value === 'zh'
  switch (status) {
    case 'APPROVED':
      return {
        class: 'bg-emerald-50 text-emerald-700',
        label: isZh ? '已通过' : 'Approved',
        description: isZh ? '商家权限已启用，可以进入商家后台继续操作。' : 'Vendor access is active. You can use the vendor workspace now.'
      }
    case 'REJECTED':
      return {
        class: 'bg-red-50 text-red-700',
        label: isZh ? '已驳回' : 'Rejected',
        description: isZh ? '请根据审核意见修改后重新提交。' : 'Please update your application and resubmit.'
      }
    case 'DISABLED':
      return {
        class: 'bg-gray-100 text-gray-700',
        label: isZh ? '已停用' : 'Disabled',
        description: isZh ? '当前商家权限已被暂停。' : 'Vendor access is currently disabled.'
      }
    default:
      return {
        class: 'bg-amber-50 text-amber-700',
        label: isZh ? '待审核' : 'Pending Review',
        description: isZh ? '您的商家入驻申请已提交，正在等待后台审核。' : 'Your vendor application has been submitted and is waiting for review.'
      }
  }
})
const statusLabel = computed(() => statusMeta.value.label)
const statusDescription = computed(() => statusMeta.value.description)
const statusClass = computed(() => statusMeta.value.class)

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

function formatDate(value) {
  if (!value) return '-'
  return new Intl.DateTimeFormat(locale.value === 'zh' ? 'zh-CN' : 'en-US', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value))
}

function fitTextClass(value) {
  const length = Array.from(String(value || '')).length
  if (length >= 90) return 'text-[10px]'
  if (length >= 54) return 'text-[11px]'
  return 'text-sm'
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const user = JSON.parse(localStorage.getItem('misicheng-user') || 'null')
    const email = user?.email || ''
    const data = await getVendorApplication(email ? { email } : {})
    application.value = data.data || null
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.loadFailed
  } finally {
    loading.value = false
  }
}

onMounted(load)

const copy = {
  en: {
    title: 'Vendor Application',
    empty: 'No vendor application was found for your account.',
    apply: 'Submit Application',
    submittedAt: 'Submitted',
    reviewedAt: 'Reviewed',
    reviewNote: 'Review note',
    companyDetails: 'Company Details',
    companyName: 'Company Name',
    contactPerson: 'Contact Person',
    email: 'Email',
    phone: 'Phone',
    country: 'Country',
    address: 'Address',
    companyProfile: 'Company Profile',
    noDescription: 'No description provided.',
    files: 'Certification Files',
    open: 'Open',
    noFiles: 'No certification files uploaded.',
    loadFailed: 'Failed to load application.'
  },
  zh: {
    title: '商家入驻申请',
    empty: '当前账号没有找到商家入驻申请。',
    apply: '提交申请',
    submittedAt: '提交时间',
    reviewedAt: '审核时间',
    reviewNote: '审核备注',
    companyDetails: '企业信息',
    companyName: '公司名称',
    contactPerson: '联系人',
    email: '邮箱',
    phone: '电话',
    country: '国家/地区',
    address: '地址',
    companyProfile: '公司简介',
    noDescription: '暂无公司简介。',
    files: '资质文件',
    open: '查看',
    noFiles: '暂无上传资质文件。',
    loadFailed: '加载申请信息失败。'
  }
}
</script>
