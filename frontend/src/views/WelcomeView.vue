<template>
  <main class="lp" :class="{ 'lp--still': reducedMotion, 'lp--reveal': revealArmed }">
    <!-- Depth layers: a slow aurora, a fine grid, and a glow that follows the
         pointer. All decorative, all behind the content. -->
    <div class="lp-backdrop" aria-hidden="true">
      <span class="lp-orb lp-orb--violet" />
      <span class="lp-orb lp-orb--cyan" />
      <span class="lp-orb lp-orb--magenta" />
      <span class="lp-grid" />
      <span class="lp-spotlight" :style="spotlightStyle" />
    </div>

    <header class="lp-nav" :class="{ 'is-stuck': scrolled }">
      <div class="lp-nav__inner">
        <AppLogo />
        <nav class="lp-nav__actions" aria-label="账户入口">
          <RouterLink class="lp-ghost-link" :to="{ name: 'login' }">登录</RouterLink>
          <RouterLink
            class="lp-cta lp-cta--small"
            :to="{ name: 'login', query: { mode: 'register' } }"
          >
            免费注册
          </RouterLink>
        </nav>
      </div>
    </header>

    <section class="lp-hero" @pointermove.passive="trackPointer" @pointerleave="resetPointer">
      <div class="lp-hero__copy">
        <p class="lp-eyebrow lp-reveal" style="--step: 0">
          <span class="lp-pulse" aria-hidden="true" />
          DAYFLOW · 时间预算
        </p>

        <h1 class="lp-title">
          <span class="lp-title__line lp-reveal" style="--step: 1">让每一分钟</span>
          <span class="lp-title__line lp-reveal" style="--step: 2">
            流向<span class="lp-shine">重要的事</span>
          </span>
        </h1>

        <p class="lp-lead lp-reveal" style="--step: 3">
          计划、专注、复盘串成一条线。<br />
          先看清时间去哪了，再谈管理时间。
        </p>

        <div class="lp-hero__actions lp-reveal" style="--step: 4">
          <RouterLink
            ref="magneticCta"
            class="lp-cta lp-cta--large"
            :style="magneticStyle"
            :to="{ name: 'login', query: { mode: 'register' } }"
            @pointermove.passive="trackMagnet"
            @pointerleave="resetMagnet"
          >
            <span>免费开始</span>
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h13M13 6l6 6-6 6" /></svg>
          </RouterLink>
          <a class="lp-ghost-link lp-ghost-link--arrow" href="#preview">看看 DayFlow</a>
        </div>

        <dl class="lp-stats lp-reveal" style="--step: 5" ref="statsEl">
          <div v-for="stat in stats" :key="stat.label">
            <dt>{{ stat.label }}</dt>
            <dd>
              <strong>{{ statsVisible ? stat.rendered.value : stat.zero }}</strong>
              <span>{{ stat.unit }}</span>
            </dd>
          </div>
        </dl>
      </div>

      <!-- The product's promise, drawn: minutes leave the clock and flow into
           the things you chose to spend them on, which fill as they arrive. -->
      <div class="lp-flow" role="img" :aria-label="flowLabel">
        <div class="lp-flow__viewport">
          <div class="lp-flow__scene" :style="parallaxStyle">
          <svg class="lp-flow__svg" viewBox="0 0 560 420" aria-hidden="true">
            <defs>
              <linearGradient id="lpStream" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stop-color="#7c5cfc" stop-opacity="0" />
                <stop offset="45%" stop-color="#8b7bff" stop-opacity=".55" />
                <stop offset="100%" stop-color="#37e2d5" stop-opacity=".2" />
              </linearGradient>
              <linearGradient id="lpFill" x1="0" y1="1" x2="0" y2="0">
                <stop offset="0%" stop-color="#7c5cfc" />
                <stop offset="100%" stop-color="#37e2d5" />
              </linearGradient>
            </defs>

            <g class="lp-flow__dial">
              <circle cx="96" cy="210" r="66" class="lp-flow__dial-track" />
              <circle
                cx="96"
                cy="210"
                r="66"
                class="lp-flow__dial-sweep"
                pathLength="1"
              />
              <line x1="96" y1="210" x2="96" y2="164" class="lp-flow__hand lp-flow__hand--minute" />
              <line x1="96" y1="210" x2="126" y2="210" class="lp-flow__hand lp-flow__hand--hour" />
              <circle cx="96" cy="210" r="5" class="lp-flow__pin" />
            </g>

            <path
              v-for="stream in streams"
              :id="`lp-path-${stream.id}`"
              :key="stream.id"
              :d="stream.d"
              class="lp-flow__stream"
            />

            <g v-for="(bucket, index) in buckets" :key="bucket.id">
              <rect
                :x="bucket.x"
                :y="VESSEL_TOP"
                :width="VESSEL_WIDTH"
                :height="VESSEL_BOTTOM - VESSEL_TOP"
                rx="16"
                class="lp-flow__vessel"
              />
              <rect
                :x="bucket.x + 6"
                :y="VESSEL_BOTTOM - 6 - bucket.height"
                :width="VESSEL_WIDTH - 12"
                :height="bucket.height"
                rx="11"
                class="lp-flow__level"
                :style="{ '--delay': `${index * 1.1}s` }"
              />
              <text :x="bucket.x + VESSEL_WIDTH / 2" y="352" class="lp-flow__vessel-label">
                {{ bucket.label }}
              </text>
              <text :x="bucket.x + VESSEL_WIDTH / 2" y="371" class="lp-flow__vessel-time">
                {{ bucket.time }}
              </text>
            </g>

            <!-- One dot per minute in flight, riding the very path the stream
                 above draws. Living inside the viewBox means they scale with
                 the artwork on any screen. -->
            <circle v-for="minute in minutes" :key="minute.id" r="3.6" class="lp-minute">
              <animateMotion
                :dur="`${minute.duration}s`"
                :begin="`${minute.delay}s`"
                repeatCount="indefinite"
                rotate="0"
                keyPoints="0;1"
                keyTimes="0;1"
                calcMode="spline"
                keySplines="0.5 0 0.6 1"
              >
                <mpath :href="`#lp-path-${minute.stream}`" />
              </animateMotion>
              <animate
                attributeName="opacity"
                values="0;1;1;0"
                keyTimes="0;0.12;0.82;1"
                :dur="`${minute.duration}s`"
                :begin="`${minute.delay}s`"
                repeatCount="indefinite"
              />
            </circle>
          </svg>
          </div>
        </div>

        <figcaption class="lp-flow__caption">
          <span class="lp-flow__caption-dot" aria-hidden="true" />
          今天的 24 小时，正在流向你选择的三件事
        </figcaption>
      </div>
    </section>

    <div class="lp-marquee" aria-hidden="true">
      <div class="lp-marquee__track">
        <span v-for="word in marqueeWords" :key="word.id">{{ word.text }}<i>◆</i></span>
      </div>
    </div>

    <section id="preview" class="lp-preview" ref="previewEl">
      <header class="lp-section-head" :class="{ 'is-in': previewVisible }">
        <p class="lp-kicker">产品一览</p>
        <h2>三个界面，一条完整的时间线</h2>
      </header>

      <div class="lp-preview__stage" :class="{ 'is-in': previewVisible }">
        <div class="lp-device">
          <div class="lp-device__bar" aria-hidden="true"><i /><i /><i /></div>
          <!-- All three stay mounted and cross-fade by class. A keyed
               <Transition> left the picture invisible whenever the enter
               transition did not run (a backgrounded tab, for one). -->
          <div class="lp-device__frame">
            <img
              v-for="(slide, index) in slides"
              :key="slide.id"
              class="lp-device__shot"
              :class="{ 'is-active': activeSlide === index }"
              :src="slide.image"
              :alt="slide.alt"
              :aria-hidden="activeSlide === index ? undefined : 'true'"
              decoding="async"
            />
          </div>
        </div>

        <ul class="lp-preview__tabs">
          <li v-for="(slide, index) in slides" :key="slide.id">
            <button
              type="button"
              :class="{ 'is-active': activeSlide === index }"
              :aria-current="activeSlide === index ? 'true' : undefined"
              @click="showSlide(index)"
            >
              <strong>{{ slide.kicker }}</strong>
              <span>{{ slide.title }}</span>
              <i class="lp-preview__timer" aria-hidden="true" />
            </button>
          </li>
        </ul>
      </div>
    </section>

    <section class="lp-features" ref="featuresEl" aria-label="核心能力">
      <article
        v-for="(item, index) in highlights"
        :key="item.title"
        class="lp-feature"
        :class="{ 'is-in': featuresVisible }"
        :style="{ '--step': index }"
      >
        <div class="lp-feature__art" aria-hidden="true" v-html="item.art" />
        <h3>{{ item.title }}</h3>
        <p>{{ item.text }}</p>
      </article>
    </section>

    <section class="lp-closing">
      <div class="lp-closing__card">
        <h2>今天就让计划流动起来</h2>
        <p>注册即用，数据存在你自己的空间里。</p>
        <RouterLink class="lp-cta lp-cta--large" :to="{ name: 'login', query: { mode: 'register' } }">
          <span>免费开始</span>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h13M13 6l6 6-6 6" /></svg>
        </RouterLink>
      </div>
    </section>

    <footer class="lp-footer">
      <AppLogo />
      <span>DayFlow · 让计划流动起来</span>
    </footer>
  </main>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, type CSSProperties } from 'vue'
