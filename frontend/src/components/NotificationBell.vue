<template>
  <div ref="containerRef" class="relative">
    <button
      type="button"
      class="relative rounded-full p-2 text-gray-600 transition-colors hover:bg-sky-50 hover:text-sky-600"
      :aria-label="`${t.notifications} (${visibleUnreadCount})`"
      @click.stop="toggle"
    >
      <Bell class="h-[18px] w-[18px]" />
      <span
        v-if="visibleUnreadCount > 0"
        class="absolute -right-0.5 -top-0.5 flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white ring-2 ring-white"
      >
        {{ visibleUnreadCount > 99 ? '99+' : visibleUnreadCount }}
      </span>
    </button>

    <Transition name="notification-panel">
      <div
        v-if="isAuthenticated && isOpen"
        class="fixed inset-x-3 top-[4.5rem] z-[60] max-h-[480px] overflow-hidden rounded-2xl border bg-white shadow-xl sm:absolute sm:inset-x-auto sm:top-auto sm:right-0 sm:mt-2 sm:w-[380px] sm:rounded-xl"
        @click.stop
      >
        <div class="flex flex-col">
          <div class="flex items-center justify-between border-b px-4 py-3">
            <h3 class="text-sm font-semibold">{{ t.notifications }}</h3>
            <button
              v-if="unreadCount > 0"
              class="text-xs text-sky-500 transition-colors hover:text-sky-600"
              type="button"
              @click="markAll"
            >
              {{ t.markAllRead }}
            </button>
          </div>

          <div class="max-h-[400px] overflow-y-auto">
            <div v-if="isLoading && notifications.length === 0" class="flex items-center justify-center py-12">
              <Loader2 class="h-5 w-5 animate-spin text-gray-400" />
            </div>
            <div v-else-if="notifications.length === 0" class="flex flex-col items-center justify-center py-12 text-gray-400">
              <Bell class="mb-2 h-8 w-8" />
              <p class="text-sm">{{ t.empty }}</p>
            </div>
            <div v-else class="divide-y">
              <button
                v-for="notification in notifications"
                :key="notification.id"
                type="button"
                class="flex w-full items-start gap-3 px-4 py-3 text-left transition-colors hover:bg-gray-50"
                :class="!notification.isRead ? 'bg-sky-50/50' : ''"
                @click="openNotification(notification)"
              >
                <div
                  class="mt-0.5 flex-shrink-0 rounded-full p-1.5"
                  :class="!notification.isRead ? 'bg-sky-100 text-sky-600' : 'bg-gray-100 text-gray-500'"
                >
                  <component :is="iconFor(notification.type)" class="h-4 w-4" />
                </div>
                <div class="min-w-0 flex-1">
                  <div class="flex items-start gap-2">
                    <p class="whitespace-normal break-words leading-snug" :class="[!notification.isRead ? 'font-semibold' : '', notificationTextClass(notification.title)]">
                      {{ notification.title }}
                    </p>
                    <span v-if="!notification.isRead" class="h-2 w-2 flex-shrink-0 rounded-full bg-sky-500"></span>
                  </div>
                  <p v-if="notification.content" class="mt-0.5 whitespace-normal break-words text-gray-500" :class="notificationTextClass(notification.content, true)">
                    {{ notification.content }}
                  </p>
                  <p class="mt-1 text-xs text-gray-400">{{ timeAgo(notification.createdAt) }}</p>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Bell,
  CheckCircle,
  FileText,
  Loader2,
  MessageCircle,
  Receipt,
  XCircle
} from 'lucide-vue-next'

import { getNotifications, markNotificationsRead } from '@/api'

const props = defineProps({
  text: { type: Object, required: true }
})

const route = useRoute()
const router = useRouter()
const containerRef = ref(null)
const notifications = ref([])
const unreadCount = ref(0)
const isOpen = ref(false)
const isLoading = ref(false)
const user = ref(readUser())

const t = computed(() => props.text)
const isAuthenticated = computed(() => Boolean(user.value))
const visibleUnreadCount = computed(() => (isAuthenticated.value ? unreadCount.value : 0))

function readUser() {
  try {
    return JSON.parse(localStorage.getItem('misicheng-user') || 'null')
  } catch {
    return null
  }
}

