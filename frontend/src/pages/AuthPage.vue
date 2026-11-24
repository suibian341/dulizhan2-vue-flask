<template>
  <div class="flex min-h-[70vh] items-center justify-center px-4 pt-24 py-12">
    <div class="w-full max-w-5xl space-y-8">
      <div v-if="!isVendorAuth" class="mx-auto w-full max-w-md space-y-8">
        <div class="text-center">
          <h1 class="text-3xl font-bold">{{ pageTitle }}</h1>
          <p class="mt-2 text-muted-foreground">{{ pageSubtitle }}</p>
        </div>

        <button v-if="!isAdminAuth" class="btn btn-outline h-10 w-full" type="button">
          <svg class="mr-2 h-4 w-4" viewBox="0 0 24 24">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4" />
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
          </svg>
          {{ isLogin ? t.googleLogin : t.googleRegister }}
        </button>

        <div v-if="!isAdminAuth" class="relative">
          <div class="absolute inset-0 flex items-center"><span class="w-full border-t"></span></div>
          <div class="relative flex justify-center text-xs uppercase">
            <span class="bg-background px-2 text-muted-foreground">{{ isLogin ? t.orEmailLogin : t.orEmailRegister }}</span>
          </div>
        </div>

        <form class="space-y-4" @submit.prevent="submitUser">
          <div v-if="error" class="rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-600">{{ error }}</div>
          <div v-if="!isLogin" class="space-y-2">
            <label for="name" class="text-sm font-medium">{{ t.name }}</label>
            <input id="name" v-model.trim="form.name" class="input h-10" :placeholder="t.namePlaceholder" required />
          </div>
          <div class="space-y-2">
            <label for="email" class="text-sm font-medium">{{ t.email }}</label>
            <input id="email" v-model.trim="form.email" :type="isLogin ? 'text' : 'email'" class="input h-10" :placeholder="isLogin ? 'root' : 'you@example.com'" required />
          </div>
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <label for="password" class="text-sm font-medium">{{ t.password }}</label>
              <RouterLink v-if="isLogin && !isAdminAuth" :to="localized('/forgot-password')" class="text-xs text-muted-foreground hover:text-foreground">{{ t.forgotPassword }}</RouterLink>
            </div>
            <div class="relative">
              <input id="password" v-model="form.password" :type="showPassword ? 'text' : 'password'" class="input h-10 pr-10" :placeholder="passwordPlaceholder" required :minlength="isLogin ? undefined : 8" />
              <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground" @click="showPassword = !showPassword">
                <EyeOff v-if="showPassword" class="h-4 w-4" />
                <Eye v-else class="h-4 w-4" />
              </button>
            </div>
          </div>
          <div v-if="!isLogin" class="space-y-2">
            <label for="confirmPassword" class="text-sm font-medium">{{ t.confirmPassword }}</label>
            <input id="confirmPassword" v-model="form.confirmPassword" type="password" class="input h-10" :placeholder="t.confirmPasswordPlaceholder" required minlength="8" />
          </div>
          <button type="submit" class="btn h-10 w-full bg-primary text-primary-foreground hover:bg-primary/90" :disabled="loading">
            {{ loading ? loadingText : submitText }}
          </button>
          <p v-if="!isLogin" class="text-center text-xs text-muted-foreground">
            {{ t.agreeTerms }}
            <RouterLink :to="localized('/terms')" class="underline underline-offset-4">{{ t.termsOfService }}</RouterLink>
            {{ t.and }}
            <RouterLink :to="localized('/privacy')" class="underline underline-offset-4">{{ t.privacyPolicy }}</RouterLink>
          </p>
        </form>

        <p v-if="!isAdminAuth" class="text-center text-sm text-muted-foreground">
          {{ isLogin ? t.noAccount : t.haveAccount }}
          <RouterLink :to="localized(isLogin ? '/register' : '/login')" class="font-medium text-foreground underline-offset-4 hover:underline">
            {{ isLogin ? t.registerNow : t.loginNow }}
          </RouterLink>
        </p>
      </div>

      <VendorPanel v-else :is-login="isLogin" :copy="vendorCopy" :auth-copy="t" @done="handleAuthDone" />
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { Eye, EyeOff } from 'lucide-vue-next'

import { loginUser, registerUser } from '@/api'
import { translatedCopy } from '@/i18n'
import VendorPanel from '@/pages/VendorPanel.vue'

const route = useRoute()
const router = useRouter()
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')
const form = reactive({ name: '', email: '', password: '', confirmPassword: '' })

