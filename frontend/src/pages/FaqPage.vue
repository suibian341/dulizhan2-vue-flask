<template>
  <div class="mx-auto max-w-4xl px-4 pt-24 py-12 lg:px-8">
    <nav class="mb-8 flex items-center gap-2 text-sm text-muted-foreground">
      <RouterLink :to="localized('/')" class="hover:text-foreground transition-colors">{{ t.common.home }}</RouterLink>
      <ChevronRight class="h-3.5 w-3.5" />
      <span class="text-foreground font-medium">{{ t.faq.breadcrumb }}</span>
    </nav>

    <div class="mb-12 text-center">
      <h1 class="text-4xl font-bold tracking-tight">{{ t.faq.title }}</h1>
      <p class="mt-4 text-lg text-muted-foreground">{{ t.faq.subtitle }}</p>
    </div>

    <div class="space-y-10">
      <section v-for="(category, categoryIndex) in categories" :key="category.title">
        <h2 class="mb-4 text-xl font-semibold">{{ category.title }}</h2>
        <div class="rounded-xl border px-4">
          <div
            v-for="(item, itemIndex) in category.items"
            :key="item.question"
            class="border-b last:border-b-0"
          >
            <button
              type="button"
              class="focus-visible:border-ring focus-visible:ring-ring/50 flex w-full flex-1 items-start justify-between gap-4 rounded-md py-4 text-left text-sm font-medium transition-all outline-none hover:underline focus-visible:ring-[3px]"
              @click="toggle(categoryIndex, itemIndex)"
            >
              <span>{{ item.question }}</span>
              <ChevronDown class="text-muted-foreground pointer-events-none size-4 shrink-0 translate-y-0.5 transition-transform duration-200" :class="isOpen(categoryIndex, itemIndex) ? 'rotate-180' : ''" />
            </button>
            <Transition name="accordion">
              <div v-if="isOpen(categoryIndex, itemIndex)" class="overflow-hidden text-sm">
                <div class="pt-0 pb-4">
                  <p class="text-muted-foreground leading-relaxed">{{ item.answer }}</p>
                </div>
              </div>
            </Transition>
          </div>
        </div>
      </section>
    </div>

    <div class="mt-16 rounded-2xl bg-gradient-to-r from-sky-500 to-cyan-500 p-8 text-center">
      <h2 class="mb-3 text-xl font-semibold text-white">{{ t.faq.ctaTitle }}</h2>
      <p class="mb-6 text-white/80">{{ t.faq.ctaDesc }}</p>
      <RouterLink :to="localized('/contact')" class="inline-flex items-center justify-center rounded-md bg-white px-6 py-2.5 text-sm font-medium text-sky-600 hover:bg-white/90">
        {{ t.faq.ctaButton }}
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { ChevronDown, ChevronRight } from 'lucide-vue-next'

const route = useRoute()
const openKey = ref('0-0')
const locale = computed(() => route.params.locale || 'en')
const t = computed(() => copy[locale.value] || copy.en)
const categories = computed(() => [
  {
    title: t.value.faq.cat1Title,
    items: [
      { question: t.value.faq.cat1Q1, answer: t.value.faq.cat1A1 },
      { question: t.value.faq.cat1Q2, answer: t.value.faq.cat1A2 },
      { question: t.value.faq.cat1Q3, answer: t.value.faq.cat1A3 },
      { question: t.value.faq.cat1Q4, answer: t.value.faq.cat1A4 }
    ]
  },
  {
    title: t.value.faq.cat2Title,
    items: [
      { question: t.value.faq.cat2Q1, answer: t.value.faq.cat2A1 },
      { question: t.value.faq.cat2Q2, answer: t.value.faq.cat2A2 },
      { question: t.value.faq.cat2Q3, answer: t.value.faq.cat2A3 }
    ]
  },
  {
    title: t.value.faq.cat3Title,
    items: [
      { question: t.value.faq.cat3Q1, answer: t.value.faq.cat3A1 },
      { question: t.value.faq.cat3Q2, answer: t.value.faq.cat3A2 },
      { question: t.value.faq.cat3Q3, answer: t.value.faq.cat3A3 }
    ]
  },
  {
    title: t.value.faq.cat4Title,
    items: [
      { question: t.value.faq.cat4Q1, answer: t.value.faq.cat4A1 },
      { question: t.value.faq.cat4Q2, answer: t.value.faq.cat4A2 },
      { question: t.value.faq.cat4Q3, answer: t.value.faq.cat4A3 }
    ]
  }
])

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

function keyOf(categoryIndex, itemIndex) {
  return `${categoryIndex}-${itemIndex}`
}

function isOpen(categoryIndex, itemIndex) {
  return openKey.value === keyOf(categoryIndex, itemIndex)
}

function toggle(categoryIndex, itemIndex) {
  const key = keyOf(categoryIndex, itemIndex)
  openKey.value = openKey.value === key ? '' : key
}