import { RouterLink } from 'vue-router'

import AppLogo from '@/components/AppLogo.vue'

const slides = [
  {
    id: 'today',
    kicker: '今天',
    title: '专注计时与当日清单',
    image: '/welcome-today.png',
    alt: 'DayFlow 今日任务与专注计时界面',
  },
  {
    id: 'tasks',
    kicker: '项目',
    title: '项目 → 模块 → 任务',
    image: '/welcome-tasks.png',
    alt: 'DayFlow 项目与任务管理界面',
  },
  {
    id: 'analytics',
    kicker: '统计',
    title: '趋势、分布与预算偏差',
    image: '/welcome-analytics.png',
    alt: 'DayFlow 时间统计与趋势分析界面',
  },
] as const

const highlights = [
  {
    title: '组织任务',
    text: '用项目、模块和任务拆解复杂计划，结构清楚才执行得动。',
    art: `<svg viewBox="0 0 120 84"><rect class="a" x="4" y="30" width="34" height="24" rx="7"/><rect class="b" x="62" y="8" width="52" height="22" rx="7"/><rect class="b" x="62" y="54" width="52" height="22" rx="7"/><path class="l" d="M38 42C50 42 50 19 62 19" pathLength="1"/><path class="l" d="M38 42C50 42 50 65 62 65" pathLength="1"/></svg>`,
  },
  {
    title: '记录投入',
    text: '专注计时自动归集到任务与当日清单，不用手动记账。',
    art: `<svg viewBox="0 0 120 84"><circle class="t" cx="60" cy="44" r="28"/><circle class="r" cx="60" cy="44" r="28" pathLength="1"/><path class="h" d="M60 28v16l11 7"/></svg>`,
  },
  {
    title: '看见趋势',
    text: '日、周、月多粒度回看节奏，及时调整下一轮计划。',
    art: `<svg viewBox="0 0 120 84"><rect class="c" x="12" y="46" width="14" height="26" rx="5"/><rect class="c" x="35" y="32" width="14" height="40" rx="5"/><rect class="c" x="58" y="20" width="14" height="52" rx="5"/><rect class="c" x="81" y="38" width="14" height="34" rx="5"/></svg>`,
  },
] as const