const locale = computed(() => route.params.locale || 'en')
const authMode = computed(() => route.meta.authMode || 'user')
const isVendorAuth = computed(() => authMode.value === 'vendor')
const isAdminAuth = computed(() => authMode.value === 'admin')
const isLogin = computed(() => ['login', 'vendor-login', 'admin-login'].includes(route.name))
const t = computed(() => translatedCopy(locale.value, copy, source => ({
  ...source.auth,
  vendorLogin: source.auth?.vendorLogin,
  vendorRegister: source.auth?.vendorRegister
})))
const vendorCopy = computed(() => vendorCopies[locale.value] || vendorCopies.en)
const pageTitle = computed(() => {
  if (isAdminAuth.value) return t.value.adminLogin
  return isLogin.value ? t.value.welcomeBack : t.value.createAccount
})
const pageSubtitle = computed(() => {
  if (isAdminAuth.value) return t.value.adminLoginSubtitle
  return isLogin.value ? t.value.loginSubtitle : t.value.createAccountSubtitle
})
const submitText = computed(() => {
  if (isAdminAuth.value) return t.value.adminLogin
  return isLogin.value ? t.value.login : t.value.createAccount
})
const loadingText = computed(() => (isLogin.value ? t.value.loggingIn : t.value.registering))
const passwordPlaceholder = computed(() => (isLogin.value ? t.value.passwordLoginPlaceholder : t.value.passwordPlaceholder))

watch(() => route.name, () => {
  error.value = ''
  loading.value = false
})

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

const adminRoles = new Set(['ADMIN', 'SENIOR_ADMIN', 'SUPER_ADMIN'])
function isAdminRole(role) {
  return adminRoles.has(role)
}

function handleAuthDone(user) {
  localStorage.setItem('misicheng-user', JSON.stringify(user))
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
  if (redirect.startsWith('/')) {
    router.push(redirect)
    return
  }
  router.push(localized(isAdminRole(user.role) ? '/admin' : user.role === 'VENDOR' ? '/vendor' : '/'))
}

async function submitUser() {
  error.value = ''
  if (!isLogin.value && form.password !== form.confirmPassword) {
    error.value = t.value.passwordMismatch
    return
  }
  loading.value = true
  try {
    const data = isLogin.value
      ? await loginUser({ email: form.email, password: form.password, type: isAdminAuth.value ? 'admin' : 'user' })
      : await registerUser({ name: form.name, email: form.email, password: form.password })
    if (isAdminAuth.value && !isAdminRole(data.user.role)) {
      error.value = t.value.adminAccessRequired
      return
    }
    if (!isAdminAuth.value && isAdminRole(data.user.role)) {
      error.value = t.value.adminUseDedicatedLogin
      return
    }
    if (!isAdminAuth.value && data.user.role === 'VENDOR') {
      error.value = t.value.vendorUseDedicatedLogin
      return
    }
    handleAuthDone(data.user)
  } catch (err) {
    error.value = err?.response?.data?.error || (isLogin.value ? t.value.invalidCredentials : t.value.registerFailed)
  } finally {
    loading.value = false
  }
}

const copy = {
  en: {
    login: 'Log In',
    register: 'Register',
    email: 'Email',
    password: 'Password',
    forgotPassword: 'Forgot Password?',
    noAccount: "Don't have an account?",
    haveAccount: 'Already have an account?',
    welcomeBack: 'Welcome Back',
    loginSubtitle: 'Log in to your account to continue',
    googleLogin: 'Sign in with Google',
    googleRegister: 'Sign up with Google',
    orEmailLogin: 'Or sign in with email',
    orEmailRegister: 'Or sign up with email',
    loggingIn: 'Logging in...',
    registering: 'Registering...',
    createAccount: 'Create Account',
    createAccountSubtitle: 'Join us and start shopping',
    name: 'Name',
    namePlaceholder: 'Enter your name',
    confirmPassword: 'Confirm Password',
    passwordPlaceholder: 'At least 8 characters',
    passwordLoginPlaceholder: 'Enter password',
    confirmPasswordPlaceholder: 'Enter password again',
    agreeTerms: 'By creating an account, you agree to our',
    termsOfService: 'Terms of Service',
    privacyPolicy: 'Privacy Policy',
    and: 'and',
    registerNow: 'Register now',
    loginNow: 'Log in now',
    invalidCredentials: 'Invalid email or password',
    passwordMismatch: 'Passwords do not match',
    registerFailed: 'Registration failed',
    adminLogin: 'Admin Sign In',
    adminLoginSubtitle: 'Dedicated access for site administrators only',
    adminAccessRequired: 'Admin access is required for this page',
    adminUseDedicatedLogin: 'Please use the dedicated admin login link',
    vendorUseDedicatedLogin: 'Please use the dedicated vendor login link',
    vendorLogin: 'Vendor Login',
    vendorRegister: 'Vendor Registration'
  },
  zh: {
    login: '登录',
    register: '注册',
    email: '邮箱',
    password: '密码',
    forgotPassword: '忘记密码？',
    noAccount: '还没有账户？',
    haveAccount: '已有账户？',
    welcomeBack: '欢迎回来',
    loginSubtitle: '登录您的账户以继续',
    googleLogin: '使用 Google 登录',
    googleRegister: '使用 Google 注册',
    orEmailLogin: '或使用邮箱登录',
    orEmailRegister: '或使用邮箱注册',
    loggingIn: '登录中...',
    registering: '注册中...',
    createAccount: '创建账户',
    createAccountSubtitle: '加入我们，开始购物',
    name: '姓名',
    namePlaceholder: '请输入您的姓名',
    confirmPassword: '确认密码',
    passwordPlaceholder: '至少8个字符',
    passwordLoginPlaceholder: '请输入密码',
    confirmPasswordPlaceholder: '再次输入密码',
    agreeTerms: '创建账户即表示您同意我们的',
    termsOfService: '服务条款',
    privacyPolicy: '隐私政策',
    and: '和',
    registerNow: '立即注册',
    loginNow: '立即登录',
    invalidCredentials: '邮箱或密码错误',
    passwordMismatch: '两次密码输入不一致',
    registerFailed: '注册失败',
    adminLogin: '管理员登录',
    adminLoginSubtitle: '仅限后台管理员通过独立入口访问',
    adminAccessRequired: '此页面需要管理员权限',
    adminUseDedicatedLogin: '请使用独立的管理员登录链接',
    vendorUseDedicatedLogin: '请使用独立的商家登录链接',
    vendorLogin: '商家登录',
    vendorRegister: '商家入驻'
  }
}

