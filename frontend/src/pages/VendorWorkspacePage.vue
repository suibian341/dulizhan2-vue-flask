<template>
  <VendorShell :user="user" @signout="signOut">
    <div class="space-y-6">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h1 class="text-2xl font-bold">{{ pageTitle }}</h1>
          <p class="text-sm text-muted-foreground">{{ pageSubtitle }}</p>
        </div>
        <RouterLink :to="primaryAction.href" class="btn h-10 px-5" :class="primaryAction.primary ? 'bg-primary text-primary-foreground' : 'btn-outline'">
          <component :is="primaryAction.icon" class="h-4 w-4" />
          {{ primaryAction.label }}
        </RouterLink>
      </div>

      <div v-if="loading" class="space-y-6">
        <div class="shimmer h-28 rounded-2xl"></div>
        <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <div v-for="i in 4" :key="i" class="shimmer h-28 rounded-xl"></div>
        </div>
      </div>

      <div v-else-if="error" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
        {{ error }}
      </div>

      <template v-else>
        <section v-if="section === 'overview'" class="space-y-6">
          <ApplicationBanner :application="application" />

          <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <div v-for="card in summaryCards" :key="card.label" class="rounded-xl border bg-background p-5 shadow-sm">
              <div class="flex items-center justify-between">
                <span class="text-sm text-muted-foreground">{{ card.label }}</span>
                <component :is="card.icon" class="h-5 w-5 text-muted-foreground" />
              </div>
              <div class="mt-3 text-3xl font-bold">{{ card.value }}</div>
            </div>
          </div>

          <div class="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
            <div class="rounded-2xl border bg-background p-6 shadow-sm">
              <h2 class="mb-4 text-lg font-semibold">{{ t.nextSteps }}</h2>
              <div class="space-y-3 text-sm text-muted-foreground">
                <div v-for="(step, index) in t.steps" :key="step.title" class="flex items-start gap-3">
                  <span class="mt-0.5 rounded-md border px-2 py-0.5 text-xs">{{ index + 1 }}</span>
                  <div>
                    <p class="font-medium text-foreground">{{ step.title }}</p>
                    <p>{{ step.description }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="rounded-2xl border bg-background p-6 shadow-sm">
              <h2 class="mb-4 text-lg font-semibold">{{ t.quickLinks }}</h2>
              <div class="grid gap-3">
                <RouterLink v-for="link in quickLinks" :key="link.href" :to="link.href" class="rounded-xl border px-4 py-3 text-sm font-medium transition-colors hover:bg-muted">
                  {{ link.label }}
                </RouterLink>
              </div>
            </div>
          </div>
        </section>

        <section v-else-if="section === 'application'" class="space-y-6">
          <ApplicationBanner :application="application" />
          <div v-if="application" class="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
            <div class="rounded-2xl border bg-background p-6 shadow-sm">
              <h2 class="mb-4 text-lg font-semibold">{{ t.companyDetails }}</h2>
              <div class="grid gap-4 sm:grid-cols-2">
                <Info :label="t.companyName" :value="application.companyName" />
                <Info :label="t.contactPerson" :value="application.contactPerson || '-'" />
                <Info :label="t.email" :value="application.email" />
                <Info :label="t.phone" :value="application.phone || '-'" />
                <Info :label="t.country" :value="application.country || '-'" />
                <Info :label="t.address" :value="application.address || '-'" />
              </div>
              <div class="mt-4 space-y-2">
                <p class="text-sm font-medium">{{ t.companyProfile }}</p>
                <p class="rounded-xl bg-muted/40 px-4 py-3 text-sm leading-6 text-muted-foreground">
                  {{ application.description || t.noDescription }}
                </p>
              </div>
            </div>

            <div class="rounded-2xl border bg-background p-6 shadow-sm">
              <h2 class="mb-4 text-lg font-semibold">{{ t.files }}</h2>
              <div class="space-y-3">
                <div v-for="file in application.certificationFiles" :key="file" class="flex items-center justify-between rounded-xl border px-4 py-3">
                  <span class="min-w-0 break-all text-sm">{{ file.split('/').pop() || file }}</span>
                  <a :href="file" target="_blank" rel="noreferrer" class="btn btn-outline h-8 px-3 text-xs">{{ t.open }}</a>
                </div>
                <p v-if="!application.certificationFiles?.length" class="rounded-xl border border-dashed px-4 py-6 text-sm text-muted-foreground">{{ t.noFiles }}</p>
              </div>
            </div>
          </div>
          <div v-else class="rounded-2xl border bg-background p-6 shadow-sm">
            <p class="text-sm text-muted-foreground">{{ t.noApplication }}</p>
            <RouterLink :to="localized('/vendor/register')" class="btn mt-5 h-10 bg-primary px-5 text-primary-foreground">{{ t.submitApplication }}</RouterLink>
          </div>
        </section>

        <section v-else-if="section === 'products'" class="space-y-4">
          <div class="overflow-x-auto rounded-xl border bg-background shadow-sm">
              <table class="w-full min-w-[760px] text-left text-sm">
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
                  v-for="product in products"
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
                  <td><span class="rounded-full px-2.5 py-1 text-xs font-medium" :class="productStatusClass(product.status)">{{ productStatusLabel(product.status) }}</span></td>
                  <td>{{ formatDate(product.updatedAt || product.createdAt) }}</td>
                  <td>
                    <div class="flex justify-end gap-2">
                      <RouterLink :to="localized(`/vendor/products/${product.id}/edit`)" class="btn h-8 border px-3 text-xs">{{ t.edit }}</RouterLink>
                    </div>
                  </td>
                </tr>
                <tr v-if="!products.length">
                  <td colspan="7" class="py-8 text-center text-sm text-muted-foreground">{{ t.noProducts }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-else-if="section === 'product-form'" class="max-w-4xl">
          <div v-if="!canCreateProduct" class="mb-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
            {{ t.approvalRequired }}
          </div>
          <div v-if="productForm.rejectionReason" class="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            <strong class="font-semibold">{{ t.reviewNote }}:</strong>
            {{ productForm.rejectionReason }}
          </div>
          <form class="flex flex-col gap-6" @submit.prevent="submitProduct">
            <div class="order-2 space-y-4 rounded-xl border bg-background p-6 shadow-sm">
              <h2 class="font-semibold">{{ t.basicInfo }}</h2>
              <div class="grid gap-4 md:grid-cols-2">
                <label v-for="field in productLocales" :key="`vendor-name-${field.code}`" class="space-y-2 text-sm font-medium">
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
                <label v-for="field in productLocales" :key="`vendor-desc-${field.code}`" class="block space-y-2 text-sm font-medium">
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
                          <input v-model.trim="row.spec.valueEn" class="input h-9" :list="`vendor-spec-options-en-${row.index}`" :placeholder="t.specValueEn" />
                          <input v-model.trim="row.spec.valueZh" class="input h-9" :list="`vendor-spec-options-zh-${row.index}`" :placeholder="t.specValueZh" />
                        </div>
                        <datalist :id="`vendor-spec-options-en-${row.index}`">
                          <option v-for="option in row.spec.optionsEn" :key="`en-${option}`" :value="option" />
                        </datalist>
                        <datalist :id="`vendor-spec-options-zh-${row.index}`">
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
              <h2 class="font-semibold">{{ t.categoryAndBrand }}</h2>
              <div class="grid gap-4 md:grid-cols-2">
                <label class="space-y-2 text-sm font-medium">
                  <span>{{ t.category }}</span>
                  <select v-model="productForm.categoryId" class="select h-10">
                    <option value="">{{ t.uncategorized }}</option>
                    <option v-for="category in categories" :key="category.id" :value="category.id">{{ category.name }}</option>
                  </select>
                </label>
                <label class="space-y-2 text-sm font-medium">
                  <span>{{ t.brandName }}</span>
                  <input v-model.trim="productForm.brandName" class="input h-10" placeholder="Misicheng" />
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

            <div class="order-7 flex justify-end gap-3 border-t pt-6">
              <RouterLink :to="localized('/vendor/products')" class="btn btn-outline h-10 px-4">{{ t.cancel }}</RouterLink>
              <button type="submit" class="btn h-10 bg-primary px-5 text-primary-foreground" :disabled="saving || !canCreateProduct">
                {{ saving ? t.saving : t.submitForReview }}
              </button>
            </div>
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
              <p v-if="!mediaItems.length" class="text-sm text-muted-foreground">{{ t.noMedia }}</p>
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

        <section v-else-if="section === 'password'" class="max-w-xl">
          <form class="space-y-4 rounded-xl border bg-card p-5 shadow-sm" @submit.prevent="submitPasswordChange">
            <input v-model.trim="passwordForm.oldPassword" class="input h-10" type="password" :placeholder="t.currentPassword" required />
            <input v-model.trim="passwordForm.newPassword" class="input h-10" type="password" :placeholder="t.newPassword" minlength="8" required />
            <input v-model.trim="passwordForm.confirmPassword" class="input h-10" type="password" :placeholder="t.confirmPassword" minlength="8" required />
            <p v-if="passwordError" class="text-sm text-red-600">{{ passwordError }}</p>
            <p v-if="passwordMessage" class="text-sm text-emerald-700">{{ passwordMessage }}</p>
            <button type="submit" class="btn h-10 bg-primary px-5 text-primary-foreground" :disabled="saving">
              {{ saving ? t.saving : t.changePassword }}
            </button>
          </form>
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
                <CheckCircle2 v-if="isMediaSelected(item)" class="h-4 w-4" />
              </span>
              <img :src="item.thumbnailUrl || item.url" alt="" class="h-32 w-full object-cover" loading="lazy" decoding="async" />
              <span class="block break-words px-3 pb-1 pt-2 text-xs font-medium">{{ item.name || item.url }}</span>
              <span class="block px-3 pb-2 text-[11px] text-muted-foreground">{{ mediaCategoryLabel(item.category) }}</span>
            </button>
          </div>
          <p v-if="!mediaItems.length" class="text-sm text-muted-foreground">{{ t.noMedia }}</p>
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
  </VendorShell>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { CheckCircle2, Clock3, GripVertical, ImageIcon, Package, Plus, ShieldX, Trash2, Upload, XCircle } from 'lucide-vue-next'

import { changePassword, createVendorMediaCategory, createVendorProduct, deleteVendorMedia, deleteVendorMediaCategory, getCategories, getSpecTemplate, getVendorApplication, getVendorMedia, getVendorProducts, reorderVendorProducts, updateVendorMediaCategoryForItem, updateVendorProduct, uploadVendorMedia } from '@/api'
import VendorShell from '@/components/VendorShell.vue'
import {
  createDefaultPowerStripSpecs,
  mergeSpecsWithTemplate,
  normalizeSpecFormRow,
  specPayloadFromForm
} from '@/specTemplates'
import { useUiStore } from '@/stores/ui'
import { price, productPriceRange } from '@/utils'
import {
  createBlankVariantOptionType,
  createDefaultVariantOptionTypes,
  localizedOptionName,
  normalizeVariantFormRow,
  normalizeVariantOptionTypes,
  optionPairsForType,
  variantOptionTypePayloadFromForm,
  variantPayloadFromForm
} from '@/variantOptions'

const Info = defineComponent({
  props: { label: String, value: String },
  setup(props) {
    return () => h('div', { class: 'space-y-1 rounded-xl bg-muted/30 px-4 py-3' }, [
      h('p', { class: 'text-xs font-medium uppercase tracking-[0.08em] text-muted-foreground' }, props.label),
      h('p', { class: 'text-sm font-medium text-foreground' }, props.value)
    ])
  }
})

const ApplicationBanner = defineComponent({
  props: { application: Object },
  setup(props) {
    return () => h('div', { class: 'rounded-2xl border bg-background p-6 shadow-sm' }, [
      h('div', { class: 'flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between' }, [
        h('div', { class: 'flex items-start gap-4' }, [
          h('div', { class: 'flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-blue-700' }, [
            h(statusIcon.value, { class: 'h-6 w-6' })
          ]),
          h('div', { class: 'space-y-2' }, [
            h('div', { class: 'flex items-center gap-3' }, [
              h('h2', { class: 'text-lg font-semibold' }, t.value.applicationTitle),
              h('span', { class: ['rounded-full px-3 py-1 text-xs font-medium', statusClass.value] }, statusLabel.value)
            ]),
            h('p', { class: 'max-w-2xl text-sm leading-6 text-muted-foreground' }, statusDescription.value),
            props.application?.reviewNote ? h('p', { class: 'rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800' }, props.application.reviewNote) : null
          ])
        ]),
        props.application?.submittedAt ? h('div', { class: 'text-sm text-muted-foreground' }, [
          h('p', `${t.value.submittedAt}: ${formatDate(props.application.submittedAt)}`),
          props.application.reviewedAt ? h('p', `${t.value.reviewedAt}: ${formatDate(props.application.reviewedAt)}`) : null
        ]) : null
      ])
    ])
  }
})

const route = useRoute()
const router = useRouter()
const ui = useUiStore()
const user = ref(null)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const pricingDialogOpen = ref(false)
const passwordError = ref('')
const passwordMessage = ref('')
const passwordForm = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })
const application = ref(null)
const products = ref([])
const reorderingProducts = ref(false)
const categories = ref([])
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
const productImageDragState = reactive({ type: '', from: -1, over: -1 })
const productListDragState = reactive({ draggedId: '', overId: '' })
const productLocales = [
  { code: 'en', label: 'English' },
  { code: 'zh', label: '中文' }
]

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
  brandName: 'Misicheng',
  displayImages: [],
  displayImageInput: '',
  posterImages: [],
  posterImageInput: '',
  specs: createDefaultPowerStripSpecs(specTemplateRows.value),
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
  return name === 'vendor-product-new' || name === 'vendor-product-edit'
}

