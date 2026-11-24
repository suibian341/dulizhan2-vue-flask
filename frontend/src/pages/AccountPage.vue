<template>
  <div class="mx-auto max-w-7xl px-4 pt-24 py-12 lg:px-8">
    <nav class="mb-8 flex items-center gap-2 text-sm text-muted-foreground">
      <RouterLink :to="localized('/')" class="hover:text-foreground transition-colors">{{ t.home }}</RouterLink>
      <ChevronRight class="h-3.5 w-3.5" />
      <span class="font-medium text-foreground">{{ t.account }}</span>
    </nav>

    <div v-if="!user" class="mx-auto max-w-md rounded-2xl border bg-white p-8 text-center shadow-sm">
      <User class="mx-auto mb-4 h-10 w-10 text-sky-500" />
      <h1 class="text-2xl font-bold">{{ t.signInRequired }}</h1>
      <p class="mt-2 text-sm text-muted-foreground">{{ t.signInDesc }}</p>
      <RouterLink :to="localized('/login')" class="btn mt-6 h-10 rounded-md bg-primary px-6 text-primary-foreground hover:bg-primary/90">{{ t.signIn }}</RouterLink>
    </div>

    <template v-else>
      <div class="mb-8 flex flex-col justify-between gap-4 rounded-2xl border bg-white p-6 shadow-sm sm:flex-row sm:items-center">
        <div>
          <h1 class="text-2xl font-bold">{{ t.account }}</h1>
          <p class="mt-1 text-muted-foreground">{{ user.name || user.email }}</p>
        </div>
        <button class="btn btn-outline h-10 rounded-md px-4" @click="logout">{{ t.logout }}</button>
      </div>

      <div class="grid grid-cols-1 gap-6 md:grid-cols-3">
        <RouterLink :to="localized('/account/orders')" class="rounded-2xl border bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg">
          <ClipboardList class="mb-4 h-6 w-6 text-sky-500" />
          <h2 class="font-semibold">{{ t.inquiries }}</h2>
          <p class="mt-2 text-sm text-muted-foreground">{{ t.inquiriesDesc }}</p>
        </RouterLink>
        <RouterLink :to="localized('/account/wishlist')" class="rounded-2xl border bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg">
          <Heart class="mb-4 h-6 w-6 text-sky-500" />
          <h2 class="font-semibold">{{ t.wishlist }}</h2>
          <p class="mt-2 text-sm text-muted-foreground">{{ t.wishlistDesc }}</p>
        </RouterLink>
        <div class="rounded-2xl border bg-white p-6 shadow-sm">
          <ShieldCheck class="mb-4 h-6 w-6 text-sky-500" />
          <h2 class="font-semibold">{{ t.role }}</h2>
          <p class="mt-2 text-sm text-muted-foreground">{{ user.role }}</p>
        </div>
      </div>

      <form class="mt-6 max-w-xl space-y-4 rounded-2xl border bg-white p-6 shadow-sm" @submit.prevent="submitPasswordChange">
        <h2 class="font-semibold">{{ t.changePassword }}</h2>
        <input v-model.trim="passwordForm.oldPassword" class="input h-10" type="password" :placeholder="t.currentPassword" required />
        <input v-model.trim="passwordForm.newPassword" class="input h-10" type="password" :placeholder="t.newPassword" minlength="8" required />
        <input v-model.trim="passwordForm.confirmPassword" class="input h-10" type="password" :placeholder="t.confirmPassword" minlength="8" required />
        <p v-if="passwordError" class="text-sm text-red-600">{{ passwordError }}</p>
        <p v-if="passwordMessage" class="text-sm text-emerald-700">{{ passwordMessage }}</p>
        <button class="btn h-10 rounded-md bg-primary px-5 text-primary-foreground" :disabled="passwordSaving">
          {{ passwordSaving ? t.saving : t.changePassword }}
        </button>
      </form>
    </template>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { ChevronRight, ClipboardList, Heart, ShieldCheck, User } from 'lucide-vue-next'
import { changePassword } from '@/api'

const route = useRoute()
const router = useRouter()
const locale = computed(() => route.params.locale || 'en')
const user = ref(readUser())
const t = computed(() => copy[locale.value] || copy.en)
const passwordSaving = ref(false)
const passwordError = ref('')
const passwordMessage = ref('')
const passwordForm = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })

function readUser() {
  try {
    return JSON.parse(localStorage.getItem('misicheng-user') || 'null')
  } catch {
    return null
  }
}

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

function logout() {
  localStorage.removeItem('misicheng-user')
  user.value = null
  router.push(localized('/'))
}

async function submitPasswordChange() {
  passwordError.value = ''
  passwordMessage.value = ''
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordError.value = t.value.passwordMismatch
    return
  }
  passwordSaving.value = true
  try {
    await changePassword({ oldPassword: passwordForm.oldPassword, newPassword: passwordForm.newPassword })
    Object.assign(passwordForm, { oldPassword: '', newPassword: '', confirmPassword: '' })
    passwordMessage.value = t.value.passwordChanged
  } catch (err) {
    passwordError.value = err?.response?.data?.error || err?.message || t.value.passwordFailed
  } finally {
    passwordSaving.value = false
  }
}

const copy = {
  en: {
    home: 'Home',
    account: 'My Account',
    signInRequired: 'Sign in required',
    signInDesc: 'Log in to view your account, inquiries, and saved products.',
    signIn: 'Log In',
    logout: 'Log Out',
    inquiries: 'Inquiries',
    inquiriesDesc: 'Review your submitted product inquiries.',
    wishlist: 'Wishlist',
    wishlistDesc: 'View products saved from the storefront.',
    role: 'Account Role',
    changePassword: 'Change Password',
    currentPassword: 'Current Password',
    newPassword: 'New Password',
    confirmPassword: 'Confirm Password',
    saving: 'Saving...',
    passwordMismatch: 'The two new passwords do not match.',
    passwordChanged: 'Password updated.',
    passwordFailed: 'Password update failed.'
  },
  zh: {
    home: '首页',
    account: '我的账户',
    signInRequired: '请先登录',
    signInDesc: '登录后查看账户、询盘和收藏商品。',
    signIn: '登录',
    logout: '退出登录',
    inquiries: '询盘',
    inquiriesDesc: '查看您已提交的产品询盘。',
    wishlist: '收藏夹',
    wishlistDesc: '查看从商城收藏的产品。',
    role: '账户角色'
  }
}

Object.assign(copy.zh, {
  changePassword: '\u4fee\u6539\u5bc6\u7801',
  currentPassword: '\u539f\u5bc6\u7801',
  newPassword: '\u65b0\u5bc6\u7801',
  confirmPassword: '\u786e\u8ba4\u65b0\u5bc6\u7801',
  saving: '\u4fdd\u5b58\u4e2d...',
  passwordMismatch: '\u4e24\u6b21\u8f93\u5165\u7684\u65b0\u5bc6\u7801\u4e0d\u4e00\u81f4\u3002',
  passwordChanged: '\u5bc6\u7801\u5df2\u66f4\u65b0\u3002',
  passwordFailed: '\u4fee\u6539\u5bc6\u7801\u5931\u8d25\u3002'
})
</script>
