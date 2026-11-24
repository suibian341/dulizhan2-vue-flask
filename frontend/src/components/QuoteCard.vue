<template>
  <div class="rounded-xl border bg-background p-4">
    <div class="mb-3 flex items-center justify-between gap-3">
      <div class="flex items-center gap-2">
        <h4 class="font-semibold">{{ text.title }}</h4>
        <span v-if="isExpired" class="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-700">{{ text.expired }}</span>
      </div>
      <p class="text-xs text-muted-foreground">{{ formatDate(quote.createdAt) }}</p>
    </div>

    <div class="mb-3 overflow-x-auto rounded-lg border">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b bg-muted/50">
            <th class="px-3 py-2 text-left font-medium">{{ text.product }}</th>
            <th class="whitespace-nowrap px-3 py-2 text-right font-medium">{{ text.quantity }}</th>
            <th class="whitespace-nowrap px-3 py-2 text-right font-medium">{{ text.unitPrice }}</th>
            <th class="whitespace-nowrap px-3 py-2 text-right font-medium">{{ text.subtotal }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in quote.items" :key="item.id" class="border-b last:border-0">
            <td class="max-w-[220px] break-words px-3 py-2">
              <p>{{ item.name }}</p>
              <p v-if="formatOptions(item.options)" class="mt-1 text-xs text-muted-foreground">{{ formatOptions(item.options) }}</p>
            </td>
            <td class="whitespace-nowrap px-3 py-2 text-right">{{ item.quantity }}</td>
            <td class="px-3 py-2 text-right">{{ money(item.unitPrice) }}</td>
            <td class="px-3 py-2 text-right">{{ money(item.totalPrice) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="mb-3 flex items-start justify-between gap-4">
      <div>
        <p class="text-sm text-muted-foreground">{{ text.validUntil }} {{ formatDate(quote.validUntil) }}</p>
        <p v-if="quote.notes" class="mt-1 break-words text-sm text-muted-foreground">{{ text.notes }} {{ quote.notes }}</p>
      </div>
      <div class="text-right">
        <p class="text-xs text-muted-foreground">{{ text.total }}</p>
        <p class="text-xl font-bold">{{ money(quote.totalAmount) }}</p>
      </div>
    </div>

    <div v-if="isAdmin || canRespond" class="flex gap-2">
      <button v-if="isAdmin" type="button" class="btn btn-outline h-9 px-3 text-sm" @click="$emit('edit')">
        <Edit class="h-3.5 w-3.5" />
        {{ text.edit }}
      </button>
      <button v-if="canRespond" type="button" class="btn h-9 flex-1 bg-primary px-3 text-sm text-primary-foreground" @click="$emit('accept')">
        <Check class="h-3.5 w-3.5" />
        {{ text.accept }}
      </button>
      <button v-if="canRespond" type="button" class="btn btn-outline h-9 flex-1 px-3 text-sm" @click="$emit('reject')">
        <X class="h-3.5 w-3.5" />
        {{ text.reject }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Check, Edit, X } from 'lucide-vue-next'
import { price } from '@/utils'
import { useUiStore } from '@/stores/ui'
import { formatVariantOptions } from '@/variantOptions'

const props = defineProps({
  quote: { type: Object, required: true },
  inquiryStatus: { type: String, default: '' },
  isAdmin: { type: Boolean, default: false },
  locale: { type: String, default: 'en' }
})

defineEmits(['edit', 'accept', 'reject'])

const ui = useUiStore()
const text = computed(() => props.locale === 'zh' ? copy.zh : copy.en)
const isExpired = computed(() => props.quote.validUntil && new Date(props.quote.validUntil) < new Date())
const canRespond = computed(() => props.inquiryStatus === 'QUOTED' && !props.isAdmin && !isExpired.value)

function money(value) {
  return price(value, ui.currency)
}

function formatDate(value) {
  if (!value) return '-'
  return new Intl.DateTimeFormat(props.locale === 'zh' ? 'zh-CN' : 'en-US', {
    year: 'numeric',
    month: 'short',
    day: '2-digit'
  }).format(new Date(value))
}

function formatOptions(options) {
  return formatVariantOptions(options, [], props.locale === 'zh' ? 'zh' : 'en')
}

const copy = {
  en: {
    title: 'Quote',
    expired: 'Expired',
    product: 'Product',
    quantity: 'Qty',
    unitPrice: 'Unit Price',
    subtotal: 'Subtotal',
    validUntil: 'Valid until:',
    notes: 'Notes:',
    total: 'Total',
    edit: 'Edit Quote',
    accept: 'Accept Quote',
    reject: 'Reject Quote'
  },
  zh: {
    title: '报价单',
    expired: '已过期',
    product: '产品',
    quantity: '数量',
    unitPrice: '单价',
    subtotal: '小计',
    validUntil: '有效期至:',
    notes: '备注:',
    total: '总金额',
    edit: '编辑报价',
    accept: '接受报价',
    reject: '拒绝报价'
  }
}
</script>
