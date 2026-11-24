import axios from 'axios'

const DEFAULT_TIMEOUT_MS = 60000
const UPLOAD_TIMEOUT_MS = 120000
const PRODUCT_SAVE_TIMEOUT_MS = 120000

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: DEFAULT_TIMEOUT_MS
})

function withLocale(params = {}, localeOverride = null) {
  const locale = localeOverride || localStorage.getItem('misicheng-locale') || 'en'
  return { locale, ...params }
}

export function currentUser() {
  try {
    return JSON.parse(localStorage.getItem('misicheng-user') || 'null')
  } catch {
    return null
  }
}

function withUser(params = {}) {
  const user = currentUser()
  if (!user) return params
  return {
    userId: user.id,
    userEmail: user.email,
    ...params
  }
}

function withUserPayload(payload = {}) {
  const user = currentUser()
  if (!user) return payload
  return {
    ...payload,
    userId: user.id,
    userEmail: user.email
  }
}

function withUserFormData(file, fields = {}) {
  const formData = new FormData()
  formData.append('file', file)
  Object.entries(fields || {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') formData.append(key, value)
  })
  const user = currentUser()
  if (user) {
    formData.append('userId', user.id)
    formData.append('userEmail', user.email)
  }
  return formData
}

async function uploadMediaFile(endpoint, file, fields = {}) {
  const { data } = await http.post(endpoint, withUserFormData(file, fields), {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: UPLOAD_TIMEOUT_MS
  })
  return data
}

export async function getHomeData(locale) {
  const { data } = await http.get('/home', { params: withLocale({}, locale) })
  return data
}

export async function getCategories(locale) {
  const { data } = await http.get('/categories', { params: withLocale({}, locale) })
  return data
}

export async function getProducts(params = {}, locale) {
  const { data } = await http.get('/products', { params: withLocale(params, locale) })
  return data
}

export async function getSpecTemplate() {
  const { data } = await http.get('/spec-template')
  return data
}

export async function getProduct(slug, locale) {
  const { data } = await http.get(`/products/${slug}`, { params: withLocale({}, locale) })
  return data
}

export async function searchProducts(q) {
  const { data } = await http.get('/search', { params: withLocale({ q }) })
  return data
}

export async function submitInquiry(payload) {
  const { data } = await http.post('/inquiries', withUserPayload(payload))
  return data
}

export async function getInquiries(params = {}) {
  const { data } = await http.get('/inquiries', { params: withUser(params) })
  return data
}

export async function getInquiry(id, params = {}) {
  const { data } = await http.get(`/inquiries/${id}`, { params: withUser(params) })
  return data
}

export async function updateInquiry(id, payload) {
  const { data } = await http.patch(`/inquiries/${id}`, withUserPayload(payload))
  return data
}

export async function getInquiryMessages(id, params = {}) {
  const { data } = await http.get(`/inquiries/${id}/messages`, { params: withUser(params) })
  return data
}

export async function sendInquiryMessage(id, payload) {
  const { data } = await http.post(`/inquiries/${id}/messages`, withUserPayload(payload))
  return data
}

export async function createInquiryQuote(id, payload) {
  const { data } = await http.post(`/inquiries/${id}/quotes`, withUserPayload(payload))
  return data
}

export async function updateInquiryQuote(id, quoteId, payload) {
  const { data } = await http.patch(`/inquiries/${id}/quotes/${quoteId}`, withUserPayload(payload))
  return data
}

export async function submitContact(payload) {
  const { data } = await http.post('/contact', payload)
  return data
}

export async function subscribeNewsletter(email) {
  const { data } = await http.post('/newsletter', { email })
  return data
}

export async function getNotifications(params = {}) {
  const { data } = await http.get('/notifications', { params: withUser(params) })
  return data
}

export async function markNotificationsRead(payload) {
  const { data } = await http.post('/notifications/read', withUserPayload(payload))
  return data
}

export async function loginUser(payload) {
  const { data } = await http.post('/auth/login', payload)
  return data
}

