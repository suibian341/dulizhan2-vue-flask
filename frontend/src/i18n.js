import { shallowReactive } from 'vue'

import en from './messages/en.json'
import zh from './messages/zh.json'

const loaders = {
  ja: () => import('./messages/ja.json'),
  ko: () => import('./messages/ko.json'),
  fr: () => import('./messages/fr.json'),
  de: () => import('./messages/de.json'),
  es: () => import('./messages/es.json'),
  ar: () => import('./messages/ar.json')
}

export const messages = shallowReactive({ en, zh })
const runtimeLoaded = new Set()

function isPlainObject(value) {
  return value && typeof value === 'object' && !Array.isArray(value)
}

export function deepMerge(base, override) {
  const result = { ...(base || {}) }
  for (const [key, value] of Object.entries(override || {})) {
    if (value === undefined) continue
    if (isPlainObject(value) && isPlainObject(result[key])) {
      result[key] = deepMerge(result[key], value)
    } else {
      result[key] = value
    }
  }
  return result
}

export function message(locale) {
  return messages[locale] || messages.en
}

async function loadBundledMessages(locale) {
  if (messages[locale]) return messages[locale]
  if (!loaders[locale]) return messages.en
  const module = await loaders[locale]()
  messages[locale] = module.default || module
  return messages[locale]
}

async function loadRuntimeMessages(locale) {
  if (typeof fetch !== 'function') return null
  const response = await fetch(`/messages/${locale}.json`, { cache: 'no-store' })
  if (!response.ok) return null
  return response.json()
}

export async function loadLocaleMessages(locale) {
  const target = locale === 'en' || locale === 'zh' || loaders[locale] ? locale : 'en'
  if (runtimeLoaded.has(target)) return messages[target] || messages.en

  try {
    const runtimeMessages = await loadRuntimeMessages(target)
    if (runtimeMessages) {
      messages[target] = runtimeMessages
      runtimeLoaded.add(target)
      return messages[target]
    }
  } catch {
    // Fall back to bundled locale files when runtime JSON is unavailable.
  }

  const bundled = await loadBundledMessages(target)
  runtimeLoaded.add(target)
  return bundled
}

export function translatedCopy(locale, localCopy = {}, mapper) {
  const current = mapper ? mapper(message(locale), locale) : message(locale)
  const fallback = mapper ? mapper(message('en'), 'en') : message('en')
  return deepMerge(deepMerge(fallback, localCopy.en || {}), deepMerge(current, localCopy[locale] || {}))
}
