<template>
  <div class="min-h-screen">
    <a v-if="showStorefrontShell" href="#main-content" class="skip-to-content">Skip to content</a>

    <header
      v-if="showStorefrontShell"
      class="fixed top-3 left-3 right-3 z-50 flex h-12 items-center justify-between rounded-2xl border border-white/40 bg-white/80 px-4 shadow-[0_8px_32px_rgba(0,0,0,0.08)] backdrop-blur-xl md:hidden"
      @click="scrollToTop"
    >
      <RouterLink :to="localized('/')" class="flex items-center">
        <span class="gradient-text text-lg font-bold tracking-wider">Misicheng</span>
      </RouterLink>
      <div class="flex items-center gap-1">
        <button class="btn btn-ghost h-9 w-9 rounded-full text-gray-600" aria-label="Search" @click.stop="searchOpen = true">
          <Search :size="18" />
        </button>
        <NotificationBell :text="text.notifications" />
        <button class="btn btn-ghost h-9 w-9 rounded-full text-gray-600" aria-label="Open menu" @click.stop="mobileOpen = true">
          <Menu :size="20" />
        </button>
      </div>
    </header>

    <div
      v-if="showStorefrontShell"
      ref="headerRef"
      class="hidden md:block fixed top-3 left-1/2 z-50 w-[calc(100%-2rem)] max-w-6xl -translate-x-1/2"
      :style="headerTiltStyle"
      @mousemove="handleHeaderMouseMove"
      @mouseleave="resetHeaderTilt"
      @mousedown="isPressed = true"
      @mouseup="isPressed = false"
    >
      <header
        class="rounded-2xl border border-white/40 bg-white/60 shadow-[0_8px_32px_rgba(0,0,0,0.08),0_2px_8px_rgba(0,0,0,0.04)] backdrop-blur-xl backdrop-saturate-150 transition-all duration-500 select-none"
        :class="shouldShowHeader ? 'translate-y-0 scale-100 opacity-100' : '-translate-y-20 scale-[0.85] opacity-0'"
        @click="scrollToTop"
      >
        <div class="mx-auto flex h-16 min-w-0 items-center justify-between gap-3 px-5 lg:px-6 xl:px-8">
          <RouterLink :to="localized('/')" class="flex shrink-0 items-center gap-2">
            <span class="gradient-text text-xl font-bold tracking-wider sm:text-2xl lg:text-3xl">Misicheng</span>
          </RouterLink>

          <nav class="hidden min-w-0 flex-1 items-center justify-center gap-0.5 overflow-hidden lg:flex">
            <RouterLink
              v-for="link in navLinks"
              :key="link.path"
              :to="localized(link.path)"
              class="relative flex h-10 min-w-0 shrink items-center rounded-full px-2 py-0 text-sm font-medium transition-colors xl:px-3"
              :class="isActive(link.path) ? 'bg-sky-50/80 text-sky-600' : 'text-gray-600 hover:bg-sky-50/80 hover:text-sky-600'"
              @click.stop
            >
              <span class="block min-w-0 whitespace-nowrap leading-none" :class="navLabelTextClass(link.label)">{{ link.label }}</span>
              <span v-if="isActive(link.path)" class="absolute bottom-0 left-1/2 h-0.5 w-4 -translate-x-1/2 rounded-full bg-sky-500"></span>
            </RouterLink>
          </nav>

          <div class="flex min-w-0 shrink-0 items-center gap-1">
            <div class="hidden shrink-0 items-center gap-1 md:flex">
              <div class="relative" data-switcher>
                <button class="btn btn-ghost h-9 w-9 shrink-0 gap-1 rounded-md px-0 text-xs leading-none whitespace-nowrap text-gray-600 2xl:w-[104px] 2xl:px-3" type="button" @click.stop="languageOpen = !languageOpen; currencyOpen = false">
                  <Globe :size="16" />
                  <span class="hidden min-w-0 whitespace-nowrap 2xl:inline" :class="localeButtonTextClass">{{ currentLocaleName }}</span>
                </button>
                <Transition name="dropdown">
                  <div
                    v-if="languageOpen"
                    class="absolute right-0 top-full mt-2 w-[150px] rounded-xl border border-white/40 bg-white/60 p-1 shadow-[0_8px_32px_rgba(0,0,0,0.08),0_2px_8px_rgba(0,0,0,0.04)] backdrop-blur-xl backdrop-saturate-150"
                    @click.stop
                  >
                    <button
                      v-for="item in locales"
                      :key="item.code"
                      type="button"
                      class="flex w-full min-w-0 rounded-lg px-3 py-2 text-left text-sm transition-colors"
                      :class="locale === item.code ? 'bg-sky-50/80 font-medium text-sky-600' : 'text-gray-700 hover:bg-white/50'"
                      @click="switchLocale(item.code)"
                    >
                      <span class="block min-w-0 whitespace-nowrap" :class="localeNameTextClass(item.name)">{{ item.name }}</span>
                    </button>
                  </div>
                </Transition>
              </div>
              <div class="relative" data-switcher>
                <button class="btn btn-ghost h-9 w-9 shrink-0 gap-1 rounded-md px-0 text-xs leading-none whitespace-nowrap text-gray-600 2xl:w-[70px] 2xl:px-3" type="button" @click.stop="currencyOpen = !currencyOpen; languageOpen = false">
                  <span>{{ currentCurrency?.symbol || '$' }}</span>
                  <span class="hidden text-[11px] 2xl:inline">{{ ui.currency }}</span>
                </button>
                <Transition name="dropdown">
                  <div
                    v-if="currencyOpen"
                    class="absolute right-0 top-full mt-2 min-w-[160px] rounded-xl border border-white/40 bg-white/60 p-1 shadow-[0_8px_32px_rgba(0,0,0,0.08),0_2px_8px_rgba(0,0,0,0.04)] backdrop-blur-xl backdrop-saturate-150"
                    @click.stop
                  >
                    <button
                      v-for="item in currencies"
                      :key="item.code"
                      type="button"
                      class="flex w-full items-center rounded-lg px-3 py-2 text-left text-sm transition-colors"
                      :class="ui.currency === item.code ? 'bg-sky-50/80 font-medium text-sky-600' : 'text-gray-700 hover:bg-white/50'"
                      @click="switchCurrency(item.code)"
                    >
                      <span class="mr-2">{{ item.symbol }}</span>
                      {{ item.code }} - {{ item.name }}
                    </button>
                  </div>
                </Transition>
              </div>
              <div class="mx-1.5 h-5 w-px bg-white/30"></div>
            </div>

            <button class="btn btn-ghost h-10 w-10 rounded-full text-gray-600 transition-colors hover:bg-white/50 hover:text-sky-600" aria-label="Search" @click.stop="searchOpen = true">
              <Search :size="18" />
            </button>
            <RouterLink :to="localized('/account/wishlist')" class="btn btn-ghost h-10 w-10 rounded-full text-gray-600 transition-colors hover:bg-white/50 hover:text-sky-600" aria-label="Wishlist" @click.stop>
              <Heart :size="18" />
            </RouterLink>
            <RouterLink :to="localized('/account')" class="btn btn-ghost h-10 w-10 rounded-full text-gray-600 transition-colors hover:bg-white/50 hover:text-sky-600" aria-label="Account" @click.stop>
              <User :size="18" />
            </RouterLink>
            <NotificationBell :text="text.notifications" />
            <div class="mx-1 hidden h-5 w-px bg-white/30 md:block"></div>
            <button
              class="btn btn-ghost relative h-10 w-10 rounded-full text-gray-600 transition-colors hover:bg-white/50 hover:text-sky-600"
              aria-label="Inquiry"
              @click.stop="inquiry.drawerOpen = true"
            >
              <ShoppingCart :size="18" />
              <span v-if="inquiry.count" class="absolute -right-0.5 -top-0.5 flex h-[18px] w-[18px] items-center justify-center rounded-full bg-sky-500 text-[10px] font-bold text-white ring-2 ring-white/60">
                {{ inquiry.count > 99 ? '99+' : inquiry.count }}
              </span>
            </button>
          </div>
        </div>
      </header>
    </div>

    <Transition name="fade">
      <div v-if="mobileOpen" class="fixed inset-0 z-[90] bg-black/50 md:hidden" @click="mobileOpen = false"></div>
    </Transition>
    <Transition name="mobile-sheet">
      <aside v-if="mobileOpen" class="fixed inset-x-0 top-0 z-[100] max-h-[80vh] overflow-y-auto rounded-b-2xl border-b border-white/40 bg-white/95 p-0 shadow-lg backdrop-blur-xl md:hidden">
        <button class="absolute right-4 top-4 rounded-xs opacity-70 transition-opacity hover:opacity-100" type="button" aria-label="Close" @click="mobileOpen = false">
          <X class="size-4" />
        </button>
        <div class="border-b px-5 py-3">
          <span class="gradient-text text-lg font-bold tracking-wider">Misicheng</span>
        </div>

        <nav class="flex flex-col px-5 py-3">
          <RouterLink
            v-for="link in mobilePrimaryLinks"
            :key="link.path"
            :to="localized(link.path)"
            class="flex items-center justify-between py-3 text-sm font-medium text-gray-700 transition-colors hover:text-sky-600"
            @click="mobileOpen = false"
          >
            {{ link.label }}
            <ChevronRight class="h-4 w-4 text-gray-400" />
          </RouterLink>
        </nav>

        <nav class="flex flex-col px-5 py-3">
          <RouterLink
            v-for="link in mobileExtraLinks"
            :key="link.path"
            :to="localized(link.path)"
            class="flex items-center justify-between py-3 text-sm font-medium text-gray-500 transition-colors hover:text-sky-600"
            @click="mobileOpen = false"
          >
            {{ link.label }}
            <ChevronRight class="h-4 w-4 text-gray-400" />
          </RouterLink>
          <RouterLink
            :to="localized('/about')"
            class="flex w-full items-center justify-between py-3 text-left text-sm font-medium text-gray-500 transition-colors hover:text-sky-600"
            @click="mobileOpen = false"
          >
            {{ text.nav.about }}
            <ChevronRight class="h-4 w-4 text-gray-400" />
          </RouterLink>
        </nav>

        <div class="h-px bg-border"></div>

        <div class="flex items-center gap-4 px-5 py-3">
          <div class="flex min-w-0 flex-1 items-center justify-between gap-2">
            <span class="shrink-0 text-xs text-muted-foreground">{{ text.nav.language }}</span>
            <button class="btn btn-ghost h-9 min-w-0 max-w-[9rem] gap-1.5 rounded-md px-3 text-xs leading-none whitespace-nowrap text-gray-600" type="button" @click.stop="mobileLanguageOpen = !mobileLanguageOpen">
              <Globe :size="16" />
              <span class="min-w-0 whitespace-nowrap" :class="localeButtonTextClass">{{ currentLocaleName }}</span>
            </button>
          </div>
          <div class="h-4 w-px bg-gray-200"></div>
          <div class="flex min-w-0 flex-1 items-center justify-between gap-2">
            <span class="shrink-0 text-xs text-muted-foreground">{{ text.nav.currency }}</span>
            <button class="btn btn-ghost h-9 min-w-0 max-w-[7rem] gap-1 rounded-md px-3 text-xs leading-none whitespace-nowrap text-gray-600" type="button" @click.stop="mobileCurrencyOpen = !mobileCurrencyOpen">
              <span>{{ currentCurrency?.symbol || '$' }}</span>
              <span class="text-[11px]">{{ ui.currency }}</span>
            </button>
          </div>
        </div>

        <div v-if="mobileLanguageOpen" class="grid grid-cols-2 gap-2 px-5 pb-3">
          <button
            v-for="item in locales"
            :key="item.code"
            type="button"
            class="min-w-0 rounded-lg px-3 py-2 text-left text-sm transition-colors"
            :class="locale === item.code ? 'bg-sky-50/80 font-medium text-sky-600' : 'text-gray-600 hover:bg-gray-50'"
            @click="switchLocale(item.code)"
          >
            <span class="block whitespace-nowrap" :class="localeNameTextClass(item.name)">{{ item.name }}</span>
          </button>
        </div>

        <div v-if="mobileCurrencyOpen" class="grid grid-cols-1 gap-2 px-5 pb-3">
          <button
            v-for="item in currencies"
            :key="item.code"
            type="button"
            class="rounded-lg px-3 py-2 text-left text-sm transition-colors"
            :class="ui.currency === item.code ? 'bg-sky-50/80 font-medium text-sky-600' : 'text-gray-600 hover:bg-gray-50'"
            @click="switchCurrency(item.code)"
          >
            <span class="mr-2">{{ item.symbol }}</span>{{ item.code }} - {{ item.name }}
          </button>
        </div>
      </aside>
    </Transition>

    <div
      v-if="showStorefrontShell"
      ref="mouseGlowRef"
      class="mouse-glow pointer-events-none fixed left-0 top-0 z-30 h-[120px] w-[120px] rounded-full opacity-0"
      style="background: radial-gradient(circle, rgba(255,255,255,0.85) 0%, rgba(255,255,255,0.3) 25%, transparent 50%); will-change: transform, opacity; transition: none;"
    ></div>

    <main id="main-content" class="min-h-screen" :class="{ 'pb-mobile-nav': showStorefrontShell }">
      <RouterView />
    </main>

    <footer v-if="showStorefrontShell" class="border-t bg-gray-50">
      <div class="gradient-bg-light">
        <div class="mx-auto flex max-w-7xl flex-col items-center gap-4 px-4 py-12 text-center lg:px-8">
          <h3 class="text-2xl font-bold">{{ text.footer.newsletter }}</h3>
          <p class="max-w-md text-sm text-muted-foreground">{{ text.footer.newsletterDesc }}</p>
          <form class="flex w-full max-w-md gap-2" @submit.prevent="subscribeFooter">
            <input v-model="footerEmail" type="email" required placeholder="your@email.com" class="input h-11 bg-white" />
            <button type="submit" class="btn gradient-bg h-11 px-6 text-white">{{ text.footer.subscribe }}</button>
          </form>
        </div>
      </div>
      <div class="mx-auto max-w-7xl px-4 py-12 lg:px-8">
        <div class="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <span class="gradient-text text-xl font-bold tracking-wider">Misicheng</span>
            <p class="mt-2 text-sm font-medium text-foreground">广州柏乐智能科技有限公司</p>
            <p class="mt-3 text-sm leading-relaxed text-muted-foreground">{{ text.footer.siteDescription || text.footer.intro }}</p>
            <p class="mt-3 text-sm leading-relaxed text-muted-foreground">
              Misicheng is operated by Guangzhou Bailo Intelligent Technology Co., Ltd.
            </p>
            <p class="mt-1 text-sm leading-relaxed text-muted-foreground">
              Misicheng由广州柏乐智能科技有限公司运营。
            </p>
            <p class="mt-3 text-sm text-muted-foreground">
              <span class="font-medium text-foreground">Official Email: </span>
              <a href="mailto:abby@bailekeji.cn" class="break-all transition-colors hover:text-foreground">
                abby@bailekeji.cn
              </a>
            </p>
          </div>
          <div>
            <h4 class="mb-4 text-sm font-semibold uppercase tracking-wider">{{ text.footer.customerService }}</h4>
            <ul class="space-y-3">
              <li><RouterLink :to="localized('/contact')" class="text-sm text-muted-foreground transition-colors hover:text-foreground">{{ text.footer.contact }}</RouterLink></li>
              <li><RouterLink :to="localized('/faq')" class="text-sm text-muted-foreground transition-colors hover:text-foreground">{{ text.footer.faq }}</RouterLink></li>
              <li><RouterLink :to="localized('/shipping')" class="text-sm text-muted-foreground transition-colors hover:text-foreground">{{ text.footer.shipping }}</RouterLink></li>
              <li><RouterLink :to="localized('/returns')" class="text-sm text-muted-foreground transition-colors hover:text-foreground">{{ text.footer.returnPolicy }}</RouterLink></li>
            </ul>
          </div>
          <div>
            <h4 class="mb-4 text-sm font-semibold uppercase tracking-wider">{{ text.footer.information }}</h4>
            <ul class="space-y-3">
              <li><RouterLink :to="localized('/about')" class="text-sm text-muted-foreground transition-colors hover:text-foreground">{{ text.footer.aboutUs }}</RouterLink></li>
              <li><RouterLink :to="localized('/blog')" class="text-sm text-muted-foreground transition-colors hover:text-foreground">{{ text.footer.blog }}</RouterLink></li>
              <li><RouterLink :to="localized('/privacy')" class="text-sm text-muted-foreground transition-colors hover:text-foreground">{{ text.footer.privacy }}</RouterLink></li>
              <li><RouterLink :to="localized('/terms')" class="text-sm text-muted-foreground transition-colors hover:text-foreground">{{ text.footer.terms }}</RouterLink></li>
            </ul>
          </div>
          <div>
            <h4 class="mb-4 text-sm font-semibold uppercase tracking-wider">{{ text.footer.followUs }}</h4>
            <div class="flex gap-3">
              <a
                :href="whatsappUrl"
                target="_blank"
                rel="noopener noreferrer"
                class="flex h-10 w-10 items-center justify-center rounded-full text-white shadow-sm transition-transform hover:scale-105"
                style="background-color: #25D366"
                :aria-label="text.whatsapp.ariaLabel"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
                </svg>
              </a>
            </div>
          </div>
        </div>
        <div class="my-8 h-px bg-border"></div>
        <div class="flex flex-col items-center justify-between gap-4 text-center text-xs text-muted-foreground sm:flex-row">
          <p>&copy; {{ new Date().getFullYear() }} Misicheng. {{ text.footer.copyright }}</p>
          <div class="flex gap-4">
            <RouterLink :to="localized('/privacy')" class="hover:text-foreground">{{ text.footer.privacy }}</RouterLink>
            <RouterLink :to="localized('/terms')" class="hover:text-foreground">{{ text.footer.terms }}</RouterLink>
          </div>
        </div>
      </div>
    </footer>

    <Transition name="search-overlay">
      <div v-if="showStorefrontShell && searchOpen" class="fixed inset-0 z-[110] bg-black/50 backdrop-blur-sm" @click="closeSearch"></div>
    </Transition>
    <Transition name="search-panel">
      <div v-if="showStorefrontShell && searchOpen" class="fixed inset-x-0 top-0 z-[120] mx-auto max-w-2xl p-4 pt-20">
        <div class="overflow-hidden rounded-2xl bg-white shadow-2xl">
          <div class="mx-4 mb-2 mt-4 flex items-center rounded-full bg-gray-100 px-4">
            <Search class="h-5 w-5 text-muted-foreground" />
            <input
              ref="searchInputRef"
              v-model="searchQuery"
              type="text"
              class="h-12 flex-1 border-none bg-transparent px-3 text-base outline-none ring-0 shadow-none placeholder:text-muted-foreground focus:border-none focus:outline-none focus:ring-0 focus:shadow-none"
              :placeholder="text.search.placeholder"
            />
            <Loader2 v-if="searchLoading" class="h-5 w-5 animate-spin text-muted-foreground" />
            <button v-else-if="searchQuery" type="button" aria-label="Clear search" @click="searchQuery = ''">
              <X class="h-5 w-5 text-muted-foreground hover:text-foreground" />
            </button>
          </div>
          <div class="max-h-[60vh] overflow-y-auto">
            <div v-if="searchQuery && !searchLoading && searchResults.length === 0" class="px-4 py-12 text-center">
              <p class="text-muted-foreground">{{ text.search.noResults.replace('{query}', searchQuery) }}</p>
              <p class="mt-1 text-sm text-muted-foreground">{{ text.search.tryDifferent }}</p>
            </div>
            <div v-if="searchResults.length > 0" class="p-2">
              <p class="px-3 py-2 text-xs font-medium text-muted-foreground">
                {{ text.search.resultCount.replace('{count}', searchResults.length) }}
              </p>
              <RouterLink
                v-for="product in searchResults"
                :key="product.id"
                :to="localized(`/product/${product.slug}`)"
                class="flex items-center gap-4 rounded-xl px-3 py-3 transition-colors hover:bg-gray-50"
                @click="closeSearch"
              >
                <div class="relative h-14 w-11 flex-shrink-0 overflow-hidden rounded-lg bg-gray-100">
                  <img v-if="product.image || product.imageThumb" :src="product.imageThumb || product.image" :alt="product.name" class="h-full w-full object-contain p-1" loading="lazy" decoding="async" />
                </div>
                <div class="flex-1">
                  <p class="text-sm font-medium">{{ product.name }}</p>
                  <p class="text-sm text-muted-foreground">{{ productSearchPrice(product) }}</p>
                </div>
              </RouterLink>
            </div>
            <div v-if="!searchQuery" class="px-4 py-8 text-center">
              <p class="text-sm text-muted-foreground">{{ text.search.startTyping }}</p>
            </div>
          </div>
          <div class="border-t px-4 py-3 text-center">
            <span class="text-xs text-muted-foreground">
              {{ text.search.escPrefix }}
              <kbd class="rounded border bg-gray-100 px-1.5 py-0.5 text-xs">ESC</kbd>
              {{ text.search.escSuffix }}
            </span>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="fade">
      <div v-if="showStorefrontShell && inquiry.drawerOpen" class="fixed inset-0 z-[110] bg-black/40 backdrop-blur-sm" @click="inquiry.drawerOpen = false"></div>
    </Transition>
    <Transition name="slide">
      <aside v-if="showStorefrontShell && inquiry.drawerOpen" class="fixed top-0 right-0 bottom-0 z-[120] flex w-full max-w-md flex-col bg-white shadow-2xl">
        <div class="flex items-center justify-between border-b p-5">
          <strong>{{ text.inquiry.basket }}</strong>
          <button class="btn btn-ghost h-9 w-9 rounded-full" @click="inquiry.drawerOpen = false"><X :size="20" /></button>
        </div>
        <div class="flex-1 overflow-auto p-5">
          <p v-if="!inquiry.items.length" class="py-12 text-center text-muted-foreground">{{ text.inquiry.empty }}</p>
          <div v-for="item in inquiry.items" :key="item.id" class="grid grid-cols-[78px_1fr] gap-3 border-b py-3">
            <img :src="item.image" :alt="item.name" class="h-[92px] w-[78px] rounded-xl bg-muted object-contain p-1" />
            <div>
              <strong class="block whitespace-normal break-words leading-snug" :class="fitTextClass(item.name)">
                {{ item.name }}
              </strong>
              <p v-if="formatOptions(item.options)" class="mt-1 text-xs text-muted-foreground">{{ formatOptions(item.options) }}</p>
              <span class="mt-1 block text-sm font-semibold text-sky-600">{{ cartItemPrice(item) }}</span>
              <div class="mt-2 flex items-center gap-2">
                <button class="h-7 w-7 rounded-md border" @click="inquiry.updateQuantity(item.id, item.quantity - 1)">-</button>
                <b class="min-w-6 text-center">{{ item.quantity }}</b>
                <button class="h-7 w-7 rounded-md border" @click="inquiry.updateQuantity(item.id, item.quantity + 1)">+</button>
                <button class="ml-auto text-xs text-red-500" @click="inquiry.removeItem(item.id)">{{ text.inquiry.remove }}</button>
              </div>
            </div>
          </div>
        </div>
        <div class="flex items-center justify-between border-t p-5">
          <div>
            <span class="text-sm text-muted-foreground">{{ inquiry.count }} {{ text.inquiry.items }}</span>
            <strong class="block">{{ cartSubtotalText() }}</strong>
          </div>
          <RouterLink class="btn gradient-bg h-11 rounded-xl px-5 text-white" :to="localized('/inquiry')" @click="inquiry.drawerOpen = false">
            {{ text.inquiry.submitInquiry }}
          </RouterLink>
        </div>
      </aside>
    </Transition>

    <nav v-if="showStorefrontShell" aria-label="Mobile navigation" class="fixed bottom-3 left-3 right-3 z-40 rounded-2xl border border-white/40 bg-white/80 shadow-[0_8px_32px_rgba(0,0,0,0.08)] backdrop-blur-xl md:hidden">
      <div class="flex h-14 items-center justify-around">
        <RouterLink :to="localized('/')" class="flex flex-col items-center gap-0.5" :class="isActive('/') ? 'text-foreground' : 'text-muted-foreground'">
          <Home class="h-5 w-5" :class="isActive('/') ? 'text-sky-500' : ''" />
          <span class="text-[10px]">{{ text.nav.home }}</span>
        </RouterLink>
        <RouterLink :to="localized('/shop')" class="flex flex-col items-center gap-0.5" :class="isActive('/shop') ? 'text-foreground' : 'text-muted-foreground'">
          <ShoppingBag class="h-5 w-5" :class="isActive('/shop') ? 'text-sky-500' : ''" />
          <span class="text-[10px]">{{ text.nav.shop }}</span>
        </RouterLink>
        <button class="relative flex flex-col items-center gap-0.5 text-muted-foreground" type="button" :aria-label="text.nav.inquiry" @click="inquiry.drawerOpen = true">
          <ShoppingCart class="h-5 w-5" />
          <span v-if="inquiry.count" class="gradient-bg absolute -right-2 -top-1 flex h-4 w-4 items-center justify-center rounded-full text-[9px] font-bold text-white">
            {{ inquiry.count > 9 ? '9+' : inquiry.count }}
          </span>
          <span class="text-[10px]">{{ text.nav.inquiry }}</span>
        </button>
        <RouterLink :to="localized('/account/wishlist')" class="flex flex-col items-center gap-0.5" :class="isActive('/account/wishlist') ? 'text-foreground' : 'text-muted-foreground'">
          <Heart class="h-5 w-5" :class="isActive('/account/wishlist') ? 'text-sky-500' : ''" />
          <span class="text-[10px]">{{ text.nav.favorites }}</span>
        </RouterLink>
        <RouterLink :to="localized('/account')" class="flex flex-col items-center gap-0.5" :class="isActive('/account') ? 'text-foreground' : 'text-muted-foreground'">
          <User class="h-5 w-5" :class="isActive('/account') ? 'text-sky-500' : ''" />
          <span class="text-[10px]">{{ text.nav.myAccount }}</span>
        </RouterLink>
      </div>
      <div class="h-[env(safe-area-inset-bottom)]"></div>
    </nav>

    <Transition name="wa">
      <div v-if="showStorefrontShell && whatsappVisible && !whatsappDismissed" class="fixed bottom-24 right-6 z-50 flex items-center gap-2 md:bottom-6">
        <button
          class="flex h-6 w-6 items-center justify-center rounded-full bg-gray-200 text-gray-500 shadow-md transition-colors hover:bg-gray-300 hover:text-gray-700"
          type="button"
          :aria-label="text.whatsapp.close"
          @click="whatsappDismissed = true"
        >
          <X class="h-3.5 w-3.5" />
        </button>
        <a
          :href="whatsappUrl"
          target="_blank"
          rel="noopener noreferrer"
          class="flex h-14 items-center rounded-full shadow-lg transition-all duration-300 hover:shadow-xl"
          style="background-color: #25D366"
          :aria-label="text.whatsapp.ariaLabel"
          @mouseenter="whatsappHovered = true"
          @mouseleave="whatsappHovered = false"
        >
          <span class="flex h-14 w-14 shrink-0 items-center justify-center">
            <svg viewBox="0 0 24 24" fill="white" class="h-7 w-7" xmlns="http://www.w3.org/2000/svg">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
            </svg>
          </span>
          <span
            class="overflow-hidden whitespace-nowrap text-sm font-medium text-white transition-all duration-300"
            :style="{ maxWidth: whatsappHovered ? '120px' : '0px', paddingRight: whatsappHovered ? '16px' : '0px', opacity: whatsappHovered ? 1 : 0 }"
          >
            {{ text.whatsapp.chat }}
          </span>
        </a>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { ChevronRight, Globe, Heart, Home, Loader2, Menu, Search, ShoppingBag, ShoppingCart, User, X } from 'lucide-vue-next'

