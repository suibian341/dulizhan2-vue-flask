<template>
  <div>
    <section class="relative h-[480px] overflow-hidden md:h-[580px]">
      <img
        src="/images/banner-2.png"
        :alt="t.heroAlt"
        class="absolute inset-0 h-full w-full object-cover"
      />
      <div class="absolute inset-0 bg-gradient-to-r from-black/70 via-black/50 to-black/30"></div>
      <div class="absolute inset-0 flex items-center">
        <div class="mx-auto max-w-7xl px-4 lg:px-8">
          <h1 class="mb-4 text-4xl font-bold text-white md:text-6xl">{{ t.heroTitle }}</h1>
          <p class="max-w-2xl text-lg text-white/80 md:text-xl">{{ t.heroSubtitle }}</p>
        </div>
      </div>
    </section>

    <section
      v-for="(step, index) in steps"
      :key="step.num"
      class="py-16 md:py-24"
      :class="index % 2 === 0 ? 'bg-white' : 'bg-gray-50'"
    >
      <div class="mx-auto max-w-7xl px-4 lg:px-8">
        <div class="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
          <div class="relative aspect-[4/3] overflow-hidden rounded-2xl" :class="index % 2 !== 0 ? 'lg:order-2' : ''">
            <img :src="step.image" :alt="step.title" class="absolute inset-0 h-full w-full object-cover" />
          </div>

          <div :class="index % 2 !== 0 ? 'lg:order-1' : ''">
            <span class="bg-gradient-to-r from-sky-500 to-cyan-500 bg-clip-text text-4xl font-bold text-transparent md:text-6xl">
              {{ step.num }}
            </span>
            <div class="mt-4 mb-4 flex items-center gap-3">
              <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-sky-50">
                <component :is="step.icon" class="h-6 w-6 text-sky-500" />
              </div>
              <h2 class="text-3xl font-bold">{{ step.title }}</h2>
            </div>
            <p class="mb-6 text-lg leading-relaxed text-gray-600">{{ step.desc }}</p>
            <ul class="space-y-3">
              <li v-for="point in step.points" :key="point" class="flex items-center gap-3">
                <div class="flex h-6 w-6 items-center justify-center rounded-full bg-sky-100">
                  <Check class="h-3.5 w-3.5 text-sky-600 stroke-[3]" />
                </div>
                <span class="text-gray-700">{{ point }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <section class="bg-gradient-to-r from-sky-500 to-cyan-500 py-16 md:py-24">
      <div class="mx-auto max-w-7xl px-4 text-center lg:px-8">
        <h2 class="mb-12 text-3xl font-bold text-white md:text-4xl">{{ t.whyTitle }}</h2>
        <div class="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="item in advantages" :key="item.title" class="rounded-2xl bg-white/10 p-8 text-white backdrop-blur-sm">
            <component :is="item.icon" class="mx-auto mb-4 h-10 w-10" />
            <h3 class="mb-2 text-xl font-semibold">{{ item.title }}</h3>
            <p class="text-sm text-white/80">{{ item.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="py-16 text-center md:py-24">
      <div class="mx-auto max-w-2xl px-4">
        <h2 class="mb-4 text-3xl font-bold md:text-4xl">{{ t.ctaTitle }}</h2>
        <p class="mb-8 text-lg text-gray-600">{{ t.ctaSubtitle }}</p>
        <div class="flex flex-col justify-center gap-4 sm:flex-row">
          <RouterLink :to="localized('/contact')" class="gradient-bg inline-flex h-10 items-center justify-center rounded-full px-8 text-sm font-medium text-white transition-all">
            {{ t.ctaInquiry }}
          </RouterLink>
          <RouterLink :to="localized('/shop')" class="inline-flex h-10 items-center justify-center rounded-full border bg-background px-8 text-sm font-medium shadow-xs transition-all hover:bg-accent hover:text-accent-foreground">
            {{ t.ctaBrowse }}
          </RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import {
  Award,
  Check,
  Factory,
  FileText,
  Headphones,
  HeartHandshake,
  MessageCircle,
  Package,
  Shield,
  Truck
} from 'lucide-vue-next'

const route = useRoute()
const locale = computed(() => route.params.locale || 'en')
const t = computed(() => copy[locale.value] || copy.en)

const steps = computed(() => [
  {
    num: '01',
    title: t.value.step1Title,
    desc: t.value.step1Desc,
    points: [t.value.step1Point1, t.value.step1Point2, t.value.step1Point3],
    image: '/images/service/customer-service.jpg',
    icon: MessageCircle
  },
  {
    num: '02',
    title: t.value.step2Title,
    desc: t.value.step2Desc,
    points: [t.value.step2Point1, t.value.step2Point2, t.value.step2Point3],
    image: '/images/service/pricing-quote.jpg',
    icon: FileText
  },
  {
    num: '03',
    title: t.value.step3Title,
    desc: t.value.step3Desc,
    points: [t.value.step3Point1, t.value.step3Point2, t.value.step3Point3],
    image: '/images/service/manufacturing.jpg',
    icon: Factory
  },
  {
    num: '04',
    title: t.value.step4Title,
    desc: t.value.step4Desc,
    points: [t.value.step4Point1, t.value.step4Point2, t.value.step4Point3],
    image: '/images/service/logistics.jpg',
    icon: Package
  },
  {
    num: '05',
    title: t.value.step5Title,
    desc: t.value.step5Desc,
    points: [t.value.step5Point1, t.value.step5Point2, t.value.step5Point3],
    image: '/images/service/aftersales.jpg',
    icon: HeartHandshake
  }
])

const advantages = computed(() => [
  { icon: Headphones, title: t.value.adv1Title, desc: t.value.adv1Desc },
  { icon: Shield, title: t.value.adv2Title, desc: t.value.adv2Desc },
  { icon: Truck, title: t.value.adv3Title, desc: t.value.adv3Desc },
  { icon: Award, title: t.value.adv4Title, desc: t.value.adv4Desc }
])

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

const copy = {
  en: {
    heroTitle: 'One-Stop Smart Power Solutions',
    heroSubtitle: 'From product consultation to after-sales service, Misicheng supports power strips, travel adapters, USB-C charging, and surge protection sourcing',
    heroAlt: 'One-stop service',
    step1Title: 'Product Consultation',
    step1Desc: 'Our professional team will recommend suitable power strips, extension sockets, travel adapters, USB-C charging stations, and surge protectors based on plug standard, outlet count, cable length, certifications, packaging, and budget.',
    step1Point1: 'Dedicated one-on-one consultant',
    step1Point2: 'Free sample shipping',
    step1Point3: 'Detailed technical specifications',
    step2Title: 'Custom Quote',
    step2Desc: 'Based on your purchase quantity and customization needs, we offer highly competitive pricing. OEM/ODM customization supported with flexible minimum order quantities.',
    step2Point1: 'Tiered pricing discounts',
    step2Point2: 'OEM/ODM customization support',
    step2Point3: 'Multiple trade terms available',
    step3Title: 'Manufacturing',
    step3Desc: 'Production follows strict quality checkpoints for conductive parts, cable specification, flame-retardant housing, assembly stability, electrical testing, and packaging before shipment.',
    step3Point1: 'ISO 9001 certified factory',
    step3Point2: 'Electrical and assembly testing',
    step3Point3: '100% factory inspection',
    step4Title: 'Logistics',
    step4Desc: 'Deep partnerships with DHL, FedEx, UPS and other international logistics providers, offering sea freight, air freight, and express delivery covering 50+ countries and regions worldwide.',
    step4Point1: 'Delivery to 50+ countries',
    step4Point2: 'Sea/air/express options',
    step4Point3: 'Real-time tracking',
    step5Title: 'After-Sales Service',
    step5Desc: '24/7 multilingual customer service team on standby, free replacement within 12-month warranty period, giving you complete peace of mind.',
    step5Point1: '24/7 online support',
    step5Point2: '12-month warranty',
    step5Point3: 'Free replacement service',
    whyTitle: 'Why Choose Misicheng',
    adv1Title: 'Expert Team',
    adv1Desc: 'Professional consultants with 10+ years of industry experience',
    adv2Title: 'Quality Assurance',
    adv2Desc: 'International certifications, 100% factory inspection',
    adv3Title: 'Global Delivery',
    adv3Desc: 'Covering 50+ countries with multiple logistics solutions',
    adv4Title: 'Worry-Free After-Sales',
    adv4Desc: '12-month warranty, 24/7 support',
    ctaTitle: 'Ready to Get Started?',
    ctaSubtitle: 'Contact us now for a customized product solution and quote',
    ctaInquiry: 'Inquire Now',
    ctaBrowse: 'Browse Products'
  },
  zh: {
    heroTitle: '一站式智能电力解决方案',
    heroSubtitle: '从产品咨询到售后服务，Misicheng 为排插、转换器、USB-C 快充和浪涌保护产品采购提供全流程支持',
    heroAlt: '一站式服务',
    step1Title: '产品咨询',
    step1Desc: '专业团队会根据插头标准、插位数量、线长、认证、包装和预算，推荐合适的排插、插线板、旅行转换器、USB-C 快充站和浪涌保护产品。',
    step1Point1: '专属一对一顾问',
    step1Point2: '免费样品寄送',
    step1Point3: '详细技术规格说明',
    step2Title: '定制报价',
    step2Desc: '根据采购数量和定制需求，我们提供具有竞争力的价格，支持 OEM/ODM 定制和灵活起订量。',
    step2Point1: '阶梯价格优惠',
    step2Point2: '支持 OEM/ODM 定制',
    step2Point3: '多种贸易条款可选',
    step3Title: '生产制造',
    step3Desc: '生产流程会围绕导电件、线材规格、阻燃外壳、装配稳定性、电气测试和包装进行多环节检查。',
    step3Point1: 'ISO 9001 认证工厂',
    step3Point2: '电气与装配测试',
    step3Point3: '100% 出厂检测',
    step4Title: '物流配送',
    step4Desc: '与 DHL、FedEx、UPS 等国际物流服务深度合作，提供海运、空运、快递等多种方案。',
    step4Point1: '配送覆盖 50+ 国家',
    step4Point2: '海运/空运/快递可选',
    step4Point3: '实时物流跟踪',
    step5Title: '售后服务',
    step5Desc: '多语言客服团队 24/7 在线，12 个月质保期内支持免费更换，让采购更安心。',
    step5Point1: '24/7 在线支持',
    step5Point2: '12 个月质保',
    step5Point3: '免费更换服务',
    whyTitle: '为什么选择 Misicheng',
    adv1Title: '专家团队',
    adv1Desc: '拥有 10 年以上行业经验的专业顾问',
    adv2Title: '品质保证',
    adv2Desc: '国际认证，100% 出厂检测',
    adv3Title: '全球配送',
    adv3Desc: '覆盖 50+ 国家，提供多种物流方案',
    adv4Title: '无忧售后',
    adv4Desc: '12 个月质保，24/7 支持',
    ctaTitle: '准备开始了吗？',
    ctaSubtitle: '现在联系我们，获取定制产品方案和报价',
    ctaInquiry: '立即询价',
    ctaBrowse: '浏览产品'
  }
}
</script>
