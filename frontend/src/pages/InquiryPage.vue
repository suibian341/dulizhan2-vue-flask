<template>
  <div class="container mx-auto max-w-7xl px-4 pt-24 py-8">
    <nav class="mb-6 flex items-center gap-2 text-sm text-muted-foreground">
      <RouterLink :to="localized('/')" class="transition-colors hover:text-foreground">{{ t.common.home }}</RouterLink>
      <span>/</span>
      <span class="text-foreground">{{ t.page.breadcrumb }}</span>
    </nav>

    <div v-if="!user" class="flex flex-col items-center justify-center py-20 text-center">
      <User class="mb-4 size-16 text-muted-foreground/40" />
      <h2 class="mb-2 text-xl font-semibold">{{ t.page.loginRequired }}</h2>
      <p class="mb-6 text-muted-foreground">{{ t.page.loginRequiredDesc }}</p>
      <RouterLink :to="localized('/login?redirect=/inquiry')" class="gradient-bg inline-flex h-9 items-center justify-center rounded-md px-4 py-2 text-sm font-medium text-white">
        {{ t.page.loginButton }}
      </RouterLink>
    </div>

    <div v-else-if="submitted" class="flex flex-col items-center justify-center py-20 text-center">
      <CheckCircle2 class="mb-4 size-16 text-green-500" />
      <h2 class="mb-2 text-xl font-semibold">{{ t.page.submitted }}</h2>
      <p class="mb-6 text-muted-foreground">{{ t.inquiry.successMessage }}</p>
      <div class="flex flex-wrap justify-center gap-3">
        <RouterLink :to="localized(`/account/inquiries/${submitted.id}`)" class="inline-flex h-9 items-center justify-center rounded-md border bg-background px-4 py-2 text-sm font-medium shadow-xs transition-all hover:bg-accent hover:text-accent-foreground">
          {{ t.page.viewInquiry }}
        </RouterLink>
        <RouterLink :to="localized('/shop')" class="gradient-bg inline-flex h-9 items-center justify-center rounded-md px-4 py-2 text-sm font-medium text-white">
          {{ t.inquiry.continueBrowsing }}
        </RouterLink>
        <RouterLink :to="localized('/contact')" class="inline-flex h-9 items-center justify-center rounded-md border bg-background px-4 py-2 text-sm font-medium shadow-xs transition-all hover:bg-accent hover:text-accent-foreground">
          {{ t.contactSales }}
        </RouterLink>
      </div>
    </div>

    <div v-else-if="!inquiry.items.length" class="flex flex-col items-center justify-center py-20">
      <ShoppingCart class="mb-4 size-16 text-muted-foreground/40" />
      <h2 class="mb-2 text-xl font-semibold">{{ t.page.emptyTitle }}</h2>
      <p class="mb-6 text-muted-foreground">{{ t.page.emptyDesc }}</p>
      <RouterLink :to="localized('/shop')" class="gradient-bg inline-flex h-9 items-center justify-center rounded-md px-4 py-2 text-sm font-medium text-white">
        {{ t.page.browseShop }}
      </RouterLink>
    </div>

    <template v-else>
      <div class="mb-6 flex items-center gap-3">
        <RouterLink :to="localized('/shop')" class="inline-flex size-9 items-center justify-center rounded-md transition-all hover:bg-accent hover:text-accent-foreground">
          <ChevronLeft class="size-5" />
        </RouterLink>
        <h1 class="text-2xl font-bold">{{ t.page.pageTitle }}</h1>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
          <div class="space-y-4 lg:col-span-2">
            <h2 class="text-lg font-semibold">{{ t.page.selectedProducts }} ({{ inquiry.items.length }})</h2>
            <div class="space-y-4">
              <div v-for="item in inquiry.items" :key="item.id" class="flex gap-4 rounded-lg border bg-card p-4">
                <RouterLink :to="item.slug ? localized(`/product/${item.slug}`) : localized('/shop')" class="relative size-20 shrink-0 overflow-hidden rounded-md bg-muted">
                  <img :src="item.image || '/images/products/product-1.png'" :alt="item.name" class="h-full w-full object-contain p-1" />
                </RouterLink>

                <div class="flex flex-1 flex-col gap-2">
                  <div class="flex items-start justify-between gap-2">
                    <div>
                      <RouterLink :to="item.slug ? localized(`/product/${item.slug}`) : localized('/shop')" class="font-medium leading-tight">
                        {{ item.name }}
                      </RouterLink>
                      <p v-if="Object.keys(item.options || {}).length" class="mt-1 text-xs text-muted-foreground">
                        {{ formatOptions(item.options) }}
                      </p>
                      <p class="mt-1 text-sm text-muted-foreground">{{ t.page.refPrice }} {{ cartItemPrice(item) }}</p>
                    </div>
                    <button
                      type="button"
                      class="inline-flex size-6 shrink-0 items-center justify-center rounded-md text-muted-foreground transition-all hover:bg-accent hover:text-destructive"
                      @click="inquiry.removeItem(item.id)"
                    >
                      <Trash2 class="size-4" />
                    </button>
                  </div>

                  <div class="flex items-center gap-4">
                    <div class="flex items-center gap-1">
                      <button
                        type="button"
                        class="inline-flex size-6 items-center justify-center rounded-md border bg-background text-xs shadow-xs transition-all hover:bg-accent hover:text-accent-foreground disabled:pointer-events-none disabled:opacity-50"
                        :disabled="item.quantity <= 1"
                        @click="inquiry.updateQuantity(item.id, item.quantity - 1)"
                      >
                        <Minus class="size-3" />
                      </button>
                      <span class="w-8 text-center text-sm font-medium">{{ item.quantity }}</span>
                      <button
                        type="button"
                        class="inline-flex size-6 items-center justify-center rounded-md border bg-background text-xs shadow-xs transition-all hover:bg-accent hover:text-accent-foreground disabled:pointer-events-none disabled:opacity-50"
                        :disabled="item.quantity >= item.maxQuantity"
                        @click="inquiry.updateQuantity(item.id, item.quantity + 1)"
                      >
                        <Plus class="size-3" />
                      </button>
                    </div>

                    <input
                      :value="item.note || ''"
                      :placeholder="t.page.notePlaceholder"
                      class="flex h-7 flex-1 rounded-md border border-input bg-transparent px-3 py-1 text-xs shadow-xs transition-colors placeholder:text-muted-foreground outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]"
                      @input="inquiry.updateNote(item.id, $event.target.value)"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="space-y-6 lg:col-span-1">
            <div class="space-y-4 rounded-lg border bg-card p-5">
              <h2 class="text-lg font-semibold">{{ t.page.contactSection }}</h2>

              <div class="space-y-1.5">
                <label for="contactName" class="text-sm font-medium">{{ t.page.nameRequired }} <span class="text-destructive">*</span></label>
                <input id="contactName" v-model.trim="form.contactName" class="form-input" :placeholder="t.page.namePlaceholder" />
                <p v-if="errors.contactName" class="text-xs text-destructive">{{ errors.contactName }}</p>
              </div>

              <div class="space-y-1.5">
                <label for="companyName" class="text-sm font-medium">{{ t.page.companyLabel }}</label>
                <input id="companyName" v-model.trim="form.companyName" class="form-input" :placeholder="t.page.companyPlaceholder" />
              </div>

              <div class="space-y-1.5">
                <label for="email" class="text-sm font-medium">{{ t.page.emailRequired }} <span class="text-destructive">*</span></label>
                <input id="email" v-model.trim="form.email" type="email" class="form-input bg-muted/40" readonly />
                <p v-if="errors.email" class="text-xs text-destructive">{{ errors.email }}</p>
              </div>

              <div class="space-y-1.5">
                <label for="phone" class="text-sm font-medium">{{ t.inquiry.phone }}</label>
                <input id="phone" v-model.trim="form.phone" class="form-input" :placeholder="t.page.phonePlaceholder" />
              </div>

              <div class="space-y-1.5">
                <label for="country" class="text-sm font-medium">{{ t.page.countryLabel }}</label>
                <input id="country" v-model.trim="form.country" class="form-input" :placeholder="t.page.countryPlaceholder" />
              </div>
            </div>

            <div class="h-px bg-border"></div>

            <div class="space-y-4 rounded-lg border bg-card p-5">
              <h2 class="text-lg font-semibold">{{ t.page.requirementsSection }}</h2>

              <div class="space-y-1.5">
                <label for="quantityRequirements" class="text-sm font-medium">{{ t.page.quantityLabel }}</label>
                <textarea id="quantityRequirements" v-model.trim="form.quantityRequirements" class="form-textarea" :placeholder="t.page.quantityPlaceholder" rows="3"></textarea>
              </div>

              <div class="space-y-1.5">
                <label for="customizationNeeds" class="text-sm font-medium">{{ t.page.customLabel }}</label>
                <textarea id="customizationNeeds" v-model.trim="form.customizationNeeds" class="form-textarea" :placeholder="t.page.customPlaceholder" rows="3"></textarea>
              </div>

              <div class="space-y-1.5">
                <label for="expectedDeliveryTime" class="text-sm font-medium">{{ t.page.deliveryLabel }}</label>
                <input id="expectedDeliveryTime" v-model.trim="form.expectedDeliveryTime" class="form-input" :placeholder="t.page.deliveryPlaceholder" />
              </div>

              <div class="space-y-1.5">
                <label for="message" class="text-sm font-medium">{{ t.page.messageLabel }}</label>
                <textarea id="message" v-model.trim="form.message" class="form-textarea" :placeholder="t.page.messagePlaceholder" rows="3"></textarea>
              </div>
            </div>

            <button
              type="submit"
              class="gradient-bg inline-flex h-10 w-full items-center justify-center gap-2 rounded-md px-6 text-sm font-medium text-white transition-all disabled:pointer-events-none disabled:opacity-50"
              :disabled="submitting"
            >
              <span v-if="submitting" class="size-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
              <Send v-else class="size-4" />
              {{ submitting ? t.page.submitting : t.page.submitButton }}
            </button>
            <p v-if="error" class="text-sm text-destructive">{{ error }}</p>
          </div>
        </div>
      </form>
    </template>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import {
  CheckCircle2,
  ChevronLeft,
  Minus,
  Plus,
  Send,
  ShoppingCart,
  Trash2,
  User
} from 'lucide-vue-next'