import { searchProducts, subscribeNewsletter } from './api'
import NotificationBell from './components/NotificationBell.vue'
import { loadLocaleMessages, translatedCopy } from './i18n'
import { useInquiryStore } from './stores/inquiry'
import { useUiStore } from './stores/ui'
import { useWishlistStore } from './stores/wishlist'
import { price, productPriceRange } from './utils'
import { formatVariantOptions } from './variantOptions'

const route = useRoute()
const router = useRouter()
const inquiry = useInquiryStore()
const ui = useUiStore()
const wishlist = useWishlistStore()
const headerRef = ref(null)
const mouseGlowRef = ref(null)
const mobileOpen = ref(false)
const searchOpen = ref(false)
const languageOpen = ref(false)
const currencyOpen = ref(false)
const mobileLanguageOpen = ref(false)
const mobileCurrencyOpen = ref(false)
const searchInputRef = ref(null)
const searchQuery = ref('')
const searchResults = ref([])
const searched = ref(false)
const searchLoading = ref(false)
const footerEmail = ref('')
const isScrolled = ref(false)
const isHoverZone = ref(false)
const isPressed = ref(false)
const tiltX = ref(0)
const tiltY = ref(0)
const whatsappVisible = ref(false)
const whatsappDismissed = ref(false)
const whatsappHovered = ref(false)
let whatsappTimer
let searchTimer
let glowRaf = 0
let glowIdle
let glowRunning = false
const whatsappUrl = 'https://wa.me/8613247309378'
const glowPos = { x: -100, y: -100 }
const glowCurrent = { x: -100, y: -100 }
const glowState = { velocity: 0, opacity: 0, scale: 0.6 }
const localePattern = /^\/(en|zh|ja|ko|fr|de|es|ar)(?=\/|$)/
const locales = [
  { code: 'en', name: 'English' },
  { code: 'zh', name: '\u4e2d\u6587' },
  { code: 'ja', name: '\u65e5\u672c\u8a9e' },
  { code: 'ko', name: '\ud55c\uad6d\uc5b4' },
  { code: 'fr', name: 'Fran\u00e7ais' },
  { code: 'de', name: 'Deutsch' },
  { code: 'es', name: 'Espa\u00f1ol' },
  { code: 'ar', name: '\u0627\u0644\u0639\u0631\u0628\u064a\u0629' }
]
const currencies = [
  { code: 'USD', symbol: '$', name: 'US Dollar' },
  { code: 'EUR', symbol: '\u20ac', name: 'Euro' },
  { code: 'GBP', symbol: '\u00a3', name: 'British Pound' },
  { code: 'JPY', symbol: '\u00a5', name: 'Japanese Yen' },
  { code: 'CNY', symbol: '\u00a5', name: 'Chinese Yuan' },
  { code: 'KRW', symbol: '\u20a9', name: 'Korean Won' }
]
const localeCurrencyMap = {
  en: 'USD',
  zh: 'CNY',
  ja: 'JPY',
  ko: 'KRW',
  fr: 'EUR',
  de: 'EUR',
  es: 'EUR',
  ar: 'USD'
}