function productDraftKey() {
  const accountId = user.value?.id || user.value?.email || 'vendor'
  const target = route.name === 'vendor-product-edit' ? route.params.id : 'new'
  return `misicheng-vendor-product-draft:${accountId}:${target}`
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
const section = computed(() => {
  if (route.name === 'vendor-product-new' || route.name === 'vendor-product-edit') return 'product-form'
  const path = route.path.replace(/^\/(en|zh|ja|ko|fr|de|es|ar)\/vendor\/?/, '')
  if (!path) return 'overview'
  return path.split('/')[0] || 'overview'
})
const canCreateProduct = computed(() => application.value?.status === 'APPROVED')
const pageTitle = computed(() => pageMeta.value.title)
const pageSubtitle = computed(() => pageMeta.value.subtitle)
const pageMeta = computed(() => {
  const map = {
    overview: [t.value.title, application.value?.companyName ? `${application.value.companyName} ${t.value.workspaceSuffix}` : t.value.subtitle],
    application: [t.value.applicationTitle, t.value.applicationSubtitle],
    products: [t.value.products, t.value.productsSubtitle],
    'product-form': [route.name === 'vendor-product-edit' ? t.value.editProduct : t.value.newProduct, t.value.productFormSubtitle],
    media: [t.value.media, t.value.mediaSubtitle],
    password: [t.value.changePassword, t.value.changePasswordSubtitle]
  }
  const item = map[section.value] || map.overview
  return { title: item[0], subtitle: item[1] }
})
const primaryAction = computed(() => {
  if (section.value === 'product-form') return { href: localized('/vendor/products'), label: t.value.backToProducts, icon: Package, primary: false }
  if (section.value === 'products') return { href: localized('/vendor/products/new'), label: t.value.newProduct, icon: Plus, primary: true }
  return { href: localized(canCreateProduct.value ? '/vendor/products/new' : '/vendor/application'), label: canCreateProduct.value ? t.value.newProduct : t.value.trackApplication, icon: canCreateProduct.value ? Plus : Clock3, primary: canCreateProduct.value }
})
const statusMeta = computed(() => {
  const status = application.value?.status || 'PENDING'
  const isZh = locale.value === 'zh'
  switch (status) {
    case 'APPROVED':
      return {
        class: 'bg-emerald-50 text-emerald-700',
        label: isZh ? '已通过' : 'Approved',
        description: isZh ? '商家权限已启用，可以提交商品进入后台审核。' : 'Vendor access is active. You can submit products for review.',
        icon: CheckCircle2
      }
    case 'REJECTED':
      return {
        class: 'bg-red-50 text-red-700',
        label: isZh ? '已驳回' : 'Rejected',
        description: isZh ? '请根据审核备注补充资料后重新提交。' : 'Please update your company profile with the requested changes.',
        icon: XCircle
      }
    case 'DISABLED':
      return {
        class: 'bg-gray-100 text-gray-700',
        label: isZh ? '已停用' : 'Disabled',
        description: isZh ? '后台已停用当前商家发布权限。' : 'Vendor publishing access has been disabled by admin.',
        icon: ShieldX
      }
    default:
      return {
        class: 'bg-amber-50 text-amber-700',
        label: isZh ? '待审核' : 'Pending Review',
        description: isZh ? '您的入驻申请正在审核中，通过后即可提交新商品。' : 'Your application is under review. Product submission will unlock after approval.',
        icon: Clock3
      }
  }
})
const statusLabel = computed(() => statusMeta.value.label)
const statusDescription = computed(() => statusMeta.value.description)
const statusIcon = computed(() => statusMeta.value.icon)
const statusClass = computed(() => statusMeta.value.class)
const summaryCards = computed(() => [
  { label: t.value.cards.total, value: products.value.length, icon: Package },
  { label: t.value.cards.pending, value: products.value.filter(item => item.status === 'PENDING_REVIEW').length, icon: Clock3 },
  { label: t.value.cards.active, value: products.value.filter(item => item.status === 'ACTIVE').length, icon: CheckCircle2 },
  { label: t.value.cards.rejected, value: products.value.filter(item => item.status === 'REJECTED').length, icon: XCircle }
])
const quickLinks = computed(() => [
  { href: localized('/vendor/application'), label: t.value.trackApplication },
  { href: localized('/vendor/products'), label: t.value.products },
  { href: localized('/vendor/media'), label: t.value.media }
])
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
}

