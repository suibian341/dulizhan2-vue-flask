function localizedValue(value, locale = 'en', fallback = '') {
  if (value && typeof value === 'object') {
    return value[locale] || value.en || value.zh || fallback
  }
  return value || fallback
}

function splitValues(value) {
  return String(value || '')
    .split(/[\n,;，；]+/)
    .map(item => item.trim())
    .filter(Boolean)
}

function uniqueRows(rows) {
  const seen = new Set()
  return rows.filter(row => {
    const key = `${row.en || ''}::${row.zh || ''}`
    if (seen.has(key)) return false
    seen.add(key)
    return row.en || row.zh
  })
}

function slugKey(value, fallback) {
  const slug = String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
  return slug || fallback
}

function labelForKey(key, locale = 'en') {
  const labels = {
    color: { en: 'Color', zh: '颜色' },
    size: { en: 'Size', zh: '规格' },
    plug: { en: 'Plug Standard', zh: '插头标准' },
    standard: { en: 'Plug Standard', zh: '插头标准' }
  }
  return labels[key]?.[locale] || labels[key]?.en || key
}

export function optionPairsForType(type = {}) {
  if (Array.isArray(type.values)) {
    return uniqueRows(type.values.map(item => ({
      en: localizedValue(item, 'en'),
      zh: localizedValue(item, 'zh', localizedValue(item, 'en'))
    })))
  }
  const enRows = splitValues(type.valuesTextEn)
  const zhRows = splitValues(type.valuesTextZh)
  const length = Math.max(enRows.length, zhRows.length)
  return uniqueRows(Array.from({ length }, (_, index) => ({
    en: enRows[index] || zhRows[index] || '',
    zh: zhRows[index] || enRows[index] || ''
  })))
}

export function createDefaultVariantOptionTypes() {
  return [
    {
      id: 'variant-type-color',
      key: 'color',
      nameEn: 'Color',
      nameZh: '颜色',
      valuesTextEn: 'White\nBlack',
      valuesTextZh: '白色\n黑色'
    },
    {
      id: 'variant-type-plug',
      key: 'plug',
      nameEn: 'Plug Standard',
      nameZh: '插头标准',
      valuesTextEn: 'UK 13A\nEU\nIndia\nCustomized',
      valuesTextZh: 'UK 13A\nEU\nIndia\n定制'
    }
  ]
}

export function createBlankVariantOptionType(index = 0) {
  const stamp = Date.now()
  return {
    id: `variant-type-${stamp}-${index}`,
    key: `option-${stamp}-${index}`,
    nameEn: '',
    nameZh: '',
    valuesTextEn: '',
    valuesTextZh: ''
  }
}

export function normalizeVariantOptionTypes(savedTypes = [], variants = []) {
  const rows = []
  const byKey = new Map()
  const pushType = type => {
    const nameEn = type.nameEn || localizedValue(type.name || type.label, 'en') || labelForKey(type.key, 'en')
    const nameZh = type.nameZh || localizedValue(type.name || type.label, 'zh', nameEn) || labelForKey(type.key, 'zh')
    const key = type.key || slugKey(nameEn, `option-${rows.length + 1}`)
    if (byKey.has(key)) return byKey.get(key)
    const valuePairs = optionPairsForType(type)
    const row = {
      id: type.id || `variant-type-${key}`,
      key,
      nameEn,
      nameZh,
      valuesTextEn: type.valuesTextEn || valuePairs.map(item => item.en).join('\n'),
      valuesTextZh: type.valuesTextZh || valuePairs.map(item => item.zh).join('\n')
    }
    byKey.set(key, row)
    rows.push(row)
    return row
  }

  if (Array.isArray(savedTypes)) savedTypes.forEach(pushType)

  for (const variant of variants || []) {
    const options = variant?.options || {}
    for (const [key, value] of Object.entries(options)) {
      const row = pushType({ key, name: { en: labelForKey(key, 'en'), zh: labelForKey(key, 'zh') } })
      const pairs = optionPairsForType(row)
      const en = localizedValue(value, 'en')
      const zh = localizedValue(value, 'zh', en)
      if (!pairs.some(item => item.en === en || item.zh === zh)) {
        row.valuesTextEn = [row.valuesTextEn, en].filter(Boolean).join('\n')
        row.valuesTextZh = [row.valuesTextZh, zh].filter(Boolean).join('\n')
      }
    }
  }

  return rows.length ? rows : createDefaultVariantOptionTypes()
}

export function variantOptionTypePayloadFromForm(type) {
  const nameEn = (type.nameEn || '').trim()
  const nameZh = (type.nameZh || '').trim()
  const key = type.key || slugKey(nameEn || nameZh, `option-${Date.now()}`)
  const values = optionPairsForType(type)
  if (!(nameEn || nameZh) || !values.length) return null
  return {
    key,
    name: { en: nameEn || nameZh, zh: nameZh || nameEn },
    values
  }
}

export function normalizeVariantFormRow(variant = {}, optionTypes = [], index = 0) {
  const options = variant.options || {}
  const optionValues = {}
  for (const type of optionTypes) {
    const value = options[type.key]
    optionValues[type.key] = localizedValue(value, 'en', localizedValue(value, 'zh'))
  }
  return {
    id: variant.id || `variant-${Date.now()}-${index}`,
    sku: variant.sku || '',
    price: variant.price ?? '',
    stock: variant.stock ?? '',
    optionValues
  }
}

export function variantPayloadFromForm(variant, optionTypes = [], fallbackPrice = 0) {
  const options = {}
  for (const type of optionTypes) {
    const selected = variant.optionValues?.[type.key] || ''
    if (!selected) continue
    const pair = optionPairsForType(type).find(item => item.en === selected || item.zh === selected)
    options[type.key] = {
      en: pair?.en || selected,
      zh: pair?.zh || pair?.en || selected
    }
  }
  return {
    sku: variant.sku,
    price: Number(variant.price || fallbackPrice || 0),
    stock: Number(variant.stock || 0),
    options
  }
}

export function localizedOptionName(type, locale = 'en') {
  return locale === 'zh' ? (type.nameZh || type.nameEn || type.key) : (type.nameEn || type.nameZh || type.key)
}

export function localizedOptionValue(value, locale = 'en') {
  if (value && typeof value === 'object' && value.value !== undefined) {
    return localizedValue(value.value, locale === 'zh' ? 'zh' : 'en')
  }
  return localizedValue(value, locale === 'zh' ? 'zh' : 'en')
}

export function formatVariantOptions(options = {}, optionTypes = [], locale = 'en') {
  const typesByKey = new Map((optionTypes || []).map(type => [type.key, type]))
  return Object.entries(options || {})
    .map(([key, value]) => {
      const type = typesByKey.get(key)
      const savedName = value && typeof value === 'object' ? value.name || value.label : null
      const name = type ? localizedOptionName(type, locale) : localizedValue(savedName, locale === 'zh' ? 'zh' : 'en', labelForKey(key, locale))
      const text = localizedOptionValue(value, locale)
      return text ? `${name}: ${text}` : ''
    })
    .filter(Boolean)
    .join(' / ')
}