const locale = computed(() => route.params.locale || ui.locale || 'en')
const text = computed(() => translatedCopy(locale.value, copy, appMessageMap))
const currentLocaleName = computed(() => locales.find(item => item.code === locale.value)?.name || locale.value)
const currentCurrency = computed(() => currencies.find(item => item.code === ui.currency) || currencies[0])
const localeButtonTextClass = computed(() => {
  const length = Array.from(currentLocaleName.value || '').length
  if (locale.value === 'ar' || length >= 8) return 'text-[9px]'
  if (length >= 7) return 'text-[11px]'
  return 'text-xs'
})
function localeNameTextClass(name) {
  const length = Array.from(name || '').length
  if (length >= 8) return 'text-[11px]'
  if (length >= 7) return 'text-xs'
  return 'text-sm'
}
function navLabelTextClass(name) {
  const length = Array.from(name || '').length
  if (locale.value === 'ar' || length >= 16) return 'text-[10px] xl:text-xs'
  if (length >= 13) return 'text-[11px] xl:text-sm'
  if (length >= 10) return 'text-xs xl:text-sm'
  return 'text-sm xl:text-base'
}
function fitTextClass(value) {
  const length = Array.from(String(value || '')).length
  if (length >= 48) return 'text-[10px]'
  if (length >= 32) return 'text-[11px]'
  if (length >= 22) return 'text-xs'
  return 'text-sm'
}

