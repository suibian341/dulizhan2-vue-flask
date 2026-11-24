<template>
  <div class="fixed inset-0 z-[140] flex items-center justify-center bg-black/40 p-4">
    <div class="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl border bg-background p-6 shadow-xl">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-lg font-semibold">{{ isEditing ? text.editTitle : text.createTitle }}</h3>
        <button type="button" class="btn btn-ghost h-8 w-8" @click="$emit('close')">
          <X class="h-4 w-4" />
        </button>
      </div>

      <div class="space-y-4">
        <div>
          <div class="mb-2 flex items-center justify-between">
            <label class="text-sm font-medium">{{ text.items }}</label>
            <button type="button" class="btn btn-outline h-8 px-3 text-xs" @click="addItem">
              <Plus class="h-3.5 w-3.5" />
              {{ text.addItem }}
            </button>
          </div>
          <div class="space-y-2">
            <div v-for="(item, index) in items" :key="index" class="grid gap-2 rounded-lg border p-2 md:grid-cols-[1fr_80px_110px_90px_32px] md:items-center">
              <div>
                <input v-model.trim="item.name" class="input h-9" :placeholder="text.productName" />
                <p v-if="formatOptions(item.options)" class="mt-1 text-xs text-muted-foreground">{{ formatOptions(item.options) }}</p>
              </div>
              <input v-model.number="item.quantity" class="input h-9" min="1" type="number" :placeholder="text.quantity" />
              <input v-model.number="item.unitPrice" class="input h-9" min="0" step="0.01" type="number" :placeholder="text.unitPrice" />
              <span class="text-right text-sm font-medium">{{ money(item.quantity * item.unitPrice) }}</span>
              <button type="button" class="btn btn-ghost h-8 w-8 text-destructive" @click="removeItem(index)">
                <Trash2 class="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </div>

        <label class="block space-y-1.5 text-sm font-medium">
          <span>{{ text.validUntil }}</span>
          <input v-model="validUntil" class="input h-10" type="date" />
        </label>

        <label class="block space-y-1.5 text-sm font-medium">
          <span>{{ text.notes }}</span>
          <textarea v-model.trim="notes" class="textarea" rows="3" :placeholder="text.notesPlaceholder"></textarea>
        </label>

        <div class="flex items-center justify-between rounded-lg bg-muted p-3">
          <span class="font-medium">{{ text.total }}</span>
          <span class="text-xl font-bold">{{ money(totalAmount) }}</span>
        </div>

        <div class="flex gap-2">
          <button type="button" class="btn btn-outline h-10 flex-1" @click="$emit('close')">{{ text.cancel }}</button>
          <button type="button" class="btn h-10 flex-1 bg-primary text-primary-foreground" :disabled="saving || !items.length || !validUntil" @click="submit">
            {{ saving ? text.saving : (isEditing ? text.update : text.submit) }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { Plus, Trash2, X } from 'lucide-vue-next'
import { createInquiryQuote, updateInquiryQuote } from '@/api'
import { useUiStore } from '@/stores/ui'
import { price } from '@/utils'
import { formatVariantOptions } from '@/variantOptions'

const props = defineProps({
  inquiryId: { type: String, required: true },
  inquiryItems: { type: Array, default: () => [] },
  quote: { type: Object, default: null },
  locale: { type: String, default: 'en' }
})

const emit = defineEmits(['close', 'success'])
const ui = useUiStore()
const items = ref([])
const validUntil = ref('')
const notes = ref('')
const saving = ref(false)
const text = computed(() => props.locale === 'zh' ? copy.zh : copy.en)
const isEditing = computed(() => Boolean(props.quote?.id))
const totalAmount = computed(() => items.value.reduce((sum, item) => sum + Number(item.quantity || 0) * Number(item.unitPrice || 0), 0))

onMounted(resetForm)
watch(() => props.quote?.id, resetForm)

function resetForm() {
  const sourceItems = isEditing.value ? props.quote.items || [] : props.inquiryItems
  items.value = sourceItems.map(item => ({
    productId: item.productId || '',
    variantId: item.variantId || '',
    name: item.name || '',
    quantity: item.quantity || 1,
    unitPrice: Number(isEditing.value ? item.unitPrice || 0 : item.price || 0),
    options: item.options || {}
  }))
  if (!items.value.length) addItem()
  if (isEditing.value) {
    validUntil.value = props.quote.validUntil ? props.quote.validUntil.slice(0, 10) : ''
    notes.value = props.quote.notes || ''
  } else {
    const date = new Date()
    date.setDate(date.getDate() + 30)
    validUntil.value = date.toISOString().split('T')[0]
    notes.value = ''
  }
}

function addItem() {
  items.value.push({ productId: '', variantId: '', name: '', quantity: 1, unitPrice: 0, options: {} })
}

function removeItem(index) {
  items.value.splice(index, 1)
}

function money(value) {
  return price(value, ui.currency)
}

function formatOptions(options) {
  return formatVariantOptions(options, [], props.locale === 'zh' ? 'zh' : 'en')
}

async function submit() {
  saving.value = true
  try {
    const payload = {
      items: items.value.filter(item => item.name),
      validUntil: validUntil.value,
      notes: notes.value
    }
    if (isEditing.value) {
      await updateInquiryQuote(props.inquiryId, props.quote.id, payload)
    } else {
      await createInquiryQuote(props.inquiryId, payload)
    }
    emit('success')
  } finally {
    saving.value = false
  }
}

const copy = {
  en: {
    createTitle: 'Create Quote',
    editTitle: 'Edit Quote',
    items: 'Quote Items',
    addItem: 'Add Item',
    productName: 'Product name',
    quantity: 'Qty',
    unitPrice: 'Unit price',
    validUntil: 'Valid Until',
    notes: 'Notes',
    notesPlaceholder: 'Quote notes...',
    total: 'Total Amount',
    cancel: 'Cancel',
    submit: 'Submit Quote',
    update: 'Update Quote',
    saving: 'Saving...'
  },
  zh: {
    createTitle: '创建报价',
    editTitle: '编辑报价',
    items: '报价项目',
    addItem: '添加项目',
    productName: '产品名称',
    quantity: '数量',
    unitPrice: '单价',
    validUntil: '有效期至',
    notes: '备注',
    notesPlaceholder: '报价备注...',
    total: '总金额',
    cancel: '取消',
    submit: '提交报价',
    update: '更新报价',
    saving: '保存中...'
  }
}
</script>
