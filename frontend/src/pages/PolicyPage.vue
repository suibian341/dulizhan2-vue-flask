<template>
  <div class="mx-auto max-w-4xl px-4 pt-24 py-12 lg:px-8">
    <nav class="mb-8 flex items-center gap-2 text-sm text-muted-foreground">
      <RouterLink :to="localized('/')" class="transition-colors hover:text-foreground">
        {{ text.home }}
      </RouterLink>
      <ChevronRight class="h-3.5 w-3.5" />
      <span class="font-medium text-foreground">{{ page.breadcrumb }}</span>
    </nav>

    <div class="mb-12 text-center">
      <h1 class="text-4xl font-bold tracking-tight">{{ page.title }}</h1>
      <p class="mt-4 text-lg text-muted-foreground">
        {{ page.subtitle || page.lastUpdated }}
      </p>
    </div>

    <template v-if="page.kind === 'shipping'">
      <div class="mb-12 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div
          v-for="item in page.highlights"
          :key="item.title"
          class="flex flex-col items-center rounded-xl border p-6 text-center"
        >
          <component :is="item.icon" class="mb-3 h-8 w-8 text-primary" />
          <h3 class="font-medium">{{ item.title }}</h3>
          <p class="mt-1 text-sm text-muted-foreground">{{ item.desc }}</p>
        </div>
      </div>

      <div class="space-y-10">
        <section>
          <h2 class="mb-4 text-2xl font-semibold">{{ page.domestic.title }}</h2>
          <div class="space-y-4 rounded-xl border p-6 leading-relaxed text-muted-foreground">
            <p v-for="row in page.domestic.rows" :key="row.label">
              <strong class="text-foreground">{{ row.label }}</strong>
              {{ row.value }}
            </p>
            <p><strong class="text-foreground">{{ page.domestic.rateLabel }}</strong></p>
            <PolicyTable :table="page.domestic.table" />
            <p>
              <strong class="text-foreground">{{ page.domestic.courierLabel }}</strong>
              {{ page.domestic.courierValue }}
            </p>
          </div>
        </section>

        <div class="h-px bg-border"></div>

        <section>
          <h2 class="mb-4 text-2xl font-semibold">{{ page.international.title }}</h2>
          <div class="space-y-4 rounded-xl border p-6 leading-relaxed text-muted-foreground">
            <p>
              <strong class="text-foreground">{{ page.international.coverageLabel }}</strong>
              {{ page.international.coverageValue }}
            </p>
            <p><strong class="text-foreground">{{ page.international.deliveryLabel }}</strong></p>
            <PolicyTable :table="page.international.table" />
            <p>
              <strong class="text-foreground">{{ page.international.courierLabel }}</strong>
              {{ page.international.courierValue }}
            </p>
          </div>
        </section>

        <div class="h-px bg-border"></div>

        <section>
          <h2 class="mb-4 text-2xl font-semibold">{{ page.tracking.title }}</h2>
          <div class="space-y-4 rounded-xl border p-6 leading-relaxed text-muted-foreground">
            <p>{{ page.tracking.intro }}</p>
            <ul class="list-disc space-y-2 pl-6">
              <li v-for="item in page.tracking.items" :key="item">{{ item }}</li>
            </ul>
          </div>
        </section>

        <div class="h-px bg-border"></div>

        <section>
          <div class="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-6">
            <AlertCircle class="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
            <div class="space-y-2 text-sm text-amber-800">
              <p class="font-medium">{{ page.notice.title }}</p>
              <ul class="list-disc space-y-1 pl-4">
                <li v-for="item in page.notice.items" :key="item">{{ item }}</li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    </template>

    <template v-else-if="page.kind === 'returns'">
      <div class="mb-12 grid grid-cols-1 gap-6 sm:grid-cols-3">
        <div
          v-for="item in page.highlights"
          :key="item.title"
          class="flex flex-col items-center rounded-xl border p-6 text-center"
        >
          <component :is="item.icon" class="mb-3 h-8 w-8 text-primary" />
          <h3 class="font-medium">{{ item.title }}</h3>
          <p class="mt-1 text-sm text-muted-foreground">{{ item.desc }}</p>
        </div>
      </div>

      <div class="space-y-10">
        <section>
          <h2 class="mb-4 text-2xl font-semibold">{{ page.returnPolicy.title }}</h2>
          <div class="space-y-4 rounded-xl border p-6 leading-relaxed text-muted-foreground">
            <p>{{ page.returnPolicy.intro }}</p>
            <div class="space-y-3">
              <div v-for="item in page.returnPolicy.items" :key="item" class="flex items-start gap-3">
                <CheckCircle class="mt-0.5 h-4 w-4 shrink-0 text-green-500" />
                <span>{{ item }}</span>
              </div>
            </div>
          </div>
        </section>

        <div class="h-px bg-border"></div>

        <section>
          <h2 class="mb-4 text-2xl font-semibold">{{ page.nonReturnable.title }}</h2>
          <div class="space-y-3 rounded-xl border p-6 leading-relaxed text-muted-foreground">
            <div v-for="item in page.nonReturnable.items" :key="item" class="flex items-start gap-3">
              <XCircle class="mt-0.5 h-4 w-4 shrink-0 text-red-500" />
              <span>{{ item }}</span>
            </div>
          </div>
        </section>

        <div class="h-px bg-border"></div>

        <section>
          <h2 class="mb-4 text-2xl font-semibold">{{ page.exchange.title }}</h2>
          <div class="space-y-4 rounded-xl border p-6 leading-relaxed text-muted-foreground">
            <p>{{ page.exchange.intro }}</p>
            <ul class="list-disc space-y-2 pl-6">
              <li v-for="item in page.exchange.items" :key="item">{{ item }}</li>
            </ul>
            <p>{{ page.exchange.note }}</p>
          </div>
        </section>

        <div class="h-px bg-border"></div>

        <section>
          <h2 class="mb-4 text-2xl font-semibold">{{ page.refund.title }}</h2>
          <div class="space-y-4 rounded-xl border p-6 leading-relaxed text-muted-foreground">
            <p>{{ page.refund.intro }}</p>
            <PolicyTable :table="page.refund.table" />
          </div>
        </section>

        <div class="h-px bg-border"></div>

        <section>
          <h2 class="mb-4 text-2xl font-semibold">{{ page.process.title }}</h2>
          <div class="space-y-6 rounded-xl border p-6 leading-relaxed text-muted-foreground">
            <div v-for="(step, index) in page.process.steps" :key="step.title" class="flex gap-4">
              <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-bold text-primary-foreground">
                {{ index + 1 }}
              </div>
              <div>
                <h3 class="font-medium text-foreground">{{ step.title }}</h3>
                <p class="mt-1">{{ step.desc }}</p>
              </div>
            </div>
          </div>
        </section>

        <section>
          <div class="flex items-start gap-3 rounded-xl border border-blue-200 bg-blue-50 p-6">
            <AlertCircle class="mt-0.5 h-5 w-5 shrink-0 text-blue-600" />
            <div class="text-sm text-blue-800">
              <p class="font-medium">{{ page.contact.title }}</p>
              <p class="mt-1">{{ page.contact.desc }}</p>
            </div>
          </div>
        </section>
      </div>
    </template>

    <div v-else class="space-y-8" :class="page.kind === 'privacy' ? 'prose-custom' : ''">
      <section>
        <p class="leading-relaxed text-muted-foreground">{{ page.intro }}</p>
      </section>

      <template v-for="section in page.sections" :key="section.title">
        <div class="h-px bg-border"></div>
        <section>
          <h2 class="mb-4 text-2xl font-semibold">{{ section.title }}</h2>
          <div class="space-y-4 leading-relaxed text-muted-foreground">
            <template v-for="block in section.blocks" :key="block.key">
              <p v-if="block.type === 'p'">{{ block.text }}</p>

              <h3 v-else-if="block.type === 'h3'" class="text-lg font-medium text-foreground">
                {{ block.text }}
              </h3>

              <ul
                v-else-if="block.type === 'ul'"
                class="space-y-2"
                :class="block.plain ? 'list-none' : 'list-disc pl-6'"
              >
                <li v-for="item in block.items" :key="item.text || item">
                  <strong v-if="item.label" class="text-foreground">{{ item.label }}</strong>
                  {{ item.text || item }}
                </li>
              </ul>

              <p v-else-if="block.type === 'linkP'">
                {{ block.prefix }}
                <RouterLink :to="localized(block.href)" class="text-primary hover:underline">
                  {{ block.linkText }}
                </RouterLink>
                {{ block.suffix }}
              </p>
            </template>
          </div>
        </section>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, defineComponent, h } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import {
  AlertCircle,
  CheckCircle,
  ChevronRight,
  Clock,
  Globe,
  Package,
  RotateCcw,
  Truck,
  XCircle
} from 'lucide-vue-next'

