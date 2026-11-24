<template>
  <div class="mx-auto max-w-7xl px-4 pt-24 pb-16 lg:px-8">
    <section class="grid items-center gap-8 py-8 lg:grid-cols-[minmax(0,0.95fr)_minmax(420px,1.05fr)] lg:py-14">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wider text-primary">{{ t.eyebrow }}</p>
        <h1 class="mt-3 text-3xl font-bold leading-tight text-gray-950 md:text-5xl">{{ t.title }}</h1>
        <p class="mt-5 max-w-2xl text-base leading-relaxed text-muted-foreground md:text-lg">{{ t.intro }}</p>
        <div class="mt-8 flex flex-wrap gap-3">
          <RouterLink :to="localized('/shop')" class="btn gradient-bg h-11 rounded-full px-6 text-white">{{ t.viewProducts }}</RouterLink>
          <RouterLink :to="localized('/contact')" class="btn h-11 rounded-full border bg-background px-6">{{ t.contact }}</RouterLink>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div class="overflow-hidden rounded-xl bg-muted">
          <img src="/images/products/product-1.png" :alt="t.imageAlt1" class="aspect-[3/4] h-full w-full object-cover" />
        </div>
        <div class="mt-10 overflow-hidden rounded-xl bg-muted">
          <img src="/images/products/product-2.png" :alt="t.imageAlt2" class="aspect-[3/4] h-full w-full object-cover" />
        </div>
      </div>
    </section>

    <section class="grid gap-4 py-8 sm:grid-cols-3">
      <div v-for="item in stats" :key="item.label" class="rounded-xl border bg-background p-5">
        <p class="text-2xl font-bold text-primary">{{ item.value }}</p>
        <p class="mt-2 text-sm text-muted-foreground">{{ item.label }}</p>
      </div>
    </section>

    <section class="grid gap-8 py-8 lg:grid-cols-[0.8fr_1.2fr]">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wider text-primary">{{ t.capabilityEyebrow }}</p>
        <h2 class="mt-2 text-2xl font-bold text-gray-950">{{ t.capabilityTitle }}</h2>
      </div>
      <div class="grid gap-4 sm:grid-cols-2">
        <article v-for="item in capabilities" :key="item.title" class="rounded-xl border bg-background p-5">
          <h3 class="font-semibold text-gray-950">{{ item.title }}</h3>
          <p class="mt-2 text-sm leading-relaxed text-muted-foreground">{{ item.desc }}</p>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

const route = useRoute()
const locale = computed(() => route.params.locale || 'en')
const isZh = computed(() => locale.value === 'zh')

const t = computed(() => isZh.value ? zh : en)
const stats = computed(() => t.value.stats)
const capabilities = computed(() => t.value.capabilities)

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

const en = {
  eyebrow: 'About Misicheng',
  title: 'Power strip and charging products built for wholesale sourcing.',
  intro: 'Misicheng focuses on smart power strips, extension sockets, plug adapters, USB-C charging stations, and surge protection solutions. We support distributors, project buyers, and OEM customers with practical product matching and quotation support.',
  viewProducts: 'View Products',
  contact: 'Contact Us',
  imageAlt1: 'Smart power strip',
  imageAlt2: 'Extension socket detail',
  capabilityEyebrow: 'What we support',
  capabilityTitle: 'From plug standard matching to packaging customization.',
  stats: [
    { value: '30+', label: 'Power strip and plug adapter categories' },
    { value: 'OEM', label: 'Logo, packaging, outlet layout, and cable options' },
    { value: 'B2B', label: 'Bulk quotation and project sourcing workflow' }
  ],
  capabilities: [
    { title: 'Plug Standards', desc: 'China, EU, UK, US, universal, travel adapter, and market-specific plug options can be matched by region.' },
    { title: 'Charging Functions', desc: 'USB-A, USB-C, PD fast charging, WiFi control, energy monitoring, and surge protection options are available by model.' },
    { title: 'Product Customization', desc: 'Outlet count, cable length, switch type, shell color, packaging, and brand identity can be confirmed before quotation.' },
    { title: 'Wholesale Support', desc: 'Product data, images, sample confirmation, and tier pricing are organized for distributors and project purchasers.' }
  ]
}

const zh = {
  eyebrow: '关于 Misicheng',
  title: '面向批发采购的排插与充电类产品供应。',
  intro: 'Misicheng 专注智能排插、延长线插座、插头转换器、USB-C 充电站和防浪涌电源解决方案，为经销商、项目采购和 OEM 客户提供产品匹配与报价支持。',
  viewProducts: '查看产品',
  contact: '联系我们',
  imageAlt1: '智能排插',
  imageAlt2: '延长线插座细节',
  capabilityEyebrow: '服务能力',
  capabilityTitle: '从插头标准匹配到包装定制，围绕排插采购流程展开。',
  stats: [
    { value: '30+', label: '排插与插头转换类目' },
    { value: 'OEM', label: 'Logo、包装、插位、线长可定制' },
    { value: 'B2B', label: '批量报价与项目采购流程支持' }
  ],
  capabilities: [
    { title: '插头标准', desc: '支持中规、欧规、英规、美规、万能转换器、旅行转换器等不同市场的插头标准匹配。' },
    { title: '充电功能', desc: '可按型号配置 USB-A、USB-C、PD 快充、WiFi 控制、能耗监测和防浪涌保护等功能。' },
    { title: '产品定制', desc: '插位数量、线长、开关类型、外壳颜色、包装方式和品牌标识可在报价前确认。' },
    { title: '批发支持', desc: '为经销商和项目采购整理产品资料、图片、样品确认和阶梯价格。' }
  ]
}
</script>