const copy = {
  en: {
    common: { home: 'Home' },
    faq: {
      breadcrumb: 'FAQ',
      title: 'Frequently Asked Questions',
      subtitle: 'Find answers to your most important questions here',
      cat1Title: 'Products',
      cat1Q1: 'What safety certifications do Misicheng airflow products have?',
      cat1A1: 'Certification and test documents vary by model and target market. Common support includes CE, RoHS, motor test reports, and project documentation.',
      cat1Q2: 'Which product categories are available?',
      cat1A2: 'Misicheng covers air curtains, duct fans, air purifiers, air coolers, portable air conditioners, wall fans, stand fans, ceiling fans, exhaust fans, heaters, and more.',
      cat1Q3: 'Can I request samples before bulk purchase?',
      cat1A3: 'Yes. Submit the target category, model, quantity, and destination, and sales will confirm sample availability and freight.',
      cat1Q4: 'Do you support OEM or custom packaging?',
      cat1A4: 'Yes. OEM labels, carton marks, packaging artwork, and model configuration can be quoted after quantity and artwork requirements are confirmed.',
      cat2Title: 'Orders & Payment',
      cat2Q1: 'What payment methods are supported?',
      cat2A1: 'We support credit cards, PayPal, Alipay, WeChat Pay, Apple Pay, Google Pay, and other common methods depending on region.',
      cat2Q2: 'Can I modify my order after placing it?',
      cat2A2: 'If the order has not shipped, you can request modifications. After shipment, changes are not possible, but return or exchange support remains available.',
      cat2Q3: 'How can I check my order status?',
      cat2A3: 'Log in to your Misicheng account to view order status. After shipping, you will also receive tracking details by email.',
      cat3Title: 'Shipping',
      cat3Q1: 'How long does shipping take?',
      cat3A1: 'We usually ship within 1-2 business days after confirmation. Delivery time depends on destination and shipping method.',
      cat3Q2: 'How much is shipping?',
      cat3A2: 'Shipping is calculated based on destination, package weight, and selected logistics method.',
      cat3Q3: 'Do you ship internationally?',
      cat3A3: 'Yes, Misicheng ships internationally through DHL, FedEx, UPS, and other logistics services.',
      cat4Title: 'Returns & Refunds',
      cat4Q1: 'Can I return a product if I am not satisfied?',
      cat4A1: 'Yes. Misicheng offers a 30-day return policy for eligible unused products in original packaging.',
      cat4Q2: 'What if I receive a defective product?',
      cat4A2: 'Contact customer service within 7 days with product photos and order information. We will arrange replacement or refund support.',
      cat4Q3: 'How long does a refund take?',
      cat4A3: 'After the returned product is verified, refunds are usually processed within 3-5 business days.',
      ctaTitle: "Can't find your question?",
      ctaDesc: 'Our customer service team is always here to help',
      ctaButton: 'Contact Support'
    }
  },
  zh: {
    common: { home: '首页' },
    faq: {
      breadcrumb: '常见问题',
      title: '常见问题',
      subtitle: '在这里找到重要问题的答案',
      cat1Title: '产品',
      cat1Q1: 'Misicheng 空气设备有哪些安全认证？',
      cat1A1: '不同产品会依据品类和目标市场执行相应安全与质量标准。下单前可与销售确认具体认证要求。',
      cat1Q2: '如何选择合适的风量或风扇尺寸？',
      cat1A2: '选型取决于空间面积、目标风量、安装位置、管道长度、噪音要求和使用环境。提供场景后我们可以协助推荐型号。',
      cat1Q3: '批量采购前可以申请样品吗？',
      cat1A3: '可以。提交目标分类、型号、数量和目的地后，销售会确认样品和运费。',
      cat1Q4: '是否支持 OEM 或定制包装？',
      cat1A4: '支持。确认订单量、包装设计和标签需求后，可提供对应报价。',
      cat2Title: '订单与支付',
      cat2Q1: '支持哪些支付方式？',
      cat2A1: '支持信用卡、PayPal、支付宝、微信支付、Apple Pay、Google Pay 等常见支付方式，具体以地区为准。',
      cat2Q2: '下单后可以修改订单吗？',
      cat2A2: '如果订单尚未发货，可以申请修改；如果已经发货，则不能修改，但可按规则申请退换货。',
      cat2Q3: '如何查看订单状态？',
      cat2A3: '登录 Misicheng 账号后可查看订单状态。发货后也会通过邮件发送物流跟踪信息。',
      cat3Title: '配送',
      cat3Q1: '发货需要多久？',
      cat3A1: '通常在订单确认后 1-2 个工作日内发货，具体配送时间取决于目的地和物流方式。',
      cat3Q2: '运费是多少？',
      cat3A2: '运费会根据目的地、包裹重量和选择的物流方式计算。',
      cat3Q3: '支持国际配送吗？',
      cat3A3: '支持。Misicheng 可通过 DHL、FedEx、UPS 等物流服务发往多个国家和地区。',
      cat4Title: '退货与退款',
      cat4Q1: '不满意可以退货吗？',
      cat4A1: '可以。符合条件且保持原包装未使用的商品可申请 30 天退货。',
      cat4Q2: '收到有质量问题的商品怎么办？',
      cat4A2: '请在收货后 7 天内联系客服并提供照片和订单信息，我们会安排换货或退款支持。',
      cat4Q3: '退款需要多久？',
      cat4A3: '退回商品核验后，通常会在 3-5 个工作日内处理退款。',
      ctaTitle: '没有找到你的问题？',
      ctaDesc: '我们的客服团队随时为您提供帮助',
      ctaButton: '联系支持'
    }
  }
}
</script>

<style scoped>
.accordion-enter-active,
.accordion-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.accordion-enter-from,
.accordion-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