export async function changePassword(payload) {
  const { data } = await http.post('/auth/change-password', withUserPayload(payload))
  return data
}

export async function registerUser(payload) {
  const { data } = await http.post('/auth/register', payload)
  return data
}

export async function registerVendor(payload) {
  const { data } = await http.post('/auth/vendor-register', payload)
  return data
}

export async function uploadVendorApplicationFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await http.post('/vendor/application-upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: UPLOAD_TIMEOUT_MS
  })
  return data
}

export async function getVendorApplication(params = {}) {
  const { data } = await http.get('/vendor/application', { params: withUser(params) })
  return data
}

export async function getAdminAnalytics() {
  const { data } = await http.get('/admin/analytics', { params: withUser() })
  return data
}

export async function getAdminProducts() {
  const { data } = await http.get('/admin/products', { params: withUser(withLocale()) })
  return data
}

export async function createAdminProduct(payload) {
  const { data } = await http.post('/admin/products', withUserPayload(payload), { timeout: PRODUCT_SAVE_TIMEOUT_MS })
  return data
}

export async function updateAdminProduct(id, payload) {
  const { data } = await http.patch(`/admin/products/${id}`, withUserPayload(payload), { timeout: PRODUCT_SAVE_TIMEOUT_MS })
  return data
}

export async function reorderAdminProducts(orderedIds) {
  const { data } = await http.patch('/admin/products/reorder', withUserPayload({ orderedIds }), { timeout: PRODUCT_SAVE_TIMEOUT_MS })
  return data
}

export async function deleteAdminProduct(id) {
  const { data } = await http.delete(`/admin/products/${id}`, { data: withUserPayload() })
  return data
}

export async function getAdminSpecTemplate() {
  const { data } = await http.get('/admin/spec-template', { params: withUser() })
  return data
}

export async function updateAdminSpecTemplate(payload) {
  const { data } = await http.put('/admin/spec-template', withUserPayload(payload))
  return data
}

export async function getAdminCategories() {
  const { data } = await http.get('/admin/categories', { params: withUser(withLocale()) })
  return data
}

export async function createAdminCategory(payload) {
  const { data } = await http.post('/admin/categories', withUserPayload(payload))
  return data
}

export async function updateAdminCategory(id, payload) {
  const { data } = await http.patch(`/admin/categories/${id}`, withUserPayload(payload))
  return data
}

export async function getAdminBanners() {
  const { data } = await http.get('/admin/banners', { params: withUser(withLocale()) })
  return data
}

export async function createAdminBanner(payload) {
  const { data } = await http.post('/admin/banners', withUserPayload(payload))
  return data
}

export async function updateAdminBanner(id, payload) {
  const { data } = await http.patch(`/admin/banners/${id}`, withUserPayload(payload))
  return data
}

export async function getAdminVendors() {
  const { data } = await http.get('/admin/vendors', { params: withUser() })
  return data
}

export async function updateAdminVendor(id, payload) {
  const { data } = await http.patch(`/admin/vendors/${id}`, withUserPayload(payload))
  return data
}

export async function getAdminInquiries() {
  const { data } = await http.get('/admin/inquiries', { params: withUser() })
  return data
}

export async function getAdminInquiry(id) {
  const { data } = await http.get(`/admin/inquiries/${id}`, { params: withUser() })
  return data
}

export async function getAdminUsers() {
  const { data } = await http.get('/admin/users', { params: withUser() })
  return data
}

export async function updateAdminUser(id, payload) {
  const { data } = await http.patch(`/admin/users/${id}`, withUserPayload(payload))
  return data
}

export async function getAdminAdmins() {
  const { data } = await http.get('/admin/admins', { params: withUser() })
  return data
}

export async function createAdminAdmin(payload) {
  const { data } = await http.post('/admin/admins', withUserPayload(payload))
  return data
}

