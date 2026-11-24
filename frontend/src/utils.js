export const currencyRates = { USD: 1, EUR: 0.92, GBP: 0.79, JPY: 149.5, CNY: 7.23, KRW: 1320 }
export const currencySymbols = { USD: '$', EUR: '€', GBP: '£', JPY: '¥', CNY: '¥', KRW: '₩' }

export function formatPrice(value, currency = localStorage.getItem('misicheng-currency') || 'USD') {
  const code = currencyRates[currency] ? currency : 'USD'
  const amount = Number(value || 0) * currencyRates[code]
  const symbol = currencySymbols[code] || '$'
  if (code === 'JPY' || code === 'KRW') {
    return `${symbol}${Math.round(amount).toLocaleString()}`
  }
  return `${symbol}${amount.toFixed(2)}`
}

export function price(value, currency = localStorage.getItem('misicheng-currency') || 'USD') {
  return formatPrice(value, currency)
}

function trimRepeatedCurrency(value) {
  return String(value || '').replace(/^[^\d-]+/, '')
}

function formatPriceRange(min, max, currency) {
  const minText = price(min, currency)
  const maxText = price(max, currency)
  if (minText === maxText) return minText
  return `${minText}-${trimRepeatedCurrency(maxText)}`
}

function tierNumber(value) {
  const number = Number(value)
  return Number.isFinite(number) && number > 0 ? number : null
}

function priceModeValue(value) {
  const mode = String(value || '').toLowerCase()
  if (['negotiable', 'tier', 'variant'].includes(mode)) return mode
  return ''
}

function tierPriceValues(product) {
  const tiers = Array.isArray(product?.tradeInfo?.priceTiers) ? product.tradeInfo.priceTiers : []
  return tiers
    .filter(tier => !(tier.negotiable || tier.priceNegotiable))
    .map(tier => tierNumber(tier.price))
    .filter(value => value !== null)
}

function variantPriceValues(product) {
  return (Array.isArray(product?.variants) ? product.variants : [])
    .filter(variant => variant.isActive !== false)
    .map(variant => tierNumber(variant.price))
    .filter(value => value !== null)
}

export function productPricingMode(product) {
  const explicitMode = priceModeValue(product?.tradeInfo?.priceMode || product?.priceMode)
  if (explicitMode) return explicitMode
  if (tierPriceValues(product).length) return 'tier'
  if (variantPriceValues(product).length) return 'variant'
  const tiers = Array.isArray(product?.tradeInfo?.priceTiers) ? product.tradeInfo.priceTiers : []
  if (tiers.some(tier => tier.negotiable || tier.priceNegotiable)) return 'negotiable'
  return tierNumber(product?.price) === null ? 'negotiable' : 'tier'
}

function fixedPriceValues(product) {
  const mode = productPricingMode(product)
  if (mode === 'negotiable') return []
  if (mode === 'tier') {
    const tierValues = tierPriceValues(product)
    if (tierValues.length) return tierValues
  }
  if (mode === 'variant') {
    const variantValues = variantPriceValues(product)
    if (variantValues.length) return variantValues
  }

  const fallback = tierNumber(product?.price)
  return fallback === null ? [] : [fallback]
}

export function productHasFixedPrice(product) {
  return fixedPriceValues(product).length > 0
}

export function productHasNegotiablePrice(product) {
  if (productPricingMode(product) === 'negotiable') return true
  const tiers = Array.isArray(product?.tradeInfo?.priceTiers) ? product.tradeInfo.priceTiers : []
  const hasNegotiableTier = tiers.some(tier => tier.negotiable || tier.priceNegotiable)
  return Boolean(
    product?.negotiable ||
    product?.priceNegotiable ||
    product?.tradeInfo?.negotiable ||
    product?.tradeInfo?.priceNegotiable ||
    (!productHasFixedPrice(product) && (hasNegotiableTier || Number(product?.price || 0) <= 0))
  )
}

export function productPriceBounds(product) {
  const values = fixedPriceValues(product)
  if (!values.length) return { min: 0, max: 0 }
  return { min: Math.min(...values), max: Math.max(...values) }
}

export function productComparePriceBounds(product) {
  const tiers = Array.isArray(product?.tradeInfo?.priceTiers) ? product.tradeInfo.priceTiers : []
  const values = tiers
    .filter(tier => !(tier.negotiable || tier.priceNegotiable))
    .map(tier => tierNumber(tier.compareAtPrice || tier.comparePrice || tier.originalPrice))
    .filter(value => value !== null)
  if (!values.length) {
    const fallback = tierNumber(product?.compareAtPrice)
    return fallback === null ? null : { min: fallback, max: fallback }
  }
  return { min: Math.min(...values), max: Math.max(...values) }
}

export function productPriceRange(product, currency = localStorage.getItem('misicheng-currency') || 'USD', options = {}) {
  if (!productHasFixedPrice(product)) return options.negotiableText || 'Negotiable'
  const bounds = productPriceBounds(product)
  return formatPriceRange(bounds.min, bounds.max, currency)
}

export function productComparePriceRange(product, currency = localStorage.getItem('misicheng-currency') || 'USD') {
  if (!productHasFixedPrice(product)) return ''
  const priceBounds = productPriceBounds(product)
  const compareBounds = productComparePriceBounds(product)
  if (!compareBounds || compareBounds.max <= priceBounds.min) return ''
  return formatPriceRange(compareBounds.min, compareBounds.max, currency)
}

export function pickImage(product, fallback = '/images/products/product-1.png') {
  return product?.image || product?.images?.[0]?.url || fallback
}

export function salePercent(product) {
  if (!productHasFixedPrice(product)) return 0
  const priceValue = productPriceBounds(product).min
  const compare = productComparePriceBounds(product)?.min || 0
  if (!compare || compare <= priceValue) return 0
  return Math.round(((compare - priceValue) / compare) * 100)
}