function formatOptions(options) {
  return formatVariantOptions(options, [], locale.value === 'zh' ? 'zh' : 'en')
}
const showStorefrontShell = computed(() => {
  const path = String(route.path || '')
  return !/^(?:\/(en|zh|ja|ko|fr|de|es|ar))?\/(admin|vendor)(?=\/|$)/.test(path)
})
const navLinks = computed(() => [
  { path: '/', label: text.value.nav.home },
  { path: '/shop', label: text.value.nav.shop },
  { path: '/service', label: text.value.nav.service },
  { path: '/contact', label: text.value.nav.contact }
])
const mobilePrimaryLinks = computed(() => navLinks.value)
const mobileExtraLinks = computed(() => [
  { path: '/blog', label: text.value.footer.blog },
  { path: '/faq', label: text.value.footer.faq }
])
const shouldShowHeader = computed(() => !isScrolled.value || isHoverZone.value || searchOpen.value || inquiry.drawerOpen)
const headerTiltStyle = computed(() => ({
  marginLeft: `${tiltX.value}px`,
  marginTop: `${tiltY.value}px`,
  transform: `scale(${isPressed.value ? 0.97 : 1})`,
  transition: isPressed.value ? 'transform 80ms ease' : 'transform 220ms ease'
}))

function appMessageMap(source) {
  return {
    nav: {
      home: source.nav?.home,
      shop: source.nav?.shop,
      service: source.nav?.service,
      contact: source.nav?.contact,
      about: source.nav?.about,
      language: source.nav?.language,
      currency: source.nav?.currency,
      inquiry: source.nav?.inquiry,
      favorites: source.nav?.favorites,
      myAccount: source.nav?.myAccount
    },
    inquiry: {
      basket: source.inquiry?.basket,
      empty: source.inquiry?.empty,
      items: source.inquiry?.items,
      remove: source.inquiry?.remove,
      submitInquiry: source.inquiry?.submitInquiry
    },
    search: {
      placeholder: source.search?.placeholder,
      noResults: source.search?.noResults,
      tryDifferent: source.search?.tryDifferent,
      resultCount: source.search?.resultCount,
      startTyping: source.search?.startTyping,
      escPrefix: source.search?.escToClose?.split('<key>')[0]?.trim() || copy.en.search.escPrefix,
      escSuffix: source.search?.escToClose?.split('</key>')[1]?.trim() || copy.en.search.escSuffix
    },
    footer: {
      aboutUs: source.footer?.aboutUs,
      customerService: source.footer?.customerService,
      information: source.footer?.information,
      followUs: source.footer?.followUs,
      newsletter: source.footer?.newsletter,
      newsletterDesc: source.footer?.newsletterDesc,
      subscribe: source.footer?.subscribe,
      copyright: source.footer?.copyright,
      privacyPolicy: source.footer?.privacyPolicy,
      termsOfService: source.footer?.termsOfService,
      returnPolicy: source.footer?.returnPolicy,
      faq: source.footer?.faq,
      contact: source.footer?.contact,
      shipping: source.footer?.shipping,
      blog: source.footer?.blog,
      siteDescription: source.footer?.siteDescription
    },
    notifications: source.notifications
  }
}