const marqueeWords = [
  '专注计时',
  '时间预算',
  '项目任务树',
  '每日计划',
  '趋势分析',
  '离线可用',
  '伙伴协作',
  '连续打卡',
].flatMap((text, index) => [
  { id: `a-${index}`, text },
  { id: `b-${index}`, text },
])

const VESSEL_WIDTH = 72
const VESSEL_TOP = 96
const VESSEL_BOTTOM = 324

const buckets = [
  { id: 'study', x: 300, label: '课程学习', time: '3h 20m', height: 150 },
  { id: 'build', x: 386, label: '项目推进', time: '2h 05m', height: 104 },
  { id: 'read', x: 472, label: '阅读', time: '45m', height: 58 },
] as const

// One curve per destination, shared by the drawn stream and the dots riding
// it, so the artwork and the motion can never disagree. Each ends just above
// its vessel, where the minutes drop in.
const streams = [
  { id: 'study', d: 'M164 204C232 196 252 140 336 118' },
  { id: 'build', d: 'M164 211C244 214 340 176 422 118' },
  { id: 'read', d: 'M164 218C252 236 420 226 508 118' },
] as const

const MINUTES_PER_STREAM = 7
const minutes = streams.flatMap((stream, streamIndex) =>
  Array.from({ length: MINUTES_PER_STREAM }, (_, index) => ({
    id: `${stream.id}-${index}`,
    stream: stream.id,
    delay: Number((streamIndex * 0.55 + index * (3.6 / MINUTES_PER_STREAM)).toFixed(2)),
    duration: 3.6 + streamIndex * 0.4,
  })),
)

const flowLabel =
  '动画：分钟从时钟流出，沿三条曲线汇入课程学习、项目推进和阅读三个容器，容器随之逐渐填满'

/**
 * Scroll reveals only hide content once this is on. Keeping the hidden state
 * out of the base stylesheet means a visitor whose JavaScript or transitions
 * never run still reads a complete page instead of a blank one.
 */
const revealArmed = ref(false)
const reducedMotion = ref(false)
const scrolled = ref(false)
const activeSlide = ref(0)
const statsVisible = ref(false)
const previewVisible = ref(false)
const featuresVisible = ref(false)
const statsEl = ref<HTMLElement | null>(null)
const previewEl = ref<HTMLElement | null>(null)
const featuresEl = ref<HTMLElement | null>(null)
const pointer = ref({ x: 0.5, y: 0.3, active: false })
const magnet = ref({ x: 0, y: 0 })