import { currentUser, submitInquiry } from '@/api'
import { translatedCopy } from '@/i18n'
import { useInquiryStore } from '@/stores/inquiry'
import { useUiStore } from '@/stores/ui'
import { price } from '@/utils'
import { formatVariantOptions } from '@/variantOptions'

const route = useRoute()
const inquiry = useInquiryStore()
const ui = useUiStore()
const user = ref(currentUser())
const submitting = ref(false)
const error = ref('')
const submitted = ref(null)
const errors = reactive({})
const form = reactive({
  contactName: user.value?.name || user.value?.email || '',
  companyName: '',
  email: user.value?.email || '',
  phone: '',
  country: '',
  quantityRequirements: '',
  customizationNeeds: '',
  expectedDeliveryTime: '',
  message: ''
})

const locale = computed(() => route.params.locale || 'en')
const t = computed(() => translatedCopy(locale.value, copy, source => ({
  common: { home: source.common?.home },
  contactSales: source.footer?.contact,
  inquiry: {
    phone: source.inquiry?.phone,
    successMessage: source.inquiry?.successMessage,
    continueBrowsing: source.inquiry?.continueBrowsing
  },
  page: source.inquiryPage
})))

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

function formatOptions(options) {
  return formatVariantOptions(options, [], locale.value === 'zh' ? 'zh' : 'en')
}

