<template>
  <div v-if="isLogin" class="grid w-full gap-8 lg:grid-cols-[1.05fr_0.95fr]">
    <div class="rounded-2xl border bg-background p-6 shadow-sm lg:p-8">
      <div class="mb-8 flex items-start gap-4">
        <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white">
          <Store class="h-6 w-6" />
        </div>
        <div>
          <h1 class="text-2xl font-semibold tracking-tight">{{ copy.signInTitle }}</h1>
          <p class="mt-2 max-w-xl text-sm leading-6 text-muted-foreground">{{ copy.signInDesc }}</p>
        </div>
      </div>

      <form class="space-y-5" @submit.prevent="submitLogin">
        <div v-if="error" class="rounded-xl border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-600">{{ error }}</div>
        <div class="space-y-2">
          <label for="vendor-email" class="text-sm font-medium">{{ authCopy.email }}</label>
          <input id="vendor-email" v-model.trim="loginForm.email" type="email" class="input h-10" required />
        </div>
        <div class="space-y-2">
          <label for="vendor-password" class="text-sm font-medium">{{ authCopy.password }}</label>
          <div class="relative">
            <input id="vendor-password" v-model="loginForm.password" :type="showPassword ? 'text' : 'password'" class="input h-10 pr-10" required />
            <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground" @click="showPassword = !showPassword">
              <EyeOff v-if="showPassword" class="h-4 w-4" />
              <Eye v-else class="h-4 w-4" />
            </button>
          </div>
        </div>
        <button type="submit" class="btn h-10 w-full bg-primary text-primary-foreground hover:bg-primary/90" :disabled="loading">
          {{ loading ? copy.signingIn : copy.signIn }}
        </button>
      </form>

      <p class="mt-6 text-sm text-muted-foreground">
        {{ copy.registerHint }}
        <RouterLink :to="localized('/vendor/register')" class="font-medium text-foreground underline-offset-4 hover:underline">{{ copy.registerLink }}</RouterLink>
      </p>
    </div>

    <div class="space-y-6">
      <div class="rounded-2xl border bg-background p-6 shadow-sm">
        <h2 class="font-semibold">{{ copy.whatYouCanDo }}</h2>
        <ul class="mt-4 space-y-3 text-sm text-muted-foreground">
          <li v-for="item in copy.capabilities" :key="item">{{ item }}</li>
        </ul>
      </div>
      <div class="rounded-2xl border bg-background p-6 shadow-sm">
        <h2 class="font-semibold">{{ copy.policyTitle }}</h2>
        <p class="mt-3 text-sm leading-6 text-muted-foreground">{{ copy.policyDescription }}</p>
      </div>
    </div>
  </div>

  <div v-else class="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
    <div class="rounded-2xl border bg-background p-6 shadow-sm lg:p-8">
      <div class="mb-8 flex items-start gap-4">
        <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white">
          <Store class="h-6 w-6" />
        </div>
        <div>
          <h1 class="text-2xl font-semibold tracking-tight">{{ copy.registerTitle }}</h1>
          <p class="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">{{ copy.registerDesc }}</p>
        </div>
      </div>

      <div v-if="error" class="mb-6 rounded-xl border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-600">{{ error }}</div>
      <div v-if="submitted" class="mb-6 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ copy.submitted }}</div>

      <form class="space-y-6" @submit.prevent="submitRegister">
        <section class="space-y-4">
          <h2 class="text-sm font-semibold uppercase tracking-[0.08em] text-muted-foreground">{{ copy.account }}</h2>
          <div class="grid gap-4 md:grid-cols-2">
            <div class="space-y-2">
              <label class="text-sm font-medium" for="vendor-name">{{ authCopy.name }}</label>
              <input id="vendor-name" v-model.trim="registerForm.name" class="input h-10" required />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium" for="vendor-register-email">{{ authCopy.email }}</label>
              <input id="vendor-register-email" v-model.trim="registerForm.email" type="email" class="input h-10" required />
            </div>
          </div>
          <div class="grid gap-4 md:grid-cols-2">
            <div class="space-y-2">
              <label class="text-sm font-medium" for="vendor-register-password">{{ authCopy.password }}</label>
              <input id="vendor-register-password" v-model="registerForm.password" type="password" class="input h-10" required minlength="8" />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium" for="vendor-confirm-password">{{ authCopy.confirmPassword }}</label>
              <input id="vendor-confirm-password" v-model="registerForm.confirmPassword" type="password" class="input h-10" required minlength="8" />
            </div>
          </div>
        </section>

        <section class="space-y-4">
          <h2 class="text-sm font-semibold uppercase tracking-[0.08em] text-muted-foreground">{{ copy.company }}</h2>
          <div class="grid gap-4 md:grid-cols-2">
            <div class="space-y-2">
              <label class="text-sm font-medium" for="company-name">{{ copy.companyName }}</label>
              <input id="company-name" v-model.trim="registerForm.companyName" class="input h-10" required />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium" for="contact-person">{{ copy.contactPerson }}</label>
              <input id="contact-person" v-model.trim="registerForm.contactPerson" class="input h-10" required />
            </div>
          </div>
          <div class="grid gap-4 md:grid-cols-2">
            <div class="space-y-2">
              <label class="text-sm font-medium" for="vendor-phone">{{ copy.phone }}</label>
              <input id="vendor-phone" v-model.trim="registerForm.phone" class="input h-10" />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium" for="vendor-country">{{ copy.country }}</label>
              <input id="vendor-country" v-model.trim="registerForm.country" class="input h-10" />
            </div>
          </div>
          <div class="space-y-2">
            <label class="text-sm font-medium" for="vendor-address">{{ copy.address }}</label>
            <input id="vendor-address" v-model.trim="registerForm.address" class="input h-10" />
          </div>
          <div class="space-y-2">
            <label class="text-sm font-medium" for="vendor-profile">{{ copy.profile }}</label>
            <textarea id="vendor-profile" v-model.trim="registerForm.description" class="textarea" rows="5" :placeholder="copy.profilePlaceholder"></textarea>
          </div>
        </section>

        <section class="space-y-4">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 class="text-sm font-semibold uppercase tracking-[0.08em] text-muted-foreground">{{ copy.filesSection }}</h2>
              <p class="mt-1 text-sm text-muted-foreground">{{ copy.fileHint }}</p>
            </div>
            <label class="btn btn-outline h-10 cursor-pointer px-4">
              <Upload class="h-4 w-4" />
              {{ uploading ? copy.uploading : copy.upload }}
              <input type="file" accept=".pdf,.jpg,.jpeg,.png,.webp" class="hidden" :disabled="uploading" @change="handleUpload" />
            </label>
          </div>

          <div v-if="files.length" class="grid gap-3 sm:grid-cols-2">
            <div v-for="(file, index) in files" :key="`${file.url}-${index}`" class="flex items-center justify-between rounded-xl border bg-muted/30 px-4 py-3">
              <div class="flex min-w-0 items-center gap-3">
                <FileText class="h-4 w-4 shrink-0 text-muted-foreground" />
                <div class="min-w-0">
                  <p class="whitespace-normal break-words font-medium leading-snug" :class="fitTextClass(file.name)">{{ file.name }}</p>
                  <p class="whitespace-normal break-all text-muted-foreground" :class="fitTextClass(file.url, true)">{{ file.url }}</p>
                </div>
              </div>
              <button type="button" class="text-sm text-muted-foreground hover:text-foreground" @click="files.splice(index, 1)">
                {{ copy.remove }}
              </button>
            </div>
          </div>
          <div v-else class="rounded-xl border border-dashed px-4 py-6 text-sm text-muted-foreground">
            {{ copy.noFiles }}
          </div>
        </section>

        <div class="flex flex-col gap-3 border-t pt-6 sm:flex-row sm:items-center sm:justify-between">
          <p class="text-sm text-muted-foreground">
            {{ copy.loginHint }}
            <RouterLink :to="localized('/vendor/login')" class="font-medium text-foreground underline-offset-4 hover:underline">{{ copy.login }}</RouterLink>
          </p>
          <button type="submit" class="btn h-10 bg-primary px-6 text-primary-foreground hover:bg-primary/90" :disabled="loading">
            {{ loading ? copy.submitting : copy.submit }}
          </button>
        </div>
      </form>
    </div>

    <div class="space-y-6">
      <div class="rounded-2xl border bg-background p-6 shadow-sm">
        <div class="mb-4 flex items-center gap-3">
          <ShieldCheck class="h-5 w-5 text-blue-600" />
          <h2 class="font-semibold">{{ copy.reviewFlow }}</h2>
        </div>
        <div class="space-y-4 text-sm text-muted-foreground">
          <div v-for="(step, index) in copy.reviewSteps" :key="step" class="flex items-start gap-3">
            <span class="mt-0.5 rounded-md border px-2 py-0.5 text-xs">{{ index + 1 }}</span>
            <p class="font-medium text-foreground">{{ step }}</p>
          </div>
        </div>
      </div>
      <div class="rounded-2xl border bg-background p-6 shadow-sm">
        <h2 class="font-semibold">{{ copy.reviewTargets }}</h2>
        <ul class="mt-4 space-y-3 text-sm text-muted-foreground">
          <li v-for="item in copy.reviewItems" :key="item">{{ item }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { Eye, EyeOff, FileText, ShieldCheck, Store, Upload } from 'lucide-vue-next'

import { loginUser, registerVendor, uploadVendorApplicationFile } from '@/api'

const props = defineProps({
  isLogin: { type: Boolean, required: true },
  copy: { type: Object, required: true },
  authCopy: { type: Object, required: true }
})
const emit = defineEmits(['done'])
const route = useRoute()
const locale = computed(() => route.params.locale || 'en')
const loading = ref(false)
const error = ref('')
const submitted = ref(false)
const showPassword = ref(false)
const uploading = ref(false)
const files = ref([])
const loginForm = reactive({ email: '', password: '' })
const registerForm = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
  companyName: '',
  contactPerson: '',
  phone: '',
  country: '',
  address: '',
  description: ''
})

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