async function fetchNotifications(limit = 30) {
  if (!isAuthenticated.value) return
  isLoading.value = true
  try {
    const data = await getNotifications({ limit })
    const payload = data?.data || data || {}
    notifications.value = Array.isArray(payload.notifications) ? payload.notifications : []
    unreadCount.value = Number(payload.unreadCount || 0)
  } catch {
    notifications.value = []
    unreadCount.value = 0
  } finally {
    isLoading.value = false
  }
}

async function fetchUnreadCount() {
  if (!isAuthenticated.value) return
  try {
    const data = await getNotifications({ unreadOnly: true, limit: 1 })
    const payload = data?.data || data || {}
    unreadCount.value = Number(payload.unreadCount || 0)
  } catch {
    unreadCount.value = 0
  }
}

function toggle() {
  user.value = readUser()
  if (!isAuthenticated.value) {
    isOpen.value = false
    return
  }
  isOpen.value = !isOpen.value
  if (isOpen.value) fetchNotifications()
}

async function openNotification(notification) {
  if (!notification.isRead) {
    await markNotificationsRead({ ids: [notification.id] })
    notifications.value = notifications.value.map(item =>
      item.id === notification.id ? { ...item, isRead: true } : item
    )
    unreadCount.value = notifications.value.filter(item => !item.isRead).length
  }
  isOpen.value = false
  if (notification.link) router.push(localized(notification.link))
}

async function markAll() {
  await markNotificationsRead({ all: true })
  notifications.value = notifications.value.map(item => ({ ...item, isRead: true }))
  unreadCount.value = 0
}

function localized(path) {
  if (!path) return `/${route.params.locale || 'en'}`
  if (/^https?:\/\//.test(path)) return path
  const current = route.params.locale || 'en'
  const clean = path.startsWith('/') ? path : `/${path}`
  if (/^\/(en|zh|ja|ko|fr|de|es|ar)(?=\/|$)/.test(clean)) return clean
  return clean === '/' ? `/${current}` : `/${current}${clean}`
}

function iconFor(type) {
  return {
    INQUIRY_SUBMITTED: FileText,
    INQUIRY_STATUS_CHANGED: Bell,
    NEW_MESSAGE: MessageCircle,
    QUOTE_RECEIVED: Receipt,
    QUOTE_ACCEPTED: CheckCircle,
    QUOTE_REJECTED: XCircle,
    CONTACT_MESSAGE: MessageCircle
  }[type] || Bell
}

function notificationTextClass(value, secondary = false) {
  const length = Array.from(String(value || '')).length
  if (secondary) {
    if (length >= 90) return 'text-[10px] leading-snug'
    if (length >= 56) return 'text-[11px] leading-snug'
    return 'text-xs'
  }
  if (length >= 72) return 'text-[10px] leading-snug'
  if (length >= 42) return 'text-[11px] leading-snug'
  return 'text-sm'
}

function timeAgo(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const seconds = Math.max(0, Math.floor((Date.now() - date.getTime()) / 1000))
  if (seconds < 60) return t.value.justNow
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return t.value.minutesAgo.replace('{count}', minutes)
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return t.value.hoursAgo.replace('{count}', hours)
  const days = Math.floor(hours / 24)
  if (days < 30) return t.value.daysAgo.replace('{count}', days)
  return date.toLocaleDateString(route.params.locale === 'zh' ? 'zh-CN' : 'en-US')
}

function handleOutside(event) {
  const el = containerRef.value
  if (isOpen.value && el && !el.contains(event.target)) {
    isOpen.value = false
  }
}

function syncUser() {
  user.value = readUser()
  if (isAuthenticated.value) fetchUnreadCount()
  else {
    isOpen.value = false
    unreadCount.value = 0
    notifications.value = []
  }
}

watch(() => route.fullPath, () => {
  user.value = readUser()
  isOpen.value = false
})

onMounted(() => {
  document.addEventListener('mousedown', handleOutside)
  document.addEventListener('touchstart', handleOutside)
  window.addEventListener('storage', syncUser)
  syncUser()
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleOutside)
  document.removeEventListener('touchstart', handleOutside)
  window.removeEventListener('storage', syncUser)
})
</script>

<style scoped>
.notification-panel-enter-active,
.notification-panel-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.notification-panel-enter-from,
.notification-panel-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
