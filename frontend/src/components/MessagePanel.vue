<template>
  <div class="flex h-[500px] flex-col overflow-hidden rounded-xl border bg-background">
    <div class="border-b px-4 py-3">
      <h3 class="text-sm font-semibold">{{ text.title }}</h3>
    </div>

    <div ref="scrollRef" class="min-h-0 flex-1 overflow-y-auto p-4">
      <div v-if="messages.length === 0" class="flex h-full items-center justify-center text-sm text-muted-foreground">
        {{ text.empty }}
      </div>
      <div v-else class="space-y-3">
        <div v-for="msg in messages" :key="msg.id">
          <div v-if="msg.senderType === 'SYSTEM'" class="flex justify-center">
            <span class="max-w-[85%] break-words rounded-full bg-muted px-3 py-1 text-center text-xs text-muted-foreground">
              {{ msg.content }}
            </span>
          </div>
          <div v-else class="flex" :class="isMine(msg) ? 'justify-end' : 'justify-start'">
            <div
              class="min-w-0 max-w-[75%] overflow-hidden rounded-2xl px-4 py-2"
              :class="isMine(msg) ? 'bg-sky-500 text-white' : 'bg-muted text-foreground'"
            >
              <p v-if="!isMine(msg)" class="mb-1 text-xs font-medium opacity-70">
                {{ msg.senderType === 'ADMIN' ? text.sales : (msg.sender?.name || text.user) }}
              </p>
              <p class="whitespace-pre-wrap break-words text-sm">{{ msg.content }}</p>
              <p class="mt-1 text-right text-[10px]" :class="isMine(msg) ? 'text-white/70' : 'text-muted-foreground'">
                {{ formatTime(msg.createdAt) }}
                <span v-if="isMine(msg)" class="ml-1">{{ msg.readAt ? text.read : text.unread }}</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="border-t p-3">
      <div class="flex gap-2">
        <textarea
          v-model.trim="input"
          class="textarea min-h-10 max-h-[100px] resize-none"
          rows="1"
          :placeholder="text.placeholder"
          @keydown.enter.exact.prevent="handleSend"
        ></textarea>
        <button class="btn h-10 w-10 shrink-0 bg-primary text-primary-foreground" type="button" :disabled="!input || sending" @click="handleSend">
          <Loader2 v-if="sending" class="h-4 w-4 animate-spin" />
          <Send v-else class="h-4 w-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { Loader2, Send } from 'lucide-vue-next'
import { getInquiryMessages, sendInquiryMessage } from '@/api'

const props = defineProps({
  inquiryId: { type: String, required: true },
  currentUserId: { type: String, default: '' },
  currentUserRole: { type: String, default: 'USER' },
  initialMessages: { type: Array, default: () => [] },
  autoFetch: { type: Boolean, default: true },
  locale: { type: String, default: 'en' }
})

const messages = ref([...props.initialMessages])
const input = ref('')
const sending = ref(false)
const scrollRef = ref(null)
const text = computed(() => props.locale === 'zh' ? copy.zh : copy.en)

watch(() => props.initialMessages, value => {
  messages.value = [...(value || [])]
  scrollToBottom()
})

onMounted(() => {
  scrollToBottom()
  if (props.autoFetch) fetchMessages()
})

function isMine(message) {
  return message.senderId === props.currentUserId && message.senderType === props.currentUserRole
}

function formatTime(value) {
  if (!value) return ''
  return new Intl.DateTimeFormat(props.locale === 'zh' ? 'zh-CN' : 'en-US', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value))
}

async function scrollToBottom() {
  await nextTick()
  if (scrollRef.value) scrollRef.value.scrollTop = scrollRef.value.scrollHeight
}

async function fetchMessages() {
  try {
    const data = await getInquiryMessages(props.inquiryId, { viewAs: props.currentUserRole })
    messages.value = data.data || data.messages || []
    scrollToBottom()
  } catch {
    // Keep the last known messages visible.
  }
}

async function handleSend() {
  if (!input.value || sending.value) return
  sending.value = true
  try {
    await sendInquiryMessage(props.inquiryId, { content: input.value, senderType: props.currentUserRole })
    input.value = ''
    await fetchMessages()
  } finally {
    sending.value = false
  }
}

const copy = {
  en: {
    title: 'Messages',
    empty: 'No messages yet. Send the first message to start the conversation.',
    placeholder: 'Enter message...',
    sales: 'Sales',
    user: 'User',
    read: 'Read',
    unread: 'Unread'
  },
  zh: {
    title: '消息',
    empty: '暂无消息，发送第一条消息开始沟通。',
    placeholder: '输入消息...',
    sales: '客服',
    user: '用户',
    read: '已读',
    unread: '未读'
  }
}
</script>