const vendorCopies = {
  en: {
    signInTitle: 'Vendor Sign In',
    signInDesc: 'Access your vendor workspace to track application status, upload products, and manage review feedback.',
    registerTitle: 'Vendor Application',
    registerDesc: 'Submit your company profile for review. After approval, the vendor workspace can publish products into the existing review flow.',
    whatYouCanDo: 'What you can do here',
    capabilities: ['Track vendor application review status', 'Create products and submit them into admin review', 'Manage drafts, rejected products, and resubmissions', 'Access vendor media and product assets'],
    policyTitle: 'Access policy',
    policyDescription: 'Vendor accounts can sign in at any time. Product submission becomes available after the company application is approved by admin.',
    account: 'Account',
    company: 'Company',
    companyName: 'Company name',
    contactPerson: 'Contact person',
    phone: 'Phone',
    country: 'Country',
    address: 'Address',
    profile: 'Company profile',
    profilePlaceholder: 'Main categories, certifications, production capability, lead time.',
    filesSection: 'Certification Files',
    fileHint: 'PDF, JPG, PNG, or WebP. Up to 10MB per file.',
    upload: 'Upload',
    uploading: 'Uploading...',
    uploadFailed: 'Upload failed',
    remove: 'Remove',
    noFiles: 'No files uploaded yet.',
    submit: 'Submit Application',
    submitting: 'Submitting...',
    submitted: 'Application submitted. You can sign in to track review status.',
    signIn: 'Sign in',
    signingIn: 'Signing in...',
    registerHint: 'Need a vendor account?',
    registerLink: 'Submit an application',
    loginHint: 'Already have a vendor account?',
    login: 'Sign in',
    reviewFlow: 'Review Flow',
    reviewSteps: ['Submit application', 'Admin review', 'Product submission'],
    reviewTargets: 'What gets reviewed',
    reviewItems: ['Company identity and contact ownership', 'Category fit and supply capability', 'Certificates and supporting documents', 'Operational status before product publishing']
  },
  zh: {
    signInTitle: '商家登录',
    signInDesc: '登录商家工作台，查看入驻审核状态、上传商品并处理审核反馈。',
    registerTitle: '商家入驻申请',
    registerDesc: '提交企业资料进入审核。审核通过后，即可在商家工作台内发布商品并进入现有商品审核流程。',
    whatYouCanDo: '这里可以做什么',
    capabilities: ['查看工厂入驻申请的审核进度', '创建商品并提交到后台审核', '管理草稿、驳回商品和重新提交', '使用商家媒体库管理图片素材'],
    policyTitle: '访问规则',
    policyDescription: '商家账号在待审核或已驳回时也可以登录，但只有申请通过后才能提交新商品进入审核。',
    account: '账号信息',
    company: '企业信息',
    companyName: '公司名称',
    contactPerson: '联系人',
    phone: '联系电话',
    country: '国家/地区',
    address: '公司地址',
    profile: '公司简介',
    profilePlaceholder: '主营品类、资质认证、产能情况、交付周期等。',
    filesSection: '资质文件',
    fileHint: '支持 PDF、JPG、PNG、WebP，单个文件不超过 10MB。',
    upload: '上传文件',
    uploading: '上传中...',
    uploadFailed: '上传失败',
    remove: '移除',
    noFiles: '暂未上传文件。',
    submit: '提交申请',
    submitting: '提交中...',
    submitted: '申请已提交，登录后可查看审核进度。',
    signIn: '登录',
    signingIn: '登录中...',
    registerHint: '还没有商家账号？',
    registerLink: '提交入驻申请',
    loginHint: '已有商家账号？',
    login: '去登录',
    reviewFlow: '审核流程',
    reviewSteps: ['提交申请', '后台审核', '商品提报'],
    reviewTargets: '审核重点',
    reviewItems: ['企业主体与联系人归属是否清晰', '品类匹配度与供应能力是否满足要求', '证照与支撑文件是否齐全', '是否满足上架前的运营条件']
  }
}
</script>