function localized(path) {
  const current = locale.value || 'en'
  if (path === '/') return `/${current}`
  return `/${current}${path}`
}

function negotiableText() {
  return locale.value === 'zh' ? '面议' : 'Negotiable'
}

function productSearchPrice(product) {
  return productPriceRange(product, ui.currency, { negotiableText: negotiableText() })
}

function isNegotiableCartItem(item) {
  return Boolean(item?.priceNegotiable || Number(item?.price || 0) <= 0)
}

function cartItemPrice(item) {
  return isNegotiableCartItem(item) ? negotiableText() : price(item.price, ui.currency)
}

function cartSubtotalText() {
  const hasNegotiable = inquiry.items.some(isNegotiableCartItem)
  if (!hasNegotiable) return price(inquiry.subtotal, ui.currency)
  if (inquiry.subtotal <= 0) return negotiableText()
  return `${price(inquiry.subtotal, ui.currency)} + ${negotiableText()}`
}

function isActive(path) {
  const rest = route.path.replace(localePattern, '') || '/'
  if (path === '/') return rest === '/'
  return rest === path || rest.startsWith(`${path}/`)
}

function switchLocale(target) {
  ui.setLocale(target)
  const defaultCurrency = localeCurrencyMap[target] || 'USD'
  ui.setCurrency(defaultCurrency)
  const rest = route.fullPath.replace(localePattern, '') || ''
  languageOpen.value = false
  mobileLanguageOpen.value = false
  router.push(`/${target}${rest}`)
}

