<template>
  <AdminShell>
    <div class="space-y-6">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 class="text-2xl font-bold">{{ pageTitle }}</h1>
          <p class="text-sm text-muted-foreground">{{ pageSubtitle }}</p>
        </div>
        <button type="button" class="btn btn-outline h-9 px-4" @click="load">
          <RefreshCw class="h-4 w-4" :class="loading ? 'animate-spin' : ''" />
          {{ t.refresh }}
        </button>
      </div>

      <div v-if="loading" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div v-for="i in 4" :key="i" class="shimmer h-32 rounded-xl"></div>
      </div>

      <div v-else-if="error" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
        {{ error }}
      </div>

      <template v-else>
        <section v-if="section === 'dashboard'" class="space-y-6">
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div v-for="stat in statCards" :key="stat.title" class="rounded-xl border bg-card text-card-foreground shadow-sm">
              <div class="flex items-center justify-between p-6 pb-2">
                <h3 class="text-sm font-medium text-muted-foreground">{{ stat.title }}</h3>
                <div class="flex h-8 w-8 items-center justify-center rounded-lg" :class="stat.color">
                  <component :is="stat.icon" class="h-4 w-4" />
                </div>
              </div>
              <div class="p-6 pt-0">
                <div class="text-2xl font-bold">{{ stat.value }}</div>
                <p v-if="stat.change" class="mt-1 text-xs text-muted-foreground">{{ stat.change }} {{ t.vsLastMonth }}</p>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <div class="rounded-xl border bg-card shadow-sm lg:col-span-2">
              <div class="p-6">
                <h3 class="flex items-center gap-2 text-base font-semibold">
                  <TrendingUp class="h-4 w-4 text-blue-600" />
                  {{ t.inquiryTrend }}
                </h3>
              </div>
              <div class="p-6 pt-0">
                <div class="flex h-[220px] items-end gap-3 border-b border-l px-3 pb-3">
                  <div v-for="row in monthlyData" :key="row.month" class="flex min-w-0 flex-1 flex-col items-center gap-2">
                    <div class="w-full rounded-t-md bg-sky-500 transition-all" :style="{ height: chartHeight(row.inquiries) }"></div>
                    <span class="text-[11px] text-muted-foreground">{{ row.month }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="rounded-xl border bg-card shadow-sm">
              <div class="p-6">
                <h3 class="text-base font-semibold">{{ t.inquiryStatus }}</h3>
              </div>
              <div class="flex items-center justify-center p-6 pt-0">
                <div v-if="statusData.length" class="relative grid h-[150px] w-[150px] place-items-center rounded-full" :style="{ background: donutBackground(statusData) }">
                  <div class="grid h-[92px] w-[92px] place-items-center rounded-full bg-white text-center">
                    <strong>{{ inquiries.length }}</strong>
                    <span class="text-xs text-muted-foreground">{{ t.inquiries }}</span>
                  </div>
                </div>
                <p v-else class="text-sm text-muted-foreground">{{ t.noData }}</p>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <DataCard class="lg:col-span-2" :title="t.recentInquiries">
              <div class="space-y-3">
                <div v-for="row in inquiries.slice(0, 5)" :key="row.id" class="flex items-center justify-between rounded-lg border p-3">
                  <div class="min-w-0">
                    <p class="whitespace-normal font-medium leading-snug" :class="fitTextClass(row.contactName)">{{ row.contactName }}</p>
                    <p class="text-xs text-muted-foreground">{{ row.inquiryNumber }} · {{ formatDate(row.createdAt) }}</p>
                  </div>
                  <span class="rounded-full px-2 py-0.5 text-xs font-medium" :class="statusClass(row.status)">
                    {{ inquiryStatusLabel(row.status) }}
                  </span>
                </div>
                <p v-if="!inquiries.length" class="text-sm text-muted-foreground">{{ t.noInquiries }}</p>
              </div>
            </DataCard>

            <DataCard :title="t.topProducts">
              <div class="space-y-4">
                <div v-for="(product, index) in topProducts" :key="product.name" class="flex items-center gap-3">
                  <span class="flex h-6 w-6 items-center justify-center rounded-full text-xs font-medium text-white" :style="{ backgroundColor: colors[index % colors.length] }">{{ index + 1 }}</span>
                  <p class="flex-1 whitespace-normal font-medium leading-snug" :class="fitTextClass(product.name)">{{ product.name }}</p>
                  <span class="text-sm text-muted-foreground">{{ product.units }} {{ t.units }}</span>
                </div>
                <p v-if="!topProducts.length" class="text-sm text-muted-foreground">{{ t.noData }}</p>
              </div>
            </DataCard>
          </div>
        </section>

        <section v-else-if="section === 'products'" class="space-y-4">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div class="flex gap-2">
              <RouterLink :to="localized('/admin/products')" class="btn h-9 border px-4" :class="!route.query.status ? 'bg-blue-600 text-white' : 'bg-background'">{{ t.allProducts }}</RouterLink>
              <RouterLink :to="localized('/admin/products?status=PENDING_REVIEW')" class="btn h-9 border px-4" :class="route.query.status === 'PENDING_REVIEW' ? 'bg-blue-600 text-white' : 'bg-background'">{{ t.pendingReview }}</RouterLink>
            </div>
            <RouterLink :to="localized('/admin/products/new')" class="btn h-9 bg-primary px-4 text-primary-foreground">
              <Plus class="h-4 w-4" />
              {{ t.newProduct }}
            </RouterLink>
          </div>
          <div class="relative max-w-xl">
            <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input v-model.trim="productSearch" class="input h-10 pl-9 pr-10" :placeholder="t.searchProducts" />
            <button v-if="productSearch" type="button" class="absolute right-2 top-1/2 -translate-y-1/2 rounded px-2 text-xs text-muted-foreground hover:text-foreground" @click="productSearch = ''">
              {{ t.clear }}
            </button>
          </div>
          <DataTable>
            <thead>
              <tr>
                <th class="w-10"></th>
                <th>{{ t.product }}</th>
                <th>{{ t.category }}</th>
                <th>{{ t.price }}</th>
                <th>{{ t.status }}</th>
                <th>{{ t.updatedAt }}</th>
                <th class="text-right">{{ t.actions }}</th>
              </tr>
            </thead>
            <tbody @dragover.prevent="setProductListDropTarget(null)" @drop.prevent="dropProductToEnd">
              <tr
                v-for="product in filteredProducts"
                :key="product.id"
                class="transition-colors"
                :class="[productListDragState.draggedId === product.id ? 'opacity-60' : '', productListDragState.overId === product.id ? 'bg-primary/5' : '']"
                @dragenter.stop.prevent="setProductListDropTarget(product.id)"
                @dragover.stop.prevent="setProductListDropTarget(product.id)"
                @drop.stop.prevent="dropProductOn(product.id)"
              >
                <td>
                  <button type="button" draggable="true" class="flex h-8 w-8 cursor-grab items-center justify-center rounded-md text-muted-foreground transition hover:bg-muted hover:text-foreground active:cursor-grabbing" @dragstart.stop="startProductListDrag(product.id, $event)" @dragend="clearProductListDrag">
                    <GripVertical class="h-4 w-4" />
                  </button>
                </td>
                <td>
                  <div class="flex items-center gap-3">
                    <img :src="product.images?.[0]?.thumbnailUrl || product.images?.[0]?.url || '/images/placeholder.svg'" alt="" class="h-11 w-11 rounded-md bg-muted object-contain p-1" loading="lazy" decoding="async" />
                    <div class="min-w-0">
                      <p class="whitespace-normal font-medium leading-snug" :class="fitTextClass(product.name)">{{ product.name }}</p>
                      <p class="text-xs text-muted-foreground">{{ product.sku }}</p>
                    </div>
                  </div>
                </td>
                <td>{{ product.category?.name || '-' }}</td>
                <td>{{ productPrice(product) }}</td>
                <td><StatusPill :label="productStatusLabel(product.status)" :class-name="productStatusClass(product.status)" /></td>
                <td>{{ formatDate(product.updatedAt || product.createdAt) }}</td>
                <td>
                  <div class="flex justify-end gap-2">
                    <button v-if="product.status === 'PENDING_REVIEW'" type="button" class="btn h-8 bg-emerald-600 px-3 text-xs text-white" @click="setProductStatus(product, 'ACTIVE')">{{ t.approve }}</button>
                    <button v-if="product.status === 'PENDING_REVIEW'" type="button" class="btn h-8 border px-3 text-xs" @click="setProductStatus(product, 'REJECTED')">{{ t.reject }}</button>
                    <RouterLink :to="localized(`/admin/products/${product.id}/edit`)" class="btn h-8 border px-3 text-xs">{{ t.edit }}</RouterLink>
                    <button type="button" class="btn h-8 border px-3 text-xs text-destructive" :disabled="saving" @click="removeProduct(product)">{{ t.deleteProduct }}</button>
                  </div>
                </td>
              </tr>
              <tr v-if="!filteredProducts.length">
                <td colspan="7" class="py-8 text-center text-sm text-muted-foreground">{{ t.noData }}</td>
              </tr>
            </tbody>
          </DataTable>
        </section>

        <section v-else-if="section === 'spec-template'" class="max-w-6xl space-y-4">
          <div class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            {{ t.specTemplateNotice.replace('{count}', specTemplateProductCount) }}
          </div>
          <div class="flex flex-wrap items-center justify-between gap-3">
            <button type="button" class="btn btn-outline h-9 px-4" @click="addTemplateSpecGroup">
              <Plus class="h-4 w-4" />
              {{ t.addSpecGroup }}
            </button>
            <button type="button" class="btn h-9 bg-primary px-4 text-primary-foreground" :disabled="savingSpecTemplate" @click="saveSpecTemplate">
              <span v-if="savingSpecTemplate" class="h-4 w-4 animate-spin rounded-full border-2 border-white/60 border-t-white"></span>
              {{ savingSpecTemplate ? t.saving : t.saveSpecTemplate }}
            </button>
          </div>
          <div class="space-y-4">
            <div v-for="group in specTemplateGroups" :key="group.key" class="rounded-xl border bg-background p-4 shadow-sm">
              <div class="mb-4 grid gap-2 lg:grid-cols-[1fr_1fr_auto_auto] lg:items-end">
                <label class="space-y-1 text-xs font-medium">
                  <span>{{ t.specGroupNameEn }}</span>
                  <input class="input h-9" :value="group.noteEn" :placeholder="t.specGroupEn" @input="updateTemplateGroupName(group, 'en', $event.target.value)" />
                </label>
                <label class="space-y-1 text-xs font-medium">
                  <span>{{ t.specGroupNameZh }}</span>
                  <input class="input h-9" :value="group.noteZh" :placeholder="t.specGroupZh" @input="updateTemplateGroupName(group, 'zh', $event.target.value)" />
                </label>
                <button type="button" class="btn btn-outline h-9 px-3 text-xs" @click="addTemplateSpec(group)">
                  <Plus class="h-3.5 w-3.5" />
                  {{ t.addSpec }}
                </button>
                <button type="button" class="btn btn-ghost h-9 px-3 text-xs text-destructive" @click="removeTemplateSpecGroup(group)">
                  <Trash2 class="h-4 w-4" />
                  {{ t.removeSpecGroup }}
                </button>
              </div>
              <div class="grid gap-3 xl:grid-cols-2">
                <div v-for="row in group.rows" :key="row.spec.id" class="rounded-lg border bg-muted/20 p-3">
                  <div class="grid gap-2 sm:grid-cols-2">
                    <input v-model.trim="row.spec.labelEn" class="input h-9" :placeholder="t.specNameEn" />
                    <input v-model.trim="row.spec.labelZh" class="input h-9" :placeholder="t.specNameZh" />
                    <label class="space-y-1 text-xs font-medium">
                      <span>{{ t.specOptionsEn }}</span>
                      <textarea class="textarea min-h-24" :value="optionText(row.spec, 'en')" @input="updateOptionText(row.spec, 'en', $event.target.value)"></textarea>
                    </label>
                    <label class="space-y-1 text-xs font-medium">
                      <span>{{ t.specOptionsZh }}</span>
                      <textarea class="textarea min-h-24" :value="optionText(row.spec, 'zh')" @input="updateOptionText(row.spec, 'zh', $event.target.value)"></textarea>
                    </label>
                  </div>
                  <button type="button" class="btn btn-ghost mt-2 h-8 px-3 text-xs text-destructive" @click="removeTemplateSpec(row.index)">
                    <Trash2 class="h-4 w-4" />
                    {{ t.removeSpec }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section v-else-if="section === 'product-form'" class="max-w-4xl">
          <form class="flex flex-col gap-6" @submit.prevent="submitProduct">
            <div v-if="['PENDING_REVIEW', 'REJECTED'].includes(productForm.status)" class="order-0 space-y-3 rounded-xl border border-amber-200 bg-amber-50 p-4">
              <div>
                <h2 class="font-semibold text-amber-900">{{ t.vendorProductReview }}</h2>
                <p class="text-sm text-amber-800">{{ t.currentStatus }} {{ productStatusLabel(productForm.status) }}</p>
              </div>
              <label class="block space-y-2 text-sm font-medium text-amber-950">
                <span>{{ t.rejectionReason }}</span>
                <textarea v-model.trim="productForm.rejectionReason" class="textarea bg-white" rows="3" :placeholder="t.rejectionReasonPlaceholder"></textarea>
              </label>
            </div>

            <div class="order-2 space-y-4 rounded-xl border bg-background p-6 shadow-sm">
              <h2 class="font-semibold">{{ t.basicInfo }}</h2>
              <div class="grid gap-4 md:grid-cols-2">
                <label v-for="field in productLocales" :key="`product-name-${field.code}`" class="space-y-2 text-sm font-medium">
                  <span>{{ t.productNameLocalized.replace('{locale}', field.label) }}</span>
                  <input v-model.trim="productForm.translations[field.code].name" class="input h-10" :required="field.code === 'en'" />
                </label>
                <label class="space-y-2 text-sm font-medium">
                  <span>{{ t.slug }}</span>
                  <input v-model.trim="productForm.slug" class="input h-10" required />
                </label>
                <label class="space-y-2 text-sm font-medium">
                  <span>{{ t.sku }}</span>
                  <input v-model.trim="productForm.sku" class="input h-10" required />
                </label>
              </div>
              <div class="grid gap-4 md:grid-cols-2">
                <label v-for="field in productLocales" :key="`product-desc-${field.code}`" class="block space-y-2 text-sm font-medium">
                  <span>{{ t.descriptionLocalized.replace('{locale}', field.label) }}</span>
                  <textarea v-model.trim="productForm.translations[field.code].description" class="textarea" rows="3"></textarea>
                </label>
              </div>
            </div>

            <div class="order-3 space-y-4 rounded-xl border bg-background p-6 shadow-sm">
              <div class="flex items-center justify-between">
                <h2 class="font-semibold">{{ t.specifications }}</h2>
                <span class="text-xs text-muted-foreground">{{ t.specTemplateLocked }}</span>
              </div>
              <p v-if="!productForm.specs.length" class="text-sm text-muted-foreground">{{ t.noSpecs }}</p>
              <div class="space-y-4">
                <div v-for="group in specFormGroups" :key="group.key" class="rounded-xl border bg-muted/20 p-4">
                  <div class="mb-3">
                    <h3 class="text-sm font-semibold">{{ group.title }}</h3>
                    <p class="mt-1 text-xs text-muted-foreground">{{ group.noteEn }} / {{ group.noteZh }}</p>
                  </div>
                  <div class="grid gap-3 lg:grid-cols-2">
                    <div v-for="row in group.rows" :key="row.spec.id" class="rounded-lg border bg-background p-3">
                      <div class="grid gap-3 sm:grid-cols-[minmax(0,0.8fr)_minmax(0,1fr)]">
                        <div class="min-w-0 rounded-md bg-muted/40 px-3 py-2">
                          <p class="break-words text-sm font-semibold">{{ row.spec.labelZh || row.spec.labelEn }}</p>
                          <p class="mt-1 break-words text-xs text-muted-foreground">{{ row.spec.labelEn }}</p>
                        </div>
                        <div class="grid gap-2">
                          <input v-model.trim="row.spec.valueEn" class="input h-9" :list="`admin-spec-options-en-${row.index}`" :placeholder="t.specValueEn" />
                          <input v-model.trim="row.spec.valueZh" class="input h-9" :list="`admin-spec-options-zh-${row.index}`" :placeholder="t.specValueZh" />
                        </div>
                        <datalist :id="`admin-spec-options-en-${row.index}`">
                          <option v-for="option in row.spec.optionsEn" :key="`en-${option}`" :value="option" />
                        </datalist>
                        <datalist :id="`admin-spec-options-zh-${row.index}`">
                          <option v-for="option in row.spec.optionsZh" :key="`zh-${option}`" :value="option" />
                        </datalist>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="order-4 space-y-4 rounded-xl border bg-background p-6 shadow-sm">
              <div class="flex items-center justify-between">
                <div>
                  <h2 class="font-semibold">{{ t.tradeDisplay }}</h2>
                  <p class="mt-1 text-xs text-muted-foreground">{{ t.pricing }}: {{ priceModeLabel() }}</p>
                </div>
                <button type="button" class="btn btn-outline h-8 px-3 text-xs" @click="openPricingDialog">
                  {{ t.edit }} {{ t.pricing }}
                </button>
              </div>
              <div class="rounded-lg border bg-muted/30 px-4 py-3">
                <p class="text-sm font-medium">{{ priceModeLabel() }}</p>
                <p class="mt-1 text-xs leading-5 text-muted-foreground">{{ priceModeDescription() }}</p>
              </div>
              <div class="grid gap-4 md:grid-cols-2">
                <label class="space-y-2 text-sm font-medium">
                  <span>{{ t.shipFromEn }}</span>
                  <input v-model.trim="productForm.shipFromEn" class="input h-10" placeholder="Shenzhen / Yiwu" />
                </label>
                <label class="space-y-2 text-sm font-medium">
                  <span>{{ t.shipFromZh }}</span>
                  <input v-model.trim="productForm.shipFromZh" class="input h-10" placeholder="深圳 / 义乌" />
                </label>
              </div>
            </div>

            <div class="order-5 space-y-4 rounded-xl border bg-background p-6 shadow-sm">
              <h2 class="font-semibold">{{ t.categoryAndAttributes }}</h2>
              <div class="grid gap-4 md:grid-cols-2">
                <label class="space-y-2 text-sm font-medium">
                  <span>{{ t.category }}</span>
                  <select v-model="productForm.categoryId" class="select h-10">
                    <option value="">{{ t.uncategorized }}</option>
                    <option v-for="category in categories" :key="category.id" :value="category.id">{{ category.name }}</option>
                  </select>
                </label>
                <label class="space-y-2 text-sm font-medium">
                  <span>{{ t.status }}</span>
                  <select v-model="productForm.status" class="select h-10">
                    <option value="DRAFT">{{ productStatusLabel('DRAFT') }}</option>
                    <option value="ACTIVE">{{ productStatusLabel('ACTIVE') }}</option>
                    <option value="PENDING_REVIEW">{{ productStatusLabel('PENDING_REVIEW') }}</option>
                    <option value="REJECTED">{{ productStatusLabel('REJECTED') }}</option>
                    <option value="ARCHIVED">{{ productStatusLabel('ARCHIVED') }}</option>
                  </select>
                </label>
              </div>
              <label class="block space-y-2 text-sm font-medium">
                <span>{{ t.brandName }}</span>
                <input v-model.trim="productForm.brandName" class="input h-10" placeholder="Misicheng" />
              </label>
              <div class="flex flex-wrap gap-6">
                <label class="inline-flex items-center gap-2 text-sm font-medium">
                  <input v-model="productForm.isFeatured" type="checkbox" class="h-4 w-4 rounded border-input" />
                  {{ t.isFeatured }}
                </label>
                <label class="inline-flex items-center gap-2 text-sm font-medium">
                  <input v-model="productForm.isNew" type="checkbox" class="h-4 w-4 rounded border-input" />
                  {{ t.isNew }}
                </label>
              </div>
            </div>

            <div class="order-1 space-y-4 rounded-xl border bg-background p-6 shadow-sm">
              <h2 class="font-semibold">{{ t.productImages }}</h2>
              <div class="space-y-3">
                <label class="text-sm font-medium">{{ t.displayImages }}</label>
                <div class="flex flex-wrap gap-3" @dragover.prevent @drop.prevent="dropProductImageToEnd('display')">
                  <div
                    v-for="(url, index) in productForm.displayImages"
                    :key="`display-${index}-${url}`"
                    draggable="true"
                    class="group relative cursor-grab rounded-lg transition active:cursor-grabbing"
                    :class="[productImageDragState.type === 'display' && productImageDragState.from === index ? 'opacity-60' : '', productImageDragState.type === 'display' && productImageDragState.over === index ? 'ring-2 ring-primary/40' : '']"
                    @dragstart.stop="startProductImageDrag('display', index, $event)"
                    @dragend="clearProductImageDrag"
                    @dragenter.prevent="setProductImageDropTarget('display', index)"
                    @dragover.prevent="setProductImageDropTarget('display', index)"
                    @drop.stop.prevent="dropProductImage('display', index)"
                  >
                    <img :src="url" alt="" draggable="false" class="h-24 w-24 rounded-lg bg-muted object-contain p-1" />
                    <span class="pointer-events-none absolute left-1 top-1 flex h-6 w-6 items-center justify-center rounded-full border bg-background/90 text-muted-foreground shadow-sm">
                      <GripVertical class="h-3.5 w-3.5" />
                    </span>
                    <button type="button" class="absolute -right-2 -top-2 hidden h-5 w-5 items-center justify-center rounded-full bg-destructive text-white group-hover:flex" @click="removeDisplayImage(index)">
                      <Trash2 class="h-3 w-3" />
                    </button>
                  </div>
                </div>
                <div class="flex flex-col gap-2 sm:flex-row">
                  <input v-model.trim="productForm.displayImageInput" class="input h-10 flex-1" :placeholder="t.displayImagePlaceholder" @keydown.enter.prevent="addDisplayImage" />
                  <div class="flex flex-wrap shrink-0 gap-2">
                    <button type="button" class="btn btn-outline h-10 px-3" @click="addDisplayImage">
                      <ImageIcon class="h-4 w-4" />
                      {{ t.addImage }}
                    </button>
                    <button type="button" class="btn btn-outline h-10 px-3" :disabled="uploadingMedia" @click="triggerMediaUpload('display')">
                      <Upload class="h-4 w-4" />
                      {{ t.uploadImage }}
                    </button>
                    <button type="button" class="btn btn-outline h-10 px-3" @click="openMediaPicker('display')">
                      <ImageIcon class="h-4 w-4" />
                      {{ t.chooseFromMedia }}
                    </button>
                  </div>
                </div>
              </div>

              <div class="space-y-3">
                <label class="text-sm font-medium">{{ t.posterImages }}</label>
                <div class="flex flex-wrap gap-3" @dragover.prevent @drop.prevent="dropProductImageToEnd('poster')">
                  <div
                    v-for="(url, index) in productForm.posterImages"
                    :key="`poster-${index}-${url}`"
                    draggable="true"
                    class="group relative cursor-grab rounded-lg transition active:cursor-grabbing"
                    :class="[productImageDragState.type === 'poster' && productImageDragState.from === index ? 'opacity-60' : '', productImageDragState.type === 'poster' && productImageDragState.over === index ? 'ring-2 ring-primary/40' : '']"
                    @dragstart.stop="startProductImageDrag('poster', index, $event)"
                    @dragend="clearProductImageDrag"
                    @dragenter.prevent="setProductImageDropTarget('poster', index)"
                    @dragover.prevent="setProductImageDropTarget('poster', index)"
                    @drop.stop.prevent="dropProductImage('poster', index)"
                  >
                    <img :src="url" alt="" draggable="false" class="h-24 w-24 rounded-lg bg-muted object-contain p-1" />
                    <span class="pointer-events-none absolute left-1 top-1 flex h-6 w-6 items-center justify-center rounded-full border bg-background/90 text-muted-foreground shadow-sm">
                      <GripVertical class="h-3.5 w-3.5" />
                    </span>
                    <button type="button" class="absolute -right-2 -top-2 hidden h-5 w-5 items-center justify-center rounded-full bg-destructive text-white group-hover:flex" @click="removePosterImage(index)">
                      <Trash2 class="h-3 w-3" />
                    </button>
                  </div>
                </div>
                <div class="flex flex-col gap-2 sm:flex-row">
                  <input v-model.trim="productForm.posterImageInput" class="input h-10 flex-1" :placeholder="t.posterImagePlaceholder" @keydown.enter.prevent="addPosterImage" />
                  <div class="flex flex-wrap shrink-0 gap-2">
                    <button type="button" class="btn btn-outline h-10 px-3" @click="addPosterImage">
                      <ImageIcon class="h-4 w-4" />
                      {{ t.addImage }}
                    </button>
                    <button type="button" class="btn btn-outline h-10 px-3" :disabled="uploadingMedia" @click="triggerMediaUpload('poster')">
                      <Upload class="h-4 w-4" />
                      {{ t.uploadImage }}
                    </button>
                    <button type="button" class="btn btn-outline h-10 px-3" @click="openMediaPicker('poster')">
                      <ImageIcon class="h-4 w-4" />
                      {{ t.chooseFromMedia }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="order-6 space-y-4 rounded-xl border bg-background p-6 shadow-sm">
              <div class="flex items-center justify-between">
                <h2 class="font-semibold">{{ t.variants }}</h2>
                <button type="button" class="btn btn-outline h-8 px-3 text-xs" @click="addVariantType">
                  <Plus class="h-3.5 w-3.5" />
                  {{ t.addVariantType }}
                </button>
              </div>

              <div class="space-y-3">
                <div v-for="(type, index) in productForm.variantTypes" :key="type.id" class="rounded-lg border p-3">
                  <div class="grid gap-2 md:grid-cols-[1fr_1fr_36px] md:items-end">
                    <label class="space-y-1 text-xs font-medium">
                      <span>{{ t.variantTypeNameEn }}</span>
                      <input v-model.trim="type.nameEn" class="input h-9" placeholder="Color" />
                    </label>
                    <label class="space-y-1 text-xs font-medium">
                      <span>{{ t.variantTypeNameZh }}</span>
                      <input v-model.trim="type.nameZh" class="input h-9" placeholder="颜色" />
                    </label>
                    <button type="button" class="btn btn-ghost h-9 w-9 text-destructive" :disabled="productForm.variantTypes.length <= 1" @click="removeVariantType(index)">
                      <Trash2 class="h-4 w-4" />
                    </button>
                  </div>
                  <div class="mt-2 grid gap-2 md:grid-cols-2">
                    <label class="space-y-1 text-xs font-medium">
                      <span>{{ t.variantTypeValuesEn }}</span>
                      <textarea v-model.trim="type.valuesTextEn" class="textarea" rows="2" placeholder="White&#10;Black"></textarea>
                    </label>
                    <label class="space-y-1 text-xs font-medium">
                      <span>{{ t.variantTypeValuesZh }}</span>
                      <textarea v-model.trim="type.valuesTextZh" class="textarea" rows="2" placeholder="白色&#10;黑色"></textarea>
                    </label>
                  </div>
                </div>
              </div>

              <div class="flex items-center justify-between border-t pt-4">
                <h3 class="text-sm font-semibold">{{ t.variantCombinations }}</h3>
                <button type="button" class="btn btn-outline h-8 px-3 text-xs" @click="addVariant">
                  <Plus class="h-3.5 w-3.5" />
                  {{ t.addVariant }}
                </button>
              </div>
              <div class="space-y-3">
                <div v-for="(variant, index) in productForm.variants" :key="variant.id" class="rounded-lg border p-3">
                  <div class="grid gap-3 md:grid-cols-[1fr_120px_100px_36px] md:items-end">
                    <label class="space-y-1 text-xs font-medium">
                      <span>SKU</span>
                      <input v-model.trim="variant.sku" class="input h-9" :placeholder="`VAR-${String(index + 1).padStart(3, '0')}`" />
                    </label>
                    <label class="space-y-1 text-xs font-medium">
                      <span>{{ t.salePrice }}</span>
                      <input v-model.number="variant.price" class="input h-9 disabled:bg-muted disabled:text-muted-foreground" min="0" step="0.01" type="number" :disabled="productForm.priceMode !== 'variant'" :placeholder="productForm.priceMode === 'variant' ? '' : t.variantPriceLocked" />
                    </label>
                    <label class="space-y-1 text-xs font-medium">
                      <span>{{ t.stock }}</span>
                      <input v-model.number="variant.stock" class="input h-9" min="0" type="number" />
                    </label>
                    <button type="button" class="btn btn-ghost h-9 w-9 text-destructive" :disabled="productForm.variants.length <= 1" @click="removeVariant(index)">
                      <Trash2 class="h-4 w-4" />
                    </button>
                  </div>
                  <div class="mt-3 grid gap-3 md:grid-cols-2">
                    <label v-for="type in productForm.variantTypes" :key="`${variant.id}-${type.key}`" class="space-y-1 text-xs font-medium">
                      <span>{{ variantTypeLabel(type) }}</span>
                      <select class="select h-9" :value="variant.optionValues?.[type.key] || ''" @change="setVariantOption(variant, type, $event.target.value)">
                        <option value="">{{ t.selectVariantValue }}</option>
                        <option v-for="value in optionValuesForType(type)" :key="`${type.key}-${value.en}-${value.zh}`" :value="value.en || value.zh">
                          {{ variantValueLabel(value) }}
                        </option>
                      </select>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <div class="order-7 flex justify-end gap-3">
              <RouterLink :to="localized('/admin/products')" class="btn btn-outline h-10 px-4">{{ t.cancel }}</RouterLink>
              <button type="submit" class="btn h-10 bg-primary px-5 text-primary-foreground" :disabled="saving">
                <Save class="h-4 w-4" />
                {{ saving ? t.saving : t.save }}
              </button>
            </div>
          </form>
        </section>

        <section v-else-if="section === 'vendors'" class="space-y-4">
          <DataTable>
            <thead>
              <tr>
                <th>{{ t.companyName }}</th>
                <th>{{ t.contactPerson }}</th>
                <th>{{ t.email }}</th>
                <th>{{ t.files }}</th>
                <th>{{ t.status }}</th>
                <th>{{ t.submittedAt }}</th>
                <th>{{ t.actions }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="vendor in vendors" :key="vendor.id">
                <td>
                  <p class="font-medium">{{ vendor.companyName }}</p>
                  <p class="max-w-xs break-words text-xs text-muted-foreground">{{ vendor.description || t.noDescription }}</p>
                </td>
                <td>{{ vendor.contactPerson || vendor.name }}</td>
                <td>{{ vendor.email }}</td>
                <td>
                  <div v-if="vendor.certificationFiles?.length" class="flex flex-wrap gap-1.5">
                    <a
                      v-for="(file, index) in vendor.certificationFiles"
                      :key="file"
                      :href="file"
                      target="_blank"
                      rel="noreferrer"
                      class="inline-flex rounded-md border px-2 py-1 text-xs font-medium hover:bg-muted"
                    >
                      {{ t.fileLabel }} {{ index + 1 }}
                    </a>
                  </div>
                  <span v-else class="text-xs text-muted-foreground">{{ t.noFiles }}</span>
                </td>
                <td><StatusPill :label="vendorStatusLabel(vendor.status)" :class-name="vendorStatusClass(vendor.status)" /></td>
                <td>{{ formatDate(vendor.submittedAt) }}</td>
                <td>
                  <div class="flex flex-col gap-2">
                    <input v-model="vendor.reviewNoteDraft" class="input h-8 text-xs" :placeholder="t.reviewNote" />
                    <div class="flex gap-2">
                      <button type="button" class="btn h-8 bg-emerald-600 px-3 text-xs text-white" @click="setVendorStatus(vendor, 'APPROVED')">{{ t.approve }}</button>
                      <button type="button" class="btn h-8 border px-3 text-xs" @click="setVendorStatus(vendor, 'REJECTED')">{{ t.reject }}</button>
                      <button type="button" class="btn h-8 border px-3 text-xs" @click="setVendorStatus(vendor, 'DISABLED')">{{ t.disable }}</button>
                    </div>
                  </div>
                </td>
              </tr>
              <tr v-if="!vendors.length">
                <td colspan="7" class="py-8 text-center text-sm text-muted-foreground">{{ t.noData }}</td>
              </tr>
            </tbody>
          </DataTable>
        </section>

        <section v-else-if="section === 'banners'" class="grid gap-6 xl:grid-cols-[minmax(0,1.3fr)_minmax(420px,0.9fr)]">
          <div class="space-y-4">
            <div v-for="banner in banners" :key="banner.id" class="overflow-hidden rounded-xl border bg-background shadow-sm">
              <img :src="banner.image" :alt="banner.title || t.banners" class="h-56 w-full object-cover" />
              <div class="space-y-3 p-4">
                <div class="flex flex-wrap items-start justify-between gap-3">
                  <div class="min-w-0">
                    <h3 class="break-words font-semibold">{{ banner.title || t.noDescription }}</h3>
                    <p class="mt-1 line-clamp-2 text-sm text-muted-foreground">{{ banner.subtitle || t.noDescription }}</p>
                  </div>
                  <StatusPill :label="banner.isActive ? t.enabled : t.disabled" :class-name="banner.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-gray-100 text-gray-700'" />
                </div>
                <div class="grid gap-2 text-xs text-muted-foreground sm:grid-cols-3">
                  <span>{{ t.position }}: {{ banner.position }}</span>
                  <span>{{ t.sortOrder }}: {{ banner.sortOrder }}</span>
                  <span class="break-all">{{ t.link }}: {{ banner.link || '-' }}</span>
                </div>
                <button type="button" class="btn btn-outline h-9 px-4" @click="editBanner(banner)">{{ t.edit }}</button>
              </div>
            </div>
            <p v-if="!banners.length" class="text-sm text-muted-foreground">{{ t.noData }}</p>
          </div>

          <form class="space-y-4 rounded-xl border bg-background p-5 shadow-sm" @submit.prevent="submitBanner">
            <div class="flex items-center justify-between gap-3">
              <h2 class="font-semibold">{{ bannerForm.id ? t.editBanner : t.newBanner }}</h2>
              <button type="button" class="btn btn-outline h-8 px-3 text-xs" @click="resetBannerForm">{{ t.newBanner }}</button>
            </div>
            <div class="grid gap-3 sm:grid-cols-2">
              <label class="space-y-1.5">
                <span class="text-sm font-medium">{{ t.position }}</span>
                <input v-model.trim="bannerForm.position" class="input h-10" placeholder="hero" />
              </label>
              <label class="space-y-1.5">
                <span class="text-sm font-medium">{{ t.sortOrder }}</span>
                <input v-model.number="bannerForm.sortOrder" type="number" class="input h-10" />
              </label>
            </div>
            <label class="flex items-center gap-2 text-sm">
              <input v-model="bannerForm.isActive" type="checkbox" />
              {{ t.enabled }}
            </label>
            <label class="space-y-1.5">
              <span class="text-sm font-medium">{{ t.link }}</span>
              <input v-model.trim="bannerForm.link" class="input h-10" placeholder="/shop" />
            </label>
            <div class="space-y-2">
              <span class="text-sm font-medium">{{ t.bannerImage }}</span>
              <img v-if="bannerForm.image" :src="bannerForm.image" alt="" class="h-40 w-full rounded-lg object-cover" />
              <input v-model.trim="bannerForm.image" class="input h-10" :placeholder="t.imageUrl" />
              <div class="flex flex-wrap gap-2">
                <button type="button" class="btn btn-outline h-9 px-3 text-xs" :disabled="uploadingMedia" @click="triggerMediaUpload('banner')">
                  <Upload class="h-3.5 w-3.5" />
                  {{ uploadingMedia ? t.uploading : t.uploadImage }}
                </button>
                <button type="button" class="btn btn-outline h-9 px-3 text-xs" @click="openMediaPicker('banner')">{{ t.chooseFromMedia }}</button>
              </div>
            </div>
            <div class="max-h-[52vh] space-y-3 overflow-y-auto pr-1">
              <div v-for="item in bannerLocales" :key="`banner-${item.code}`" class="rounded-lg border p-3">
                <h3 class="mb-3 text-sm font-semibold">{{ item.label }}</h3>
                <input v-model.trim="bannerForm.translations[item.code].title" class="input h-9" :placeholder="t.title" />
                <textarea v-model.trim="bannerForm.translations[item.code].subtitle" class="textarea mt-2 min-h-20" :placeholder="t.description"></textarea>
                <input v-model.trim="bannerForm.translations[item.code].buttonText" class="input mt-2 h-9" :placeholder="t.buttonText" />
              </div>
            </div>
            <button type="submit" class="btn h-10 bg-primary px-5 text-primary-foreground" :disabled="saving">
              <Save class="h-4 w-4" />
              {{ saving ? t.saving : t.save }}
            </button>
          </form>
        </section>

        <section v-else-if="section === 'categories'" class="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(420px,0.8fr)]">
          <DataTable>
            <thead><tr><th>{{ t.coverImage }}</th><th>{{ t.category }}</th><th>Slug</th><th>{{ t.productCount }}</th><th>{{ t.status }}</th><th class="text-right">{{ t.actions }}</th></tr></thead>
            <tbody>
              <tr v-for="category in categories" :key="category.id">
                <td><img v-if="category.image" :src="category.image" :alt="category.name" class="h-14 w-20 rounded-lg object-cover" /></td>
                <td class="font-medium">{{ category.name }}</td>
                <td>{{ category.slug }}</td>
                <td>{{ category._count?.products || 0 }}</td>
                <td><StatusPill :label="category.isActive ? t.enabled : t.disabled" :class-name="category.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-gray-100 text-gray-700'" /></td>
                <td><div class="flex justify-end"><button type="button" class="btn btn-outline h-8 px-3 text-xs" @click="editCategory(category)">{{ t.edit }}</button></div></td>
              </tr>
            </tbody>
          </DataTable>

          <form class="space-y-4 rounded-xl border bg-background p-5 shadow-sm" @submit.prevent="submitCategory">
            <div class="flex items-center justify-between gap-3">
              <h2 class="font-semibold">{{ categoryForm.id ? t.editCategory : t.newCategory }}</h2>
              <button type="button" class="btn btn-outline h-8 px-3 text-xs" @click="resetCategoryForm">{{ t.newCategory }}</button>
            </div>
            <div class="grid gap-3 sm:grid-cols-2">
              <label class="space-y-1.5">
                <span class="text-sm font-medium">{{ t.slug }}</span>
                <input v-model.trim="categoryForm.slug" class="input h-10" />
              </label>
              <label class="space-y-1.5">
                <span class="text-sm font-medium">{{ t.sortOrder }}</span>
                <input v-model.number="categoryForm.sortOrder" type="number" class="input h-10" />
              </label>
            </div>
            <label class="flex items-center gap-2 text-sm">
              <input v-model="categoryForm.isActive" type="checkbox" />
              {{ t.enabled }}
            </label>
            <div class="space-y-2">
              <span class="text-sm font-medium">{{ t.coverImage }}</span>
              <img v-if="categoryForm.image" :src="categoryForm.image" alt="" class="h-36 w-full rounded-lg object-cover" />
              <input v-model.trim="categoryForm.image" class="input h-10" :placeholder="t.imageUrl" />
              <div class="flex flex-wrap gap-2">
                <button type="button" class="btn btn-outline h-9 px-3 text-xs" :disabled="uploadingMedia" @click="triggerMediaUpload('category')">
                  <Upload class="h-3.5 w-3.5" />
                  {{ uploadingMedia ? t.uploading : t.uploadImage }}
                </button>
                <button type="button" class="btn btn-outline h-9 px-3 text-xs" @click="openMediaPicker('category')">{{ t.chooseFromMedia }}</button>
              </div>
            </div>
            <div class="space-y-3">
              <div v-for="item in productLocales" :key="`category-${item.code}`" class="rounded-lg border p-3">
                <h3 class="mb-3 text-sm font-semibold">{{ item.label }}</h3>
                <input v-model.trim="categoryForm.translations[item.code].name" class="input h-9" :placeholder="t.name" />
                <textarea v-model.trim="categoryForm.translations[item.code].description" class="textarea mt-2 min-h-20" :placeholder="t.description"></textarea>
              </div>
            </div>
            <button type="submit" class="btn h-10 bg-primary px-5 text-primary-foreground" :disabled="saving">
              <Save class="h-4 w-4" />
              {{ saving ? t.saving : t.save }}
            </button>
          </form>
        </section>

        <section v-else-if="section === 'orders' && route.name !== 'admin-order-detail'">
          <DataTable>
            <thead><tr><th>{{ t.inquiryNumber }}</th><th>{{ t.contactPerson }}</th><th>{{ t.email }}</th><th>{{ t.status }}</th><th>{{ t.createdAt }}</th><th class="text-right">{{ t.actions }}</th></tr></thead>
            <tbody>
              <tr v-for="row in inquiries" :key="row.id">
                <td class="font-medium">{{ row.inquiryNumber }}</td>
                <td>{{ row.contactName }}</td>
                <td>{{ row.email }}</td>
                <td><StatusPill :label="inquiryStatusLabel(row.status)" :class-name="statusClass(row.status)" /></td>
                <td>{{ formatDate(row.createdAt) }}</td>
                <td>
                  <div class="flex justify-end">
                    <RouterLink :to="localized(`/admin/orders/${row.id}`)" class="btn h-8 border px-3 text-xs">{{ t.view }}</RouterLink>
                  </div>
                </td>
              </tr>
            </tbody>
          </DataTable>
        </section>

        <section v-else-if="section === 'orders' && route.name === 'admin-order-detail'" class="space-y-6">
          <div v-if="!selectedInquiry" class="rounded-xl border bg-background p-10 text-center text-sm text-muted-foreground">
            {{ t.noData }}
          </div>
          <template v-else>
            <div class="flex items-center justify-between gap-3">
              <div class="flex items-center gap-3">
                <RouterLink :to="localized('/admin/orders')" class="btn btn-ghost h-9 w-9">
                  <ChevronLeft class="h-5 w-5" />
                </RouterLink>
                <div>
                  <h2 class="text-2xl font-bold">{{ selectedInquiry.inquiryNumber }}</h2>
                  <p class="text-sm text-muted-foreground">{{ formatDate(selectedInquiry.createdAt) }}</p>
                </div>
              </div>
              <StatusPill :label="inquiryStatusLabel(selectedInquiry.status)" :class-name="statusClass(selectedInquiry.status)" />
            </div>

            <div class="flex border-b">
              <button type="button" class="btn h-10 rounded-none border-b-2 px-4" :class="orderTab === 'overview' ? 'border-blue-600 text-blue-700' : 'border-transparent text-muted-foreground'" @click="orderTab = 'overview'">
                <Package class="h-4 w-4" />
                {{ t.overview }}
              </button>
              <button type="button" class="btn h-10 rounded-none border-b-2 px-4" :class="orderTab === 'quotes' ? 'border-blue-600 text-blue-700' : 'border-transparent text-muted-foreground'" @click="orderTab = 'quotes'">
                <FileText class="h-4 w-4" />
                {{ t.quotes }} ({{ selectedInquiry.quotes?.length || 0 }})
              </button>
              <button type="button" class="btn h-10 rounded-none border-b-2 px-4" :class="orderTab === 'messages' ? 'border-blue-600 text-blue-700' : 'border-transparent text-muted-foreground'" @click="orderTab = 'messages'">
                <MessageSquare class="h-4 w-4" />
                {{ t.messages }} ({{ selectedInquiry.messages?.length || 0 }})
              </button>
            </div>

            <div v-if="orderTab === 'overview'" class="space-y-4">
              <div class="rounded-xl border bg-background p-4">
                <h3 class="mb-3 flex items-center gap-2 font-semibold"><User class="h-4 w-4" />{{ t.contactInfo }}</h3>
                <div class="grid gap-2 text-sm sm:grid-cols-2">
                  <div><span class="text-muted-foreground">{{ t.contactPerson }}: </span>{{ selectedInquiry.contactName }}</div>
                  <div><span class="text-muted-foreground">{{ t.email }}: </span>{{ selectedInquiry.email }}</div>
                  <div v-if="selectedInquiry.companyName"><span class="text-muted-foreground">{{ t.companyName }}: </span>{{ selectedInquiry.companyName }}</div>
                  <div v-if="selectedInquiry.phone"><span class="text-muted-foreground">{{ t.phone }}: </span>{{ selectedInquiry.phone }}</div>
                  <div v-if="selectedInquiry.country"><span class="text-muted-foreground">{{ t.country }}: </span>{{ selectedInquiry.country }}</div>
                  <div v-if="selectedInquiry.expectedDeliveryTime"><span class="text-muted-foreground">{{ t.expectedDeliveryTime }}: </span>{{ selectedInquiry.expectedDeliveryTime }}</div>
                </div>
                <div v-if="selectedInquiry.message" class="mt-3 border-t pt-3">
                  <p class="text-sm text-muted-foreground">{{ t.message }}</p>
                  <p class="break-words text-sm">{{ selectedInquiry.message }}</p>
                </div>
                <div v-if="selectedInquiry.quantityRequirements" class="mt-2">
                  <p class="text-sm text-muted-foreground">{{ t.quantityRequirements }}</p>
                  <p class="break-words text-sm">{{ selectedInquiry.quantityRequirements }}</p>
                </div>
                <div v-if="selectedInquiry.customizationNeeds" class="mt-2">
                  <p class="text-sm text-muted-foreground">{{ t.customizationNeeds }}</p>
                  <p class="break-words text-sm">{{ selectedInquiry.customizationNeeds }}</p>
                </div>
              </div>

              <div class="rounded-xl border bg-background p-4">
                <h3 class="mb-3 flex items-center gap-2 font-semibold"><Package class="h-4 w-4" />{{ t.productList }} ({{ selectedInquiry.items?.length || 0 }})</h3>
                <div class="max-h-[300px] space-y-2 overflow-y-auto">
                  <div v-for="item in selectedInquiry.items" :key="item.id" class="flex items-center gap-3 rounded-lg border p-3">
                    <img v-if="item.image" :src="item.image" :alt="item.name" class="h-12 w-12 rounded-lg bg-muted object-contain p-1" />
                    <div class="min-w-0 flex-1">
                      <p class="break-words font-medium">{{ item.name }}</p>
                      <p v-if="formatOptions(item.options)" class="mt-1 text-xs text-muted-foreground">{{ formatOptions(item.options) }}</p>
                      <p class="text-sm text-muted-foreground">{{ t.quantity }} {{ item.quantity }}<span v-if="item.price"> · {{ money(item.price) }}</span></p>
                      <p v-if="item.note" class="break-words text-sm text-muted-foreground">{{ t.note }} {{ item.note }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <div class="rounded-xl border bg-background p-4">
                <h3 class="mb-3 font-semibold">{{ t.actions }}</h3>
                <div class="flex flex-wrap items-center gap-3">
                  <span class="text-sm text-muted-foreground">{{ t.status }}</span>
                  <select v-model="selectedInquiry.status" class="select h-10 w-44" @change="setInquiryStatus(selectedInquiry.status)">
                    <option value="SUBMITTED">{{ inquiryStatusLabel('SUBMITTED') }}</option>
                    <option value="REVIEWING">{{ inquiryStatusLabel('REVIEWING') }}</option>
                    <option value="QUOTED">{{ inquiryStatusLabel('QUOTED') }}</option>
                    <option value="ACCEPTED">{{ inquiryStatusLabel('ACCEPTED') }}</option>
                    <option value="REJECTED">{{ inquiryStatusLabel('REJECTED') }}</option>
                    <option value="EXPIRED">{{ inquiryStatusLabel('EXPIRED') }}</option>
                    <option value="CANCELLED">{{ inquiryStatusLabel('CANCELLED') }}</option>
                  </select>
                  <button type="button" class="btn h-10 bg-primary px-4 text-primary-foreground" @click="openQuoteDialog()">
                    <Plus class="h-4 w-4" />
                    {{ t.createQuote }}
                  </button>
                </div>
              </div>
            </div>

            <div v-else-if="orderTab === 'quotes'" class="space-y-4">
              <div class="flex justify-end">
                <button type="button" class="btn h-10 bg-primary px-4 text-primary-foreground" @click="openQuoteDialog()">
                  <Plus class="h-4 w-4" />
                  {{ t.createQuote }}
                </button>
              </div>
              <div v-if="!selectedInquiry.quotes?.length" class="flex flex-col items-center justify-center py-12 text-center">
                <FileText class="mb-2 h-8 w-8 text-muted-foreground/40" />
                <p class="text-sm text-muted-foreground">{{ t.noQuotes }}</p>
              </div>
              <QuoteCard
                v-for="quote in selectedInquiry.quotes"
                :key="quote.id"
                :quote="quote"
                :inquiry-status="selectedInquiry.status"
                :is-admin="true"
                :locale="locale"
                @edit="openQuoteDialog(quote)"
              />
            </div>

            <div v-else-if="orderTab === 'messages'">
              <MessagePanel
                :inquiry-id="selectedInquiry.id"
                :current-user-id="adminUser?.id || ''"
                current-user-role="ADMIN"
                :initial-messages="selectedInquiry.messages || []"
                :locale="locale"
              />
            </div>
          </template>

          <QuoteEditDialog
            v-if="showQuoteDialog && selectedInquiry"
            :inquiry-id="selectedInquiry.id"
            :inquiry-items="selectedInquiry.items || []"
            :quote="editingQuote"
            :locale="locale"
            @close="closeQuoteDialog"
            @success="handleQuoteSaved"
          />
        </section>

        <section v-else-if="section === 'customers'" class="grid gap-6 xl:grid-cols-[minmax(0,1.3fr)_minmax(360px,0.7fr)]">
          <div v-if="!canManageCustomers" class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            {{ t.elevatedOnly }}
          </div>
          <template v-else>
            <DataTable>
              <thead><tr><th>{{ t.name }}</th><th>{{ t.email }}</th><th>{{ t.role }}</th><th>{{ t.status }}</th><th>{{ t.createdAt }}</th><th class="text-right">{{ t.actions }}</th></tr></thead>
              <tbody>
                <tr v-for="user in users" :key="user.id">
                  <td class="font-medium">{{ user.name || '-' }}</td>
                  <td>{{ user.email }}</td>
                  <td>{{ userRoleLabel(user.role) }}</td>
                  <td><StatusPill :label="user.isActive ? t.enabled : t.disabled" :class-name="user.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-gray-100 text-gray-700'" /></td>
                  <td>{{ formatDate(user.createdAt) }}</td>
                  <td class="text-right">
                    <button type="button" class="btn h-8 border px-3 text-xs" @click="editCustomerAccount(user)">{{ t.edit }}</button>
                  </td>
                </tr>
                <tr v-if="!users.length">
                  <td colspan="6" class="py-8 text-center text-sm text-muted-foreground">{{ t.noData }}</td>
                </tr>
              </tbody>
            </DataTable>

            <form class="space-y-4 rounded-xl border bg-card p-4 shadow-sm" @submit.prevent="saveCustomerAccount">
              <div class="flex items-center justify-between gap-3">
                <h2 class="font-semibold">{{ customerForm.id ? t.editCustomerAccount : t.selectCustomer }}</h2>
                <button type="button" class="btn btn-outline h-8 px-3 text-xs" @click="resetCustomerForm">{{ t.cancel }}</button>
              </div>
              <label class="space-y-1.5">
                <span class="text-sm font-medium">{{ t.name }}</span>
                <input v-model="customerForm.name" class="input h-10 bg-muted/40" disabled />
              </label>
              <label class="space-y-1.5">
                <span class="text-sm font-medium">{{ t.email }}</span>
                <input v-model.trim="customerForm.email" class="input h-10" type="text" :disabled="!customerForm.id" required />
              </label>
              <label class="space-y-1.5">
                <span class="text-sm font-medium">{{ t.role }}</span>
                <select v-model="customerForm.role" class="select h-10" :disabled="!customerForm.id">
                  <option value="USER">{{ t.personalUser }}</option>
                  <option value="VENDOR">{{ t.vendorAccount }}</option>
                </select>
              </label>
              <label class="space-y-1.5">
                <span class="text-sm font-medium">{{ t.newPassword }}</span>
                <input v-model.trim="customerForm.password" class="input h-10" type="password" minlength="8" :disabled="!customerForm.id" :placeholder="t.passwordOptional" />
              </label>
              <label class="flex items-center gap-2 text-sm">
                <input v-model="customerForm.isActive" type="checkbox" class="h-4 w-4 rounded border-input" :disabled="!customerForm.id" />
                {{ t.enabled }}
              </label>
              <button type="submit" class="btn h-10 bg-primary px-4 text-primary-foreground" :disabled="saving || !customerForm.id">
                <Save class="h-4 w-4" />
                {{ saving ? t.saving : t.save }}
              </button>
            </form>
          </template>
        </section>

        <section v-else-if="section === 'admins'" class="space-y-4">
          <div v-if="!canManageAdmins" class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            {{ t.superAdminOnly }}
          </div>
          <template v-else>
            <form class="grid gap-3 rounded-xl border bg-card p-4 shadow-sm md:grid-cols-[1fr_1fr_1fr_160px_auto_auto]" @submit.prevent="saveAdminAccount">
              <input v-model.trim="adminForm.name" class="input h-10" :placeholder="t.name" required />
              <input v-model.trim="adminForm.email" class="input h-10" :placeholder="t.email" type="text" required />
              <input v-model.trim="adminForm.password" class="input h-10" :placeholder="adminForm.id ? t.passwordOptional : t.password" type="password" :required="!adminForm.id" minlength="8" />
              <select v-model="adminForm.role" class="select h-10" :disabled="!canDeleteAdmins">
                <option value="ADMIN">{{ t.normalAdmin }}</option>
                <option value="SENIOR_ADMIN">{{ t.seniorAdmin }}</option>
              </select>
              <label class="flex items-center gap-2 text-sm">
                <input v-model="adminForm.isActive" type="checkbox" class="h-4 w-4 rounded border-input" />
                {{ t.enabled }}
              </label>
              <button type="submit" class="btn h-10 bg-primary px-4 text-primary-foreground" :disabled="saving">
                <Save class="h-4 w-4" />
                {{ saving ? t.saving : (adminForm.id ? t.save : t.createAdmin) }}
              </button>
              <button type="button" class="btn btn-outline h-10 px-4" @click="resetAdminForm">{{ t.cancel }}</button>
            </form>

            <DataTable>
              <thead><tr><th>{{ t.name }}</th><th>{{ t.email }}</th><th>{{ t.role }}</th><th>{{ t.status }}</th><th>{{ t.createdAt }}</th><th class="text-right">{{ t.actions }}</th></tr></thead>
              <tbody>
                <tr v-for="admin in admins" :key="admin.id">
                  <td class="font-medium">{{ admin.name || '-' }}</td>
                  <td>{{ admin.email }}</td>
                  <td>{{ adminRoleLabel(admin.role) }}</td>
                  <td><StatusPill :label="admin.isActive ? t.enabled : t.disabled" :class-name="admin.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-gray-100 text-gray-700'" /></td>
                  <td>{{ formatDate(admin.createdAt) }}</td>
                  <td class="text-right">
                    <button
                      v-if="canEditAdminAccount(admin)"
                      type="button"
                      class="btn h-8 border px-3 text-xs"
                      :disabled="saving"
                      @click="editAdminAccount(admin)"
                    >
                      {{ t.edit }}
                    </button>
                    <button
                      v-if="admin.role === 'ADMIN'"
                      type="button"
                      class="btn h-8 border px-3 text-xs"
                      :class="admin.isActive ? 'text-destructive' : 'text-emerald-700'"
                      :disabled="saving"
                      @click="setAdminActive(admin, !admin.isActive)"
                    >
                      {{ admin.isActive ? t.disable : t.enable }}
                    </button>
                    <button
                      v-if="canDeleteAdmins && admin.role !== 'SUPER_ADMIN' && admin.id !== adminUser?.id"
                      type="button"
                      class="btn h-8 border px-3 text-xs text-destructive"
                      :disabled="saving"
                      @click="removeAdmin(admin)"
                    >
                      {{ t.deleteAdmin }}
                    </button>
                    <span v-if="admin.role === 'SUPER_ADMIN'" class="text-xs text-muted-foreground">{{ t.protectedAccount }}</span>
                  </td>
                </tr>
                <tr v-if="!admins.length">
                  <td colspan="6" class="py-8 text-center text-sm text-muted-foreground">{{ t.noData }}</td>
                </tr>
              </tbody>
            </DataTable>
          </template>
        </section>

        <section v-else-if="section === 'password'" class="max-w-xl">
          <form class="space-y-4 rounded-xl border bg-card p-5 shadow-sm" @submit.prevent="submitPasswordChange">
            <label class="space-y-1 text-sm font-medium">
              <span>{{ t.currentPassword }}</span>
              <input v-model.trim="passwordForm.oldPassword" class="input h-10" type="password" required />
            </label>
            <label class="space-y-1 text-sm font-medium">
              <span>{{ t.newPassword }}</span>
              <input v-model.trim="passwordForm.newPassword" class="input h-10" type="password" minlength="8" required />
            </label>
            <label class="space-y-1 text-sm font-medium">
              <span>{{ t.confirmPassword }}</span>
              <input v-model.trim="passwordForm.confirmPassword" class="input h-10" type="password" minlength="8" required />
            </label>
            <p v-if="passwordMessage" class="text-sm text-emerald-700">{{ passwordMessage }}</p>
            <button type="submit" class="btn h-10 bg-primary px-4 text-primary-foreground" :disabled="saving">
              {{ saving ? t.saving : t.changePassword }}
            </button>
          </form>
        </section>

        <section v-else-if="section === 'media'" class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_340px]">
          <div class="space-y-4">
            <div class="flex flex-col gap-3 rounded-xl border bg-card p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between">
              <div class="space-y-1 text-sm">
                <p class="font-medium">{{ t.mediaLibrary }}</p>
                <p class="text-xs text-muted-foreground">{{ t.uploadToCategory }}: {{ mediaCategoryLabel(mediaUploadCategory) }}</p>
                <p class="text-xs text-muted-foreground">{{ t.filterCategory }}: {{ mediaFilterLabel }}</p>
              </div>
              <button type="button" class="btn h-9 bg-primary px-4 text-primary-foreground" :disabled="uploadingMedia" @click="triggerMediaUpload('library')">
                <Upload class="h-4 w-4" />
                {{ uploadingMedia ? t.uploading : t.uploadImage }}
              </button>
            </div>
            <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
              <div v-for="item in mediaItems" :key="item.url" class="overflow-hidden rounded-xl border bg-background shadow-sm">
                <img :src="item.thumbnailUrl || item.url" alt="" class="h-44 w-full cursor-zoom-in object-cover" loading="lazy" decoding="async" @click="openMediaPreview(item)" />
                <div class="p-3">
                  <p class="break-words text-sm font-medium">{{ item.name }}</p>
                  <span class="mt-2 inline-flex rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">{{ mediaCategoryLabel(item.category) }}</span>
                  <p class="break-all text-xs text-muted-foreground">{{ item.url }}</p>
                  <div class="mt-3 flex flex-wrap gap-2">
                    <button type="button" class="btn btn-outline h-8 px-3 text-xs" @click="openMediaPreview(item)">{{ t.view }}</button>
                    <button v-if="canDeleteMedia(item)" type="button" class="btn btn-outline h-8 px-3 text-xs text-destructive" :disabled="deletingMedia" @click="deleteMediaItem(item)">{{ t.deleteImage }}</button>
                  </div>
                </div>
              </div>
              <p v-if="!mediaItems.length" class="text-sm text-muted-foreground">{{ t.noData }}</p>
            </div>
          </div>
          <aside class="space-y-4 lg:sticky lg:top-24 lg:self-start">
            <div class="rounded-xl border bg-card p-4 shadow-sm">
              <div class="mb-3 flex items-center justify-between gap-3">
                <h2 class="text-sm font-semibold">{{ t.mediaCategoryTree }}</h2>
                <span class="text-xs text-muted-foreground">{{ mediaCategoryTree.length }}</span>
              </div>
              <div class="space-y-1">
                <button
                  type="button"
                  class="flex h-9 w-full items-center justify-between rounded-lg border px-3 text-left text-sm transition"
                  :class="mediaFilterCategory === '__all__' ? 'border-primary bg-primary/5 text-primary' : 'hover:border-primary'"
                  @click="setMediaFilterCategory('__all__')"
                >
                  <span>{{ t.allMedia }}</span>
                  <span class="text-xs">{{ t.filterHere }}</span>
                </button>
                <button
                  type="button"
                  class="flex h-9 w-full items-center justify-between rounded-lg border px-3 text-left text-sm transition"
                  :class="mediaFilterCategory === '__uncategorized__' ? 'border-primary bg-primary/5 text-primary' : 'hover:border-primary'"
                  @click="setMediaFilterCategory('__uncategorized__')"
                >
                  <span>{{ t.mediaCategoryUncategorized }}</span>
                  <span class="text-xs">{{ t.filterHere }}</span>
                </button>
                <div v-for="node in mediaCategoryTree" :key="`tree-${node.category.id}`" class="flex items-center gap-2">
                  <button
                    type="button"
                    class="min-w-0 flex-1 rounded-lg border py-2 pr-2 text-left text-sm transition"
                    :class="mediaFilterCategory === node.category.slug ? 'border-primary bg-primary/5 text-primary' : 'hover:border-primary'"
                    :style="{ paddingLeft: `${node.depth * 16 + 12}px` }"
                    @click="setMediaFilterCategory(node.category.slug)"
                  >
                    <span class="block truncate">{{ node.label }}</span>
                  </button>
                  <button
                    type="button"
                    class="btn btn-outline h-9 shrink-0 px-2 text-xs"
                    :class="mediaUploadCategory === node.category.slug ? 'border-primary text-primary' : ''"
                    @click="setMediaUploadCategory(node.category.slug)"
                  >
                    {{ mediaUploadCategory === node.category.slug ? t.selectedForUpload : t.useForUpload }}
                  </button>
                </div>
                <p v-if="!mediaCategoryTree.length" class="py-4 text-center text-xs text-muted-foreground">{{ t.noMediaCategories }}</p>
              </div>
            </div>
            <div class="rounded-xl border bg-card p-4 shadow-sm">
              <h2 class="mb-3 text-sm font-semibold">{{ t.mediaCategoryManagement }}</h2>
              <div class="space-y-3">
                <input v-model.trim="mediaCategoryForm.nameZh" class="input h-9" :placeholder="t.mediaCategoryNameZhPlaceholder" @keydown.enter.prevent="createMediaCategory" />
                <input v-model.trim="mediaCategoryForm.nameEn" class="input h-9" :placeholder="t.mediaCategoryNameEnPlaceholder" @keydown.enter.prevent="createMediaCategory" />
                <select v-model="mediaCategoryForm.parentId" class="input h-9">
                  <option value="">{{ t.topLevelCategory }}</option>
                  <option v-for="node in mediaCategoryTree" :key="`parent-${node.category.id}`" :value="node.category.id">{{ node.pathLabel }}</option>
                </select>
                <button type="button" class="btn btn-outline h-9 w-full px-4" :disabled="savingMediaCategory || !canCreateMediaCategory" @click="createMediaCategory">
                  <Plus class="h-4 w-4" />
                  {{ t.addMediaCategory }}
                </button>
              </div>
              <div class="mt-4 space-y-1">
                <div v-for="node in mediaCategoryTree" :key="`manage-${node.category.id}`" class="flex items-center gap-2 rounded-lg border bg-background px-2 py-2">
                  <div class="min-w-0 flex-1" :style="{ paddingLeft: `${node.depth * 14}px` }">
                    <p class="truncate text-sm font-medium">{{ node.label }}</p>
                    <p class="truncate text-xs text-muted-foreground">{{ node.subLabel }}</p>
                  </div>
                  <button type="button" class="btn btn-ghost h-8 w-8 text-destructive" :disabled="savingMediaCategory" :title="t.deleteImage" @click="deleteMediaCategory(node.category)">
                    <Trash2 class="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </aside>
        </section>

        <section v-else-if="section === 'contacts'">
          <DataTable>
            <thead><tr><th>{{ t.name }}</th><th>{{ t.email }}</th><th>{{ t.subject }}</th><th>{{ t.message }}</th><th>{{ t.createdAt }}</th></tr></thead>
            <tbody>
              <tr v-for="row in contacts" :key="row.id">
                <td class="font-medium">{{ row.name }}</td>
                <td>{{ row.email }}</td>
                <td>{{ row.subject }}</td>
                <td class="max-w-md whitespace-normal break-words">{{ row.message }}</td>
                <td>{{ formatDate(row.createdAt) }}</td>
              </tr>
            </tbody>
          </DataTable>
        </section>

        <section v-else-if="section === 'i18n'" class="space-y-4">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 class="text-lg font-semibold">{{ t.i18nManager }}</h2>
              <p class="text-sm text-muted-foreground">{{ t.i18nKeyCount.replace('{count}', i18nKeys.length) }}</p>
            </div>
            <button
              v-if="selectedI18nLocale !== 'en'"
              type="button"
              class="btn h-9 bg-blue-600 px-4 text-white hover:bg-blue-700"
              :disabled="savingTranslations"
              @click="saveTranslations"
            >
              <Check v-if="savedTranslations" class="h-4 w-4" />
              <RefreshCw v-else-if="savingTranslations" class="h-4 w-4 animate-spin" />
              <Save v-else class="h-4 w-4" />
              {{ savedTranslations ? t.saved : savingTranslations ? t.saving : t.save }}
            </button>
          </div>

          <div class="grid grid-cols-2 gap-2 sm:grid-cols-4 lg:grid-cols-8">
            <button
              v-for="item in i18nLocales"
              :key="item.code"
              type="button"
              class="rounded-lg border-2 p-2 text-left transition-colors"
              :class="selectedI18nLocale === item.code ? 'border-blue-600 bg-blue-50' : 'border-transparent hover:border-blue-300'"
              @click="selectI18nLocale(item.code)"
            >
              <div class="flex items-center gap-1.5">
                <span class="text-base">{{ localeMeta[item.code]?.flag || item.code.toUpperCase() }}</span>
                <span class="min-w-0 whitespace-nowrap font-medium" :class="i18nLocaleTextClass(localeMeta[item.code]?.name || item.code)">
                  {{ localeMeta[item.code]?.name || item.code }}
                </span>
              </div>
              <div v-if="item.code !== 'en'" class="mt-1.5">
                <div class="h-1 rounded-full bg-blue-100">
                  <div class="h-1 rounded-full bg-blue-600 transition-all" :style="{ width: `${item.progress}%` }"></div>
                </div>
                <p class="mt-0.5 text-[10px] text-muted-foreground">{{ item.progress }}%</p>
              </div>
              <p v-else class="mt-1 text-[10px] text-muted-foreground">{{ t.sourceText }}</p>
            </button>
          </div>

          <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-3">
            <div class="relative flex-1">
              <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input v-model.trim="translationSearch" class="input h-10 pl-9" :placeholder="t.searchTranslations" />
            </div>
            <select v-model="translationFilter" class="select h-10 w-full sm:w-[160px]">
              <option value="all">{{ t.allNamespaces }}</option>
              <option v-for="namespace in i18nNamespaces" :key="namespace" :value="namespace">{{ namespace }}</option>
            </select>
          </div>

          <div class="max-h-[calc(100vh-380px)] space-y-2 overflow-y-auto rounded-xl border bg-background p-3 shadow-sm">
            <div v-if="loadingTranslations" class="rounded-lg border border-blue-100 bg-blue-50 p-3 text-sm text-blue-700">
              {{ t.loadingTranslations }}
            </div>
            <div v-for="key in filteredI18nKeys" :key="`${selectedI18nLocale}-${key}`" class="rounded-lg border p-3">
              <code class="text-xs text-muted-foreground">{{ key }}</code>
              <p class="mt-1 text-sm">{{ i18nTranslations.en?.[key] || '' }}</p>
              <input
                v-if="selectedI18nLocale !== 'en'"
                :key="`${selectedI18nLocale}-${key}-input`"
                class="input mt-2 h-8 text-sm"
                :dir="selectedI18nLocale === 'ar' ? 'rtl' : 'ltr'"
                :value="i18nTranslations[selectedI18nLocale]?.[key] || ''"
                :placeholder="i18nTranslations.en?.[key] || ''"
                @input="changeTranslation(key, $event.target.value)"
              />
            </div>
            <p v-if="!loadingTranslations && !filteredI18nKeys.length" class="py-12 text-center text-sm text-muted-foreground">{{ t.noTranslationMatches }}</p>
          </div>

          <p class="text-xs text-muted-foreground">
            {{ t.showingKeys.replace('{shown}', filteredI18nKeys.length).replace('{total}', i18nKeys.length) }}
            <span v-if="selectedI18nLocale === 'en'">{{ t.englishReadonly }}</span>
          </p>
        </section>

        <section v-else class="grid gap-4 lg:grid-cols-3">
          <DataCard v-for="card in settingCards" :key="card.title" :title="card.title">
            <p class="text-sm leading-6 text-muted-foreground">{{ card.description }}</p>
          </DataCard>
        </section>
      </template>
    </div>
    <input ref="mediaUploadInput" type="file" accept="image/*" multiple class="hidden" @change="handleMediaUpload" />
    <div v-if="pricingDialogOpen && isProductFormRoute()" class="fixed inset-0 z-50 flex items-center justify-center bg-black/45 px-4 py-6" @click.self="closePricingDialog">
      <div class="max-h-[90vh] w-full max-w-5xl overflow-hidden rounded-xl border bg-background shadow-xl">
        <div class="flex items-center justify-between border-b px-5 py-4">
          <div>
            <h2 class="font-semibold">{{ t.pricing }}</h2>
            <p class="mt-1 text-xs text-muted-foreground">{{ priceModeLabel() }}</p>
          </div>
          <button type="button" class="btn btn-ghost h-9 w-9" @click="closePricingDialog">x</button>
        </div>
        <div class="max-h-[72vh] space-y-5 overflow-y-auto p-5">
          <div class="grid gap-3 md:grid-cols-3">
            <button
              v-for="mode in priceModeOptions"
              :key="mode.value"
              type="button"
              class="rounded-lg border p-3 text-left text-sm transition"
              :class="productForm.priceMode === mode.value ? 'border-primary bg-primary/5 text-primary' : 'hover:border-primary/60'"
              @click="setProductPriceMode(mode.value)"
            >
              <span class="block font-semibold">{{ mode.label }}</span>
              <span class="mt-1 block text-xs leading-5 text-muted-foreground">{{ mode.description }}</span>
            </button>
          </div>
          <div v-if="productForm.priceMode === 'tier'" class="space-y-3">
            <div class="flex items-center justify-between gap-3">
              <h3 class="text-sm font-semibold">{{ t.priceModeTier }}</h3>
              <button type="button" class="btn btn-outline h-8 px-3 text-xs" @click="addTradeTier">
                <Plus class="h-3.5 w-3.5" />
                {{ t.addTier }}
              </button>
            </div>
            <div v-for="(tier, index) in productForm.priceTiers" :key="tier.id" class="grid gap-3 rounded-lg border p-3 md:grid-cols-[1fr_1fr_1fr_1fr_auto_36px] md:items-end">
              <label class="space-y-1 text-xs font-medium">
                <span>{{ t.minQty }}</span>
                <input v-model.number="tier.minQty" class="input h-9" min="1" type="number" />
              </label>
              <label class="space-y-1 text-xs font-medium">
                <span>{{ t.maxQty }}</span>
                <input v-model.number="tier.maxQty" class="input h-9" min="1" type="number" :placeholder="t.leaveBlankUnlimited" />
              </label>
              <label class="space-y-1 text-xs font-medium">
                <span>{{ t.tierPrice }}</span>
                <input v-model.number="tier.price" class="input h-9 disabled:bg-muted disabled:text-muted-foreground" min="0" step="0.01" type="number" :disabled="tier.negotiable" :placeholder="tier.negotiable ? t.negotiable : ''" />
              </label>
              <label class="space-y-1 text-xs font-medium">
                <span>{{ t.compareAtPrice }}</span>
                <input v-model.number="tier.compareAtPrice" class="input h-9 disabled:bg-muted disabled:text-muted-foreground" min="0" step="0.01" type="number" :disabled="tier.negotiable" :placeholder="tier.negotiable ? t.negotiable : ''" />
              </label>
              <label class="flex h-9 items-center gap-2 rounded-lg border px-3 text-xs font-medium">
                <input v-model="tier.negotiable" type="checkbox" class="h-4 w-4 rounded border-border" />
                <span>{{ t.negotiable }}</span>
              </label>
              <button type="button" class="btn btn-ghost h-9 w-9 text-destructive" :disabled="productForm.priceTiers.length <= 1" :aria-label="t.removeTier" @click="removeTradeTier(index)">
                <Trash2 class="h-4 w-4" />
              </button>
            </div>
          </div>
          <p v-else class="rounded-lg border border-dashed bg-muted/30 px-4 py-3 text-sm text-muted-foreground">
            {{ productForm.priceMode === 'variant' ? t.priceModeVariantNotice : t.priceModeNegotiableNotice }}
          </p>
        </div>
        <div class="flex justify-end border-t px-5 py-4">
          <button type="button" class="btn h-9 bg-primary px-4 text-primary-foreground" @click="closePricingDialog">{{ t.done || t.cancel }}</button>
        </div>
      </div>
    </div>
    <div v-if="mediaPicker.open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/45 px-4 py-6" @click.self="closeMediaPicker">
      <div class="max-h-[82vh] w-full max-w-4xl overflow-hidden rounded-xl border bg-background shadow-xl">
        <div class="flex items-center justify-between border-b px-5 py-4">
          <h2 class="font-semibold">{{ t.mediaLibrary }}</h2>
          <button type="button" class="btn btn-ghost h-9 w-9" @click="closeMediaPicker">x</button>
        </div>
        <div class="max-h-[65vh] overflow-y-auto p-5">
          <div class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <label class="space-y-1 text-xs font-medium">
              <span>{{ t.filterCategory }}</span>
              <select v-model="mediaFilterCategory" class="input h-9 min-w-40">
                <option v-for="option in mediaFilterOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
              </select>
            </label>
            <div class="flex flex-col gap-2 sm:items-end">
              <button type="button" class="btn btn-outline h-9 px-3 text-xs" :disabled="uploadingMedia" @click="triggerMediaUpload(mediaPicker.type, mediaPicker.index)">
                <Upload class="h-3.5 w-3.5" />
                {{ uploadingMedia ? t.uploading : t.uploadImage }}
              </button>
              <span v-if="mediaPickerAllowsMultiple" class="text-xs text-muted-foreground">{{ selectedMediaText }}</span>
            </div>
          </div>
          <div class="grid gap-3 sm:grid-cols-3 lg:grid-cols-4">
            <button
              v-for="item in mediaItems"
              :key="`pick-${item.url}`"
              type="button"
              :class="[
                'relative overflow-hidden rounded-xl border bg-background text-left shadow-sm transition',
                isMediaSelected(item) ? 'border-primary ring-2 ring-primary/30' : 'hover:border-primary'
              ]"
              @click="selectMediaImage(item)"
            >
              <span v-if="mediaPickerAllowsMultiple" class="pointer-events-none absolute right-2 top-2 flex h-6 w-6 items-center justify-center rounded-full border bg-background/90 text-primary shadow-sm">
                <Check v-if="isMediaSelected(item)" class="h-4 w-4" />
              </span>
              <img :src="item.thumbnailUrl || item.url" alt="" class="h-32 w-full object-cover" loading="lazy" decoding="async" />
              <span class="block break-words px-3 pb-1 pt-2 text-xs font-medium">{{ item.name || item.url }}</span>
              <span class="block px-3 pb-2 text-[11px] text-muted-foreground">{{ mediaCategoryLabel(item.category) }}</span>
            </button>
          </div>
          <p v-if="!mediaItems.length" class="text-sm text-muted-foreground">{{ t.noData }}</p>
        </div>
        <div v-if="mediaPickerAllowsMultiple" class="flex items-center justify-between gap-3 border-t px-5 py-4">
          <span class="text-sm text-muted-foreground">{{ selectedMediaText }}</span>
          <div class="flex items-center gap-2">
            <button type="button" class="btn btn-outline h-9 px-4" @click="closeMediaPicker">{{ t.cancel }}</button>
            <button type="button" class="btn h-9 bg-primary px-4 text-primary-foreground" :disabled="!mediaPicker.selectedUrls.length" @click="confirmMediaSelection">
              {{ t.useSelectedMedia }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="mediaPreview.open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4 py-6" @click.self="closeMediaPreview">
      <div class="max-h-[90vh] w-full max-w-5xl overflow-hidden rounded-xl border bg-background shadow-xl">
        <div class="flex items-center justify-between border-b px-5 py-4">
          <h2 class="break-words font-semibold">{{ mediaPreview.item?.name || t.viewImage }}</h2>
          <button type="button" class="btn btn-ghost h-9 w-9" @click="closeMediaPreview">x</button>
        </div>
        <div class="max-h-[70vh] overflow-y-auto p-5">
          <img :src="mediaPreview.item?.url" alt="" class="mx-auto max-h-[62vh] w-auto max-w-full rounded-lg object-contain" />
          <div class="mt-4 grid gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(220px,0.7fr)_auto] lg:items-end">
            <label class="space-y-1 text-xs font-medium">
              <span>{{ t.imageName }}</span>
              <input v-model.trim="mediaPreviewName" class="input h-9" :placeholder="t.imageNamePlaceholder" />
            </label>
            <label class="space-y-1 text-xs font-medium">
              <span>{{ t.category }}</span>
              <select v-model="mediaPreviewCategory" class="input h-9">
                <option v-for="option in mediaPreviewCategoryOptions" :key="option.value || '__uncategorized__'" :value="option.value">{{ option.label }}</option>
              </select>
            </label>
            <button type="button" class="btn h-9 bg-primary px-4 text-primary-foreground" :disabled="savingMediaItemCategory" @click="saveMediaItemCategory">
              {{ savingMediaItemCategory ? t.saving : t.saveMediaCategory }}
            </button>
          </div>
          <p class="mt-4 break-all text-xs text-muted-foreground">{{ mediaPreview.item?.url }}</p>
        </div>
        <div class="flex justify-end gap-2 border-t px-5 py-4">
          <button type="button" class="btn btn-outline h-9 px-4" @click="closeMediaPreview">{{ t.cancel }}</button>
          <button v-if="canDeleteMedia(mediaPreview.item)" type="button" class="btn h-9 bg-destructive px-4 text-white" :disabled="deletingMedia" @click="deleteMediaItem(mediaPreview.item)">
            {{ deletingMedia ? t.saving : t.deleteImage }}
          </button>
        </div>
      </div>
    </div>
  </AdminShell>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { Check, ChevronLeft, ClipboardList, Eye, FileText, GripVertical, ImageIcon, MessageSquare, Package, Plus, RefreshCw, Save, Search, Trash2, TrendingUp, Upload, User, Users } from 'lucide-vue-next'

import {
  changePassword,
  createAdminBanner,
  createAdminAdmin,
  createAdminCategory,
  createAdminMediaCategory,
  createAdminProduct,
  currentUser,
  deleteAdminMedia,
  deleteAdminMediaCategory,
  deleteAdminAdmin,
  deleteAdminProduct,
  getAdminAdmins,
  getAdminInquiry,
  getAdminAnalytics,
  getAdminBanners,
  getAdminCategories,
  getAdminContacts,
  getAdminI18n,
  getAdminInquiries,
  getAdminMedia,
  getAdminProducts,
  getAdminSpecTemplate,
  getAdminUsers,
  getAdminVendors,
  reorderAdminProducts,
  updateAdminI18n,
  updateAdminAdmin,
  updateAdminBanner,
  updateAdminCategory,
  updateAdminSpecTemplate,
  updateAdminUser,
  updateInquiry,
  updateAdminProduct,
  updateAdminVendor,
  updateAdminMediaCategoryForItem,
  uploadAdminMedia
} from '@/api'
import AdminShell from '@/components/AdminShell.vue'
import MessagePanel from '@/components/MessagePanel.vue'
import QuoteCard from '@/components/QuoteCard.vue'
import QuoteEditDialog from '@/components/QuoteEditDialog.vue'
import {
  createDefaultPowerStripSpecs,
  mergeSpecsWithTemplate,
  normalizeSpecFormRow,
  specPayloadFromForm,
  specTemplatePayloadFromForm
} from '@/specTemplates'
import { useUiStore } from '@/stores/ui'
import { price, productPriceRange } from '@/utils'
import {
  createBlankVariantOptionType,
  createDefaultVariantOptionTypes,
  formatVariantOptions,
  localizedOptionName,
  normalizeVariantFormRow,
  normalizeVariantOptionTypes,
  optionPairsForType,
  variantOptionTypePayloadFromForm,
  variantPayloadFromForm
} from '@/variantOptions'

const DataCard = defineComponent({
  props: { title: String },
  setup(props, { slots, attrs }) {
    return () => h('div', { ...attrs, class: ['rounded-xl border bg-card text-card-foreground shadow-sm', attrs.class] }, [
      h('div', { class: 'p-6' }, h('h3', { class: 'text-base font-semibold' }, props.title)),
      h('div', { class: 'p-6 pt-0' }, slots.default?.())
    ])
  }
})

const DataTable = defineComponent({
  setup(_, { slots }) {
    return () => h('div', { class: 'overflow-x-auto rounded-xl border bg-background shadow-sm' }, [
      h('table', { class: 'w-full min-w-[760px] text-left text-sm' }, slots.default?.())
    ])
  }
})

const StatusPill = defineComponent({
  props: { label: String, className: String },
  setup(props) {
    return () => h('span', { class: ['inline-flex rounded-full px-2.5 py-1 text-xs font-medium', props.className] }, props.label)
  }
})

const route = useRoute()
const router = useRouter()
const ui = useUiStore()
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const pricingDialogOpen = ref(false)
const analytics = ref(null)
const products = ref([])
const productSearch = ref('')
const reorderingProducts = ref(false)
const categories = ref([])
const banners = ref([])
const contacts = ref([])
const vendors = ref([])
const inquiries = ref([])
const selectedInquiry = ref(null)
const orderTab = ref('overview')
const showQuoteDialog = ref(false)
const editingQuote = ref(null)
const adminUser = ref(currentUser())
const users = ref([])
const admins = ref([])
const adminForm = reactive({
  id: '',
  name: '',
  email: '',
  password: '',
  role: 'ADMIN',
  isActive: true
})
const customerForm = reactive({
  id: '',
  name: '',
  email: '',
  password: '',
  role: 'USER',
  isActive: true
})
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const passwordMessage = ref('')
const media = ref([])
const mediaCategories = ref([])
const mediaUploadInput = ref(null)
const uploadingMedia = ref(false)
const deletingMedia = ref(false)
const savingMediaCategory = ref(false)
const savingMediaItemCategory = ref(false)
const mediaUploadTarget = ref({ type: 'library', index: null })
const mediaUploadCategory = ref('')
const mediaCategoryForm = reactive({ nameZh: '', nameEn: '', parentId: '' })
const mediaFilterCategory = ref('__all__')
const mediaPicker = reactive({ open: false, type: 'display', index: null, selectedUrls: [] })
const mediaPreview = reactive({ open: false, item: null })
const mediaPreviewCategory = ref('')
const mediaPreviewName = ref('')
const specTemplateRows = ref(createDefaultPowerStripSpecs())
const specTemplateProductCount = ref(0)
const savingSpecTemplate = ref(false)
const productImageDragState = reactive({ type: '', from: -1, over: -1 })
const productListDragState = reactive({ draggedId: '', overId: '' })
const colors = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
const i18nLocales = ref([])
const i18nKeys = ref([])
const i18nTranslations = ref({})
const selectedI18nLocale = ref(route.params.locale || 'zh')
const translationSearch = ref('')
const translationFilter = ref('all')
const translationChanges = ref({})
const loadingTranslations = ref(false)
const savingTranslations = ref(false)
const savedTranslations = ref(false)
const localeMeta = {
  en: { name: 'English', flag: 'US' },
  zh: { name: '中文', flag: 'CN' },
  ja: { name: '日本語', flag: 'JP' },
  ko: { name: '한국어', flag: 'KR' },
  fr: { name: 'Français', flag: 'FR' },
  de: { name: 'Deutsch', flag: 'DE' },
  es: { name: 'Español', flag: 'ES' },
  ar: { name: 'العربية', flag: 'AR' }
}
const productLocales = [
  { code: 'en', label: 'English' },
  { code: 'zh', label: '中文' }
]

const bannerLocales = [
  { code: 'en', label: 'English' },
  { code: 'zh', label: '\u4e2d\u6587' },
  { code: 'ja', label: 'Japanese' },
  { code: 'ko', label: 'Korean' },
  { code: 'fr', label: 'French' },
  { code: 'de', label: 'German' },
  { code: 'es', label: 'Spanish' },
  { code: 'ar', label: 'Arabic' }
]

function createBannerTranslations() {
  return Object.fromEntries(
    bannerLocales.map(item => [item.code, { title: '', subtitle: '', buttonText: '' }])
  )
}

function createCategoryTranslations() {
  return Object.fromEntries(
    productLocales.map(item => [item.code, { name: '', description: '', metaTitle: '', metaDescription: '' }])
  )
}

function createProductTranslations() {
  return Object.fromEntries(
    productLocales.map(item => [
      item.code,
      { name: '', description: '', shortDescription: '', metaTitle: '', metaDescription: '' }
    ])
  )
}

const productForm = reactive({
  id: '',
  translations: createProductTranslations(),
  slug: '',
  sku: '',
  categoryId: '',
  priceMode: 'tier',
  price: 0,
  compareAtPrice: '',
  costPrice: '',
  priceTiers: [{ id: 'tier-1', minQty: 10, maxQty: 99, price: '', compareAtPrice: '', negotiable: false }, { id: 'tier-2', minQty: 100, maxQty: 499, price: '', compareAtPrice: '', negotiable: false }, { id: 'tier-3', minQty: 500, maxQty: '', price: '', compareAtPrice: '', negotiable: false }],
  samplePrice: '',
  moq: 1000,
  cartonSpec: '12',
  displayStock: '',
  shipFromEn: 'Shenzhen / Yiwu',
  shipFromZh: '深圳 / 义乌',
  status: 'ACTIVE',
  brandName: '',
  isFeatured: false,
  isNew: true,
  specs: createDefaultPowerStripSpecs(specTemplateRows.value),
  displayImages: [],
  displayImageInput: '',
  posterImages: [],
  posterImageInput: '',
  variantTypes: createDefaultVariantOptionTypes(),
  variants: [normalizeVariantFormRow({ id: '1' }, createDefaultVariantOptionTypes(), 0)],
  rejectionReason: ''
})
const PRODUCT_DRAFT_MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000
const productFormHydrating = ref(false)
const productFormDirty = ref(false)
const productFormRouteKey = ref('')
let productFormDraftTimer = null

function isProductFormRoute(name = route.name) {
  return name === 'admin-product-new' || name === 'admin-product-edit'
}

function productDraftKey() {
  const accountId = adminUser.value?.id || adminUser.value?.email || 'admin'
  const target = route.name === 'admin-product-edit' ? route.params.id : 'new'
  return `misicheng-admin-product-draft:${accountId}:${target}`
}

function currentProductFormRouteKey() {
  return `${String(route.name || '')}:${route.params.id || 'new'}`
}

function readProductDraft() {
  if (!isProductFormRoute()) return null
  try {
    const raw = localStorage.getItem(productDraftKey())
    if (!raw) return null
    const draft = JSON.parse(raw)
    if (!draft?.form || Date.now() - Number(draft.updatedAt || 0) > PRODUCT_DRAFT_MAX_AGE_MS) {
      localStorage.removeItem(productDraftKey())
      return null
    }
    return draft.form
  } catch {
    return null
  }
}

function saveProductDraft() {
  if (!isProductFormRoute() || productFormHydrating.value) return
  window.clearTimeout(productFormDraftTimer)
  productFormDraftTimer = window.setTimeout(() => {
    try {
      localStorage.setItem(productDraftKey(), JSON.stringify({
        updatedAt: Date.now(),
        form: JSON.parse(JSON.stringify(productForm))
      }))
    } catch {
      // Ignore localStorage quota/private-mode failures; the live form state still remains.
    }
  }, 300)
}

function restoreProductDraft() {
  productFormRouteKey.value = currentProductFormRouteKey()
  const draft = readProductDraft()
  if (!draft) {
    productFormDirty.value = false
    return
  }
  productFormHydrating.value = true
  Object.assign(productForm, draft)
  syncProductFormSpecsWithTemplate()
  ensureProductFormPricingState()
  productFormHydrating.value = false
  productFormDirty.value = true
}

function clearProductDraft() {
  window.clearTimeout(productFormDraftTimer)
  try {
    localStorage.removeItem(productDraftKey())
  } catch {
    // Ignore storage failures.
  }
  productFormDirty.value = false
}

const bannerForm = reactive({
  id: '',
  image: '',
  link: '/shop',
  position: 'hero',
  sortOrder: 0,
  isActive: true,
  translations: createBannerTranslations()
})

const categoryForm = reactive({
  id: '',
  slug: '',
  image: '',
  sortOrder: 0,
  isActive: true,
  translations: createCategoryTranslations()
})

const locale = computed(() => route.params.locale || 'en')
const t = computed(() => copy[locale.value] || copy.en)
const priceModeOptions = computed(() => [
  { value: 'tier', label: t.value.priceModeTier, description: t.value.priceModeTierDesc },
  { value: 'variant', label: t.value.priceModeVariant, description: t.value.priceModeVariantDesc },
  { value: 'negotiable', label: t.value.priceModeNegotiable, description: t.value.priceModeNegotiableDesc }
])

function priceModeOption(mode = productForm.priceMode) {
  return priceModeOptions.value.find(option => option.value === mode) || priceModeOptions.value[0]
}

function priceModeLabel(mode = productForm.priceMode) {
  return priceModeOption(mode)?.label || ''
}

function priceModeDescription(mode = productForm.priceMode) {
  return priceModeOption(mode)?.description || ''
}

function openPricingDialog() {
  ensureProductFormPricingState()
  pricingDialogOpen.value = true
}

function closePricingDialog() {
  pricingDialogOpen.value = false
}

function setProductPriceMode(mode) {
  productForm.priceMode = normalizedPriceMode(mode) || 'tier'
  ensureProductFormPricingState()
}

const specFormGroups = computed(() => {
  const groups = []
  const byKey = new Map()
  productForm.specs.forEach((spec, index) => {
    const noteEn = spec.noteEn || ''
    const noteZh = spec.noteZh || ''
    const title = locale.value === 'zh'
      ? (noteZh || noteEn || t.value.specifications)
      : (noteEn || noteZh || t.value.specifications)
    const groupKey = `${noteEn}::${noteZh}`
    if (!byKey.has(groupKey)) {
      const group = { key: `spec-group-${spec.id}`, groupKey, title, noteEn, noteZh, rows: [] }
      byKey.set(groupKey, group)
      groups.push(group)
    }
    byKey.get(groupKey).rows.push({ spec, index })
  })
  return groups
})
const specTemplateGroups = computed(() => {
  const groups = []
  const byKey = new Map()
  specTemplateRows.value.forEach((spec, index) => {
    const noteEn = spec.noteEn || ''
    const noteZh = spec.noteZh || ''
    const title = locale.value === 'zh'
      ? (noteZh || noteEn || t.value.specifications)
      : (noteEn || noteZh || t.value.specifications)
    const groupKey = `${noteEn}::${noteZh}`
    if (!byKey.has(groupKey)) {
      const group = { key: `template-group-${spec.id}`, groupKey, title, noteEn, noteZh, rows: [] }
      byKey.set(groupKey, group)
      groups.push(group)
    }
    byKey.get(groupKey).rows.push({ spec, index })
  })
  return groups
})
const section = computed(() => {
  if (route.name === 'admin-product-new' || route.name === 'admin-product-edit') return 'product-form'
  if (route.name === 'admin-order-detail') return 'orders'
  const path = route.path.replace(/^\/(en|zh|ja|ko|fr|de|es|ar)\/admin\/?/, '')
  if (!path) return 'dashboard'
  return path.split('/')[0] || 'dashboard'
})
const pageTitle = computed(() => pageMeta.value.title)
const pageSubtitle = computed(() => pageMeta.value.subtitle)
const isSuperAdminAccount = computed(() => adminUser.value?.role === 'SUPER_ADMIN' || adminUser.value?.email === 'baomiai@126.com')
const isElevatedAdmin = computed(() => isSuperAdminAccount.value || adminUser.value?.role === 'SENIOR_ADMIN')
const canManageAdmins = computed(() => isElevatedAdmin.value)
const canDeleteAdmins = computed(() => isSuperAdminAccount.value)
const canManageCustomers = computed(() => isElevatedAdmin.value)
const pageMeta = computed(() => {
  const map = {
    dashboard: [t.value.dashboard, t.value.dashboardSubtitle],
    products: [route.query.status === 'PENDING_REVIEW' ? t.value.productReview : t.value.products, t.value.productsSubtitle],
    'product-form': [route.name === 'admin-product-edit' ? t.value.editProduct : t.value.newProduct, t.value.productFormSubtitle],
    'spec-template': [t.value.specTemplateSettings, t.value.specTemplateSubtitle],
    vendors: [t.value.vendorReview, t.value.vendorReviewSubtitle],
    banners: [t.value.banners, t.value.bannersSubtitle],
    categories: [t.value.categories, t.value.categoriesSubtitle],
    orders: [t.value.orders, t.value.ordersSubtitle],
    customers: [t.value.customers, t.value.customersSubtitle],
    admins: [t.value.adminManagement, t.value.adminManagementSubtitle],
    media: [t.value.media, t.value.mediaSubtitle],
    contacts: [t.value.contacts, t.value.contactsSubtitle],
    coupons: [t.value.coupons, t.value.couponsSubtitle],
    shipping: [t.value.shipping, t.value.shippingSubtitle],
    analytics: [t.value.analytics, t.value.analyticsSubtitle],
    i18n: [t.value.translations, t.value.translationsSubtitle],
    password: [t.value.changePassword, t.value.changePasswordSubtitle]
  }
  const item = map[section.value] || map.dashboard
  return { title: item[0], subtitle: item[1] }
})

const monthlyData = computed(() => analytics.value?.monthlyData || [])
const topProducts = computed(() => analytics.value?.topProducts || [])
const filteredProducts = computed(() => {
  const query = productSearch.value.trim().toLowerCase()
  return products.value.filter(product => {
    if (route.query.status && product.status !== route.query.status) return false
    if (!query) return true
    return [
      product.name,
      product.sku,
      product.slug,
      product.category?.name,
      product.brandName,
      product.status,
      ...(product.translations || []).flatMap(row => [row.name, row.description, row.shortDescription])
    ]
      .filter(Boolean)
      .some(value => String(value).toLowerCase().includes(query))
  })
})
const statCards = computed(() => {
  const s = analytics.value?.stats || {}
  return [
    { title: t.value.pageViews, value: s.pageViews ?? 0, change: s.pageViewsChange, icon: Eye, color: 'text-blue-600 bg-blue-50' },
    { title: t.value.totalInquiries, value: s.totalInquiries ?? inquiries.value.length, change: s.inquiriesChange, icon: ClipboardList, color: 'text-emerald-600 bg-emerald-50' },
    { title: t.value.registeredUsers, value: s.totalUsers ?? users.value.length, change: s.newUsersChange, icon: Users, color: 'text-violet-600 bg-violet-50' },
    { title: t.value.activeProducts, value: `${s.activeProducts ?? 0} / ${s.totalProducts ?? products.value.length}`, icon: Package, color: 'text-amber-600 bg-amber-50' }
  ]
})
const statusData = computed(() => {
  const counts = {}
  for (const row of inquiries.value) counts[row.status] = (counts[row.status] || 0) + 1
  return Object.entries(counts).map(([label, value], index) => ({ label, value, color: colors[index % colors.length] }))
})
const normalizedMediaCategories = computed(() => {
  const rows = []
  const addCategory = (category, index = rows.length) => {
    if (!category) return
    if (typeof category === 'string') {
      rows.push({
        id: category,
        slug: category,
        nameEn: category,
        nameZh: category,
        parentId: null,
        sortOrder: 1000 + index,
        isDefault: false
      })
      return
    }
    if (category.isDefault || String(category.id || '').startsWith('default-')) return
    const slug = category.slug || category.category || category.id || category.nameEn || category.nameZh
    if (!slug) return
    rows.push({
      id: category.id || slug,
      slug,
      nameEn: category.nameEn || category.name || slug,
      nameZh: category.nameZh || category.name || category.nameEn || slug,
      parentId: category.parentId || null,
      sortOrder: Number(category.sortOrder ?? index),
      isDefault: Boolean(category.isDefault)
    })
  }
  mediaCategories.value.forEach(addCategory)
  return rows.filter((category, index, list) => list.findIndex(item => item.slug === category.slug) === index)
})
const mediaCategoryBySlug = computed(() => new Map(normalizedMediaCategories.value.map(category => [category.slug, category])))
const mediaCategoryById = computed(() => new Map(normalizedMediaCategories.value.map(category => [category.id, category])))
const mediaCategoryTree = computed(() => {
  const children = new Map()
  for (const category of normalizedMediaCategories.value) {
    const parentId = mediaCategoryById.value.has(category.parentId) ? category.parentId : ''
    if (!children.has(parentId)) children.set(parentId, [])
    children.get(parentId).push(category)
  }
  for (const group of children.values()) {
    group.sort((a, b) => (a.sortOrder - b.sortOrder) || mediaCategoryLabel(a.slug).localeCompare(mediaCategoryLabel(b.slug)))
  }
  const tree = []
  const visit = (category, depth, parentPath = '') => {
    const label = mediaCategoryLabel(category.slug)
    const subLabel = locale.value === 'zh' ? category.nameEn : category.nameZh
    const pathLabel = parentPath ? `${parentPath} / ${label}` : label
    tree.push({ category, depth, label, subLabel, pathLabel })
    for (const child of children.get(category.id) || []) visit(child, depth + 1, pathLabel)
  }
  for (const category of children.get('') || []) visit(category, 0)
  return tree
})
const mediaCategoryOptions = computed(() => {
  const options = new Map()
  const addOption = (value, label) => {
    if (!options.has(value)) options.set(value, { value, label })
  }
  for (const node of mediaCategoryTree.value) {
    addOption(node.category.slug, node.pathLabel)
  }
  for (const item of media.value) {
    if (!item.url) continue
    const value = item.category || '__uncategorized__'
    addOption(value, mediaCategoryLabel(value))
  }
  return Array.from(options.values())
})
const mediaFilterOptions = computed(() => [
  { value: '__all__', label: t.value.allMedia },
  ...mediaCategoryOptions.value
])
const mediaPreviewCategoryOptions = computed(() => [
  { value: '', label: t.value.mediaCategoryUncategorized },
  ...mediaCategoryTree.value.map(node => ({ value: node.category.slug, label: node.pathLabel }))
])
const canCreateMediaCategory = computed(() => Boolean(mediaCategoryForm.nameZh && mediaCategoryForm.nameEn))
const mediaFilterLabel = computed(() => {
  if (mediaFilterCategory.value === '__all__') return t.value.allMedia
  return mediaCategoryLabel(mediaFilterCategory.value)
})
const mediaItems = computed(() => {
  const items = media.value.filter(item => item.url)
  if (mediaFilterCategory.value === '__all__') return items
  if (mediaFilterCategory.value === '__uncategorized__') return items.filter(item => !item.category)
  return items.filter(item => item.category === mediaFilterCategory.value)
})
const mediaPickerAllowsMultiple = computed(() => ['display', 'poster'].includes(mediaPicker.type))
const selectedMediaText = computed(() => {
  const count = mediaPicker.selectedUrls.length
  return locale.value === 'zh' ? `已选择 ${count} 张` : `${count} selected`
})

function mediaCategoryLabel(value) {
  if (!value || value === '__uncategorized__') return t.value.mediaCategoryUncategorized
  const category = mediaCategoryBySlug.value.get(value) || mediaCategoryById.value.get(value)
  if (!category) return value
  return locale.value === 'zh' ? (category.nameZh || category.nameEn || category.slug) : (category.nameEn || category.nameZh || category.slug)
}

function setMediaFilterCategory(value) {
  mediaFilterCategory.value = value
}

function setMediaUploadCategory(value) {
  mediaUploadCategory.value = value || 'general'
}

function mediaCategoryForTarget(type) {
  return mediaUploadCategory.value || ''
}

function applyMediaData(data = {}) {
  media.value = data.media || []
  mediaCategories.value = data.categories || []
  if (mediaUploadCategory.value && !mediaCategoryBySlug.value.has(mediaUploadCategory.value)) mediaUploadCategory.value = ''
  if (!['__all__', '__uncategorized__'].includes(mediaFilterCategory.value) && !mediaCategoryBySlug.value.has(mediaFilterCategory.value)) {
    mediaFilterCategory.value = '__all__'
  }
  if (mediaPreview.open && mediaPreviewCategory.value && !mediaCategoryBySlug.value.has(mediaPreviewCategory.value)) {
    mediaPreviewCategory.value = ''
  }
}

function applyMediaUrl(url, type, index = null) {
  if (!url || type === 'library') return
  if (type === 'banner') {
    bannerForm.image = url
    return
  }
  if (type === 'category') {
    categoryForm.image = url
    return
  }
  if (type === 'poster') {
    productForm.posterImages.push(url)
    productForm.posterImageInput = ''
    return
  }
  productForm.displayImages.push(url)
  productForm.displayImageInput = ''
}

function applyMediaUrls(urls, type, index = null) {
  const cleanUrls = Array.from(new Set((urls || []).filter(Boolean)))
  if (!cleanUrls.length || type === 'library') return
  if (type === 'poster') {
    productForm.posterImages.push(...cleanUrls)
    productForm.posterImageInput = ''
    return
  }
  if (type === 'display') {
    productForm.displayImages.push(...cleanUrls)
    productForm.displayImageInput = ''
    return
  }
  applyMediaUrl(cleanUrls[0], type, index)
}

function openMediaPicker(type, index = null) {
  mediaPicker.open = true
  mediaPicker.type = type
  mediaPicker.index = index
  mediaPicker.selectedUrls = []
}

function closeMediaPicker() {
  mediaPicker.open = false
  mediaPicker.selectedUrls = []
}

function selectMediaImage(item) {
  if (!item?.url) return
  if (mediaPickerAllowsMultiple.value) {
    const selectedIndex = mediaPicker.selectedUrls.indexOf(item.url)
    if (selectedIndex >= 0) mediaPicker.selectedUrls.splice(selectedIndex, 1)
    else mediaPicker.selectedUrls.push(item.url)
    return
  }
  applyMediaUrl(item.url, mediaPicker.type, mediaPicker.index)
  closeMediaPicker()
}

function isMediaSelected(item) {
  return Boolean(item?.url && mediaPicker.selectedUrls.includes(item.url))
}

function confirmMediaSelection() {
  applyMediaUrls(mediaPicker.selectedUrls, mediaPicker.type, mediaPicker.index)
  closeMediaPicker()
}

function canDeleteMedia(item) {
  return Boolean(item?.deletable ?? item?.storageKey ?? item?.url?.startsWith('/api/uploads/media/'))
}

function openMediaPreview(item) {
  mediaPreview.open = true
  mediaPreview.item = item
  mediaPreviewCategory.value = item?.category || ''
  mediaPreviewName.value = item?.name || ''
}

function closeMediaPreview() {
  mediaPreview.open = false
  mediaPreview.item = null
  mediaPreviewCategory.value = ''
  mediaPreviewName.value = ''
}

function replaceMediaUrlInForm(oldUrl, newUrl) {
  if (!oldUrl || !newUrl || oldUrl === newUrl) return
  productForm.displayImages = productForm.displayImages.map(item => item === oldUrl ? newUrl : item)
  if (productForm.displayImageInput === oldUrl) productForm.displayImageInput = newUrl
  productForm.posterImages = productForm.posterImages.map(item => item === oldUrl ? newUrl : item)
  if (productForm.posterImageInput === oldUrl) productForm.posterImageInput = newUrl
  if (bannerForm.image === oldUrl) bannerForm.image = newUrl
  if (categoryForm.image === oldUrl) categoryForm.image = newUrl
}

function removeMediaUrlFromForm(url) {
  productForm.displayImages = productForm.displayImages.filter(item => item !== url)
  if (productForm.displayImageInput === url) productForm.displayImageInput = ''
  productForm.posterImages = productForm.posterImages.filter(item => item !== url)
  if (productForm.posterImageInput === url) productForm.posterImageInput = ''
  if (bannerForm.image === url) bannerForm.image = ''
  if (categoryForm.image === url) categoryForm.image = ''
}

function triggerMediaUpload(type = 'library', index = null) {
  mediaUploadTarget.value = { type, index, category: mediaCategoryForTarget(type) }
  mediaUploadInput.value?.click()
}

async function handleMediaUpload(event) {
  const files = Array.from(event.target.files || [])
  event.target.value = ''
  if (!files.length) return
  uploadingMedia.value = true
  const target = { ...mediaUploadTarget.value }
  const uploadedItems = []
  const uploadErrors = []
  try {
    for (const file of files) {
      try {
        const uploaded = await uploadAdminMedia(file, target.category)
        uploadedItems.push(uploaded)
      } catch (err) {
        uploadErrors.push(err)
      }
    }
    applyMediaData(await getAdminMedia())
    if (target.type !== 'library' && uploadedItems.length) {
      applyMediaUrls(uploadedItems.map(item => item.url), target.type, target.index)
      closeMediaPicker()
    }
    if (uploadErrors.length) {
      const firstError = uploadErrors[0]
      error.value = uploadedItems.length
        ? (locale.value === 'zh'
            ? `已上传 ${uploadedItems.length} 个文件，${uploadErrors.length} 个失败`
            : `${uploadedItems.length} files uploaded, ${uploadErrors.length} failed`)
        : firstError?.response?.data?.error || firstError?.message || t.value.uploadFailed
    } else {
      error.value = ''
    }
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.uploadFailed
  } finally {
    uploadingMedia.value = false
  }
}

async function deleteMediaItem(item) {
  if (!canDeleteMedia(item) || deletingMedia.value) return
  deletingMedia.value = true
  try {
    await deleteAdminMedia(item.storageKey || item.url)
    applyMediaData(await getAdminMedia())
    removeMediaUrlFromForm(item.url)
    closeMediaPreview()
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.deleteFailed
  } finally {
    deletingMedia.value = false
  }
}

async function saveMediaItemCategory() {
  const item = mediaPreview.item
  if (!item?.url || savingMediaItemCategory.value) return
  savingMediaItemCategory.value = true
  try {
    const data = await updateAdminMediaCategoryForItem(item, mediaPreviewCategory.value, mediaPreviewName.value)
    const oldUrls = data.oldUrls?.length ? data.oldUrls : [data.oldUrl || item.url]
    if (data.newUrl) oldUrls.forEach(oldUrl => replaceMediaUrlInForm(oldUrl, data.newUrl))
    applyMediaData(data.media ? data : await getAdminMedia())
    if (data.item) {
      mediaPreview.item = data.item
      mediaPreviewCategory.value = data.item.category || ''
      mediaPreviewName.value = data.item.name || ''
    } else if (data.newUrl) {
      mediaPreview.item = media.value.find(row => row.url === data.newUrl) || { ...item, url: data.newUrl, category: mediaPreviewCategory.value }
      mediaPreviewName.value = mediaPreview.item.name || mediaPreviewName.value
    }
    error.value = ''
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.saveFailed
  } finally {
    savingMediaItemCategory.value = false
  }
}

async function createMediaCategory() {
  if (!canCreateMediaCategory.value || savingMediaCategory.value) return
  savingMediaCategory.value = true
  try {
    const data = await createAdminMediaCategory({
      nameZh: mediaCategoryForm.nameZh,
      nameEn: mediaCategoryForm.nameEn,
      parentId: mediaCategoryForm.parentId || null
    })
    applyMediaData(data)
    const createdCategory = data.category
    if (createdCategory?.slug) {
      mediaUploadCategory.value = createdCategory.slug
      mediaFilterCategory.value = createdCategory.slug
    }
    mediaCategoryForm.nameZh = ''
    mediaCategoryForm.nameEn = ''
    mediaCategoryForm.parentId = ''
    error.value = ''
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.saveFailed
  } finally {
    savingMediaCategory.value = false
  }
}

async function deleteMediaCategory(category) {
  const target = typeof category === 'string' ? (mediaCategoryBySlug.value.get(category) || mediaCategoryById.value.get(category)) : category
  if (!target?.id || savingMediaCategory.value) return
  if (!confirm(t.value.deleteMediaCategoryConfirm.replace('{name}', mediaCategoryLabel(target.slug)))) return
  savingMediaCategory.value = true
  try {
    const localDeletedIds = new Set([target.id])
    let changed = true
    while (changed) {
      changed = false
      for (const row of normalizedMediaCategories.value) {
        if (localDeletedIds.has(row.parentId) && !localDeletedIds.has(row.id)) {
          localDeletedIds.add(row.id)
          changed = true
        }
      }
    }
    const deletedSlugs = normalizedMediaCategories.value.filter(row => localDeletedIds.has(row.id)).map(row => row.slug)
    const data = await deleteAdminMediaCategory({ id: target.id })
    applyMediaData(data)
    if (deletedSlugs.includes(mediaUploadCategory.value)) mediaUploadCategory.value = ''
    if (deletedSlugs.includes(mediaFilterCategory.value)) mediaFilterCategory.value = '__all__'
    error.value = ''
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.deleteFailed
  } finally {
    savingMediaCategory.value = false
  }
}

const i18nNamespaces = computed(() => [...new Set(i18nKeys.value.map(key => key.split('.')[0]))].sort())
const filteredI18nKeys = computed(() => {
  const search = translationSearch.value.toLowerCase()
  return i18nKeys.value.filter(key => {
    const source = String(i18nTranslations.value.en?.[key] || '').toLowerCase()
    const current = String(i18nTranslations.value[selectedI18nLocale.value]?.[key] || '').toLowerCase()
    const matchesSearch = !search || key.toLowerCase().includes(search) || source.includes(search) || current.includes(search)
    const matchesNamespace = translationFilter.value === 'all' || key.startsWith(`${translationFilter.value}.`)
    return matchesSearch && matchesNamespace
  })
})
const settingCards = computed(() => {
  const cards = {
    coupons: [
      { title: t.value.couponRules, description: t.value.couponRulesDesc },
      { title: t.value.couponUsage, description: t.value.couponUsageDesc }
    ],
    shipping: [
      { title: t.value.shippingZones, description: t.value.shippingZonesDesc },
      { title: t.value.shippingMethods, description: t.value.shippingMethodsDesc }
    ],
    analytics: [
      { title: t.value.trafficSources, description: t.value.analyticsDesc },
      { title: t.value.visitorRegions, description: t.value.regionDesc }
    ],
    i18n: [
      { title: t.value.localeCoverage, description: t.value.localeCoverageDesc },
      { title: t.value.currencyCoverage, description: t.value.currencyCoverageDesc }
    ]
  }
  return cards[section.value] || []
})

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

function chartHeight(value) {
  const max = Math.max(...monthlyData.value.map(row => row.inquiries), 1)
  return `${Math.max(4, (Number(value || 0) / max) * 190)}px`
}

function donutBackground(rows) {
  const total = rows.reduce((sum, row) => sum + row.value, 0)
  let current = 0
  return `conic-gradient(${rows.map(row => {
    const start = (current / total) * 100
    current += row.value
    const end = (current / total) * 100
    return `${row.color} ${start}% ${end}%`
  }).join(', ')})`
}

function formatDate(value) {
  if (!value) return '-'
  return new Intl.DateTimeFormat(locale.value === 'zh' ? 'zh-CN' : 'en-US', {
    year: 'numeric',
    month: 'short',
    day: '2-digit'
  }).format(new Date(value))
}

function money(value) {
  return price(value, ui.currency)
}

function formatOptions(options) {
  return formatVariantOptions(options, [], locale.value === 'zh' ? 'zh' : 'en')
}

function productPrice(product) {
  return productPriceRange(product, ui.currency, { negotiableText: t.value.negotiable })
}

function statusClass(status) {
  return {
    SUBMITTED: 'bg-blue-100 text-blue-800',
    REVIEWING: 'bg-yellow-100 text-yellow-800',
    QUOTED: 'bg-purple-100 text-purple-800',
    ACCEPTED: 'bg-green-100 text-green-800',
    REJECTED: 'bg-red-100 text-red-800',
    EXPIRED: 'bg-gray-100 text-gray-800',
    CANCELLED: 'bg-red-100 text-red-800'
  }[status] || 'bg-gray-100 text-gray-800'
}

function inquiryStatusLabel(status) {
  return (locale.value === 'zh' ? {
    SUBMITTED: '\u5df2\u63d0\u4ea4',
    REVIEWING: '\u5ba1\u6838\u4e2d',
    QUOTED: '\u5df2\u62a5\u4ef7',
    ACCEPTED: '\u5df2\u63a5\u53d7',
    REJECTED: '\u5df2\u62d2\u7edd',
    EXPIRED: '\u5df2\u8fc7\u671f',
    CANCELLED: '\u5df2\u53d6\u6d88'
  } : {
    SUBMITTED: 'Submitted',
    REVIEWING: 'Under Review',
    QUOTED: 'Quoted',
    ACCEPTED: 'Accepted',
    REJECTED: 'Rejected',
    EXPIRED: 'Expired',
    CANCELLED: 'Cancelled'
  })[status] || status
}

function productStatusLabel(status) {
  return (locale.value === 'zh' ? {
    ACTIVE: '\u5df2\u4e0a\u67b6',
    DRAFT: '\u8349\u7a3f',
    PENDING_REVIEW: '\u5f85\u5ba1\u6838',
    REJECTED: '\u5df2\u9a73\u56de',
    ARCHIVED: '\u5df2\u5f52\u6863'
  } : {
    ACTIVE: 'Active',
    DRAFT: 'Draft',
    PENDING_REVIEW: 'Pending Review',
    REJECTED: 'Rejected',
    ARCHIVED: 'Archived'
  })[status] || status
}
function productStatusClass(status) {
  return {
    ACTIVE: 'bg-emerald-50 text-emerald-700',
    DRAFT: 'bg-gray-100 text-gray-700',
    PENDING_REVIEW: 'bg-amber-50 text-amber-700',
    REJECTED: 'bg-red-50 text-red-700',
    ARCHIVED: 'bg-gray-100 text-gray-700'
  }[status] || 'bg-gray-100 text-gray-700'
}

function i18nLocaleTextClass(name) {
  const length = Array.from(name || '').length
  if (length >= 10) return 'text-[9px]'
  if (length >= 8) return 'text-[10px]'
  return 'text-xs'
}

function fitTextClass(value) {
  const length = Array.from(value || '').length
  if (length >= 40) return 'text-[11px]'
  if (length >= 28) return 'text-xs'
  return 'text-sm'
}

function vendorStatusLabel(status) {
  return (locale.value === 'zh' ? {
    PENDING: '\u5f85\u5ba1\u6838',
    APPROVED: '\u5df2\u901a\u8fc7',
    REJECTED: '\u5df2\u9a73\u56de',
    DISABLED: '\u5df2\u505c\u7528'
  } : {
    PENDING: 'Pending',
    APPROVED: 'Approved',
    REJECTED: 'Rejected',
    DISABLED: 'Disabled'
  })[status] || status
}
function vendorStatusClass(status) {
  return {
    PENDING: 'bg-amber-50 text-amber-700',
    APPROVED: 'bg-emerald-50 text-emerald-700',
    REJECTED: 'bg-red-50 text-red-700',
    DISABLED: 'bg-gray-100 text-gray-700'
  }[status] || 'bg-gray-100 text-gray-700'
}

function translationFor(product, targetLocale) {
  return (product.translations || []).find(item => item.locale === targetLocale) || null
}

function resetBannerForm() {
  Object.assign(bannerForm, {
    id: '',
    image: '',
    link: '/shop',
    position: 'hero',
    sortOrder: banners.value.length,
    isActive: true,
    translations: createBannerTranslations()
  })
}

function editBanner(banner) {
  const translations = createBannerTranslations()
  for (const item of bannerLocales) {
    const row = translationFor(banner, item.code)
    translations[item.code] = {
      title: row?.title || '',
      subtitle: row?.subtitle || '',
      buttonText: row?.buttonText || ''
    }
  }
  Object.assign(bannerForm, {
    id: banner.id,
    image: banner.image || '',
    link: banner.link || '/shop',
    position: banner.position || 'hero',
    sortOrder: banner.sortOrder || 0,
    isActive: !!banner.isActive,
    translations
  })
}

function bannerPayload() {
  return {
    image: bannerForm.image,
    link: bannerForm.link,
    position: bannerForm.position || 'hero',
    sortOrder: Number(bannerForm.sortOrder || 0),
    isActive: bannerForm.isActive,
    translations: bannerLocales.map(item => ({
      locale: item.code,
      title: bannerForm.translations[item.code]?.title || '',
      subtitle: bannerForm.translations[item.code]?.subtitle || '',
      buttonText: bannerForm.translations[item.code]?.buttonText || ''
    }))
  }
}

async function submitBanner() {
  saving.value = true
  try {
    if (bannerForm.id) await updateAdminBanner(bannerForm.id, bannerPayload())
    else await createAdminBanner(bannerPayload())
    await load()
    resetBannerForm()
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.saveFailed
  } finally {
    saving.value = false
  }
}

function resetCategoryForm() {
  Object.assign(categoryForm, {
    id: '',
    slug: '',
    image: '',
    sortOrder: categories.value.length,
    isActive: true,
    translations: createCategoryTranslations()
  })
}

function editCategory(category) {
  const translations = createCategoryTranslations()
  for (const item of productLocales) {
    const row = translationFor(category, item.code)
    translations[item.code] = {
      name: row?.name || (item.code === 'en' ? category.name || '' : ''),
      description: row?.description || '',
      metaTitle: row?.metaTitle || '',
      metaDescription: row?.metaDescription || ''
    }
  }
  Object.assign(categoryForm, {
    id: category.id,
    slug: category.slug || '',
    image: category.image || '',
    sortOrder: category.sortOrder || 0,
    isActive: !!category.isActive,
    translations
  })
}

function categoryPayload() {
  return {
    slug: categoryForm.slug,
    image: categoryForm.image,
    sortOrder: Number(categoryForm.sortOrder || 0),
    isActive: categoryForm.isActive,
    translations: productLocales.map(item => ({
      locale: item.code,
      name: categoryForm.translations[item.code]?.name || '',
      description: categoryForm.translations[item.code]?.description || '',
      metaTitle: categoryForm.translations[item.code]?.metaTitle || '',
      metaDescription: categoryForm.translations[item.code]?.metaDescription || ''
    }))
  }
}

async function submitCategory() {
  saving.value = true
  try {
    if (categoryForm.id) await updateAdminCategory(categoryForm.id, categoryPayload())
    else await createAdminCategory(categoryPayload())
    await load()
    resetCategoryForm()
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.saveFailed
  } finally {
    saving.value = false
  }
}

function splitProductImages(product) {
  const display = []
  const poster = []
  for (const image of product.images || []) {
    if ((image.sortOrder || 0) >= 100) poster.push(image.url)
    else display.push(image.url)
  }
  return {
    display: display.length ? display : [product.images?.[0]?.url || ''],
    poster
  }
}

function normalizedPriceMode(value) {
  const mode = String(value || '').toLowerCase()
  return ['tier', 'variant', 'negotiable'].includes(mode) ? mode : ''
}

function createDefaultPriceTiers() {
  return [
    { id: 'tier-1', minQty: 10, maxQty: 99, price: '', compareAtPrice: '', negotiable: false },
    { id: 'tier-2', minQty: 100, maxQty: 499, price: '', compareAtPrice: '', negotiable: false },
    { id: 'tier-3', minQty: 500, maxQty: '', price: '', compareAtPrice: '', negotiable: false }
  ]
}

function ensureProductFormPricingState() {
  productForm.priceMode = normalizedPriceMode(productForm.priceMode) || 'tier'
  if (!Array.isArray(productForm.priceTiers) || !productForm.priceTiers.length) {
    productForm.priceTiers = createDefaultPriceTiers()
  }
  if (!Array.isArray(productForm.variantTypes) || !productForm.variantTypes.length) {
    productForm.variantTypes = createDefaultVariantOptionTypes()
  }
  if (!Array.isArray(productForm.variants) || !productForm.variants.length) {
    productForm.variants = [normalizeVariantFormRow({ id: '1' }, productForm.variantTypes, 0)]
  }
}

function syncProductFormSpecsWithTemplate() {
  productForm.specs = mergeSpecsWithTemplate(productForm.specs || [], specTemplateRows.value)
}

function positivePrice(value) {
  const number = Number(value)
  return Number.isFinite(number) && number > 0 ? number : null
}

function inferProductPriceMode(product, tradeInfo = product?.tradeInfo || {}) {
  const explicit = normalizedPriceMode(tradeInfo.priceMode || product?.priceMode)
  if (explicit) return explicit
  const tiers = Array.isArray(tradeInfo.priceTiers) ? tradeInfo.priceTiers : []
  if (tiers.some(tier => positivePrice(tier.price) !== null && !(tier.negotiable || tier.priceNegotiable))) return 'tier'
  if ((product?.variants || []).some(variant => positivePrice(variant.price) !== null)) return 'variant'
  if (tiers.some(tier => tier.negotiable || tier.priceNegotiable)) return 'negotiable'
  return positivePrice(product?.price) === null ? 'negotiable' : 'tier'
}

function resetProductForm() {
  Object.assign(productForm, {
    id: '',
    translations: createProductTranslations(),
    slug: '',
    sku: '',
    categoryId: '',
    priceMode: 'tier',
    price: 0,
    compareAtPrice: '',
    costPrice: '',
    priceTiers: [{ id: 'tier-1', minQty: 10, maxQty: 99, price: '', compareAtPrice: '', negotiable: false }, { id: 'tier-2', minQty: 100, maxQty: 499, price: '', compareAtPrice: '', negotiable: false }, { id: 'tier-3', minQty: 500, maxQty: '', price: '', compareAtPrice: '', negotiable: false }],
    samplePrice: '',
    moq: 1000,
    cartonSpec: '12',
    displayStock: '',
    shipFromEn: 'Shenzhen / Yiwu',
    shipFromZh: '深圳 / 义乌',
    status: 'ACTIVE',
    brandName: 'Misicheng',
    isFeatured: false,
    isNew: true,
    specs: createDefaultPowerStripSpecs(specTemplateRows.value),
    displayImages: [],
    displayImageInput: '',
    posterImages: [],
    posterImageInput: '',
    variantTypes: createDefaultVariantOptionTypes(),
    variants: [normalizeVariantFormRow({ id: '1' }, createDefaultVariantOptionTypes(), 0)],
    rejectionReason: ''
  })
}

function syncProductForm() {
  if (
    isProductFormRoute()
    && productFormDirty.value
    && productFormRouteKey.value === currentProductFormRouteKey()
  ) {
    syncProductFormSpecsWithTemplate()
    return
  }
  if (route.name === 'admin-product-new') {
    productFormHydrating.value = true
    resetProductForm()
    productForm.status = 'ACTIVE'
    productFormHydrating.value = false
    restoreProductDraft()
    return
  }
  if (route.name !== 'admin-product-edit') return
  const product = products.value.find(item => item.id === route.params.id)
  if (!product) return
  const translations = createProductTranslations()
  for (const item of productLocales) {
    const row = translationFor(product, item.code)
    translations[item.code] = {
      name: row?.name || (item.code === 'en' ? product.name || '' : ''),
      description: row?.description || (item.code === 'en' ? product.description || '' : ''),
      shortDescription: row?.shortDescription || '',
      metaTitle: row?.metaTitle || '',
      metaDescription: row?.metaDescription || ''
    }
  }
  const images = splitProductImages(product)
  const tradeInfo = product.tradeInfo || {}
  const variantTypes = normalizeVariantOptionTypes(tradeInfo.variantOptionTypes || [], product.variants || [])
  productFormHydrating.value = true
  Object.assign(productForm, {
    id: product.id,
    translations,
    slug: product.slug,
    sku: product.sku,
    categoryId: product.category?.id || product.categoryId || '',
    priceMode: inferProductPriceMode(product, tradeInfo),
    price: product.price || 0,
    compareAtPrice: product.compareAtPrice || '',
    costPrice: product.costPrice || '',
    priceTiers: (tradeInfo.priceTiers || []).length
      ? tradeInfo.priceTiers.map((tier, index) => ({
          id: `tier-${index}`,
          minQty: tier.minQty || '',
          maxQty: tier.maxQty ?? '',
          price: tier.price || '',
          compareAtPrice: tier.compareAtPrice || tier.comparePrice || tier.originalPrice || '',
          negotiable: !!(tier.negotiable || tier.priceNegotiable)
        }))
      : [{ id: 'tier-1', minQty: 10, maxQty: 99, price: product.price || '', compareAtPrice: product.compareAtPrice || '', negotiable: false }, { id: 'tier-2', minQty: 100, maxQty: 499, price: product.price ? Number(product.price) * 0.92 : '', compareAtPrice: product.compareAtPrice ? Number(product.compareAtPrice) * 0.92 : '', negotiable: false }, { id: 'tier-3', minQty: 500, maxQty: '', price: product.price ? Number(product.price) * 0.85 : '', compareAtPrice: product.compareAtPrice ? Number(product.compareAtPrice) * 0.85 : '', negotiable: false }],
    samplePrice: tradeInfo.samplePrice ?? product.price ?? '',
    moq: tradeInfo.moq ?? 1000,
    cartonSpec: tradeInfo.cartonSpec ?? '12',
    displayStock: tradeInfo.stock ?? '',
    shipFromEn: tradeInfo.shipFrom?.en || tradeInfo.shipFrom || 'Shenzhen / Yiwu',
    shipFromZh: tradeInfo.shipFrom?.zh || '深圳 / 义乌',
    status: product.status || 'DRAFT',
    brandName: product.brandName || 'Misicheng',
    isFeatured: !!product.isFeatured,
    isNew: !!product.isNew,
    specs: mergeSpecsWithTemplate(product.specifications || [], specTemplateRows.value),
    displayImages: images.display,
    displayImageInput: '',
    posterImages: images.poster,
    posterImageInput: '',
    variantTypes,
    variants: (product.variants || []).length
      ? product.variants.map((variant, index) => normalizeVariantFormRow(variant, variantTypes, index))
      : [normalizeVariantFormRow({ id: '1' }, variantTypes, 0)],
    rejectionReason: product.rejectionReason || ''
  })
  ensureProductFormPricingState()
  productFormHydrating.value = false
  restoreProductDraft()
}

function createSpecRowForGroup(group = null) {
  return normalizeSpecFormRow({
    id: `spec-${Date.now()}-${productForm.specs.length}`,
    noteEn: group?.noteEn || '',
    noteZh: group?.noteZh || group?.noteEn || ''
  }, productForm.specs.length)
}

function addSpec(group = null) {
  productForm.specs.push(createSpecRowForGroup(group))
}

function addSpecGroup() {
  const index = specFormGroups.value.length + 1
  addSpec({
    noteEn: `${t.value.specGroupDefault} ${index}`,
    noteZh: `${t.value.specGroupDefaultZh || t.value.specGroupDefault} ${index}`
  })
}

function removeSpec(index) {
  productForm.specs.splice(index, 1)
}

function removeSpecGroup(group) {
  const removeIndexes = new Set(group.rows.map(row => row.index))
  productForm.specs = productForm.specs.filter((_, index) => !removeIndexes.has(index))
}

function updateSpecGroupName(group, target, value) {
  for (const row of group.rows) {
    if (target === 'zh') row.spec.noteZh = value
    else row.spec.noteEn = value
  }
}

function createTemplateSpecRowForGroup(group = null) {
  return normalizeSpecFormRow({
    id: `template-spec-${Date.now()}-${specTemplateRows.value.length}`,
    noteEn: group?.noteEn || '',
    noteZh: group?.noteZh || group?.noteEn || '',
    optionsEn: ['To be provided', 'To be confirmed', 'Included', 'Optional', 'Customizable', 'Not included'],
    optionsZh: ['待补充', '待确认', '支持', '可选', '可定制', '不支持']
  }, specTemplateRows.value.length)
}

function addTemplateSpec(group = null) {
  specTemplateRows.value.push(createTemplateSpecRowForGroup(group))
}

function addTemplateSpecGroup() {
  const index = specTemplateGroups.value.length + 1
  addTemplateSpec({
    noteEn: `${t.value.specGroupDefault} ${index}`,
    noteZh: `${t.value.specGroupDefaultZh || t.value.specGroupDefault} ${index}`
  })
}

function removeTemplateSpec(index) {
  specTemplateRows.value.splice(index, 1)
}

function removeTemplateSpecGroup(group) {
  const removeIndexes = new Set(group.rows.map(row => row.index))
  specTemplateRows.value = specTemplateRows.value.filter((_, index) => !removeIndexes.has(index))
}

function updateTemplateGroupName(group, target, value) {
  for (const row of group.rows) {
    if (target === 'zh') row.spec.noteZh = value
    else row.spec.noteEn = value
  }
}

function optionText(spec, target) {
  return ((target === 'zh' ? spec.optionsZh : spec.optionsEn) || []).join('\n')
}

function updateOptionText(spec, target, value) {
  const rows = String(value || '').split(/\r?\n/).map(item => item.trim()).filter(Boolean)
  if (target === 'zh') spec.optionsZh = rows
  else spec.optionsEn = rows
}

async function saveSpecTemplate() {
  savingSpecTemplate.value = true
  try {
    const data = await updateAdminSpecTemplate({
      template: specTemplatePayloadFromForm(specTemplateRows.value),
      syncProducts: true
    })
    specTemplateRows.value = createDefaultPowerStripSpecs(data.template || [])
    specTemplateProductCount.value = data.syncedCount ?? specTemplateProductCount.value
    const refreshedProducts = await getAdminProducts()
    products.value = refreshedProducts.products || products.value
    syncProductFormSpecsWithTemplate()
    syncProductForm()
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.saveFailed
  } finally {
    savingSpecTemplate.value = false
  }
}

function moveArrayItem(list, from, to) {
  if (!Array.isArray(list) || from === to || from < 0 || to < 0 || from >= list.length || to >= list.length) return false
  const [item] = list.splice(from, 1)
  list.splice(to, 0, item)
  return true
}

function productImageList(type) {
  return type === 'poster' ? productForm.posterImages : productForm.displayImages
}

function clearProductImageDrag() {
  productImageDragState.type = ''
  productImageDragState.from = -1
  productImageDragState.over = -1
}

function startProductImageDrag(type, index, event) {
  productImageDragState.type = type
  productImageDragState.from = index
  productImageDragState.over = index
  if (event?.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', `${type}:${index}`)
  }
}

function setProductImageDropTarget(type, index) {
  if (productImageDragState.type !== type) return
  productImageDragState.over = index
}

function dropProductImage(type, index) {
  if (productImageDragState.type !== type) {
    clearProductImageDrag()
    return
  }
  moveArrayItem(productImageList(type), productImageDragState.from, index)
  clearProductImageDrag()
}

function dropProductImageToEnd(type) {
  if (productImageDragState.type !== type) {
    clearProductImageDrag()
    return
  }
  const list = productImageList(type)
  moveArrayItem(list, productImageDragState.from, list.length - 1)
  clearProductImageDrag()
}

function clearProductListDrag() {
  productListDragState.draggedId = ''
  productListDragState.overId = ''
}

function startProductListDrag(productId, event) {
  if (reorderingProducts.value) {
    event?.preventDefault()
    return
  }
  productListDragState.draggedId = productId
  productListDragState.overId = productId
  if (event?.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', productId)
  }
}

function setProductListDropTarget(productId) {
  if (!productListDragState.draggedId) return
  productListDragState.overId = productId || ''
}

function moveProductId(ids, draggedId, targetId = null) {
  const next = ids.slice()
  const from = next.indexOf(draggedId)
  if (from < 0) return next
  const [item] = next.splice(from, 1)
  if (!targetId) {
    next.push(item)
    return next
  }
  const to = next.indexOf(targetId)
  if (to < 0) {
    next.push(item)
    return next
  }
  next.splice(to, 0, item)
  return next
}

function reorderProductRowsByVisibleIds(rows, orderedIds) {
  const selectedSet = new Set(orderedIds)
  const rowById = new Map(rows.map(row => [row.id, row]))
  const selectedRows = orderedIds.map(id => rowById.get(id)).filter(Boolean)
  let cursor = 0
  return rows.map(row => (selectedSet.has(row.id) ? (selectedRows[cursor++] || row) : row))
}

function sameProductOrder(a, b) {
  return a.length === b.length && a.every((id, index) => id === b[index])
}

async function saveProductListOrder(orderedIds) {
  const previousProducts = products.value.slice()
  products.value = reorderProductRowsByVisibleIds(products.value, orderedIds)
  reorderingProducts.value = true
  try {
    await reorderAdminProducts(orderedIds)
  } catch (err) {
    products.value = previousProducts
    error.value = err?.response?.data?.error || err?.message || t.value.saveFailed
  } finally {
    reorderingProducts.value = false
    clearProductListDrag()
  }
}

async function dropProductOn(targetId) {
  const draggedId = productListDragState.draggedId
  if (!draggedId || draggedId === targetId) {
    clearProductListDrag()
    return
  }
  const visibleIds = filteredProducts.value.map(product => product.id)
  const orderedIds = moveProductId(visibleIds, draggedId, targetId)
  if (sameProductOrder(visibleIds, orderedIds)) {
    clearProductListDrag()
    return
  }
  await saveProductListOrder(orderedIds)
}

async function dropProductToEnd() {
  const draggedId = productListDragState.draggedId
  if (!draggedId) return
  const visibleIds = filteredProducts.value.map(product => product.id)
  const orderedIds = moveProductId(visibleIds, draggedId)
  if (sameProductOrder(visibleIds, orderedIds)) {
    clearProductListDrag()
    return
  }
  await saveProductListOrder(orderedIds)
}

function removeDisplayImage(index) {
  productForm.displayImages.splice(index, 1)
}

function addDisplayImage() {
  const value = productForm.displayImageInput.trim()
  if (!value) return
  productForm.displayImages.push(value)
  productForm.displayImageInput = ''
}

function addPosterImage() {
  const value = productForm.posterImageInput.trim()
  if (!value) return
  productForm.posterImages.push(value)
  productForm.posterImageInput = ''
}

function removePosterImage(index) {
  productForm.posterImages.splice(index, 1)
}

function activeVariantTypes() {
  return productForm.variantTypes.map(variantOptionTypePayloadFromForm).filter(Boolean)
}

function addVariantType() {
  productForm.variantTypes.push(createBlankVariantOptionType(productForm.variantTypes.length))
}

function removeVariantType(index) {
  if (productForm.variantTypes.length <= 1) return
  const [removed] = productForm.variantTypes.splice(index, 1)
  if (!removed?.key) return
  for (const variant of productForm.variants) {
    if (variant.optionValues) delete variant.optionValues[removed.key]
  }
}

function variantTypeLabel(type) {
  return localizedOptionName(type, locale.value === 'zh' ? 'zh' : 'en')
}

function optionValuesForType(type) {
  return optionPairsForType(type)
}

function variantValueLabel(value) {
  return locale.value === 'zh' ? (value.zh || value.en) : (value.en || value.zh)
}

function setVariantOption(variant, type, value) {
  if (!variant.optionValues) variant.optionValues = {}
  variant.optionValues[type.key] = value
}

function addVariant() {
  productForm.variants.push(normalizeVariantFormRow({ id: `variant-${Date.now()}` }, productForm.variantTypes, productForm.variants.length))
}

function removeVariant(index) {
  if (productForm.variants.length <= 1) return
  productForm.variants.splice(index, 1)
}

function addTradeTier() {
  productForm.priceTiers.push({ id: `tier-${Date.now()}`, minQty: '', maxQty: '', price: '', compareAtPrice: '', negotiable: false })
}

function removeTradeTier(index) {
  if (productForm.priceTiers.length <= 1) return
  productForm.priceTiers.splice(index, 1)
}

function activeTradeTiers() {
  if (productForm.priceMode !== 'tier') return []
  return productForm.priceTiers
    .filter(item => item.minQty && (item.negotiable || item.price))
    .map(item => ({
      minQty: Number(item.minQty),
      maxQty: item.maxQty === '' || item.maxQty === null || item.maxQty === undefined ? null : Number(item.maxQty),
      price: item.negotiable ? null : Number(item.price),
      compareAtPrice: item.negotiable || item.compareAtPrice === '' || item.compareAtPrice === null || item.compareAtPrice === undefined ? null : Number(item.compareAtPrice),
      negotiable: !!item.negotiable
    }))
}

function basePriceFromTiers(tiers) {
  const prices = tiers.map(item => Number(item.price || 0)).filter(value => value > 0)
  return prices.length ? Math.min(...prices) : Number(productForm.price || 0)
}

function basePriceFromVariants() {
  const prices = productForm.variants
    .map(item => Number(item.price || 0))
    .filter(value => value > 0)
  return prices.length ? Math.min(...prices) : 0
}

function baseComparePriceFromTiers(tiers) {
  const prices = tiers.map(item => Number(item.compareAtPrice || 0)).filter(value => value > 0)
  return prices.length ? Math.min(...prices) : null
}

function productPayload() {
  ensureProductFormPricingState()
  const variantTypes = activeVariantTypes()
  const tradeTiers = activeTradeTiers()
  const basePrice = productForm.priceMode === 'negotiable'
    ? 0
    : productForm.priceMode === 'variant'
      ? basePriceFromVariants()
      : basePriceFromTiers(tradeTiers)
  const baseCompareAtPrice = productForm.priceMode === 'tier' ? baseComparePriceFromTiers(tradeTiers) : null
  return {
    slug: productForm.slug,
    sku: productForm.sku,
    status: productForm.status,
    price: basePrice,
    compareAtPrice: baseCompareAtPrice,
    categoryId: productForm.categoryId || null,
    brandName: productForm.brandName || null,
    isFeatured: productForm.isFeatured,
    isNew: productForm.isNew,
    rejectionReason: productForm.rejectionReason,
    tradeInfo: {
      priceMode: productForm.priceMode,
      priceNegotiable: productForm.priceMode === 'negotiable',
      priceTiers: tradeTiers,
      shipFrom: {
        en: productForm.shipFromEn || '',
        zh: productForm.shipFromZh || productForm.shipFromEn || ''
      },
      variantOptionTypes: variantTypes
    },
    specifications: productForm.specs.map(specPayloadFromForm).filter(Boolean),
    translations: productLocales
      .map(item => ({
        locale: item.code,
        name: productForm.translations[item.code].name,
        description: productForm.translations[item.code].description,
        shortDescription: productForm.translations[item.code].shortDescription,
        metaTitle: productForm.translations[item.code].metaTitle,
        metaDescription: productForm.translations[item.code].metaDescription
      }))
      .filter(item => item.locale === 'en' || item.name),
    images: [
      ...productForm.displayImages.filter(Boolean).map((url, index) => ({ url, sortOrder: index })),
      ...productForm.posterImages.filter(Boolean).map((url, index) => ({ url, sortOrder: 100 + index }))
    ],
    variants: productForm.variants.filter(item => item.sku).map((item, index) => ({
      ...(() => {
        const payload = variantPayloadFromForm(item, variantTypes, basePrice)
        return {
          ...payload,
          price: productForm.priceMode === 'variant' ? payload.price : basePrice
        }
      })(),
      sortOrder: index,
    }))
  }
}

async function submitProduct() {
  saving.value = true
  try {
    const payload = productPayload()
    if (productForm.id) {
      await updateAdminProduct(productForm.id, payload)
    } else {
      await createAdminProduct(payload)
    }
    clearProductDraft()
    await load()
    router.push(localized('/admin/products'))
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.saveFailed
  } finally {
    saving.value = false
  }
}
async function setProductStatus(product, status) {
  await updateAdminProduct(product.id, { status })
  await load()
}

async function removeProduct(product) {
  const confirmed = window.confirm(t.value.deleteProductConfirm.replace('{name}', product.name || product.sku || product.id))
  if (!confirmed) return
  saving.value = true
  try {
    await deleteAdminProduct(product.id)
    products.value = products.value.filter(item => item.id !== product.id)
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.deleteFailed
  } finally {
    saving.value = false
  }
}

function adminRoleLabel(role) {
  if (role === 'SUPER_ADMIN') return t.value.superAdmin
  if (role === 'SENIOR_ADMIN') return t.value.seniorAdmin
  return t.value.normalAdmin
}

function userRoleLabel(role) {
  return role === 'VENDOR' ? t.value.vendorAccount : t.value.personalUser
}

function canEditAdminAccount(admin) {
  if (!admin || admin.role === 'SUPER_ADMIN') return false
  if (isSuperAdminAccount.value) return true
  return admin.role === 'ADMIN' || admin.id === adminUser.value?.id
}

function resetAdminForm() {
  Object.assign(adminForm, { id: '', name: '', email: '', password: '', role: 'ADMIN', isActive: true })
}

function editAdminAccount(admin) {
  Object.assign(adminForm, {
    id: admin.id,
    name: admin.name || '',
    email: admin.email || '',
    password: '',
    role: admin.role === 'SENIOR_ADMIN' ? 'SENIOR_ADMIN' : 'ADMIN',
    isActive: !!admin.isActive
  })
}

async function saveAdminAccount() {
  saving.value = true
  try {
    const payload = {
      name: adminForm.name,
      email: adminForm.email,
      role: adminForm.role,
      isActive: adminForm.isActive
    }
    if (adminForm.password) payload.password = adminForm.password
    if (adminForm.id) {
      await updateAdminAdmin(adminForm.id, payload)
    } else {
      await createAdminAdmin({
        ...payload,
        password: adminForm.password
      })
    }
    resetAdminForm()
    const data = await getAdminAdmins()
    admins.value = data.admins || []
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.saveFailed
  } finally {
    saving.value = false
  }
}

function resetCustomerForm() {
  Object.assign(customerForm, { id: '', name: '', email: '', password: '', role: 'USER', isActive: true })
}

function editCustomerAccount(user) {
  Object.assign(customerForm, {
    id: user.id,
    name: user.name || '-',
    email: user.email || '',
    password: '',
    role: user.role === 'VENDOR' ? 'VENDOR' : 'USER',
    isActive: !!user.isActive
  })
}

async function saveCustomerAccount() {
  if (!customerForm.id) return
  saving.value = true
  try {
    const payload = {
      email: customerForm.email,
      role: customerForm.role,
      isActive: customerForm.isActive
    }
    if (customerForm.password) payload.password = customerForm.password
    const data = await updateAdminUser(customerForm.id, payload)
    users.value = users.value.map(item => item.id === customerForm.id ? data.user : item)
    resetCustomerForm()
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.saveFailed
  } finally {
    saving.value = false
  }
}

async function setAdminActive(admin, isActive) {
  saving.value = true
  try {
    const data = await updateAdminAdmin(admin.id, { isActive })
    admins.value = admins.value.map(item => item.id === admin.id ? data.admin : item)
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.saveFailed
  } finally {
    saving.value = false
  }
}

async function removeAdmin(admin) {
  const confirmed = window.confirm(t.value.deleteAdminConfirm.replace('{name}', admin.name || admin.email))
  if (!confirmed) return
  saving.value = true
  try {
    await deleteAdminAdmin(admin.id)
    admins.value = admins.value.filter(item => item.id !== admin.id)
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.deleteFailed
  } finally {
    saving.value = false
  }
}

async function submitPasswordChange() {
  passwordMessage.value = ''
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    error.value = t.value.passwordMismatch
    return
  }
  saving.value = true
  try {
    await changePassword({
      oldPassword: passwordForm.oldPassword,
      newPassword: passwordForm.newPassword
    })
    Object.assign(passwordForm, { oldPassword: '', newPassword: '', confirmPassword: '' })
    error.value = ''
    passwordMessage.value = t.value.passwordChanged
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.saveFailed
  } finally {
    saving.value = false
  }
}

async function loadSelectedInquiry() {
  if (route.name !== 'admin-order-detail') {
    selectedInquiry.value = null
    showQuoteDialog.value = false
    editingQuote.value = null
    return
  }
  const id = route.params.id
  if (!id) return
  const cached = inquiries.value.find(item => item.id === id)
  if (cached && cached.messages && cached.quotes) {
    selectedInquiry.value = cached
  }
  try {
    const data = await getAdminInquiry(id)
    selectedInquiry.value = data.data || data.inquiry
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.loadFailed
  }
}

async function setInquiryStatus(status) {
  if (!selectedInquiry.value) return
  const data = await updateInquiry(selectedInquiry.value.id, { status })
  selectedInquiry.value = data.data || data.inquiry || { ...selectedInquiry.value, status }
  const index = inquiries.value.findIndex(item => item.id === selectedInquiry.value.id)
  if (index >= 0) inquiries.value[index] = selectedInquiry.value
}

function openQuoteDialog(quote = null) {
  editingQuote.value = quote
  showQuoteDialog.value = true
}

function closeQuoteDialog() {
  showQuoteDialog.value = false
  editingQuote.value = null
}

async function handleQuoteSaved() {
  showQuoteDialog.value = false
  editingQuote.value = null
  await loadSelectedInquiry()
  await load()
}

async function setVendorStatus(vendor, status) {
  await updateAdminVendor(vendor.id, { status, reviewNote: vendor.reviewNoteDraft || vendor.reviewNote || '' })
  await load()
}

function applyI18nData(payload) {
  const data = payload?.data || payload || {}
  i18nLocales.value = data.locales || []
  i18nKeys.value = data.keys || []
  i18nTranslations.value = {
    ...i18nTranslations.value,
    ...(data.translations || {})
  }
}

async function selectI18nLocale(code) {
  selectedI18nLocale.value = code
  translationChanges.value = {}
  savedTranslations.value = false
  if (i18nTranslations.value[code]) return
  loadingTranslations.value = true
  try {
    applyI18nData(await getAdminI18n(code))
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.loadFailed
  } finally {
    loadingTranslations.value = false
  }
}

function changeTranslation(key, value) {
  translationChanges.value = { ...translationChanges.value, [key]: value }
  i18nTranslations.value = {
    ...i18nTranslations.value,
    [selectedI18nLocale.value]: {
      ...(i18nTranslations.value[selectedI18nLocale.value] || {}),
      [key]: value
    }
  }
}

async function saveTranslations() {
  if (selectedI18nLocale.value === 'en') return
  const updates = translationChanges.value
  if (!Object.keys(updates).length) {
    savedTranslations.value = true
    window.setTimeout(() => { savedTranslations.value = false }, 1800)
    return
  }
  savingTranslations.value = true
  try {
    applyI18nData(await updateAdminI18n({ locale: selectedI18nLocale.value, translations: updates }))
    translationChanges.value = {}
    savedTranslations.value = true
    window.setTimeout(() => { savedTranslations.value = false }, 1800)
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.saveFailed
  } finally {
    savingTranslations.value = false
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    adminUser.value = currentUser()
    if (!adminUser.value || !['ADMIN', 'SENIOR_ADMIN', 'SUPER_ADMIN'].includes(adminUser.value.role)) {
      router.replace(localized(`/admin/login?redirect=${encodeURIComponent(route.fullPath)}`))
      return
    }
    const [analyticsData, productsData, categoriesData, bannersData, contactsData, vendorsData, inquiriesData, usersData, mediaData, i18nData, specTemplateData, adminsData] = await Promise.all([
      getAdminAnalytics(),
      getAdminProducts(),
      getAdminCategories(),
      isElevatedAdmin.value ? getAdminBanners() : Promise.resolve({ banners: [] }),
      getAdminContacts(),
      getAdminVendors(),
      getAdminInquiries(),
      isElevatedAdmin.value ? getAdminUsers() : Promise.resolve({ users: [] }),
      getAdminMedia(),
      isElevatedAdmin.value ? getAdminI18n(selectedI18nLocale.value) : Promise.resolve({ data: {} }),
      getAdminSpecTemplate(),
      canManageAdmins.value ? getAdminAdmins() : Promise.resolve({ admins: [] })
    ])
    analytics.value = analyticsData
    products.value = productsData.products || []
    categories.value = categoriesData.categories || []
    banners.value = bannersData.banners || []
    contacts.value = contactsData.contacts || []
    vendors.value = (vendorsData.vendors || []).map(item => ({ ...item, reviewNoteDraft: item.reviewNote || '' }))
    inquiries.value = inquiriesData.inquiries || []
    users.value = usersData.users || []
    admins.value = adminsData.admins || []
    applyMediaData(mediaData)
    specTemplateRows.value = createDefaultPowerStripSpecs(specTemplateData.template || [])
    specTemplateProductCount.value = specTemplateData.productCount || 0
    applyI18nData(i18nData)
    if (!bannerForm.id) resetBannerForm()
    if (!categoryForm.id) resetCategoryForm()
    syncProductForm()
    await loadSelectedInquiry()
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.loadFailed
  } finally {
    loading.value = false
  }
}

watch(productForm, () => {
  if (productFormHydrating.value || !isProductFormRoute()) return
  productFormDirty.value = true
  productFormRouteKey.value = currentProductFormRouteKey()
  saveProductDraft()
}, { deep: true, flush: 'sync' })
watch(() => route.fullPath, () => {
  syncProductForm()
  loadSelectedInquiry()
})
watch(products, () => {
  syncProductForm()
})
onMounted(load)

const copy = {
  en: {
    refresh: 'Refresh', dashboard: 'Dashboard', dashboardSubtitle: 'Store operations overview for the last 30 days',
    products: 'Products', productReview: 'Product Review', productsSubtitle: 'Manage catalog items and review submitted products', productFormSubtitle: 'Edit product data used by the storefront and review flow', specTemplateSettings: 'Template Settings', specTemplateSubtitle: 'Control the fixed product parameter template and sync it to all products',
    vendorReview: 'Vendor Review', vendorReviewSubtitle: 'Review vendor applications and publishing access', banners: 'Banners', bannersSubtitle: 'Hero banner images and multilingual copy', categories: 'Categories', categoriesSubtitle: 'Catalog category structure',
    orders: 'Inquiries', ordersSubtitle: 'Submitted quotation requests', customers: 'Customers', customersSubtitle: 'Registered customer and vendor accounts', adminManagement: 'Admin Management', adminManagementSubtitle: 'Create ordinary admins and enable or disable their access', changePassword: 'Change Password', changePasswordSubtitle: 'Update your administrator password',
    media: 'Media', mediaSubtitle: 'Product images used across the site', contacts: 'Contact Messages', contactsSubtitle: 'Messages submitted from the contact page',
    coupons: 'Coupons', couponsSubtitle: 'Promotion rules and coupon settings', shipping: 'Shipping', shippingSubtitle: 'Shipping zones and delivery options', analytics: 'Analytics', analyticsSubtitle: 'Traffic and conversion reporting', translations: 'Translations', translationsSubtitle: 'Language coverage and currency settings',
    pageViews: 'Page Views', totalInquiries: 'Total Inquiries', registeredUsers: 'Registered Customers', activeProducts: 'Active Products', vsLastMonth: 'vs last month', inquiryTrend: 'Inquiry Trend (Last 12 Months)', inquiryStatus: 'Inquiry Status Distribution', inquiries: 'Inquiries', recentInquiries: 'Recent Inquiries', topProducts: 'Top Products', trafficSources: 'Traffic Sources', visitorRegions: 'Visitor Regions', viewAll: 'View all', units: 'units', noData: 'No data', noInquiries: 'No inquiries',
    allProducts: 'All Products', pendingReview: 'Pending Review', newProduct: 'New Product', editProduct: 'Edit Product', deleteProduct: 'Delete', deleteProductConfirm: 'Delete product \"{name}\"? This cannot be undone.', product: 'Product', category: 'Category', price: 'Price', status: 'Status', updatedAt: 'Updated', createdAt: 'Created', actions: 'Actions', approve: 'Approve', reject: 'Reject', edit: 'Edit', cancel: 'Cancel', save: 'Save', saving: 'Saving...', view: 'View',
    productName: 'Product Name', productNameLocalized: 'Product Name ({locale})', productNameEn: 'Product Name (English)', productNameZh: 'Product Name (Chinese)', slug: 'Slug', sku: 'SKU', uncategorized: 'Uncategorized', compareAtPrice: 'Compare-at Price', imageUrl: 'Image URL', shortDescription: 'Short Description', description: 'Description', descriptionLocalized: 'Description ({locale})', descriptionEn: 'Description (English)', descriptionZh: 'Description (Chinese)',
    basicInfo: 'Basic Information', specifications: 'Specifications', addSpecGroup: 'Add Group', removeSpecGroup: 'Delete group', addSpec: 'Add Parameter', removeSpec: 'Remove parameter', noSpecs: 'No specifications yet.', specName: 'Spec name', specValue: 'Spec value', specNameEn: 'Spec name (English)', specNameZh: 'Spec name (Chinese)', specValueEn: 'Spec value (English)', specValueZh: 'Spec value (Chinese)', specOptionsEn: 'Options (English, one per line)', specOptionsZh: 'Options (Chinese, one per line)', specTemplateLocked: 'Parameter structure is controlled in Template Settings', specTemplateNotice: 'Saving this template will synchronize editable/displayed fields and candidate values for {count} products without overwriting filled values.', saveSpecTemplate: 'Save Template & Sync Fields', specGroupNameEn: 'Group name (English)', specGroupNameZh: 'Group name (Chinese)', specGroupDefault: 'Specification Group', specGroupDefaultZh: '规格大类', specGroupEn: 'Group / note (English)', specGroupZh: 'Group / note (Chinese)', pricing: 'Pricing', salePrice: 'Sale Price', costPrice: 'Cost Price', priceNegotiable: 'Price negotiable', negotiable: 'Negotiable', tradeDisplay: 'Trade Display', addTier: 'Add Tier', removeTier: 'Remove tier', minQty: 'Min qty', maxQty: 'Max qty', tierPrice: 'Tier price', leaveBlankUnlimited: 'Blank = unlimited', samplePrice: 'Sample Price', minimumOrderShort: 'MOQ', cartonSpec: 'Carton Spec', displayStock: 'Display Stock', shipFromEn: 'Ship From (English)', shipFromZh: 'Ship From (Chinese)', categoryAndAttributes: 'Category & Attributes', brandName: 'Brand Name', isFeatured: 'Featured', isNew: 'New Arrival', productImages: 'Product Images', displayImages: 'Product display images', displayImage: 'Display image', posterImages: 'Detail poster images', posterImagePlaceholder: 'Enter poster image URL', addImage: 'Add Image', uploadImage: 'Upload Image', chooseFromMedia: 'Choose from Media', mediaLibrary: 'Media Library', uploadCategory: 'Upload category', uploadCategoryPlaceholder: 'Enter or choose a category', filterCategory: 'Filter category', allMedia: 'All media', mediaCategoryGeneral: 'General', mediaCategoryProducts: 'Product images', mediaCategoryPosters: 'Detail posters', mediaCategoryBanners: 'Banners', mediaCategoryCategories: 'Category images', mediaCategoryUncategorized: 'Uncategorized', viewImage: 'View Image', deleteImage: 'Delete Image', uploading: 'Uploading...', uploadFailed: 'Upload failed.', deleteFailed: 'Delete failed.', variants: 'Variants', addVariant: 'Add Variant', addVariantType: 'Add Spec Type', variantTypeNameEn: 'Spec type name (English)', variantTypeNameZh: 'Spec type name (Chinese)', variantTypeValuesEn: 'Spec values (English, one per line)', variantTypeValuesZh: 'Spec values (Chinese, one per line)', variantCombinations: 'SKU / Stock Combinations', selectVariantValue: 'Select value', stock: 'Stock', optionsJson: 'Options (JSON)', vendorProductReview: 'Vendor Product Review', currentStatus: 'Current status:', rejectionReason: 'Rejection Reason', rejectionReasonPlaceholder: 'Enter rejection reason when rejecting a product',
    overview: 'Overview', quotes: 'Quotes', messages: 'Messages', contactInfo: 'Contact Information', phone: 'Phone', country: 'Country', expectedDeliveryTime: 'Expected Delivery', quantityRequirements: 'Quantity Requirements', customizationNeeds: 'Customization Needs', productList: 'Product List', quantity: 'Quantity:', note: 'Note:', createQuote: 'Create Quote', noQuotes: 'No quote yet',
    companyName: 'Company Name', contactPerson: 'Contact Person', email: 'Email', password: 'Password', currentPassword: 'Current Password', newPassword: 'New Password', confirmPassword: 'Confirm Password', passwordMismatch: 'The two new passwords do not match.', passwordChanged: 'Password updated.', files: 'Files', fileLabel: 'File', noFiles: 'No files', submittedAt: 'Submitted', reviewNote: 'Review note', disable: 'Disable', enable: 'Enable', noDescription: 'No description', productCount: 'Products', enabled: 'Enabled', disabled: 'Disabled', inquiryNumber: 'Inquiry Number', name: 'Name', role: 'Role', superAdmin: 'Super Admin', seniorAdmin: 'Senior Admin', normalAdmin: 'Admin', createAdmin: 'Create Admin', deleteAdmin: 'Delete Admin', deleteAdminConfirm: 'Delete admin \"{name}\"? This cannot be undone.', superAdminOnly: 'Only elevated admins can manage administrator accounts.', protectedAccount: 'Protected', subject: 'Subject', message: 'Message', title: 'Title', buttonText: 'Button Text', position: 'Position', sortOrder: 'Sort Order', link: 'Link', bannerImage: 'Banner Image', coverImage: 'Cover Image', newBanner: 'New Banner', editBanner: 'Edit Banner', newCategory: 'New Category', editCategory: 'Edit Category',
    couponRules: 'Coupon Rules', couponRulesDesc: 'Create amount, percentage, validity and usage-limit rules in this section.', couponUsage: 'Usage Control', couponUsageDesc: 'Track usage by customer, product and campaign before enabling coupons on the storefront.', shippingZones: 'Shipping Zones', shippingZonesDesc: 'Group countries and regions for quote-based shipping.', shippingMethods: 'Delivery Methods', shippingMethodsDesc: 'Configure express, ocean freight, sample delivery and pickup options.', analyticsDesc: 'Traffic data is prepared for dashboards and can be connected to live tracking later.', regionDesc: 'Visitor region charts follow the same dashboard slot as the original admin page.', localeCoverage: 'Language Coverage', localeCoverageDesc: 'Supported storefront locales: English, Chinese, Japanese, Korean, French, German, Spanish and Arabic.', currencyCoverage: 'Currency Coverage', currencyCoverageDesc: 'Supported currencies: USD, EUR, GBP, JPY, CNY and KRW.',
    i18nManager: 'Translation Key Management', i18nKeyCount: 'Total {count} translation keys', sourceText: 'Source', searchTranslations: 'Search translation keys...', allNamespaces: 'All', loadingTranslations: 'Loading language pack...', noTranslationMatches: 'No matching translation keys found.', showingKeys: 'Showing {shown} / {total}', englishReadonly: ' - English is the read-only source text', saved: 'Saved', loadFailed: 'Failed to load admin data.', saveFailed: 'Save failed.'
  },
  zh: {
    refresh: '\u5237\u65b0', dashboard: '\u4eea\u8868\u76d8', dashboardSubtitle: '\u5e97\u94fa\u8fd1 30 \u5929\u8fd0\u8425\u6570\u636e\u6982\u89c8',
    products: '\u5546\u54c1', productReview: '\u5546\u54c1\u5ba1\u6838', productsSubtitle: '\u7ba1\u7406\u5546\u54c1\u8d44\u6599\u5e76\u5ba1\u6838\u5546\u5bb6\u63d0\u4ea4\u7684\u5546\u54c1', productFormSubtitle: '\u7f16\u8f91\u524d\u53f0\u5c55\u793a\u548c\u5ba1\u6838\u6d41\u7a0b\u4f7f\u7528\u7684\u5546\u54c1\u6570\u636e', specTemplateSettings: '\u6a21\u677f\u8bbe\u7f6e', specTemplateSubtitle: '\u7ba1\u7406\u56fa\u5b9a\u5546\u54c1\u53c2\u6570\u6a21\u677f\uff0c\u5e76\u540c\u6b65\u5230\u6240\u6709\u5546\u54c1',
    vendorReview: '\u5546\u5bb6\u5ba1\u6838', vendorReviewSubtitle: '\u5ba1\u6838\u5546\u5bb6\u5165\u9a7b\u7533\u8bf7\u548c\u53d1\u5e03\u6743\u9650', banners: '\u6a2a\u5e45', bannersSubtitle: '\u7ba1\u7406\u9996\u9875 Banner \u56fe\u7247\u548c\u591a\u8bed\u8a00\u6587\u6848', categories: '\u5206\u7c7b', categoriesSubtitle: '\u5546\u54c1\u5206\u7c7b\u7ed3\u6784',
    orders: '\u8be2\u4ef7', ordersSubtitle: '\u5ba2\u6237\u63d0\u4ea4\u7684\u62a5\u4ef7\u8bf7\u6c42', customers: '\u5ba2\u6237', customersSubtitle: '\u5df2\u6ce8\u518c\u5ba2\u6237\u548c\u5546\u5bb6\u8d26\u53f7', adminManagement: '\u7ba1\u7406\u5458\u7ba1\u7406', adminManagementSubtitle: '\u521b\u5efa\u666e\u901a\u7ba1\u7406\u5458\u5e76\u542f\u7528\u6216\u505c\u7528\u6743\u9650', changePassword: '\u4fee\u6539\u5bc6\u7801', changePasswordSubtitle: '\u66f4\u65b0\u5f53\u524d\u7ba1\u7406\u5458\u8d26\u53f7\u5bc6\u7801',
    media: '\u5a92\u4f53\u5e93', mediaSubtitle: '\u7ad9\u70b9\u4e2d\u4f7f\u7528\u7684\u5546\u54c1\u56fe\u7247', contacts: '\u8054\u7cfb\u6d88\u606f', contactsSubtitle: '\u8054\u7cfb\u9875\u9762\u63d0\u4ea4\u7684\u6d88\u606f',
    coupons: '\u4f18\u60e0\u5238', couponsSubtitle: '\u4fc3\u9500\u89c4\u5219\u548c\u4f18\u60e0\u5238\u8bbe\u7f6e', shipping: '\u7269\u6d41', shippingSubtitle: '\u7269\u6d41\u533a\u57df\u548c\u914d\u9001\u65b9\u5f0f', analytics: '\u5206\u6790', analyticsSubtitle: '\u8bbf\u95ee\u4e0e\u8f6c\u5316\u6570\u636e\u62a5\u8868', translations: '\u7ffb\u8bd1', translationsSubtitle: '\u8bed\u8a00\u8986\u76d6\u548c\u8d27\u5e01\u8bbe\u7f6e',
    pageViews: '\u9875\u9762\u6d4f\u89c8', totalInquiries: '\u603b\u8be2\u4ef7\u6570', registeredUsers: '\u6ce8\u518c\u5ba2\u6237', activeProducts: '\u5728\u552e\u5546\u54c1', vsLastMonth: '\u8f83\u4e0a\u6708', inquiryTrend: '\u8be2\u4ef7\u8d8b\u52bf\uff08\u8fd1 12 \u4e2a\u6708\uff09', inquiryStatus: '\u8be2\u4ef7\u72b6\u6001\u5206\u5e03', inquiries: '\u8be2\u4ef7', recentInquiries: '\u6700\u8fd1\u8be2\u4ef7', topProducts: '\u70ed\u95e8\u5546\u54c1', trafficSources: '\u6d41\u91cf\u6765\u6e90', visitorRegions: '\u8bbf\u5ba2\u5730\u533a', viewAll: '\u67e5\u770b\u5168\u90e8', units: '\u4ef6', noData: '\u6682\u65e0\u6570\u636e', noInquiries: '\u6682\u65e0\u8be2\u4ef7',
    allProducts: '\u5168\u90e8\u5546\u54c1', pendingReview: '\u5f85\u5ba1\u6838', newProduct: '\u65b0\u589e\u5546\u54c1', editProduct: '\u7f16\u8f91\u5546\u54c1', deleteProduct: '\u5220\u9664', deleteProductConfirm: '\u786e\u5b9a\u5220\u9664\u5546\u54c1\u201c{name}\u201d\uff1f\u6b64\u64cd\u4f5c\u4e0d\u53ef\u6062\u590d\u3002', product: '\u5546\u54c1', category: '\u5206\u7c7b', price: '\u4ef7\u683c', status: '\u72b6\u6001', updatedAt: '\u66f4\u65b0', createdAt: '\u521b\u5efa\u65f6\u95f4', actions: '\u64cd\u4f5c', approve: '\u901a\u8fc7', reject: '\u9a73\u56de', edit: '\u7f16\u8f91', cancel: '\u53d6\u6d88', save: '\u4fdd\u5b58', saving: '\u4fdd\u5b58\u4e2d...', view: '\u67e5\u770b',
    productName: '\u5546\u54c1\u540d\u79f0', productNameLocalized: '\u5546\u54c1\u540d\u79f0\uff08{locale}\uff09', productNameEn: '\u5546\u54c1\u540d\u79f0\uff08\u82f1\u6587\uff09', productNameZh: '\u5546\u54c1\u540d\u79f0\uff08\u4e2d\u6587\uff09', slug: '\u94fe\u63a5\u6807\u8bc6', sku: 'SKU', uncategorized: '\u672a\u5206\u7c7b', compareAtPrice: '\u5212\u7ebf\u4ef7', imageUrl: '\u56fe\u7247\u5730\u5740', shortDescription: '\u7b80\u77ed\u63cf\u8ff0', description: '\u8be6\u7ec6\u63cf\u8ff0', descriptionLocalized: '\u63cf\u8ff0\uff08{locale}\uff09', descriptionEn: '\u63cf\u8ff0\uff08\u82f1\u6587\uff09', descriptionZh: '\u63cf\u8ff0\uff08\u4e2d\u6587\uff09',
    basicInfo: '\u57fa\u672c\u4fe1\u606f', specifications: '\u89c4\u683c\u53c2\u6570', addSpecGroup: '\u6dfb\u52a0\u5927\u7c7b', removeSpecGroup: '\u5220\u9664\u5927\u7c7b', addSpec: '\u6dfb\u52a0\u53c2\u6570', removeSpec: '\u5220\u9664\u53c2\u6570', noSpecs: '\u6682\u65e0\u89c4\u683c\u53c2\u6570\u3002', specName: '\u53c2\u6570\u540d', specValue: '\u53c2\u6570\u503c', specNameEn: '\u53c2\u6570\u540d\uff08\u82f1\u6587\uff09', specNameZh: '\u53c2\u6570\u540d\uff08\u4e2d\u6587\uff09', specValueEn: '\u53c2\u6570\u503c\uff08\u82f1\u6587\uff09', specValueZh: '\u53c2\u6570\u503c\uff08\u4e2d\u6587\uff09', specOptionsEn: '\u5019\u9009\u503c\uff08\u82f1\u6587\uff0c\u6bcf\u884c\u4e00\u4e2a\uff09', specOptionsZh: '\u5019\u9009\u503c\uff08\u4e2d\u6587\uff0c\u6bcf\u884c\u4e00\u4e2a\uff09', specTemplateLocked: '\u53c2\u6570\u7ed3\u6784\u7531\u6a21\u677f\u8bbe\u7f6e\u7edf\u4e00\u63a7\u5236', specTemplateNotice: '\u4fdd\u5b58\u6b64\u6a21\u677f\u53ea\u4f1a\u540c\u6b65 {count} \u4e2a\u5546\u54c1\u7684\u53ef\u7f16\u8f91/\u524d\u53f0\u5c55\u793a\u5b57\u6bb5\u548c\u5019\u9009\u503c\uff0c\u4e0d\u4f1a\u8986\u76d6\u5df2\u586b\u5199\u7684\u503c\u3002', saveSpecTemplate: '\u4fdd\u5b58\u6a21\u677f\u5e76\u540c\u6b65\u5b57\u6bb5', specGroupNameEn: '\u5927\u7c7b\u540d\uff08\u82f1\u6587\uff09', specGroupNameZh: '\u5927\u7c7b\u540d\uff08\u4e2d\u6587\uff09', specGroupDefault: 'Specification Group', specGroupDefaultZh: '\u89c4\u683c\u5927\u7c7b', specGroupEn: '\u5206\u7ec4/\u5907\u6ce8\uff08\u82f1\u6587\uff09', specGroupZh: '\u5206\u7ec4/\u5907\u6ce8\uff08\u4e2d\u6587\uff09', pricing: '\u5b9a\u4ef7', salePrice: '\u552e\u4ef7', costPrice: '\u6210\u672c\u4ef7', priceNegotiable: '\u4ef7\u683c\u9762\u8bae', negotiable: '\u9762\u8bae', tradeDisplay: '\u4ea4\u6613\u5c55\u793a\u4fe1\u606f', addTier: '\u6dfb\u52a0\u9636\u68af', removeTier: '\u5220\u9664\u9636\u68af', minQty: '\u6700\u5c0f\u6570\u91cf', maxQty: '\u6700\u5927\u6570\u91cf', tierPrice: '\u9636\u68af\u4ef7', leaveBlankUnlimited: '\u7559\u7a7a\u8868\u793a\u4ee5\u4e0a', samplePrice: '\u6837\u54c1\u4ef7', minimumOrderShort: '\u8d77\u8ba2\u91cf', cartonSpec: '\u7bb1\u89c4', displayStock: '\u524d\u53f0\u5c55\u793a\u5e93\u5b58', shipFromEn: '\u53d1\u8d27\u5730\uff08\u82f1\u6587\uff09', shipFromZh: '\u53d1\u8d27\u5730\uff08\u4e2d\u6587\uff09', categoryAndAttributes: '\u5206\u7c7b\u4e0e\u5c5e\u6027', brandName: '\u54c1\u724c\u540d\u79f0', isFeatured: '\u7cbe\u9009\u63a8\u8350', isNew: '\u65b0\u54c1\u4e0a\u67b6', productImages: '\u5546\u54c1\u56fe\u7247', displayImages: '\u5546\u54c1\u5c55\u793a\u56fe', displayImage: '\u5c55\u793a\u56fe', posterImages: '\u8be6\u60c5\u6d77\u62a5\u56fe', posterImagePlaceholder: '\u8f93\u5165\u6d77\u62a5\u56fe URL', addImage: '\u6dfb\u52a0\u56fe\u7247', uploadImage: '\u4e0a\u4f20\u56fe\u7247', chooseFromMedia: '\u4ece\u5a92\u4f53\u5e93\u9009\u62e9', mediaLibrary: '\u5a92\u4f53\u5e93', uploadCategory: '\u4e0a\u4f20\u5206\u7c7b', uploadCategoryPlaceholder: '\u8f93\u5165\u6216\u9009\u62e9\u5206\u7c7b', filterCategory: '\u7b5b\u9009\u5206\u7c7b', allMedia: '\u5168\u90e8\u7d20\u6750', mediaCategoryGeneral: '\u901a\u7528\u7d20\u6750', mediaCategoryProducts: '\u5546\u54c1\u56fe\u7247', mediaCategoryPosters: '\u8be6\u60c5\u6d77\u62a5', mediaCategoryBanners: '\u6a2a\u5e45\u56fe\u7247', mediaCategoryCategories: '\u5206\u7c7b\u56fe\u7247', mediaCategoryUncategorized: '\u672a\u5206\u7c7b', viewImage: '\u67e5\u770b\u56fe\u7247', deleteImage: '\u5220\u9664\u56fe\u7247', uploading: '\u4e0a\u4f20\u4e2d...', uploadFailed: '\u4e0a\u4f20\u5931\u8d25\u3002', deleteFailed: '\u5220\u9664\u5931\u8d25\u3002', variants: '\u89c4\u683c\u53d8\u4f53', addVariant: '\u6dfb\u52a0\u53d8\u4f53', addVariantType: '\u6dfb\u52a0\u89c4\u683c\u7c7b\u578b', variantTypeNameEn: '\u89c4\u683c\u7c7b\u578b\u540d\uff08\u82f1\u6587\uff09', variantTypeNameZh: '\u89c4\u683c\u7c7b\u578b\u540d\uff08\u4e2d\u6587\uff09', variantTypeValuesEn: '\u89c4\u683c\u503c\uff08\u82f1\u6587\uff0c\u6bcf\u884c\u4e00\u4e2a\uff09', variantTypeValuesZh: '\u89c4\u683c\u503c\uff08\u4e2d\u6587\uff0c\u6bcf\u884c\u4e00\u4e2a\uff09', variantCombinations: 'SKU / \u5e93\u5b58\u7ec4\u5408', selectVariantValue: '\u9009\u62e9\u89c4\u683c\u503c', stock: '\u5e93\u5b58', optionsJson: '\u9009\u9879\uff08JSON\uff09', vendorProductReview: '\u5546\u5bb6\u5546\u54c1\u5ba1\u6838', currentStatus: '\u5f53\u524d\u72b6\u6001:', rejectionReason: '\u9a73\u56de\u539f\u56e0', rejectionReasonPlaceholder: '\u9a73\u56de\u5546\u54c1\u65f6\u8f93\u5165\u539f\u56e0',
    overview: '\u6982\u89c8', quotes: '\u62a5\u4ef7', messages: '\u6d88\u606f', contactInfo: '\u8054\u7cfb\u4fe1\u606f', phone: '\u7535\u8bdd', country: '\u56fd\u5bb6', expectedDeliveryTime: '\u671f\u671b\u4ea4\u671f', quantityRequirements: '\u6570\u91cf\u8981\u6c42', customizationNeeds: '\u5b9a\u5236\u9700\u6c42', productList: '\u4ea7\u54c1\u5217\u8868', quantity: '\u6570\u91cf:', note: '\u5907\u6ce8:', createQuote: '\u521b\u5efa\u62a5\u4ef7', noQuotes: '\u6682\u65e0\u62a5\u4ef7',
    companyName: '\u516c\u53f8\u540d\u79f0', contactPerson: '\u8054\u7cfb\u4eba', email: '\u90ae\u7bb1', password: '\u5bc6\u7801', currentPassword: '\u539f\u5bc6\u7801', newPassword: '\u65b0\u5bc6\u7801', confirmPassword: '\u786e\u8ba4\u65b0\u5bc6\u7801', passwordMismatch: '\u4e24\u6b21\u8f93\u5165\u7684\u65b0\u5bc6\u7801\u4e0d\u4e00\u81f4\u3002', passwordChanged: '\u5bc6\u7801\u5df2\u66f4\u65b0\u3002', files: '\u6587\u4ef6', fileLabel: '\u6587\u4ef6', noFiles: '\u6682\u65e0\u6587\u4ef6', submittedAt: '\u63d0\u4ea4\u65f6\u95f4', reviewNote: '\u5ba1\u6838\u5907\u6ce8', disable: '\u505c\u7528', enable: '\u542f\u7528', noDescription: '\u6682\u65e0\u63cf\u8ff0', productCount: '\u5546\u54c1\u6570', enabled: '\u542f\u7528', disabled: '\u505c\u7528', inquiryNumber: '\u8be2\u4ef7\u7f16\u53f7', name: '\u59d3\u540d', role: '\u89d2\u8272', superAdmin: '\u6700\u9ad8\u7ba1\u7406\u5458', seniorAdmin: '\u7b2c\u4e8c\u9ad8\u7ea7\u7ba1\u7406\u5458', normalAdmin: '\u666e\u901a\u7ba1\u7406\u5458', createAdmin: '\u521b\u5efa\u7ba1\u7406\u5458', deleteAdmin: '\u5220\u9664\u7ba1\u7406\u5458', deleteAdminConfirm: '\u786e\u5b9a\u5220\u9664\u7ba1\u7406\u5458\u201c{name}\u201d\uff1f\u6b64\u64cd\u4f5c\u4e0d\u53ef\u6062\u590d\u3002', superAdminOnly: '\u53ea\u6709\u9ad8\u7ea7\u7ba1\u7406\u5458\u53ef\u4ee5\u7ba1\u7406\u7ba1\u7406\u5458\u8d26\u53f7\u3002', protectedAccount: '\u53d7\u4fdd\u62a4', subject: '\u4e3b\u9898', message: '\u6d88\u606f', title: '\u6807\u9898', buttonText: '\u6309\u94ae\u6587\u5b57', position: '\u4f4d\u7f6e', sortOrder: '\u6392\u5e8f', link: '\u94fe\u63a5', bannerImage: 'Banner \u56fe\u7247', coverImage: '\u5c01\u9762\u56fe', newBanner: '\u65b0\u589e Banner', editBanner: '\u7f16\u8f91 Banner', newCategory: '\u65b0\u589e\u5206\u7c7b', editCategory: '\u7f16\u8f91\u5206\u7c7b',
    couponRules: '\u4f18\u60e0\u89c4\u5219', couponRulesDesc: '\u914d\u7f6e\u6ee1\u51cf\u3001\u6298\u6263\u3001\u6709\u6548\u671f\u548c\u4f7f\u7528\u9650\u5236\u3002', couponUsage: '\u4f7f\u7528\u63a7\u5236', couponUsageDesc: '\u4e0a\u7ebf\u524d\u53ef\u8ddf\u8e2a\u5ba2\u6237\u3001\u5546\u54c1\u548c\u6d3b\u52a8\u7684\u4f18\u60e0\u5238\u4f7f\u7528\u60c5\u51b5\u3002', shippingZones: '\u7269\u6d41\u533a\u57df', shippingZonesDesc: '\u6309\u56fd\u5bb6\u548c\u5730\u533a\u7ec4\u7ec7\u8be2\u4ef7\u5f0f\u7269\u6d41\u89c4\u5219\u3002', shippingMethods: '\u914d\u9001\u65b9\u5f0f', shippingMethodsDesc: '\u914d\u7f6e\u5feb\u9012\u3001\u6d77\u8fd0\u3001\u6837\u54c1\u5bc4\u9001\u548c\u81ea\u63d0\u7b49\u9009\u9879\u3002', analyticsDesc: '\u8bbf\u95ee\u6570\u636e\u5df2\u9884\u7559\u62a5\u8868\u4f4d\u7f6e\u3002', regionDesc: '\u8bbf\u5ba2\u5730\u533a\u56fe\u8868\u6cbf\u7528\u539f\u540e\u53f0\u4eea\u8868\u76d8\u533a\u57df\u3002', localeCoverage: '\u8bed\u8a00\u8986\u76d6', localeCoverageDesc: '\u524d\u53f0\u652f\u6301\u82f1\u8bed\u3001\u4e2d\u6587\u3001\u65e5\u8bed\u3001\u97e9\u8bed\u3001\u6cd5\u8bed\u3001\u5fb7\u8bed\u3001\u897f\u73ed\u7259\u8bed\u548c\u963f\u62c9\u4f2f\u8bed\u3002', currencyCoverage: '\u8d27\u5e01\u8986\u76d6', currencyCoverageDesc: '\u652f\u6301 USD\u3001EUR\u3001GBP\u3001JPY\u3001CNY \u548c KRW\u3002',
    i18nManager: '\u591a\u8bed\u8a00\u952e\u7ba1\u7406', i18nKeyCount: '\u5171 {count} \u4e2a\u7ffb\u8bd1\u952e', sourceText: '\u539f\u6587', searchTranslations: '\u641c\u7d22\u7ffb\u8bd1\u952e...', allNamespaces: '\u5168\u90e8', loadingTranslations: '\u6b63\u5728\u52a0\u8f7d\u8bed\u8a00\u5305...', noTranslationMatches: '\u672a\u627e\u5230\u5339\u914d\u7684\u7ffb\u8bd1\u952e\u3002', showingKeys: '\u663e\u793a {shown} / {total}', englishReadonly: ' - \u82f1\u8bed\u4e3a\u53ea\u8bfb\u539f\u6587', saved: '\u5df2\u4fdd\u5b58', loadFailed: '\u540e\u53f0\u6570\u636e\u52a0\u8f7d\u5931\u8d25\u3002', saveFailed: '\u4fdd\u5b58\u5931\u8d25\u3002'
  }
}

Object.assign(copy.en, {
  elevatedOnly: 'Only elevated admins can manage this section.',
  editCustomerAccount: 'Edit Customer Account',
  selectCustomer: 'Select Customer',
  personalUser: 'Personal User',
  vendorAccount: 'Vendor Account',
  passwordOptional: 'New password (optional)',
  displayImagePlaceholder: 'Enter display image URL',
  mediaCategoryManagement: 'Category Management',
  mediaCategoryNamePlaceholder: 'Enter category name',
  mediaCategoryTree: 'Category Tree',
  mediaCategoryNameZhPlaceholder: 'Chinese category name',
  mediaCategoryNameEnPlaceholder: 'English category name',
  topLevelCategory: 'Top-level category',
  uploadToCategory: 'Upload to',
  filterHere: 'Filter',
  useForUpload: 'Upload',
  selectedForUpload: 'Selected',
  addMediaCategory: 'Add Category',
  noMediaCategories: 'No categories yet.',
  deleteMediaCategoryConfirm: 'Delete category "{name}" and its subcategories? Images in them will move to Uncategorized.',
  saveMediaCategory: 'Save Category',
  useSelectedMedia: 'Use Selected',
  searchProducts: 'Search product name, SKU, category, brand...',
  clear: 'Clear',
  imageName: 'Image name',
  imageNamePlaceholder: 'Enter image filename',
  priceModeTier: 'Unified tier pricing',
  priceModeTierDesc: 'Show one B2B ladder price table. Variants only control SKU and stock.',
  priceModeVariant: 'Variant pricing',
  priceModeVariantDesc: 'Each SKU/specification has its own price. Tier prices are hidden.',
  priceModeNegotiable: 'Negotiable',
  priceModeNegotiableDesc: 'No fixed price is shown. Buyers submit inquiries for quotes.',
  priceModeVariantNotice: 'Variant pricing is enabled. Enter prices in SKU / Stock Combinations; the storefront will not show the tier price table.',
  priceModeNegotiableNotice: 'Negotiable pricing is enabled. Fixed prices and tier prices will be hidden on the storefront.',
  variantPriceLocked: 'Controlled by price mode',
  done: 'Done'
})

Object.assign(copy.zh, {
  elevatedOnly: '\u53ea\u6709\u9ad8\u7ea7\u7ba1\u7406\u5458\u53ef\u4ee5\u7ba1\u7406\u6b64\u9879\u3002',
  editCustomerAccount: '\u7f16\u8f91\u5ba2\u6237\u8d26\u53f7',
  selectCustomer: '\u9009\u62e9\u5ba2\u6237',
  personalUser: '\u4e2a\u4eba\u7528\u6237',
  vendorAccount: '\u5546\u5bb6\u8d26\u53f7',
  passwordOptional: '\u65b0\u5bc6\u7801\uff08\u53ef\u9009\uff09',
  displayImagePlaceholder: '\u8f93\u5165\u5c55\u793a\u56fe URL',
  mediaCategoryManagement: '\u5206\u7c7b\u7ba1\u7406',
  mediaCategoryNamePlaceholder: '\u8f93\u5165\u5206\u7c7b\u540d\u79f0',
  mediaCategoryTree: '\u5206\u7c7b\u6811',
  mediaCategoryNameZhPlaceholder: '\u5206\u7c7b\u4e2d\u6587\u540d',
  mediaCategoryNameEnPlaceholder: '\u5206\u7c7b\u82f1\u6587\u540d',
  topLevelCategory: '\u9876\u7ea7\u5206\u7c7b',
  uploadToCategory: '\u4e0a\u4f20\u5230',
  filterHere: '\u7b5b\u9009',
  useForUpload: '\u4e0a\u4f20',
  selectedForUpload: '\u5df2\u9009',
  addMediaCategory: '\u65b0\u589e\u5206\u7c7b',
  noMediaCategories: '\u6682\u65e0\u5206\u7c7b\u3002',
  deleteMediaCategoryConfirm: '\u786e\u5b9a\u5220\u9664\u5206\u7c7b\u201c{name}\u201d\u53ca\u5176\u5b50\u5206\u7c7b\uff1f\u5206\u7c7b\u5185\u56fe\u7247\u4f1a\u79fb\u5230\u672a\u5206\u7c7b\u3002',
  saveMediaCategory: '\u4fdd\u5b58\u5206\u7c7b',
  useSelectedMedia: '\u4f7f\u7528\u5df2\u9009',
  searchProducts: '\u641c\u7d22\u5546\u54c1\u540d\u79f0\u3001SKU\u3001\u5206\u7c7b\u3001\u54c1\u724c...',
  clear: '\u6e05\u9664',
  imageName: '\u56fe\u7247\u540d\u79f0',
  imageNamePlaceholder: '\u8f93\u5165\u56fe\u7247\u6587\u4ef6\u540d',
  priceModeTier: '\u7edf\u4e00\u9636\u68af\u4ef7',
  priceModeTierDesc: '\u524d\u53f0\u663e\u793a\u4e00\u5957 B2B \u9636\u68af\u4ef7\uff0c\u89c4\u683c\u53ea\u7ba1 SKU \u548c\u5e93\u5b58\u3002',
  priceModeVariant: '\u6309\u89c4\u683c\u5b9a\u4ef7',
  priceModeVariantDesc: '\u6bcf\u4e2a SKU/\u89c4\u683c\u5355\u72ec\u5b9a\u4ef7\uff0c\u4e0d\u663e\u793a\u9636\u68af\u4ef7\u8868\u3002',
  priceModeNegotiable: '\u9762\u8bae',
  priceModeNegotiableDesc: '\u524d\u53f0\u4e0d\u663e\u793a\u56fa\u5b9a\u4ef7\u683c\uff0c\u5ba2\u6237\u63d0\u4ea4\u8be2\u76d8\u540e\u62a5\u4ef7\u3002',
  priceModeVariantNotice: '\u5df2\u542f\u7528\u6309\u89c4\u683c\u5b9a\u4ef7\uff0c\u8bf7\u5728 SKU / \u5e93\u5b58\u7ec4\u5408\u91cc\u586b\u5199\u4ef7\u683c\uff0c\u524d\u53f0\u4e0d\u663e\u793a\u9636\u68af\u4ef7\u8868\u3002',
  priceModeNegotiableNotice: '\u5df2\u542f\u7528\u9762\u8bae\uff0c\u524d\u53f0\u4f1a\u9690\u85cf\u56fa\u5b9a\u4ef7\u548c\u9636\u68af\u4ef7\u3002',
  variantPriceLocked: '\u7531\u4ef7\u683c\u6a21\u5f0f\u63a7\u5236',
  done: '\u5b8c\u6210'
})
</script>

<style scoped>
th {
  padding: 0.875rem 1rem;
  border-bottom: 1px solid var(--border);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--muted-foreground);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

td {
  padding: 0.875rem 1rem;
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
}

tbody tr:last-child td {
  border-bottom: 0;
}
</style>
