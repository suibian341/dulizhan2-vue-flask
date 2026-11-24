<template>
  <div class="flex min-h-[70vh] items-center justify-center px-4 pt-24 py-12">
    <div class="w-full max-w-md space-y-8">
      <nav class="flex items-center gap-2 text-sm text-muted-foreground">
        <RouterLink :to="localized('/')" class="transition-colors hover:text-foreground">{{ t.home }}</RouterLink>
        <ChevronRight class="h-3.5 w-3.5" />
        <span class="font-medium text-foreground">{{ t.forgotPasswordTitle }}</span>
      </nav>

      <div v-if="submitted" class="text-center">
        <div class="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
          <Mail class="h-8 w-8 text-green-600" />
        </div>
        <h1 class="text-2xl font-bold">{{ t.emailSent }}</h1>
        <p class="mt-3 text-muted-foreground">{{ t.emailSentDesc.replace('{email}', email) }}</p>
        <p class="mt-2 text-sm text-muted-foreground">{{ t.linkExpiry }}</p>

        <div class="mt-8 space-y-3">
          <button class="btn btn-outline h-10 w-full" type="button" @click="resetForm">{{ t.resend }}</button>
          <RouterLink :to="localized('/login')" class="btn btn-ghost h-10 w-full">
            <ArrowLeft class="mr-2 h-4 w-4" />
            {{ t.backToLogin }}
          </RouterLink>
        </div>
      </div>

      <template v-else>
        <div class="text-center">
          <div class="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
            <Mail class="h-8 w-8 text-primary" />
          </div>
          <h1 class="text-2xl font-bold">{{ t.forgotPasswordTitle }}</h1>
          <p class="mt-3 text-muted-foreground">{{ t.forgotPasswordDesc }}</p>
        </div>

        <form class="space-y-6" @submit.prevent="submit">
          <div class="space-y-2">
            <label for="reset-email" class="text-sm font-medium">{{ t.email }}</label>
            <input id="reset-email" v-model.trim="email" type="email" class="input h-10" :placeholder="t.emailPlaceholder" required autocomplete="email" />
          </div>
          <button type="submit" class="btn h-10 w-full bg-primary text-primary-foreground hover:bg-primary/90" :disabled="loading">
            {{ loading ? t.sending : t.sendResetLink }}
          </button>
        </form>

        <div class="text-center">
          <RouterLink :to="localized('/login')" class="inline-flex items-center text-sm text-muted-foreground hover:text-foreground">
            <ArrowLeft class="mr-1 h-4 w-4" />
            {{ t.backToLogin }}
          </RouterLink>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { ArrowLeft, ChevronRight, Mail } from 'lucide-vue-next'

const route = useRoute()
const locale = computed(() => route.params.locale || 'en')
const t = computed(() => copy[locale.value] || copy.en)
const email = ref('')
const submitted = ref(false)
const loading = ref(false)

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

function submit() {
  loading.value = true
  window.setTimeout(() => {
    loading.value = false
    submitted.value = true
  }, 1000)
}

function resetForm() {
  submitted.value = false
  email.value = ''
}

const copy = {
  en: {
    home: 'Home',
    forgotPasswordTitle: 'Forgot Password?',
    forgotPasswordDesc: "Enter your email and we'll send you a password reset link.",
    email: 'Email',
    emailPlaceholder: 'Enter your email',
    sendResetLink: 'Send Reset Link',
    sending: 'Sending...',
    emailSent: 'Email Sent',
    emailSentDesc: "We've sent a password reset link to {email}. Please check your inbox (including spam folder).",
    linkExpiry: 'The link is valid for 24 hours.',
    resend: 'Resend',
    backToLogin: 'Back to Login'
  },
  zh: {
    home: '首页',
    forgotPasswordTitle: '忘记密码？',
    forgotPasswordDesc: '请输入您的邮箱，我们将向您发送密码重置链接。',
    email: '邮箱',
    emailPlaceholder: '请输入您的邮箱',
    sendResetLink: '发送重置链接',
    sending: '发送中...',
    emailSent: '邮件已发送',
    emailSentDesc: '我们已向 {email} 发送密码重置链接，请查看收件箱（包括垃圾邮件）。',
    linkExpiry: '链接有效期为 24 小时。',
    resend: '重新发送',
    backToLogin: '返回登录'
  }
}
</script>