const PolicyTable = defineComponent({
  name: 'PolicyTable',
  props: {
    table: { type: Object, required: true }
  },
  setup(props) {
    return () => h('div', { class: 'overflow-x-auto overflow-hidden rounded-lg border' }, [
      h('table', { class: 'w-full text-sm' }, [
        h('thead', [
          h('tr', { class: 'border-b bg-gray-50' },
            props.table.head.map(head => h('th', { class: 'px-4 py-3 text-left font-medium text-foreground' }, head))
          )
        ]),
        h('tbody',
          props.table.rows.map(row => h('tr', { class: 'border-b last:border-b-0' },
            row.cells.map((cell, index) => h('td', {
              class: ['px-4 py-3', row.highlightIndex === index ? row.highlightClass : '']
            }, cell))
          ))
        )
      ])
    ])
  }
})

const route = useRoute()
const locale = computed(() => route.params.locale || 'en')
const slug = computed(() => route.path.replace(/^\/(en|zh|ja|ko|fr|de|es|ar)\//, '').split('/')[0])
const text = computed(() => copy[locale.value] || copy.en)
const page = computed(() => text.value.pages[slug.value] || text.value.pages.privacy)

function localized(path) {
  return path === '/' ? `/${locale.value}` : `/${locale.value}${path}`
}

function row(cells, options = {}) {
  return { cells, ...options }
}

const copy = {
  en: {
    home: 'Home',
    pages: {
      shipping: {
        kind: 'shipping',
        breadcrumb: 'Shipping',
        title: 'Shipping & Delivery',
        subtitle: "Learn about Misicheng's shipping policies and logistics information",
        highlights: [
          { icon: Truck, title: 'Free Shipping', desc: 'Domestic orders over 99 yuan' },
          { icon: Clock, title: 'Fast Dispatch', desc: 'Within 1-2 business days' },
          { icon: Globe, title: 'Global Delivery', desc: 'Covering 30+ countries' },
          { icon: Package, title: 'Package Tracking', desc: 'Full tracking available' }
        ],
        domestic: {
          title: 'Domestic Shipping',
          rows: [
            { label: 'Dispatch Time:', value: ' Orders ship within 1-2 business days after confirmation (may extend to 3-5 business days during major promotions).' },
            { label: 'Delivery Time:', value: ' Standard express 2-5 business days, remote areas may require an additional 1-3 days.' }
          ],
          rateLabel: 'Shipping Rates:',
          table: {
            head: ['Order Amount', 'Shipping Fee'],
            rows: [
              row(['99 yuan and above', 'Free Shipping'], { highlightIndex: 1, highlightClass: 'text-green-600 font-medium' }),
              row(['50 - 98 yuan', '8 yuan']),
              row(['Under 50 yuan', '12 yuan'])
            ]
          },
          courierLabel: 'Courier Partners:',
          courierValue: ' SF Express, ZTO Express, YTO Express, Yunda Express. SF Express is used by default. To specify a courier, please add a note when placing your order.'
        },
        international: {
          title: 'International Shipping',
          coverageLabel: 'Coverage:',
          coverageValue: ' Misicheng ships to over 30 countries and regions worldwide, including the US, Canada, UK, Germany, France, Japan, South Korea, Australia, Singapore, and more.',
          deliveryLabel: 'Delivery Time:',
          table: {
            head: ['Destination', 'Estimated Time', 'Shipping Fee'],
            rows: [
              row(['Asia', '5-10 business days', 'Calculated by weight']),
              row(['North America', '7-15 business days', 'Calculated by weight']),
              row(['Europe', '7-15 business days', 'Calculated by weight']),
              row(['Other Regions', '10-20 business days', 'Calculated by weight'])
            ]
          },
          courierLabel: 'Logistics Partners:',
          courierValue: ' DHL, FedEx, UPS. International shipping fees are automatically calculated at checkout based on destination and package weight.'
        },
        tracking: {
          title: 'Package Tracking',
          intro: 'After your order ships, you will receive an email with a tracking number. You can track your package through:',
          items: [
            'Log in to your Misicheng account and check logistics status in "My Orders"',
            "Use the tracking number from the email to check on the courier's official website",
            'Contact our customer service team for logistics information'
          ]
        },
        notice: {
          title: 'Important Notes',
          items: [
            'The delivery times above are estimates. Actual delivery may vary due to weather, holidays, and other factors.',
            'International orders may be subject to import duties and taxes at the destination country, which are the responsibility of the recipient.',
            'If there are any special circumstances causing delivery delays, we will notify you promptly via email.',
            'For any shipping questions, please contact our customer service team: anna@gzjixing-tech.com'
          ]
        }
      },
      returns: {
        kind: 'returns',
        breadcrumb: 'Return Policy',
        title: 'Return Policy',
        subtitle: 'Misicheng is committed to providing you with a satisfying shopping experience',
        highlights: [
          { icon: RotateCcw, title: '30-Day Returns', desc: 'Within 30 days of receiving your order' },
          { icon: CheckCircle, title: '18-Month Warranty', desc: 'Free repair for non-human damage' },
          { icon: RotateCcw, title: 'Free Return Shipping', desc: 'Free shipping for quality issues' }
        ],
        returnPolicy: {
          title: 'Return Policy',
          intro: 'Within 30 days of receiving your product, you may request a no-questions-asked return. Returns must meet the following conditions:',
          items: [
            'Product is in original packaging, unopened or opened without affecting resale',
            'Product and accessories are complete, nothing missing',
            'No human-caused damage or signs of use',
            'Valid order number or proof of purchase provided'
          ]
        },
        nonReturnable: {
          title: 'Non-Returnable Items',
          items: [
            'Products past the 30-day return period',
            'Products damaged due to human causes (e.g., drops, water damage, unauthorized disassembly)',
            'Used products that affect resale',
            'Gifts and promotional items (marked as "non-returnable")',
            'Products without valid proof of purchase'
          ]
        },
        exchange: {
          title: 'Exchange Policy',
          intro: 'If your product has any of the following issues, you can apply for a free exchange within 7 days of delivery:',
          items: [
            'Product has quality defects or functional failures',
            'Product received does not match the order (wrong model, color, or quantity)',
            'Product was damaged during shipping'
          ],
          note: 'Replacement products will be shipped within 3 business days after receiving and inspecting the returned item.'
        },
        refund: {
          title: 'Refund Information',
          intro: 'Refunds will be processed after we receive and inspect the returned product:',
          table: {
            head: ['Payment Method', 'Refund Time'],
            rows: [
              row(['Alipay / WeChat Pay', '1-3 business days']),
              row(['Credit / Debit Card', '3-5 business days']),
              row(['PayPal', '3-5 business days']),
              row(['Apple Pay / Google Pay', '3-5 business days'])
            ]
          }
        },
        process: {
          title: 'Return & Exchange Process',
          steps: [
            { title: 'Submit Request', desc: 'Log in to your account, find the order in "My Orders", click "Request Return/Exchange" and fill in the reason.' },
            { title: 'Review & Confirm', desc: 'Our customer service team will review your request within 1 business day and notify you of the result via email.' },
            { title: 'Ship the Product', desc: 'Once approved, ship the product to the return address provided in the email. Shipping costs for quality issues are covered by us.' },
            { title: 'Refund / Exchange', desc: 'After receiving and inspecting the returned product, we will complete the refund or reship within the specified timeframe.' }
          ]
        },
        contact: {
          title: 'Need Help?',
          desc: 'For any return or exchange questions, please contact our customer service team: anna@gzjixing-tech.com or call +86 13247309378 / +86 13288805588 (Mon-Fri 9:00-18:00).'
        }
      },
      privacy: {
        kind: 'privacy',
        breadcrumb: 'Privacy Policy',
        title: 'Privacy Policy',
        lastUpdated: 'Last updated: January 1, 2025',
        intro: 'Misicheng (hereinafter referred to as "we") takes your privacy very seriously. This Privacy Policy is intended to explain how we collect, use, store, and protect your personal information. Please read this policy carefully before using our services.',
        sections: [
          {
            title: '1. Information Collection',
            blocks: [
              { key: 'intro', type: 'p', text: 'We may collect the following types of personal information:' },
              { key: 'sub1', type: 'h3', text: '1.1 Information You Provide' },
              { key: 'ul1', type: 'ul', items: ['Account registration: name, email, phone number, password', 'Order information: shipping address, contact number, payment information', 'Customer service records: communications with our support team', 'Feedback: product reviews, survey responses'] },
              { key: 'sub2', type: 'h3', text: '1.2 Automatically Collected Information' },
              { key: 'ul2', type: 'ul', items: ['Device information: device model, operating system, browser type', 'Log information: IP address, access time, pages viewed, click records', 'Information collected through cookies and similar technologies', 'Location information (only with your authorization)'] }
            ]
          },
          {
            title: '2. Use of Information',
            blocks: [
              { key: 'intro', type: 'p', text: 'Personal information we collect will be used for the following purposes:' },
              { key: 'items', type: 'ul', items: [
                { label: 'Service Delivery:', text: ' Processing orders, delivering products, providing after-sales service' },
                { label: 'Account Management:', text: ' Creating and managing your user account' },
                { label: 'Customer Communication:', text: ' Sending order notifications, shipping updates, service change notices' },
                { label: 'Service Improvement:', text: ' Analyzing user behavior to optimize products and service experience' },
                { label: 'Marketing:', text: ' With your consent, sending promotional information and new product recommendations' },
                { label: 'Security:', text: ' Preventing fraud and protecting account security' },
                { label: 'Legal Compliance:', text: ' Complying with applicable laws and regulations' }
              ] }
            ]
          },
          {
            title: '3. Information Sharing',
            blocks: [
              { key: 'intro', type: 'p', text: 'We will not sell your personal information. We may share your information with third parties only in the following circumstances:' },
              { key: 'items', type: 'ul', items: [
                { label: 'Service Providers:', text: ' Sharing necessary order information with logistics companies, payment processors, and other partners to complete services' },
                { label: 'Legal Requirements:', text: ' Disclosing information as required by laws, legal processes, or government requests' },
                { label: 'Business Transfers:', text: ' In the event of a merger, acquisition, or asset sale, your information may be transferred as part of business assets' },
                { label: 'Your Consent:', text: ' Sharing with third parties with your explicit consent' }
              ] }
            ]
          },
          {
            title: '4. Information Security',
            blocks: [
              { key: 'intro', type: 'p', text: 'We take multiple security measures to protect your personal information:' },
              { key: 'items', type: 'ul', items: ['Using SSL/TLS encryption to protect data transmission', 'Encrypting sensitive information (such as payment details) for storage', 'Implementing strict access controls, only authorized personnel can access personal information', 'Conducting regular security audits and vulnerability scans', 'Maintaining a data breach emergency response plan'] }
            ]
          },
          {
            title: '5. Cookie Policy',
            blocks: [
              { key: 'intro', type: 'p', text: 'We use cookies and similar technologies to:' },
              { key: 'items', type: 'ul', items: ['Remember your login status and preferences', 'Analyze website traffic and user behavior', 'Provide personalized shopping experiences', 'Deliver relevant advertising content'] },
              { key: 'note', type: 'p', text: 'You can manage or delete cookies through your browser settings. Please note that disabling cookies may affect some website functionality.' }
            ]
          },
          {
            title: '6. Your Rights',
            blocks: [
              { key: 'intro', type: 'p', text: 'Under applicable data protection laws, you have the following rights:' },
              { key: 'items', type: 'ul', items: [
                { label: 'Right of Access:', text: ' You have the right to access your personal information held by us' },
                { label: 'Right of Rectification:', text: ' You have the right to request correction of inaccurate personal information' },
                { label: 'Right of Erasure:', text: ' You have the right to request deletion of your personal information' },
                { label: 'Right to Restrict Processing:', text: ' You have the right to request restriction of processing of your personal information' },
                { label: 'Right to Data Portability:', text: ' You have the right to obtain a copy of your personal information' },
                { label: 'Right to Withdraw Consent:', text: ' You have the right to withdraw your consent to information processing at any time' }
              ] },
              { key: 'contact', type: 'p', text: 'To exercise these rights, please contact us at anna@gzjixing-tech.com.' }
            ]
          },
          { title: '7. Protection of Minors', blocks: [{ key: 'p', type: 'p', text: 'Our services are not intended for minors under 16 years of age. We do not knowingly collect personal information from minors. If you discover that we have inadvertently collected information from a minor, please contact us immediately and we will promptly delete the relevant information.' }] },
          { title: '8. Policy Updates', blocks: [{ key: 'p', type: 'p', text: 'We may update this Privacy Policy from time to time. Updated policies will be posted on this page with an updated "Last Updated" date. For significant changes, we will notify you via email or website notification. We recommend that you review this policy periodically for the latest information.' }] },
          {
            title: '9. Contact Us',
            blocks: [
              { key: 'intro', type: 'p', text: 'If you have any questions or suggestions about this Privacy Policy, please contact us through:' },
              { key: 'items', type: 'ul', plain: true, items: ['Email: anna@gzjixing-tech.com', 'Customer Service: +86 13247309378 / +86 13288805588', 'Address: 8F, Building B, TCL Xitian Science Park, Huangpu District, Guangzhou, Guangdong, China'] }
            ]
          }
        ]
      },
      terms: {
        kind: 'terms',
        breadcrumb: 'Terms of Service',
        title: 'Terms of Service',
        lastUpdated: 'Last updated: January 1, 2025',
        intro: 'Welcome to the Misicheng website and related services (hereinafter referred to as "the Service"). Please carefully read the following Terms of Service before using the Service. By using the Service, you agree to be bound by these Terms. If you do not agree to any part of these Terms, please do not use the Service.',
        sections: [
          {
            title: '1. Service Description',
            blocks: [
              { key: 'intro', type: 'p', text: 'Misicheng provides online shopping services for ventilation, cooling, air purification, and heating equipment through this website and related services, including but not limited to:' },
              { key: 'items', type: 'ul', items: ['Display and sale of air curtains, duct fans, air purifiers, air coolers, fans, heaters, and related products', 'User account registration and management', 'Order processing and logistics delivery', 'After-sales service and customer support', 'Product information and blog content'] }
            ]
          },
          {
            title: '2. User Accounts',
            blocks: [
              { key: 'sub1', type: 'h3', text: '2.1 Account Registration' },
              { key: 'p1', type: 'p', text: 'Some features of the Service require account registration. When registering, you must provide true, accurate, and complete personal information, and update it promptly when changes occur.' },
              { key: 'sub2', type: 'h3', text: '2.2 Account Security' },
              { key: 'p2', type: 'p', text: 'You are responsible for safeguarding your account password and for all activities conducted through your account. If you discover unauthorized use of your account, please notify us immediately.' },
              { key: 'sub3', type: 'h3', text: '2.3 Account Termination' },
              { key: 'p3', type: 'p', text: "We reserve the right to suspend or terminate your account in the following circumstances: violation of these Terms, providing false information, engaging in fraudulent behavior, or other actions that harm Misicheng or other users' interests." }
            ]
          },
          {
            title: '3. Products & Orders',
            blocks: [
              { key: 'sub1', type: 'h3', text: '3.1 Product Information' },
              { key: 'p1', type: 'p', text: 'We strive to ensure that product information displayed on the website (including descriptions, images, prices, etc.) is accurate. However, due to technical limitations, product images may differ slightly from actual products. We reserve the right to correct any errors in product information.' },
              { key: 'sub2', type: 'h3', text: '3.2 Pricing & Promotions' },
              { key: 'p2', type: 'p', text: 'All product prices are as displayed on the website and may be adjusted at any time. Promotional activities have specific time and condition restrictions as described on the promotion page. Prices do not include potential import duties and taxes.' },
              { key: 'sub3', type: 'h3', text: '3.3 Order Confirmation' },
              { key: 'p3', type: 'p', text: 'After you submit an order, we will confirm the order information via email. The sending of the order confirmation email constitutes our acceptance of the order. We reserve the right to cancel orders due to insufficient stock, pricing errors, or other reasons.' }
            ]
          },
          { title: '4. Payment Terms', blocks: [{ key: 'p', type: 'p', text: 'You agree to pay the product price and related shipping fees as displayed at the time of order confirmation. All payments are processed through third-party payment service providers; we do not directly store your payment card information. If a refund is needed after payment, it will be handled according to our Return Policy.' }] },
          { title: '5. Shipping & Delivery', blocks: [{ key: 'p', type: 'linkP', prefix: 'We will arrange shipment to the delivery address you provide. Delivery times are estimates and may be delayed due to force majeure factors. Risk of the goods transfers to you upon delivery to the carrier. For detailed shipping policies, please refer to our ', href: '/shipping', linkText: 'Shipping & Delivery', suffix: ' page.' }] },
          { title: '6. Return & Exchange Policy', blocks: [{ key: 'p', type: 'linkP', prefix: 'We offer 30-day no-questions-asked returns and 18-month warranty service. For detailed return and exchange conditions and procedures, please refer to our ', href: '/returns', linkText: 'Return Policy', suffix: ' page.' }] },
          { title: '7. Intellectual Property', blocks: [{ key: 'p1', type: 'p', text: 'All content on this website, including but not limited to text, images, graphics, logos, button icons, audio, video, software, and their arrangement, is the property of Misicheng or its content providers and is protected by copyright law and international copyright treaties.' }, { key: 'p2', type: 'p', text: 'Without our written permission, you may not copy, modify, distribute, display, transmit, or otherwise use any content on this website. The Misicheng name, logo, and related trademarks are our registered trademarks and may not be used without authorization.' }] },
          { title: '8. User Conduct', blocks: [{ key: 'intro', type: 'p', text: 'When using the Service, you agree not to:' }, { key: 'items', type: 'ul', items: ['Violate any applicable laws and regulations', "Infringe on others' intellectual property or other legal rights", 'Publish false, misleading, or fraudulent information', 'Distribute malware, viruses, or other harmful code', 'Interfere with or disrupt the normal operation of this website', "Access the website's systems or data without authorization", 'Use the Service for any commercial purpose (other than normal shopping)'] }] },
          { title: '9. Disclaimer', blocks: [{ key: 'p1', type: 'p', text: 'The Service is provided "as is". To the maximum extent permitted by law, Misicheng makes no express or implied warranties regarding the suitability, reliability, availability, timeliness, or accuracy of the Service.' }, { key: 'p2', type: 'p', text: 'Misicheng shall not be liable for any direct, indirect, incidental, special, or consequential damages arising from the use or inability to use the Service, even if we have been advised of the possibility of such damages.' }] },
          { title: '10. Modification of Terms', blocks: [{ key: 'p', type: 'p', text: 'We reserve the right to modify these Terms at any time. Modified terms will be posted on this page with an updated "Last Updated" date. Continued use of the Service constitutes acceptance of the modified terms. For significant changes, we will notify you via email or website notification.' }] },
          { title: '11. Governing Law & Dispute Resolution', blocks: [{ key: 'p', type: 'p', text: "These Terms are governed by the laws of the People's Republic of China. Any disputes arising from or related to these Terms shall first be resolved through friendly negotiation. If negotiation fails, either party may file a lawsuit with the competent people's court in the jurisdiction where Misicheng is located." }] },
          { title: '12. Contact Information', blocks: [{ key: 'intro', type: 'p', text: 'If you have any questions about these Terms of Service, please contact us through:' }, { key: 'items', type: 'ul', plain: true, items: ['Email: anna@gzjixing-tech.com', 'Customer Service: +86 13247309378 / +86 13288805588', 'Address: 8F, Building B, TCL Xitian Science Park, Huangpu District, Guangzhou, Guangdong, China'] }] }
        ]
      }
    }
  },
  zh: {
    home: '首页',
    pages: {
      shipping: {
        kind: 'shipping',
        breadcrumb: '物流配送',
        title: '物流配送',
        subtitle: '了解 Misicheng 的配送政策和物流信息',
        highlights: [
          { icon: Truck, title: '免费配送', desc: '国内订单满 99 元' },
          { icon: Clock, title: '快速发货', desc: '1-2 个工作日内' },
          { icon: Globe, title: '全球配送', desc: '覆盖 30+ 个国家' },
          { icon: Package, title: '包裹追踪', desc: '全程物流追踪' }
        ],
        domestic: {
          title: '国内配送',
          rows: [
            { label: '发货时间：', value: '订单确认后 1-2 个工作日内发货（大促期间可能延长至 3-5 个工作日）。' },
            { label: '配送时效：', value: '标准快递 2-5 个工作日，偏远地区可能额外增加 1-3 天。' }
          ],
          rateLabel: '运费标准：',
          table: {
            head: ['订单金额', '运费'],
            rows: [
              row(['99 元及以上', '免费配送'], { highlightIndex: 1, highlightClass: 'text-green-600 font-medium' }),
              row(['50 - 98 元', '8 元']),
              row(['50 元以下', '12 元'])
            ]
          },
          courierLabel: '合作快递：',
          courierValue: '顺丰速运、中通快递、圆通速递、韵达快递。默认使用顺丰速运，如需指定快递请在下单时备注。'
        },
        international: {
          title: '国际配送',
          coverageLabel: '配送范围：',
          coverageValue: 'Misicheng 支持全球 30 多个国家和地区的配送服务，包括美国、加拿大、英国、德国、法国、日本、韩国、澳大利亚、新加坡等。',
          deliveryLabel: '配送时效：',
          table: {
            head: ['目的地', '预计时效', '运费'],
            rows: [
              row(['亚洲地区', '5-10 个工作日', '按重量计算']),
              row(['北美地区', '7-15 个工作日', '按重量计算']),
              row(['欧洲地区', '7-15 个工作日', '按重量计算']),
              row(['其他地区', '10-20 个工作日', '按重量计算'])
            ]
          },
          courierLabel: '合作物流：',
          courierValue: 'DHL、FedEx、UPS。国际订单运费在结算页面根据目的地和包裹重量自动计算。'
        },
        tracking: {
          title: '物流追踪',
          intro: '订单发货后，您将收到一封包含物流追踪号的邮件通知。您可以通过以下方式追踪包裹：',
          items: ['登录 Misicheng 账户，在“我的订单”中查看物流状态', '使用邮件中的追踪号在对应快递公司官网查询', '联系我们的客服团队获取物流信息']
        },
        notice: {
          title: '重要提示',
          items: ['以上配送时效为预计时间，实际到达时间可能因天气、节假日等因素有所变化。', '国际订单可能需要缴纳目的地国家的进口关税和税费，该费用由收件人承担。', '如遇特殊情况导致配送延迟，我们会及时通过邮件通知您。', '如有任何物流问题，请联系客服：anna@gzjixing-tech.com']
        }
      },
      returns: {
        kind: 'returns',
        breadcrumb: '退换货政策',
        title: '退换货政策',
        subtitle: 'Misicheng 致力于为您提供满意的购物体验',
        highlights: [
          { icon: RotateCcw, title: '30 天退货', desc: '收货后 30 天内可申请' },
          { icon: CheckCircle, title: '18 个月质保', desc: '非人为损坏免费维修' },
          { icon: RotateCcw, title: '质量问题包邮', desc: '质量问题退换免运费' }
        ],
        returnPolicy: {
          title: '退货政策',
          intro: '自收到商品之日起 30 天内，您可以申请无理由退货。退货商品需满足以下条件：',
          items: ['商品保持原包装，未拆封或已拆封但不影响二次销售', '商品及配件完整，无缺失', '无人为损坏或使用痕迹', '可提供有效订单号或购买凭证']
        },
        nonReturnable: {
          title: '不可退货情况',
          items: ['超过 30 天退货期限的商品', '因人为原因造成损坏的商品（如跌落、进水、私自拆解等）', '已使用且影响二次销售的商品', '赠品和促销品（明确标注不可退换）', '无法提供有效购买凭证的商品']
        },
        exchange: {
          title: '换货政策',
          intro: '如果商品存在以下问题，您可以在签收后 7 天内申请免费换货：',
          items: ['商品存在质量缺陷或功能故障', '收到的商品与订单不符（型号、颜色或数量错误）', '运输过程中造成商品损坏'],
          note: '换货商品将在收到并检测退回商品后的 3 个工作日内重新发出。'
        },
        refund: {
          title: '退款信息',
          intro: '我们将在收到并检测退回商品后处理退款：',
          table: {
            head: ['支付方式', '退款时间'],
            rows: [
              row(['支付宝 / 微信支付', '1-3 个工作日']),
              row(['信用卡 / 借记卡', '3-5 个工作日']),
              row(['PayPal', '3-5 个工作日']),
              row(['Apple Pay / Google Pay', '3-5 个工作日'])
            ]
          }
        },
        process: {
          title: '退换货流程',
          steps: [
            { title: '提交申请', desc: '登录账户，在“我的订单”中找到对应订单，点击“申请退换货”并填写原因。' },
            { title: '审核确认', desc: '客服团队将在 1 个工作日内审核申请，并通过邮件通知结果。' },
            { title: '寄回商品', desc: '审核通过后，请将商品寄回邮件中提供的退货地址。质量问题运费由我们承担。' },
            { title: '退款 / 换货', desc: '收到并检测退回商品后，我们将在规定时间内完成退款或重新发货。' }
          ]
        },
        contact: {
          title: '需要帮助？',
          desc: '如有任何退换货问题，请联系客服：anna@gzjixing-tech.com 或拨打 +86 13247309378 / +86 13288805588（周一至周五 9:00-18:00）。'
        }
      },
      privacy: {
        kind: 'privacy',
        breadcrumb: '隐私政策',
        title: '隐私政策',
        lastUpdated: '最后更新：2025 年 1 月 1 日',
        intro: 'Misicheng 非常重视您的隐私。本政策说明我们如何收集、使用、存储和保护您的个人信息，请在使用服务前仔细阅读。',
        sections: [
          { title: '1. 信息收集', blocks: [{ key: 'p', type: 'p', text: '我们可能收集账户注册、订单、客服沟通、设备、日志、Cookie 以及在授权情况下的位置等信息。' }] },
          { title: '2. 信息使用', blocks: [{ key: 'p', type: 'p', text: '我们会将信息用于订单处理、账户管理、客户沟通、服务优化、营销、安全保障及法律合规。' }] },
          { title: '3. 信息共享', blocks: [{ key: 'p', type: 'p', text: '我们不会出售您的个人信息，仅在服务提供、法律要求、业务转让或获得您明确同意时共享必要信息。' }] },
          { title: '4. 信息安全', blocks: [{ key: 'p', type: 'p', text: '我们通过加密传输、访问控制、安全审计和应急响应机制保护您的信息安全。' }] },
          { title: '5. Cookie 政策', blocks: [{ key: 'p', type: 'p', text: '您可以通过浏览器设置管理或删除 Cookie，关闭 Cookie 可能影响部分网站功能。' }] },
          { title: '6. 您的权利', blocks: [{ key: 'p', type: 'p', text: '您有权访问、更正、删除、限制处理、获取副本或撤回同意。如需行使权利，请联系 anna@gzjixing-tech.com。' }] },
          { title: '7. 未成年人保护', blocks: [{ key: 'p', type: 'p', text: '我们的服务不面向 16 岁以下未成年人，也不会故意收集未成年人信息。' }] },
          { title: '8. 政策更新', blocks: [{ key: 'p', type: 'p', text: '我们可能不时更新本政策，并在本页面发布更新内容。' }] },
          { title: '9. 联系我们', blocks: [{ key: 'items', type: 'ul', plain: true, items: ['邮箱：anna@gzjixing-tech.com', '客服电话：+86 13247309378 / +86 13288805588', '地址：广东省广州市黄埔区TCL喜天科学园B栋8楼'] }] }
        ]
      },
      terms: {
        kind: 'terms',
        breadcrumb: '服务条款',
        title: '服务条款',
        lastUpdated: '最后更新：2025 年 1 月 1 日',
        intro: '欢迎使用 Misicheng 网站及相关服务。使用本服务即表示您同意受本服务条款约束。',
        sections: [
          { title: '1. 服务说明', blocks: [{ key: 'p', type: 'p', text: 'Misicheng 通过本网站提供空气流动、通风、制冷、净化和采暖产品的在线展示、询盘、账户管理、订单处理、物流配送和售后支持等服务。' }] },
          { title: '2. 用户账户', blocks: [{ key: 'p', type: 'p', text: '注册账户时您应提供真实、准确、完整的信息，并妥善保管账户密码。' }] },
          { title: '3. 商品与订单', blocks: [{ key: 'p', type: 'p', text: '我们会尽力保证商品信息准确，但图片、价格、库存和交期可能因实际情况调整。' }] },
          { title: '4. 支付条款', blocks: [{ key: 'p', type: 'p', text: '支付通过第三方支付服务完成，我们不会直接存储您的支付卡信息。' }] },
          { title: '5. 配送与交付', blocks: [{ key: 'p', type: 'linkP', prefix: '详细配送政策请参考 ', href: '/shipping', linkText: '物流配送', suffix: ' 页面。' }] },
          { title: '6. 退换货政策', blocks: [{ key: 'p', type: 'linkP', prefix: '详细退换货条件和流程请参考 ', href: '/returns', linkText: '退换货政策', suffix: ' 页面。' }] },
          { title: '7. 知识产权', blocks: [{ key: 'p', type: 'p', text: '网站内容、品牌名称、标识及相关素材受知识产权法律保护，未经授权不得使用。' }] },
          { title: '8. 用户行为', blocks: [{ key: 'p', type: 'p', text: '使用服务时不得违反法律法规、侵犯他人权益、发布虚假信息、传播恶意代码或干扰网站运行。' }] },
          { title: '9. 免责声明', blocks: [{ key: 'p', type: 'p', text: '在法律允许范围内，本服务按现状提供，我们不对间接或后果性损失承担责任。' }] },
          { title: '10. 条款修改', blocks: [{ key: 'p', type: 'p', text: '我们保留随时修改条款的权利，修改后的条款将在本页面发布。' }] },
          { title: '11. 适用法律与争议解决', blocks: [{ key: 'p', type: 'p', text: '本条款受中华人民共和国法律管辖，争议应先友好协商解决。' }] },
          { title: '12. 联系方式', blocks: [{ key: 'items', type: 'ul', plain: true, items: ['邮箱：anna@gzjixing-tech.com', '客服电话：+86 13247309378 / +86 13288805588', '地址：广东省广州市黄埔区TCL喜天科学园B栋8楼'] }] }
        ]
      }
    }
  }
}
</script>