function cartItemPrice(item) {
  if (item?.priceNegotiable || Number(item?.price || 0) <= 0) return t.value.page.negotiable
  return price(item.price, ui.currency)
}

function validate() {
  errors.contactName = ''
  errors.email = ''
  form.email = user.value?.email || form.email
  if (!form.contactName) errors.contactName = t.value.page.nameError
  if (!form.email) errors.email = t.value.page.emailError
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errors.email = t.value.page.emailInvalid
  return !errors.contactName && !errors.email
}

async function handleSubmit() {
  error.value = ''
  if (!user.value) {
    error.value = t.value.page.loginRequiredDesc
    return
  }
  if (!validate()) return
  if (!inquiry.items.length) {
    error.value = t.value.page.addProductsFirst
    return
  }

  submitting.value = true
  try {
    const payload = {
      contact: { ...form, email: user.value.email },
      items: inquiry.items.map(item => ({
        productId: item.productId,
        variantId: item.variantId,
        name: item.name,
        image: item.image,
        price: item.price,
        quantity: item.quantity,
        options: item.options,
        note: item.note
      }))
    }
    const data = await submitInquiry(payload)
    submitted.value = data.data || data.inquiry
    inquiry.clear()
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.page.submitFailedDesc
  } finally {
    submitting.value = false
  }
}

