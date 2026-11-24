<template>
  <div class="mx-auto max-w-7xl px-4 pt-24 py-12 lg:px-8">
    <nav class="mb-8 flex items-center gap-2 text-sm text-muted-foreground">
      <RouterLink :to="localized('/')" class="hover:text-foreground transition-colors">{{ t.common.home }}</RouterLink>
      <ChevronRight class="h-3.5 w-3.5" />
      <span class="text-foreground font-medium">{{ t.contact.breadcrumb }}</span>
    </nav>

    <div class="mb-12 text-center">
      <h1 class="text-4xl font-bold tracking-tight">{{ t.contact.title }}</h1>
      <p class="mt-4 text-lg text-muted-foreground">{{ t.contact.subtitle }}</p>
    </div>

    <div class="grid grid-cols-1 gap-12 lg:grid-cols-3">
      <div class="lg:col-span-1">
        <h2 class="mb-6 text-xl font-semibold">{{ t.contact.contactInfo }}</h2>
        <div class="space-y-6">
          <div v-for="item in infoItems" :key="item.title" class="flex items-start gap-4">
            <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
              <component :is="item.icon" class="h-5 w-5 text-primary" />
            </div>
            <div>
              <h3 class="font-medium">{{ item.title }}</h3>
              <p v-for="line in item.lines" :key="line" class="text-sm text-muted-foreground" :class="line === item.lines[0] ? 'mt-1' : ''">
                {{ line }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div class="lg:col-span-2">
        <div class="rounded-xl border p-6 lg:p-8">
          <h2 class="mb-6 text-xl font-semibold">{{ t.contact.sendMessage }}</h2>

          <div v-if="sent" class="py-12 text-center">
            <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
              <Send class="h-8 w-8 text-green-600" />
            </div>
            <h3 class="mb-2 text-lg font-semibold">{{ t.contact.messageSent }}</h3>
            <p class="text-muted-foreground">{{ t.contact.messageSentDesc }}</p>
            <button
              type="button"
              class="mt-6 inline-flex h-9 items-center justify-center rounded-md border bg-background px-4 py-2 text-sm font-medium shadow-xs transition-all hover:bg-accent hover:text-accent-foreground"
              @click="resetForm"
            >
              {{ t.contact.sendAnother }}
            </button>
          </div>

          <form v-else class="space-y-6" @submit.prevent="handleSubmit">
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div class="space-y-2">
                <label for="name" class="text-sm font-medium leading-none">{{ t.contact.nameLabel }}</label>
                <input
                  id="name"
                  v-model.trim="form.name"
                  class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-xs transition-colors placeholder:text-muted-foreground outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] md:text-sm"
                  :placeholder="t.contact.namePlaceholder"
                  required
                />
              </div>
              <div class="space-y-2">
                <label for="email" class="text-sm font-medium leading-none">{{ t.contact.emailLabel }}</label>
                <input
                  id="email"
                  v-model.trim="form.email"
                  type="email"
                  class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-xs transition-colors placeholder:text-muted-foreground outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] md:text-sm"
                  :placeholder="t.contact.emailPlaceholder"
                  required
                />
              </div>
            </div>

            <div class="space-y-2">
              <label for="subject" class="text-sm font-medium leading-none">{{ t.contact.subjectLabel }}</label>
              <input
                id="subject"
                v-model.trim="form.subject"
                class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-xs transition-colors placeholder:text-muted-foreground outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] md:text-sm"
                :placeholder="t.contact.subjectPlaceholder"
                required
              />
            </div>

            <div class="space-y-2">
              <label for="message" class="text-sm font-medium leading-none">{{ t.contact.messageLabel }}</label>
              <textarea
                id="message"
                v-model.trim="form.message"
                class="flex min-h-[150px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-base shadow-xs transition-colors placeholder:text-muted-foreground outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] md:text-sm"
                :placeholder="t.contact.messagePlaceholder"
                required
              ></textarea>
            </div>

            <button
              type="submit"
              class="inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-primary px-6 text-sm font-medium text-primary-foreground transition-all hover:bg-primary/90 disabled:pointer-events-none disabled:opacity-50 sm:w-auto"
              :disabled="submitting"
            >
              <Loader2 v-if="submitting" class="h-4 w-4 animate-spin" />
              <Send v-else class="h-4 w-4" />
              {{ submitting ? t.contact.submitting : t.contact.submitButton }}
            </button>
            <p v-if="error" class="text-sm text-red-500">{{ error }}</p>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { ChevronRight, Clock, Loader2, Mail, MapPin, Phone, Send } from 'lucide-vue-next'

import { submitContact } from '@/api'
import { translatedCopy } from '@/i18n'

const route = useRoute()
const submitting = ref(false)
const sent = ref(false)
const error = ref('')
const form = reactive({
  name: '',
  email: '',
  subject: '',
  message: ''
})

const locale = computed(() => route.params.locale || 'en')
const t = computed(() => translatedCopy(locale.value, {}, source => ({
  common: source.common || {},
  contact: source.contact || {}
})))
const contactEmail = 'anna@gzjixing-tech.com'
const contactPhones = ['+86 13247309378', '+86 13288805588']
const infoItems = computed(() => [
  { icon: Mail, title: t.value.contact.emailLabel, lines: [contactEmail] },
  { icon: Phone, title: t.value.contact.phoneLabel, lines: contactPhones },
  {
    icon: MapPin,
    title: t.value.contact.addressLabel,
    lines: [
      t.value.contact.companyName,
      t.value.contact.addressLine1,
      t.value.contact.addressLine2
    ].filter(Boolean)
  },
  { icon: Clock, title: t.value.contact.businessHours, lines: [t.value.contact.hours1, t.value.contact.hours2, t.value.contact.hours3] }
])

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

function resetForm() {
  sent.value = false
  form.name = ''
  form.email = ''
  form.subject = ''
  form.message = ''
}

async function handleSubmit() {
  error.value = ''
  submitting.value = true
  try {
    await submitContact({ ...form })
    sent.value = true
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.contact.errorSend
  } finally {
    submitting.value = false
  }
}
</script>