export async function updateAdminAdmin(id, payload) {
  const { data } = await http.patch(`/admin/admins/${id}`, withUserPayload(payload))
  return data
}

export async function deleteAdminAdmin(id) {
  const { data } = await http.delete(`/admin/admins/${id}`, { data: withUserPayload() })
  return data
}

export async function getAdminMedia() {
  const { data } = await http.get('/admin/media', { params: withUser() })
  return data
}

export async function uploadAdminMedia(file, category = '') {
  return uploadMediaFile('/admin/media', file, { category })
}

export async function deleteAdminMedia(url) {
  const { data } = await http.delete('/admin/media', { data: withUserPayload({ url }) })
  return data
}

export async function updateAdminMediaCategoryForItem(itemOrUrl, category = '', name = undefined) {
  const payload = typeof itemOrUrl === 'object'
    ? { url: itemOrUrl.url, storageKey: itemOrUrl.storageKey, category }
    : { url: itemOrUrl, category }
  if (name !== undefined) payload.name = name
  const { data } = await http.patch('/admin/media', withUserPayload(payload))
  return data
}

export async function createAdminMediaCategory(payload) {
  const body = typeof payload === 'string' ? { nameEn: payload, nameZh: payload } : payload
  const { data } = await http.post('/admin/media/categories', withUserPayload(body))
  return data
}

export async function deleteAdminMediaCategory(category) {
  const body = typeof category === 'object' ? category : { category }
  const { data } = await http.delete('/admin/media/categories', { data: withUserPayload(body) })
  return data
}

export async function getAdminContacts() {
  const { data } = await http.get('/admin/contacts', { params: withUser() })
  return data
}

export async function getAdminI18n(locale) {
  const { data } = await http.get('/admin/i18n', { params: withUser(locale ? { locale } : {}) })
  return data
}

export async function updateAdminI18n(payload) {
  const { data } = await http.put('/admin/i18n', withUserPayload(payload))
  return data
}

export async function getVendorProducts(params = {}) {
  const { data } = await http.get('/vendor/products', { params: withUser(withLocale(params)) })
  return data
}

export async function createVendorProduct(payload) {
  const { data } = await http.post('/vendor/products', withUserPayload(payload), { timeout: PRODUCT_SAVE_TIMEOUT_MS })
  return data
}

export async function updateVendorProduct(id, payload) {
  const { data } = await http.patch(`/vendor/products/${id}`, withUserPayload(payload), { timeout: PRODUCT_SAVE_TIMEOUT_MS })
  return data
}

export async function reorderVendorProducts(orderedIds) {
  const { data } = await http.patch('/vendor/products/reorder', withUserPayload({ orderedIds }), { timeout: PRODUCT_SAVE_TIMEOUT_MS })
  return data
}

export async function getVendorMedia(params = {}) {
  const { data } = await http.get('/vendor/media', { params: withUser(params) })
  return data
}

export async function uploadVendorMedia(file, category = '') {
  return uploadMediaFile('/vendor/media', file, { category })
}

export async function deleteVendorMedia(url) {
  const { data } = await http.delete('/vendor/media', { data: withUserPayload({ url }) })
  return data
}

export async function updateVendorMediaCategoryForItem(itemOrUrl, category = '', name = undefined) {
  const payload = typeof itemOrUrl === 'object'
    ? { url: itemOrUrl.url, storageKey: itemOrUrl.storageKey, category }
    : { url: itemOrUrl, category }
  if (name !== undefined) payload.name = name
  const { data } = await http.patch('/vendor/media', withUserPayload(payload))
  return data
}

export async function createVendorMediaCategory(payload) {
  const body = typeof payload === 'string' ? { nameEn: payload, nameZh: payload } : payload
  const { data } = await http.post('/vendor/media/categories', withUserPayload(body))
  return data
}

export async function deleteVendorMediaCategory(category) {
  const body = typeof category === 'object' ? category : { category }
  const { data } = await http.delete('/vendor/media/categories', { data: withUserPayload(body) })
  return data
}