const copy = {
  en: {
    common: { home: 'Home' },
    contactSales: 'Contact Sales',
    inquiry: {
      phone: 'Phone',
      successMessage: 'Thank you for your inquiry. We will respond within 1-2 business days.',
      continueBrowsing: 'Continue Browsing'
    },
    page: {
      breadcrumb: 'Submit Inquiry',
      emptyTitle: 'Cart is empty',
      emptyDesc: "You haven't added any products to the cart yet",
      browseShop: 'Browse Products',
      pageTitle: 'Submit Inquiry',
      selectedProducts: 'Selected Products',
      refPrice: 'Ref. Price:',
      negotiable: 'Negotiable',
      notePlaceholder: 'Note (optional)',
      contactSection: 'Contact Information',
      nameRequired: 'Name',
      namePlaceholder: 'Enter your name',
      companyLabel: 'Company Name',
      companyPlaceholder: 'Company name (optional)',
      emailRequired: 'Email',
      phonePlaceholder: 'Phone (optional)',
      countryLabel: 'Country/Region',
      countryPlaceholder: 'Country or region (optional)',
      requirementsSection: 'Requirements',
      quantityLabel: 'Quantity Requirements',
      quantityPlaceholder: 'Describe your quantity needs, e.g.: initial 500 units, then 1000 units/month',
      customLabel: 'Customization Needs',
      customPlaceholder: 'Describe your customization requirements if needed',
      deliveryLabel: 'Expected Delivery Time',
      deliveryPlaceholder: 'e.g.: within 2 weeks, within 1 month',
      messageLabel: 'Additional Notes',
      messagePlaceholder: 'Any other information to add',
      submitting: 'Submitting...',
      submitButton: 'Submit Inquiry',
      submitted: 'Inquiry Submitted!',
      viewInquiry: 'View Inquiry',
      loginRequired: 'Please log in first',
      loginRequiredDesc: 'Log in to submit an inquiry',
      loginButton: 'Log In',
      addProductsFirst: 'Please add products to the cart first',
      submitFailedDesc: 'Failed to submit inquiry, please try again later',
      nameError: 'Please enter your name',
      emailError: 'Please enter your email',
      emailInvalid: 'Please enter a valid email address'
    }
  },
  zh: {
    common: { home: '首页' },
    contactSales: '联系销售',
    inquiry: {
      phone: '电话',
      successMessage: '感谢您的询价，我们会在 1-2 个工作日内回复。',
      continueBrowsing: '继续浏览'
    },
    page: {
      breadcrumb: '提交询价',
      emptyTitle: '购物车是空的',
      emptyDesc: '您还没有添加商品到购物车',
      browseShop: '浏览产品',
      pageTitle: '提交询价',
      selectedProducts: '已选产品',
      refPrice: '参考价:',
      negotiable: '面议',
      notePlaceholder: '备注（可选）',
      contactSection: '联系信息',
      nameRequired: '姓名',
      namePlaceholder: '请输入您的姓名',
      companyLabel: '公司名称',
      companyPlaceholder: '公司名称（可选）',
      emailRequired: '邮箱',
      phonePlaceholder: '电话（可选）',
      countryLabel: '国家/地区',
      countryPlaceholder: '国家或地区（可选）',
      requirementsSection: '需求说明',
      quantityLabel: '数量要求',
      quantityPlaceholder: '描述数量需求，例如：首批 500 件，后续每月 1000 件',
      customLabel: '定制需求',
      customPlaceholder: '如有定制需求请说明',
      deliveryLabel: '期望交期',
      deliveryPlaceholder: '例如：2 周内、1 个月内',
      messageLabel: '补充说明',
      messagePlaceholder: '其他需要补充的信息',
      submitting: '提交中...',
      submitButton: '提交询价',
      submitted: '询价已提交！',
      viewInquiry: '查看询价',
      loginRequired: '请先登录',
      loginRequiredDesc: '登录后才能提交询价',
      loginButton: '登录',
      addProductsFirst: '请先添加商品到购物车',
      submitFailedDesc: '提交询价失败，请稍后重试',
      nameError: '请输入姓名',
      emailError: '请输入邮箱',
      emailInvalid: '请输入有效邮箱地址'
    }
  }
}
</script>

<style scoped>
.form-input {
  display: flex;
  height: 2.25rem;
  width: 100%;
  border-radius: 0.375rem;
  border: 1px solid var(--input);
  background: transparent;
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  outline: none;
}

.form-textarea {
  display: flex;
  width: 100%;
  min-height: 80px;
  border-radius: 0.375rem;
  border: 1px solid var(--input);
  background: transparent;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  outline: none;
  resize: vertical;
}
</style>
