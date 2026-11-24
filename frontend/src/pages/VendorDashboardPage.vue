<template>
  <div class="mx-auto max-w-7xl px-4 pt-24 py-8 lg:px-8">
    <div class="space-y-6">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h1 class="text-2xl font-bold">{{ t.title }}</h1>
          <p class="text-sm text-muted-foreground">{{ subtitle }}</p>
        </div>
        <RouterLink :to="actionHref" class="btn gradient-bg h-10 px-5 text-white">
          <Plus class="mr-1 h-4 w-4" />
          {{ actionLabel }}
        </RouterLink>
      </div>

      <div class="rounded-2xl border bg-background p-6 shadow-sm">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div class="flex items-start gap-4">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-blue-700">
              <component :is="statusIcon" class="h-6 w-6" />
            </div>
            <div class="space-y-2">
              <div class="flex items-center gap-3">
                <h2 class="text-lg font-semibold">{{ t.applicationTitle }}</h2>
                <span class="rounded-full px-3 py-1 text-xs font-medium" :class="statusClass">
                  {{ statusLabel }}
                </span>
              </div>
              <p class="max-w-2xl text-sm text-muted-foreground">{{ statusDescription }}</p>
            </div>
          </div>
          <RouterLink :to="localized('/vendor/application')" class="btn btn-outline h-10 px-5">
            {{ t.trackApplication }}
          </RouterLink>
        </div>
      </div>

      <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div v-for="card in cards" :key="card.label" class="rounded-xl border bg-background p-5">
          <div class="flex items-center justify-between">
            <span class="text-sm text-muted-foreground">{{ card.label }}</span>
            <component :is="card.icon" class="h-5 w-5 text-muted-foreground" />
          </div>
          <div class="mt-3 text-3xl font-bold">{{ card.value }}</div>
        </div>
      </div>

      <div class="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <div class="rounded-2xl border bg-background p-6 shadow-sm">
          <h2 class="mb-4 text-lg font-semibold">{{ t.nextSteps }}</h2>
          <div class="space-y-3 text-sm text-muted-foreground">
            <div v-for="(step, index) in t.steps" :key="step.title" class="flex items-start gap-3">
              <span class="mt-0.5 rounded-md border px-2 py-0.5 text-xs">{{ index + 1 }}</span>
              <div>
                <p class="font-medium text-foreground">{{ step.title }}</p>
                <p>{{ step.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="rounded-2xl border bg-background p-6 shadow-sm">
          <h2 class="mb-4 text-lg font-semibold">{{ t.quickLinks }}</h2>
          <div class="grid gap-3">
            <RouterLink v-for="link in links" :key="link.href" :to="localized(link.href)" class="rounded-xl border px-4 py-3 text-sm font-medium transition-colors hover:bg-muted">
              {{ link.label }}
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { CheckCircle2, ClipboardCheck, Clock3, Package, Plus, ShieldX, XCircle } from 'lucide-vue-next'

import { getVendorApplication } from '@/api'

const route = useRoute()
const locale = computed(() => route.params.locale || 'en')
const application = ref(null)
const productsCount = ref(0)

const t = computed(() => copy[locale.value] || copy.en)
const statusMeta = computed(() => {
  const status = application.value?.status || 'PENDING'
  const isZh = locale.value === 'zh'
  switch (status) {
    case 'APPROVED':
      return {
        class: 'bg-emerald-50 text-emerald-700',
        label: isZh ? '已通过' : 'Approved',
        description: isZh ? '商家权限已启用，可以发布和管理商品。' : 'Vendor access is active. You can manage products now.',
        icon: CheckCircle2,
        actionLabel: isZh ? '发布商品' : 'Create Product',
        actionHref: '/vendor/products/new'
      }
    case 'REJECTED':
      return {
        class: 'bg-red-50 text-red-700',
        label: isZh ? '已驳回' : 'Rejected',
        description: isZh ? '请先查看申请页中的审核意见。' : 'Please review the note on the application page.',
        icon: XCircle,
        actionLabel: isZh ? '查看申请' : 'View Application',
        actionHref: '/vendor/application'
      }
    case 'DISABLED':
      return {
        class: 'bg-gray-100 text-gray-700',
        label: isZh ? '已停用' : 'Disabled',
        description: isZh ? '当前商家权限已暂停。' : 'Vendor access is currently disabled.',
        icon: ShieldX,
        actionLabel: isZh ? '查看申请' : 'View Application',
        actionHref: '/vendor/application'
      }
    default:
      return {
        class: 'bg-amber-50 text-amber-700',
        label: isZh ? '待审核' : 'Pending Review',
        description: isZh ? '入驻申请还在审核中，先查看审核状态。' : 'Your application is still under review.',
        icon: Clock3,
        actionLabel: isZh ? '查看申请' : 'View Application',
        actionHref: '/vendor/application'
      }
  }
})
const statusLabel = computed(() => statusMeta.value.label)
const statusDescription = computed(() => statusMeta.value.description)
const statusIcon = computed(() => statusMeta.value.icon)
const statusClass = computed(() => statusMeta.value.class)
const actionLabel = computed(() => statusMeta.value.actionLabel)
const actionHref = computed(() => localized(statusMeta.value.actionHref))
const subtitle = computed(() => {
  const company = application.value?.companyName
  return company ? `${company} ${t.value.workspaceSuffix}` : t.value.subtitle
})
const cards = computed(() => [
  { label: t.value.cards.total, value: productsCount.value, icon: Package },
  { label: t.value.cards.pending, value: application.value?.status === 'PENDING' ? 1 : 0, icon: Clock3 },
  { label: t.value.cards.active, value: application.value?.status === 'APPROVED' ? 1 : 0, icon: CheckCircle2 },
  { label: t.value.cards.rejected, value: application.value?.status === 'REJECTED' ? 1 : 0, icon: XCircle },
])
const links = computed(() => [
  { href: '/vendor/application', label: t.value.trackApplication },
  { href: '/vendor/register', label: t.value.applyAgain }
])

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

async function load() {
  try {
    const user = JSON.parse(localStorage.getItem('misicheng-user') || 'null')
    const data = await getVendorApplication(user?.email ? { email: user.email } : {})
    application.value = data.data || null
  } catch {
    application.value = null
  }
}

onMounted(load)

const copy = {
  en: {
    title: 'Vendor Center',
    subtitle: 'Track onboarding status and manage the vendor workspace.',
    workspaceSuffix: 'workspace',
    applicationTitle: 'Application Status',
    trackApplication: 'View Application',
    applyAgain: 'Submit Application',
    nextSteps: 'Next Steps',
    quickLinks: 'Quick Links',
    cards: {
      total: 'Products',
      pending: 'Pending',
      active: 'Active',
      rejected: 'Rejected'
    },
    steps: [
      { title: 'Submit application', description: 'Complete the company profile and supporting files.' },
      { title: 'Admin review', description: 'The admin team reviews your vendor profile.' },
      { title: 'Publish products', description: 'Approved vendors can create products and send them to review.' }
    ]
  },
  zh: {
    title: '商家中心',
    subtitle: '查看入驻状态并管理商家工作台。',
    workspaceSuffix: '工作台',
    applicationTitle: '入驻状态',
    trackApplication: '查看申请',
    applyAgain: '重新提交申请',
    nextSteps: '下一步',
    quickLinks: '快捷入口',
    cards: {
      total: '商品数',
      pending: '待审核',
      active: '已启用',
      rejected: '已驳回'
    },
    steps: [
      { title: '提交申请', description: '完善企业资料和附件文件。' },
      { title: '后台审核', description: '管理员会审核你的商家资料。' },
      { title: '发布商品', description: '通过后可以创建商品并提交审核。' }
    ]
  }
}
</script>