function switchCurrency(code) {
  ui.setCurrency(code)
  currencyOpen.value = false
  mobileCurrencyOpen.value = false
}

function scrollToTop(event) {
  if (event?.target?.closest?.('a, button, input, select')) return
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function handleHeaderMouseMove(event) {
  const rect = headerRef.value?.getBoundingClientRect()
  if (!rect) return
  const centerX = rect.left + rect.width / 2
  const centerY = rect.top + rect.height / 2
  tiltX.value = Math.max(-4, Math.min(4, (event.clientX - centerX) / 100))
  tiltY.value = Math.max(-2, Math.min(2, (event.clientY - centerY) / 100))
}

function resetHeaderTilt() {
  tiltX.value = 0
  tiltY.value = 0
}

function handleScroll() {
  isScrolled.value = window.scrollY > 10
}

function handleGlobalMouse(event) {
  isHoverZone.value = event.clientY < 60
  updateMouseGlow(event)
}

function animateMouseGlow() {
  const dx = glowPos.x - glowCurrent.x
  const dy = glowPos.y - glowCurrent.y
  glowCurrent.x += dx * 0.35
  glowCurrent.y += dy * 0.35

  const speed = Math.sqrt(dx * dx + dy * dy)
  const targetVelocity = Math.min(speed / 8, 1)
  glowState.velocity += (targetVelocity - glowState.velocity) * 0.1
  const targetOpacity = glowState.velocity > 0.02 ? 0.6 : 0
  glowState.opacity += (targetOpacity - glowState.opacity) * 0.08
  const targetScale = 0.8 + glowState.velocity * 0.4
  glowState.scale += (targetScale - glowState.scale) * 0.1

  if (mouseGlowRef.value) {
    mouseGlowRef.value.style.transform = `translate(${glowCurrent.x}px, ${glowCurrent.y}px) translate(-50%, -50%) scale(${glowState.scale})`
    mouseGlowRef.value.style.opacity = `${glowState.opacity}`
  }

  if (glowState.opacity < 0.01 && glowState.velocity < 0.01) {
    glowRunning = false
    glowRaf = 0
    return
  }
  glowRaf = window.requestAnimationFrame(animateMouseGlow)
}

function updateMouseGlow(event) {
  glowPos.x = event.clientX
  glowPos.y = event.clientY
  if (!glowRunning) {
    glowRunning = true
    glowRaf = window.requestAnimationFrame(animateMouseGlow)
  }
  if (glowIdle) window.clearTimeout(glowIdle)
  glowIdle = window.setTimeout(() => {
    glowState.velocity = 0
  }, 100)
}

async function runSearch() {
  searched.value = true
  if (searchQuery.value.trim().length < 2) {
    searchResults.value = []
    return
  }
  searchLoading.value = true
  try {
    const data = await searchProducts(searchQuery.value.trim())
    searchResults.value = data.products || []
  } catch {
    searchResults.value = []
  } finally {
    searchLoading.value = false
  }
}

function closeSearch() {
  searchOpen.value = false
}

function handleKeyDown(event) {
  if (event.key === 'Escape' && searchOpen.value) closeSearch()
}

function handleDocumentClick(event) {
  if (event.target?.closest?.('[data-switcher]')) return
  languageOpen.value = false
  currencyOpen.value = false
}

function syncAccountStores() {
  inquiry.syncAccount()
  wishlist.syncAccount()
}

function handleStorage(event) {
  if (event.key === 'misicheng-user') syncAccountStores()
}

async function subscribeFooter() {
  if (!footerEmail.value) return
  await subscribeNewsletter(footerEmail.value)
  footerEmail.value = ''
  window.alert(text.value.footer.subscribeOk)
}

watch(searchOpen, async open => {
  if (open) {
    document.body.style.overflow = 'hidden'
    await nextTick()
    window.setTimeout(() => searchInputRef.value?.focus(), 100)
  } else {
    document.body.style.overflow = ''
    searchQuery.value = ''
    searchResults.value = []
    searched.value = false
    searchLoading.value = false
  }
})

watch(searchQuery, value => {
  if (searchTimer) window.clearTimeout(searchTimer)
  if (value.trim().length >= 2) {
    searchTimer = window.setTimeout(runSearch, 300)
  } else {
    searched.value = false
    searchResults.value = []
    searchLoading.value = false
  }
})

watch(locale, target => {
  loadLocaleMessages(target).catch(() => {})
}, { immediate: true })

watch(() => route.fullPath, syncAccountStores, { immediate: true })

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  window.addEventListener('mousemove', handleGlobalMouse, { passive: true })
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('storage', handleStorage)
  document.addEventListener('click', handleDocumentClick)
  whatsappTimer = window.setTimeout(() => {
    whatsappVisible.value = true
  }, 3000)
  handleScroll()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('mousemove', handleGlobalMouse)
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('storage', handleStorage)
  document.removeEventListener('click', handleDocumentClick)
  window.clearTimeout(whatsappTimer)
  if (searchTimer) window.clearTimeout(searchTimer)
  document.body.style.overflow = ''
  if (glowRaf) window.cancelAnimationFrame(glowRaf)
  if (glowIdle) window.clearTimeout(glowIdle)
})