const stats = [
  { label: '每天可分配', target: 24, unit: '小时', zero: '0', rendered: ref('0') },
  { label: '记录粒度', target: 1, unit: '秒', zero: '0', rendered: ref('0') },
  { label: '离线可用', target: 100, unit: '%', zero: '0', rendered: ref('0') },
]

const spotlightStyle = computed<CSSProperties>(() => ({
  opacity: pointer.value.active ? '1' : '0',
  transform: `translate3d(${pointer.value.x * 100}vw, ${pointer.value.y * 100}vh, 0)`,
}))

const parallaxStyle = computed<CSSProperties>(() => {
  if (reducedMotion.value) return {}
  const x = (pointer.value.x - 0.5) * 18
  const y = (pointer.value.y - 0.5) * 14
  return {
    transform: `perspective(1100px) rotateY(${x * 0.55}deg) rotateX(${-y * 0.55}deg) translate3d(${-x}px, ${-y}px, 0)`,
  }
})

const magneticStyle = computed<CSSProperties>(() =>
  reducedMotion.value
    ? {}
    : { transform: `translate3d(${magnet.value.x}px, ${magnet.value.y}px, 0)` },
)

let scrollFrame = 0
let slideTimer = 0
let observer: IntersectionObserver | null = null
let revealFallback = 0
let motionQuery: MediaQueryList | null = null

function onScroll(): void {
  if (scrollFrame) return
  scrollFrame = window.requestAnimationFrame(() => {
    scrolled.value = window.scrollY > 12
    scrollFrame = 0
  })
}

function trackPointer(event: PointerEvent): void {
  pointer.value = {
    x: event.clientX / window.innerWidth,
    y: event.clientY / window.innerHeight,
    active: true,
  }
}

function resetPointer(): void {
  pointer.value = { ...pointer.value, active: false }
}

/** Let the primary call to action lean a little toward the cursor. */
function trackMagnet(event: PointerEvent): void {
  const bounds = (event.currentTarget as HTMLElement).getBoundingClientRect()
  magnet.value = {
    x: (event.clientX - bounds.left - bounds.width / 2) * 0.22,
    y: (event.clientY - bounds.top - bounds.height / 2) * 0.3,
  }
}

function resetMagnet(): void {
  magnet.value = { x: 0, y: 0 }
}

function showSlide(index: number): void {
  activeSlide.value = index
  restartSlideTimer()
}

function restartSlideTimer(): void {
  window.clearInterval(slideTimer)
  if (reducedMotion.value) return
  slideTimer = window.setInterval(() => {
    activeSlide.value = (activeSlide.value + 1) % slides.length
  }, 5200)
}

/** Count a number up once its panel is on screen. */
function runCounters(): void {
  if (reducedMotion.value) {
    stats.forEach((stat) => {
      stat.rendered.value = String(stat.target)
    })
    return
  }
  const startedAt = performance.now()
  const duration = 1100
  const step = (now: number): void => {
    const progress = Math.min(1, (now - startedAt) / duration)
    // Ease-out cubic: fast first, settling gently on the real number.
    const eased = 1 - (1 - progress) ** 3
    stats.forEach((stat) => {
      stat.rendered.value = String(Math.round(stat.target * eased))
    })
    if (progress < 1) window.requestAnimationFrame(step)
  }
  window.requestAnimationFrame(step)
}

onMounted(() => {
  motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  reducedMotion.value = motionQuery.matches
  const onMotionChange = (event: MediaQueryListEvent): void => {
    reducedMotion.value = event.matches
    restartSlideTimer()
  }
  motionQuery.addEventListener('change', onMotionChange)

  window.addEventListener('scroll', onScroll, { passive: true })
  onScroll()
  restartSlideTimer()
  if (!reducedMotion.value) revealArmed.value = true

  observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue
        if (entry.target === statsEl.value && !statsVisible.value) {
          statsVisible.value = true
          runCounters()
        }
        if (entry.target === previewEl.value) previewVisible.value = true
        if (entry.target === featuresEl.value) featuresVisible.value = true
        observer?.unobserve(entry.target)
      }
    },
    { threshold: 0.25 },
  )
  for (const target of [statsEl.value, previewEl.value, featuresEl.value]) {
    if (target) observer.observe(target)
  }

  // Safety net: whatever happens to the observer, nothing stays hidden.
  revealFallback = window.setTimeout(() => {
    if (!statsVisible.value) {
      statsVisible.value = true
      runCounters()
    }
    previewVisible.value = true
    featuresVisible.value = true
  }, 2500)

  onBeforeUnmount(() => {
    motionQuery?.removeEventListener('change', onMotionChange)
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll)
  if (scrollFrame) window.cancelAnimationFrame(scrollFrame)
  window.clearInterval(slideTimer)
  window.clearTimeout(revealFallback)
  observer?.disconnect()
})
</script>