function fitTextClass(value, secondary = false) {
  const length = Array.from(String(value || '')).length
  if (secondary) {
    if (length >= 90) return 'text-[10px]'
    if (length >= 54) return 'text-[11px]'
    return 'text-xs'
  }
  if (length >= 48) return 'text-[10px]'
  if (length >= 32) return 'text-[11px]'
  if (length >= 22) return 'text-xs'
  return 'text-sm'
}

async function submitLogin() {
  error.value = ''
  loading.value = true
  try {
    const data = await loginUser({ email: loginForm.email, password: loginForm.password, type: 'vendor' })
    emit('done', data.user)
  } catch (err) {
    error.value = err?.response?.data?.error || props.authCopy.invalidCredentials
  } finally {
    loading.value = false
  }
}

async function handleUpload(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  uploading.value = true
  error.value = ''
  try {
    const data = await uploadVendorApplicationFile(file)
    files.value.push({ name: data.name || file.name, url: data.url })
  } catch (err) {
    error.value = err?.response?.data?.error || props.copy.uploadFailed
  } finally {
    uploading.value = false
  }
}

async function submitRegister() {
  error.value = ''
  if (registerForm.password !== registerForm.confirmPassword) {
    error.value = props.authCopy.passwordMismatch
    return
  }
  loading.value = true
  try {
    const data = await registerVendor({
      ...registerForm,
      certificationFiles: files.value.map(file => file.url)
    })
    submitted.value = true
    window.setTimeout(() => emit('done', data.user), 900)
  } catch (err) {
    error.value = err?.response?.data?.error || props.authCopy.registerFailed
  } finally {
    loading.value = false
  }
}
</script>