const copy = {
  en: {
    nav: {
      home: 'Home',
      shop: 'Products',
      service: 'Service',
      contact: 'Contact',
      about: 'About',
      language: 'Language',
      currency: 'Currency',
      languageName: 'English',
      inquiry: 'Cart',
      favorites: 'Favorites',
      myAccount: 'My Account'
    },
    inquiry: {
      basket: 'Shopping Cart',
      empty: 'Your cart is empty.',
      remove: 'Remove',
      items: 'items',
      submitInquiry: 'Submit Inquiry'
    },
    search: {
      placeholder: 'Search products...',
      noResults: 'No results for "{query}"',
      tryDifferent: 'Try a different search term',
      resultCount: '{count} result(s)',
      startTyping: 'Start typing to search products',
      escPrefix: 'Press ',
      escSuffix: ' to close'
    },
    footer: {
      newsletter: 'Newsletter',
      newsletterDesc: 'Subscribe to get special offers, free giveaways, and exclusive deals',
      subscribe: 'Subscribe',
      subscribeOk: 'Subscribed successfully.',
      intro: 'Smart power strips, extension sockets, plug adapters, USB-C charging stations, and surge protection solutions for wholesale and project sourcing.',
      aboutUs: 'About Us',
      customerService: 'Customer Service',
      information: 'Information',
      followUs: 'Follow Us',
      copyright: 'All rights reserved.',
      contact: 'Contact Us',
      faq: 'FAQ',
      shipping: 'Shipping Info',
      returnPolicy: 'Return Policy',
      blog: 'Blog',
      privacy: 'Privacy Policy',
      terms: 'Terms of Service'
    },
    notifications: {
      notifications: 'Notifications',
      markAllRead: 'Mark all as read',
      empty: 'No notifications',
      justNow: 'just now',
      minutesAgo: '{count} minutes ago',
      hoursAgo: '{count} hours ago',
      daysAgo: '{count} days ago'
    },
    whatsapp: {
      close: 'Close',
      ariaLabel: 'Contact us on WhatsApp',
      chat: 'Chat'
    }
  },
  zh: {
    nav: {
      home: '首页',
      shop: '产品',
      service: '服务',
      contact: '联系我们',
      about: '关于我们',
      language: '语言',
      currency: '货币',
      languageName: '中文',
      inquiry: '购物车',
      favorites: '收藏',
      myAccount: '我的'
    },
    inquiry: {
      basket: '购物车',
      empty: '购物车还是空的。',
      remove: '移除',
      items: '件商品',
      submitInquiry: '提交询盘'
    },
    search: {
      placeholder: '搜索商品...',
      noResults: '未找到「{query}」的相关结果',
      tryDifferent: '试试其他关键词',
      resultCount: '{count} 个结果',
      startTyping: '输入关键词搜索商品',
      escPrefix: '按 ',
      escSuffix: ' 关闭'
    },
    footer: {
      newsletter: '订阅通讯',
      newsletterDesc: '订阅以获取特别优惠、免费赠品和独家折扣',
      subscribe: '订阅',
      subscribeOk: '订阅成功。',
      intro: '智能排插、延长线插座、插头转换器、USB-C 充电站与防浪涌电源解决方案，支持批发采购和项目配套。',
      aboutUs: '关于我们',
      customerService: '客户服务',
      information: '信息中心',
      followUs: '关注我们',
      copyright: '版权所有。',
      contact: '联系我们',
      faq: '常见问题',
      shipping: '物流信息',
      returnPolicy: '退换政策',
      blog: '博客',
      privacy: '隐私政策',
      terms: '服务条款'
    },
    notifications: {
      notifications: '通知',
      markAllRead: '全部标记为已读',
      empty: '暂无通知',
      justNow: '刚刚',
      minutesAgo: '{count} 分钟前',
      hoursAgo: '{count} 小时前',
      daysAgo: '{count} 天前'
    },
    whatsapp: {
      close: '关闭',
      ariaLabel: '通过 WhatsApp 联系我们',
      chat: '聊天'
    }
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active,
.search-overlay-enter-active,
.search-overlay-leave-active,
.search-panel-enter-active,
.search-panel-leave-active,
.slide-enter-active,
.slide-leave-active,
.mobile-sheet-enter-active,
.mobile-sheet-leave-active,
.wa-enter-active,
.wa-leave-active {
  transition: all 0.22s ease;
}

.fade-enter-from,
.fade-leave-to,
.search-overlay-enter-from,
.search-overlay-leave-to,
.wa-enter-from,
.wa-leave-to {
  opacity: 0;
}

.search-panel-enter-active,
.search-panel-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.search-panel-enter-from,
.search-panel-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.wa-enter-from,
.wa-leave-to {
  transform: scale(0.8);
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}

.mobile-sheet-enter-from,
.mobile-sheet-leave-to {
  opacity: 0;
  transform: translateY(-100%);
}

.pb-mobile-nav {
  padding-bottom: 4.5rem;
}

@media (min-width: 768px) {
  .pb-mobile-nav {
    padding-bottom: 0;
  }
}
</style>