function removeMediaUrlFromForm(url) {
  productForm.displayImages = productForm.displayImages.filter(item => item !== url)
  if (productForm.displayImageInput === url) productForm.displayImageInput = ''
  productForm.posterImages = productForm.posterImages.filter(item => item !== url)
  if (productForm.posterImageInput === url) productForm.posterImageInput = ''
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
        const uploaded = await uploadVendorMedia(file, target.category)
        uploadedItems.push(uploaded)
      } catch (err) {
        uploadErrors.push(err)
      }
    }
    applyMediaData(await getVendorMedia())
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
    await deleteVendorMedia(item.storageKey || item.url)
    applyMediaData(await getVendorMedia())
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
    const data = await updateVendorMediaCategoryForItem(item, mediaPreviewCategory.value, mediaPreviewName.value)
    const oldUrls = data.oldUrls?.length ? data.oldUrls : [data.oldUrl || item.url]
    if (data.newUrl) oldUrls.forEach(oldUrl => replaceMediaUrlInForm(oldUrl, data.newUrl))
    applyMediaData(data.media ? data : await getVendorMedia())
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
    const data = await createVendorMediaCategory({
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
    const data = await deleteVendorMediaCategory({ id: target.id })
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

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

function signOut() {
  localStorage.removeItem('misicheng-user')
  router.push(localized('/vendor/login'))
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

function productPrice(product) {
  return productPriceRange(product, ui.currency, { negotiableText: t.value.negotiable })
}

function productStatusLabel(status) {
  return (locale.value === 'zh' ? {
    ACTIVE: '已上架',
    DRAFT: '草稿',
    PENDING_REVIEW: '待审核',
    REJECTED: '已驳回',
    ARCHIVED: '已归档'
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

function fitTextClass(value) {
  const length = Array.from(value || '').length
  if (length >= 40) return 'text-[11px]'
  if (length >= 28) return 'text-xs'
  return 'text-sm'
}

function translationFor(product, targetLocale) {
  return (product.translations || []).find(item => item.locale === targetLocale) || null
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
    brandName: 'Misicheng',
    displayImages: [],
    displayImageInput: '',
    posterImages: [],
    posterImageInput: '',
    specs: createDefaultPowerStripSpecs(specTemplateRows.value),
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
  if (route.name === 'vendor-product-new') {
    productFormHydrating.value = true
    resetProductForm()
    productFormHydrating.value = false
    restoreProductDraft()
    return
  }
  if (route.name !== 'vendor-product-edit') return
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
    slug: product.slug || '',
    sku: product.sku || '',
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
    brandName: product.brandName || 'Misicheng',
    displayImages: images.display,
    displayImageInput: '',
    posterImages: images.poster,
    posterImageInput: '',
    specs: mergeSpecsWithTemplate(product.specifications || [], specTemplateRows.value),
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
    await reorderVendorProducts(orderedIds)
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
  const visibleIds = products.value.map(product => product.id)
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
  const visibleIds = products.value.map(product => product.id)
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
    status: 'PENDING_REVIEW',
    price: basePrice,
    compareAtPrice: baseCompareAtPrice,
    categoryId: productForm.categoryId || null,
    brandName: productForm.brandName || null,
    vendorEmail: user.value?.email,
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
  if (!canCreateProduct.value) return
  saving.value = true
  try {
    const payload = productPayload()
    if (productForm.id) {
      await updateVendorProduct(productForm.id, payload)
    } else {
      await createVendorProduct(payload)
    }
    clearProductDraft()
    await load()
    router.push(localized('/vendor/products'))
  } catch (err) {
    error.value = err?.response?.data?.error || err?.message || t.value.saveFailed
  } finally {
    saving.value = false
  }
}

async function submitPasswordChange() {
  passwordError.value = ''
  passwordMessage.value = ''
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordError.value = t.value.passwordMismatch
    return
  }
  saving.value = true
  try {
    await changePassword({
      oldPassword: passwordForm.oldPassword,
      newPassword: passwordForm.newPassword
    })
    Object.assign(passwordForm, { oldPassword: '', newPassword: '', confirmPassword: '' })
    passwordMessage.value = t.value.passwordChanged
  } catch (err) {
    passwordError.value = err?.response?.data?.error || err?.message || t.value.saveFailed
  } finally {
    saving.value = false
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    user.value = JSON.parse(localStorage.getItem('misicheng-user') || 'null')
    if (!user.value || user.value.role !== 'VENDOR') {
      router.replace(localized('/vendor/login'))
      return
    }
    const [applicationData, productsData, categoriesData, mediaData, specTemplateData] = await Promise.all([
      getVendorApplication({ email: user.value.email }).catch(() => ({ data: null })),
      getVendorProducts({ email: user.value.email }),
      getCategories(),
      getVendorMedia({ email: user.value.email }),
      getSpecTemplate()
    ])
    application.value = applicationData.data || null
    products.value = productsData.products || []
    categories.value = categoriesData || []
    applyMediaData(mediaData)
    specTemplateRows.value = createDefaultPowerStripSpecs(specTemplateData.template || [])
    syncProductForm()
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
watch(() => route.fullPath, syncProductForm)
watch(products, () => {
  syncProductForm()
})
onMounted(load)

const copy = {
  en: {
    title: 'Vendor Center',
    subtitle: 'Track onboarding status and manage the vendor workspace.',
    workspaceSuffix: 'workspace',
    applicationTitle: 'Application Status',
    applicationSubtitle: 'Company profile and review result',
    products: 'Products',
    productsSubtitle: 'Manage drafts, submissions and review feedback',
    media: 'Media',
    mediaSubtitle: 'Images attached to your products',
    changePassword: 'Change Password',
    changePasswordSubtitle: 'Update your vendor account password',
    newProduct: 'Create Product',
    editProduct: 'Edit Product',
    productFormSubtitle: 'Submit product information into the admin review flow',
    backToProducts: 'Back to Products',
    trackApplication: 'View Application',
    nextSteps: 'Next Steps',
    quickLinks: 'Quick Links',
    companyDetails: 'Company Details',
    companyName: 'Company Name',
    contactPerson: 'Contact Person',
    email: 'Email',
    phone: 'Phone',
    country: 'Country',
    address: 'Address',
    currentPassword: 'Current Password',
    newPassword: 'New Password',
    confirmPassword: 'Confirm Password',
    passwordMismatch: 'The two new passwords do not match.',
    passwordChanged: 'Password updated.',
    companyProfile: 'Company Profile',
    noDescription: 'No description provided.',
    files: 'Certification Files',
    open: 'Open',
    noFiles: 'No certification files uploaded.',
    noApplication: 'No vendor application was found for this account.',
    submitApplication: 'Submit Application',
    submittedAt: 'Submitted',
    reviewedAt: 'Reviewed',
    product: 'Product',
    category: 'Category',
    price: 'Price',
    status: 'Status',
    updatedAt: 'Updated',
    actions: 'Actions',
    edit: 'Edit',
    view: 'View',
    noProducts: 'No products yet.',
    productName: 'Product Name',
    basicInfo: 'Basic Information',
    productNameLocalized: 'Product Name ({locale})',
    productNameEn: 'Product Name (English)',
    productNameZh: 'Product Name (Chinese)',
    slug: 'Slug',
    sku: 'SKU',
    uncategorized: 'Uncategorized',
    pricing: 'Pricing',
    salePrice: 'Sale Price',
    compareAtPrice: 'Compare-at Price',
    description: 'Description',
    descriptionLocalized: 'Description ({locale})',
    descriptionEn: 'Description (English)',
    descriptionZh: 'Description (Chinese)',
    costPrice: 'Cost Price',
    priceNegotiable: 'Price negotiable',
    negotiable: 'Negotiable',
    tradeDisplay: 'Trade Display',
    addTier: 'Add Tier',
    removeTier: 'Remove tier',
    minQty: 'Min qty',
    maxQty: 'Max qty',
    tierPrice: 'Tier price',
    leaveBlankUnlimited: 'Blank = unlimited',
    samplePrice: 'Sample Price',
    minimumOrderShort: 'MOQ',
    cartonSpec: 'Carton Spec',
    displayStock: 'Display Stock',
    shipFromEn: 'Ship From (English)',
    shipFromZh: 'Ship From (Chinese)',
    specifications: 'Specifications',
    addSpecGroup: 'Add Group',
    removeSpecGroup: 'Delete group',
    addSpec: 'Add Parameter',
    removeSpec: 'Remove parameter',
    noSpecs: 'No specifications yet.',
    specName: 'Spec name',
    specValue: 'Spec value',
    specNameEn: 'Spec name (English)',
    specNameZh: 'Spec name (Chinese)',
    specValueEn: 'Spec value (English)',
    specValueZh: 'Spec value (Chinese)',
    specTemplateLocked: 'Parameter structure is controlled by admin template',
    specGroupNameEn: 'Group name (English)',
    specGroupNameZh: 'Group name (Chinese)',
    specGroupDefault: 'Specification Group',
    specGroupDefaultZh: '规格大类',
    specGroupEn: 'Group / note (English)',
    specGroupZh: 'Group / note (Chinese)',
    categoryAndBrand: 'Category & Brand',
    brandName: 'Brand Name',
    productImages: 'Product Images',
    displayImages: 'Product display images',
    displayImage: 'Display image',
    displayImagePlaceholder: 'Enter display image URL',
    posterImages: 'Detail poster images',
    posterImagePlaceholder: 'Enter poster image URL',
    addImage: 'Add Image',
    uploadImage: 'Upload Image',
    chooseFromMedia: 'Choose from Media',
    mediaLibrary: 'Media Library',
    uploadCategory: 'Upload category',
    uploadCategoryPlaceholder: 'Enter or choose a category',
    filterCategory: 'Filter category',
    allMedia: 'All media',
    useSelectedMedia: 'Use Selected',
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
    mediaCategoryGeneral: 'General',
    mediaCategoryProducts: 'Product images',
    mediaCategoryPosters: 'Detail posters',
    mediaCategoryUncategorized: 'Uncategorized',
    viewImage: 'View Image',
    imageName: 'Image name',
    imageNamePlaceholder: 'Enter image filename',
    deleteImage: 'Delete Image',
    uploading: 'Uploading...',
    variants: 'Variants',
    addVariant: 'Add Variant',
    addVariantType: 'Add Spec Type',
    variantTypeNameEn: 'Spec type name (English)',
    variantTypeNameZh: 'Spec type name (Chinese)',
    variantTypeValuesEn: 'Spec values (English, one per line)',
    variantTypeValuesZh: 'Spec values (Chinese, one per line)',
    variantCombinations: 'SKU / Stock Combinations',
    selectVariantValue: 'Select value',
    stock: 'Stock',
    optionsJson: 'Options (JSON)',
    reviewNote: 'Review note',
    cancel: 'Cancel',
    submitForReview: 'Submit for Review',
    saving: 'Saving...',
    approvalRequired: 'Product submission is available after the vendor application is approved.',
    noMedia: 'No media yet.',
    loadFailed: 'Failed to load vendor workspace.',
    saveFailed: 'Save failed.',
    uploadFailed: 'Upload failed.',
    deleteFailed: 'Delete failed.',
    cards: {
      total: 'Products',
      pending: 'Pending Review',
      active: 'Active',
      rejected: 'Rejected'
    },
    steps: [
      { title: 'Submit application', description: 'Complete the company profile and supporting files.' },
      { title: 'Admin review', description: 'The admin team reviews your vendor profile.' },
      { title: 'Publish products', description: 'Approved vendors can create products and send them to review.' }
    ]
  },
  zh: {
    title: '商家中心',
    subtitle: '查看入驻状态并管理商家工作台。',
    workspaceSuffix: '工作台',
    applicationTitle: '入驻状态',
    applicationSubtitle: '企业资料和审核结果',
    products: '商品管理',
    productsSubtitle: '管理草稿、提报和审核反馈',
    media: '媒体库',
    mediaSubtitle: '商品关联图片素材',
    newProduct: '发布商品',
    editProduct: '编辑商品',
    productFormSubtitle: '提交商品资料进入后台审核流程',
    backToProducts: '返回商品',
    trackApplication: '查看申请',
    nextSteps: '下一步',
    quickLinks: '快捷入口',
    companyDetails: '企业信息',
    companyName: '公司名称',
    contactPerson: '联系人',
    email: '邮箱',
    phone: '联系电话',
    country: '国家/地区',
    address: '公司地址',
    companyProfile: '公司简介',
    noDescription: '暂无描述。',
    files: '资质文件',
    open: '查看',
    noFiles: '暂无上传资质文件。',
    noApplication: '当前账号没有找到商家入驻申请。',
    submitApplication: '提交申请',
    submittedAt: '提交时间',
    reviewedAt: '审核时间',
    product: '商品',
    category: '分类',
    price: '价格',
    status: '状态',
    updatedAt: '更新',
    actions: '操作',
    edit: '编辑',
    view: '查看',
    noProducts: '暂无商品。',
    productName: '商品名称',
    basicInfo: '基本信息',
    productNameLocalized: '商品名称（{locale}）',
    productNameEn: '商品名称（英文）',
    productNameZh: '商品名称（中文）',
    slug: '链接标识',
    sku: 'SKU',
    uncategorized: '未分类',
    pricing: '价格信息',
    salePrice: '售价',
    compareAtPrice: '划线价',
    description: '详细描述',
    descriptionLocalized: '商品描述（{locale}）',
    descriptionEn: '商品描述（英文）',
    descriptionZh: '商品描述（中文）',
    costPrice: '成本价',
    priceNegotiable: '价格面议',
    negotiable: '面议',
    tradeDisplay: '交易展示信息',
    addTier: '添加阶梯',
    removeTier: '删除阶梯',
    minQty: '最小数量',
    maxQty: '最大数量',
    tierPrice: '阶梯价',
    leaveBlankUnlimited: '留空表示以上',
    samplePrice: '样品价',
    minimumOrderShort: '起订量',
    cartonSpec: '箱规',
    displayStock: '前台展示库存',
    shipFromEn: '发货地（英文）',
    shipFromZh: '发货地（中文）',
    specifications: '规格参数',
    addSpecGroup: '添加大类',
    removeSpecGroup: '删除大类',
    addSpec: '添加参数',
    removeSpec: '删除参数',
    noSpecs: '暂无规格参数。',
    specName: '参数名',
    specValue: '参数值',
    specNameEn: '参数名（英文）',
    specNameZh: '参数名（中文）',
    specValueEn: '参数值（英文）',
    specValueZh: '参数值（中文）',
    specTemplateLocked: '参数结构由后台模板控制',
    specGroupNameEn: '大类名（英文）',
    specGroupNameZh: '大类名（中文）',
    specGroupDefault: 'Specification Group',
    specGroupDefaultZh: '规格大类',
    specGroupEn: '分组/备注（英文）',
    specGroupZh: '分组/备注（中文）',
    categoryAndBrand: '分类与品牌',
    brandName: '品牌名称',
    productImages: '商品图片',
    displayImages: '商品展示图',
    displayImage: '展示图',
    displayImagePlaceholder: '输入展示图 URL',
    posterImages: '详情海报图',
    posterImagePlaceholder: '输入海报图 URL',
    addImage: '添加图片',
    uploadImage: '上传图片',
    chooseFromMedia: '从媒体库选择',
    mediaLibrary: '媒体库',
    uploadCategory: '上传分类',
    uploadCategoryPlaceholder: '输入或选择分类',
    filterCategory: '筛选分类',
    allMedia: '全部素材',
    useSelectedMedia: '使用已选',
    mediaCategoryManagement: '分类管理',
    mediaCategoryNamePlaceholder: '输入分类名称',
    mediaCategoryTree: '分类树',
    mediaCategoryNameZhPlaceholder: '分类中文名',
    mediaCategoryNameEnPlaceholder: '分类英文名',
    topLevelCategory: '顶级分类',
    uploadToCategory: '上传到',
    filterHere: '筛选',
    useForUpload: '上传',
    selectedForUpload: '已选',
    addMediaCategory: '新增分类',
    noMediaCategories: '暂无分类。',
    deleteMediaCategoryConfirm: '确定删除分类“{name}”及其子分类？分类内图片会移到未分类。',
    saveMediaCategory: '保存分类',
    mediaCategoryGeneral: '通用素材',
    mediaCategoryProducts: '商品图片',
    mediaCategoryPosters: '详情海报',
    mediaCategoryUncategorized: '未分类',
    viewImage: '查看图片',
    imageName: '图片名称',
    imageNamePlaceholder: '输入图片文件名',
    deleteImage: '删除图片',
    uploading: '上传中...',
    variants: '规格变体',
    addVariant: '添加变体',
    addVariantType: '添加规格类型',
    variantTypeNameEn: '规格类型名（英文）',
    variantTypeNameZh: '规格类型名（中文）',
    variantTypeValuesEn: '规格值（英文，每行一个）',
    variantTypeValuesZh: '规格值（中文，每行一个）',
    variantCombinations: 'SKU / 库存组合',
    selectVariantValue: '选择规格值',
    stock: '库存',
    optionsJson: '选项（JSON）',
    reviewNote: '审核备注',
    cancel: '取消',
    submitForReview: '提交审核',
    saving: '保存中...',
    approvalRequired: '商家入驻申请通过后才能提交商品。',
    noMedia: '暂无媒体素材。',
    loadFailed: '商家工作台加载失败。',
    saveFailed: '保存失败。',
    uploadFailed: '上传失败。',
    deleteFailed: '删除失败。',
    cards: {
      total: '商品数',
      pending: '待审核',
      active: '已上架',
      rejected: '已驳回'
    },
    steps: [
      { title: '提交申请', description: '完善企业资料和附件文件。' },
      { title: '后台审核', description: '管理员会审核你的商家资料。' },
      { title: '发布商品', description: '通过后可创建商品并提交审核。' }
    ]
  }
}

Object.assign(copy.en, {
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
  changePassword: '\u4fee\u6539\u5bc6\u7801',
  changePasswordSubtitle: '\u66f4\u65b0\u5f53\u524d\u5546\u5bb6\u8d26\u53f7\u5bc6\u7801',
  currentPassword: '\u539f\u5bc6\u7801',
  newPassword: '\u65b0\u5bc6\u7801',
  confirmPassword: '\u786e\u8ba4\u65b0\u5bc6\u7801',
  passwordMismatch: '\u4e24\u6b21\u8f93\u5165\u7684\u65b0\u5bc6\u7801\u4e0d\u4e00\u81f4\u3002',
  passwordChanged: '\u5bc6\u7801\u5df2\u66f4\u65b0\u3002',
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
