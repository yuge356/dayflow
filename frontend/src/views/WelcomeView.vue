<template>
  <main class="jr" :class="{ 'jr--still': reducedMotion, 'jr--reveal': revealArmed }">
    <!-- Soft blue / mint / lavender wash. Decorative, transform-only. -->
    <div class="jr-wash" aria-hidden="true">
      <span class="jr-glow jr-glow--blue" />
      <span class="jr-glow jr-glow--mint" />
      <span class="jr-glow jr-glow--lavender" />
    </div>

    <header class="jr-nav" :class="{ 'is-stuck': scrolled }">
      <div class="jr-shell jr-nav__inner">
        <AppLogo />
        <nav class="jr-nav__actions" aria-label="账户入口">
          <RouterLink class="jr-quiet" :to="{ name: 'login' }">登录</RouterLink>
          <RouterLink class="jr-cta jr-cta--sm" :to="{ name: 'login', query: { mode: 'register' } }">
            免费开始
          </RouterLink>
        </nav>
      </div>
    </header>

    <section class="jr-hero">
      <div class="jr-shell jr-hero__inner">
        <p class="jr-eyebrow jr-rise" style="--i: 0">
          <span class="jr-live" aria-hidden="true" />
          学习旅程 · 一路累积
        </p>
        <h1 class="jr-title">
          <span class="jr-rise" style="--i: 1">一节一节学下去</span>
          <span class="jr-rise" style="--i: 2">整个计划就完成了</span>
        </h1>
        <p class="jr-lead jr-rise" style="--i: 3">
          看见每一分钟<br />
          如何积累成成果
        </p>
        <div class="jr-actions jr-rise" style="--i: 4">
          <RouterLink
            class="jr-cta jr-cta--lg"
            :style="magnetStyle"
            :to="{ name: 'login', query: { mode: 'register' } }"
            @pointermove.passive="trackMagnet"
            @pointerleave="resetMagnet"
          >
            <span>免费开始</span>
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h13M13 6l6 6-6 6" /></svg>
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- The journey: a tall track whose stage stays pinned, so scrolling
         scrubs the animation instead of merely moving past it. -->
    <section ref="journeyEl" class="jr-journey" :aria-label="journeyLabel">
      <div class="jr-stage">
        <div class="jr-shell jr-stage__inner">
          <aside class="jr-summary">
            <p class="jr-kicker">学习计划</p>
            <h2>机器学习入门</h2>

            <div class="jr-ring" role="img" :aria-label="`完成度 ${percent}%`">
              <svg viewBox="0 0 120 120">
                <defs>
                  <linearGradient id="jrRing" x1="0" y1="1" x2="1" y2="0">
                    <stop offset="0%" stop-color="#5b8cff" />
                    <stop offset="52%" stop-color="#a58cff" />
                    <stop offset="100%" stop-color="#47d7b0" />
                  </linearGradient>
                  <radialGradient id="jrRingCore">
                    <stop offset="0%" stop-color="#5b8cff" stop-opacity=".16" />
                    <stop offset="70%" stop-color="#a58cff" stop-opacity=".07" />
                    <stop offset="100%" stop-color="#47d7b0" stop-opacity="0" />
                  </radialGradient>
                </defs>

                <!-- The disc fills in as the ring closes, so the centre is not
                     an empty hole for most of the journey. -->
                <circle
                  cx="60"
                  cy="60"
                  r="47"
                  class="jr-ring__core"
                  :style="{ opacity: 0.25 + streamProgress * 0.75 }"
                />
                <circle cx="60" cy="60" r="52" class="jr-ring__track" />
                <circle
                  cx="60"
                  cy="60"
                  r="52"
                  class="jr-ring__value"
                  pathLength="1"
                  :style="{ strokeDashoffset: 1 - streamProgress }"
                />
                <!-- A bright head riding the end of the arc. -->
                <circle
                  :cx="ringHead.x"
                  :cy="ringHead.y"
                  r="5"
                  class="jr-ring__head"
                  :style="{ opacity: streamProgress > 0.01 ? 1 : 0 }"
                />
              </svg>
              <div class="jr-ring__center">
                <strong>{{ percent }}<i>%</i></strong>
                <span>已完成</span>
              </div>
            </div>

            <dl class="jr-summary__stats">
              <div>
                <dt>已完成</dt>
                <dd>{{ completedCount }} / {{ lessons.length }} 节</dd>
              </div>
              <div>
                <dt>累计投入</dt>
                <dd>{{ investedHours }} 小时</dd>
              </div>
            </dl>
          </aside>

          <div class="jr-stream">
            <div
              class="jr-beam"
              aria-hidden="true"
              :style="{ '--lit': streamProgress }"
            />

            <ul class="jr-cards">
              <li
                v-for="(lesson, index) in lessons"
                :key="lesson.id"
                class="jr-card"
                :class="cardState(index)"
                :style="cardStyle(index)"
              >
                <span class="jr-card__node" aria-hidden="true">
                  <svg viewBox="0 0 24 24"><path d="M5 12.5 10 17l9-10" pathLength="1" /></svg>
                </span>
                <div class="jr-card__body">
                  <p class="jr-card__meta">
                    <span>第 {{ index + 1 }} 节</span>
                    <span>{{ lesson.hours }}h</span>
                  </p>
                  <h3>{{ lesson.title }}</h3>
                  <div class="jr-card__bar">
                    <i :style="{ transform: `scaleX(${lessonFill(index)})` }" />
                  </div>
                  <p class="jr-card__foot">
                    <span>{{ Math.round(lessonFill(index) * 100) }}%</span>
                    <span>{{ lesson.topic }}</span>
                  </p>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <!-- Arrives only at the end of the track. -->
        <div class="jr-finale" :class="{ 'is-on': finale > 0 }" :style="{ opacity: finale }">
          <div class="jr-finale__card" :style="{ transform: `scale(${0.94 + finale * 0.06})` }">
            <span class="jr-finale__spark" aria-hidden="true" />
            <p class="jr-kicker">学习路线完成</p>
            <strong>100%</strong>
            <h2>机器学习入门 · 全部完成</h2>
            <p>{{ lessons.length }} 节课 · 累计 {{ totalHours }} 小时，全部由计时记录累积而来。</p>
            <RouterLink class="jr-cta jr-cta--lg" :to="{ name: 'login', query: { mode: 'register' } }">
              <span>开始你的计划</span>
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h13M13 6l6 6-6 6" /></svg>
            </RouterLink>
          </div>
        </div>
      </div>
    </section>

    <section class="jr-templates">
      <div class="jr-shell">
        <header :ref="registerReveal" class="jr-head jr-slide">
          <p class="jr-kicker">从模板开始</p>
          <h2>三种计划，开箱即用</h2>
        </header>

        <div class="jr-templates__grid">
          <article
            v-for="(template, index) in templates"
            :key="template.id"
            :ref="registerReveal"
            class="jr-template jr-slide"
            :style="{ '--i': index, '--accent': template.accent }"
          >
            <span class="jr-template__badge" aria-hidden="true">{{ template.icon }}</span>
            <h3>{{ template.name }}</h3>
            <p>{{ template.text }}</p>
            <ul class="jr-template__outline">
              <li v-for="step in template.outline" :key="step">
                <i aria-hidden="true" />
                {{ step }}
              </li>
            </ul>
            <p class="jr-template__foot">{{ template.meta }}</p>
          </article>
        </div>
      </div>
    </section>

    <section class="jr-band">
      <div class="jr-shell">
        <article
          v-for="(item, index) in pillars"
          :key="item.title"
          :ref="registerReveal"
          class="jr-pillar jr-slide"
          :style="{ '--i': index }"
        >
          <span class="jr-pillar__dot" aria-hidden="true" />
          <h3>{{ item.title }}</h3>
          <p>{{ item.text }}</p>
        </article>
      </div>
    </section>

    <section id="preview" class="jr-preview">
      <div class="jr-shell">
        <header :ref="registerReveal" class="jr-head jr-slide">
          <p class="jr-kicker">产品一览</p>
          <h2>三个界面，一条完整的时间线</h2>
        </header>

        <div :ref="registerReveal" class="jr-preview__grid jr-slide">
          <div class="jr-window">
            <div class="jr-window__bar" aria-hidden="true">
              <i /><i /><i />
              <span>{{ shots[activeShot]!.title }}</span>
            </div>
            <div class="jr-window__frame">
              <img
                v-for="(shot, index) in shots"
                :key="shot.id"
                class="jr-window__shot"
                :class="{ 'is-active': activeShot === index }"
                :src="shot.image"
                :alt="shot.alt"
                :aria-hidden="activeShot === index ? undefined : 'true'"
                decoding="async"
              />
            </div>
          </div>

          <ul class="jr-tabs">
            <li v-for="(shot, index) in shots" :key="shot.id">
              <button
                type="button"
                :class="{ 'is-active': activeShot === index }"
                :aria-current="activeShot === index ? 'true' : undefined"
                @click="showShot(index)"
              >
                <strong>{{ shot.kicker }}</strong>
                <span>{{ shot.title }}</span>
                <i class="jr-tabs__timer" aria-hidden="true" />
              </button>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <section class="jr-closing">
      <div class="jr-shell">
        <div :ref="registerReveal" class="jr-closing__card jr-slide">
          <h2>让今天的专注，落在计划上</h2>
          <p>注册即用，数据存在你自己的空间里。</p>
          <RouterLink class="jr-cta jr-cta--lg" :to="{ name: 'login', query: { mode: 'register' } }">
            <span>免费开始</span>
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h13M13 6l6 6-6 6" /></svg>
          </RouterLink>
        </div>
      </div>
    </section>

    <footer class="jr-footer">
      <div class="jr-shell jr-footer__inner">
        <AppLogo />
        <span>DayFlow · 让计划流动起来</span>
      </div>
    </footer>
  </main>
</template>

<script setup lang="ts">
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  type ComponentPublicInstance,
  type CSSProperties,
} from 'vue'
import { RouterLink } from 'vue-router'

import AppLogo from '@/components/AppLogo.vue'

const shots = [
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

const templates = [
  {
    id: 'study',
    name: '学习课程',
    icon: '📘',
    accent: '#5b8cff',
    text: '把一门课拆成章节与练习，按周推进。',
    outline: ['课程大纲', '每章任务', '练习与复盘'],
    meta: '适合网课、教材、语言学习',
  },
  {
    id: 'exam',
    name: '考试备考',
    icon: '🎯',
    accent: '#a58cff',
    text: '倒推考试日期，安排复习轮次与模考。',
    outline: ['考纲拆解', '三轮复习', '真题与模考'],
    meta: '适合升学、证书、资格考试',
  },
  {
    id: 'project',
    name: '项目推进',
    icon: '🚀',
    accent: '#47d7b0',
    text: '按里程碑组织模块，跟踪投入与偏差。',
    outline: ['里程碑', '模块拆分', '交付与验收'],
    meta: '适合毕设、副业、团队项目',
  },
] as const

const pillars = [
  { title: '一节一节推进', text: '把课程拆成可执行的小节，每节都有自己的计划用时。' },
  { title: '时间自动累积', text: '专注计时归集到每节课，学过多久不用自己记。' },
  { title: '进度看得见', text: '完成度只认真实计时，不靠感觉估算。' },
] as const

const lessons = [
  { id: 'basics', title: 'Python 基础语法', hours: 6, topic: '语言基础' },
  { id: 'data', title: '数据结构与算法', hours: 10, topic: '编程基本功' },
  { id: 'math', title: '线性代数复习', hours: 8, topic: '数学准备' },
  { id: 'intro', title: '机器学习导论', hours: 12, topic: '核心概念' },
  { id: 'nn', title: '神经网络实战', hours: 14, topic: '动手实践' },
  { id: 'capstone', title: '毕业项目', hours: 10, topic: '综合应用' },
] as const

const totalHours = lessons.reduce((sum, lesson) => sum + lesson.hours, 0)

/** Fraction of the track spent on the closing celebration. */
const FINALE_SHARE = 0.16

const progress = ref(0)
const stageHeight = ref(720)
/**
 * Read before the first paint, so the page never renders its content and then
 * fades it out again. Nothing is hidden unless `revealArmed` is on, which only
 * happens when scripts run — a visitor without them reads a complete page.
 */
const reducedMotion = ref(
  typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches,
)
const revealArmed = ref(!reducedMotion.value)
const scrolled = ref(false)
const activeShot = ref(0)
const journeyEl = ref<HTMLElement | null>(null)
const revealTargets = new Set<Element>()
const magnet = ref({ x: 0, y: 0 })

/** How far the lesson stream itself has run, ignoring the closing card. */
const streamProgress = computed(() =>
  Math.min(1, progress.value / (1 - FINALE_SHARE)),
)

/** The fractional lesson currently sitting in the middle of the stage. */
const head = computed(() => streamProgress.value * lessons.length)

/**
 * Where the column sits, which is not the same as how far the head has run: a
 * lesson stays parked in the centre while its bar fills, and only then slides
 * up to let the next one in. Without the hold, a card drifted out of the
 * centre while still only part-finished.
 */
const HOLD = 0.72
const layoutHead = computed(() => {
  const whole = Math.floor(head.value)
  const frac = head.value - whole
  return whole + (frac <= HOLD ? 0 : (frac - HOLD) / (1 - HOLD))
})

const percent = computed(() => Math.round(streamProgress.value * 100))

/** Where the arc currently ends, for the bright head that rides it. */
const ringHead = computed(() => {
  const angle = (-90 + streamProgress.value * 360) * (Math.PI / 180)
  return {
    x: Number((60 + 52 * Math.cos(angle)).toFixed(2)),
    y: Number((60 + 52 * Math.sin(angle)).toFixed(2)),
  }
})

const completedCount = computed(() =>
  Math.min(lessons.length, Math.floor(head.value)),
)

const investedHours = computed(() => {
  let total = 0
  lessons.forEach((lesson, index) => {
    total += lesson.hours * lessonFill(index)
  })
  return Math.round(total)
})

/** 0 until the stream is done, then eases the celebration in. */
const finale = computed(() => {
  const start = 1 - FINALE_SHARE * 0.7
  if (progress.value <= start) return 0
  return Math.min(1, (progress.value - start) / (1 - start))
})

const journeyLabel =
  '滚动驱动的学习旅程：课程逐节进入画面中央、进度条填满并完成后向上堆叠，计划完成度随滚动持续上升，最后展示全部完成的路线图'

function lessonFill(index: number): number {
  return Math.max(0, Math.min(1, head.value - index))
}

function cardState(index: number): Record<string, boolean> {
  // Read from the bar itself, so "completed" always means a full bar.
  const fill = lessonFill(index)
  return {
    'is-done': fill >= 1,
    'is-active': fill > 0 && fill < 1,
    'is-next': fill <= 0,
  }
}

/**
 * Lay the lessons out as one continuous column that slides upward as the head
 * advances. Finished lessons keep moving but with a much smaller gap, so they
 * collect into a compact stack at the top instead of drifting off screen.
 */
function cardStyle(index: number): CSSProperties {
  const spacing = Math.max(112, Math.min(168, stageHeight.value * 0.2))
  const doneSpacing = 36
  const delta = index - layoutHead.value
  const distance = Math.abs(delta)
  // Finished lessons collect into a small pile above the centre: tighter
  // spacing, smaller, and fading out quickly so only the most recent few read.
  // Below the centre lessons queue at full spacing. Above it they first clear
  // the active card by `baseGap`, then pile up tightly. Splitting it this way
  // keeps the motion continuous across the centre instead of jumping.
  const baseGap = Math.max(104, spacing * 0.78)
  const offset =
    delta >= 0
      ? delta * spacing
      : delta > -1
        ? delta * baseGap
        : -(baseGap + (distance - 1) * doneSpacing)
  const scale =
    delta < 0
      ? Math.max(0.66, 0.82 - (distance - 1) * 0.05)
      : Math.max(0.86, 1 - distance * 0.05)
  const opacity =
    delta < 0
      ? Math.max(0, 0.62 - Math.max(0, distance - 1) * 0.26)
      : Math.max(0, 1 - Math.max(0, distance - 0.6) * 0.42)
  return {
    transform: `translate3d(-50%, calc(-50% + ${offset.toFixed(1)}px), 0) scale(${scale.toFixed(3)})`,
    opacity: String(Number(opacity.toFixed(3))),
    zIndex: String(100 - index),
  }
}

const magnetStyle = computed<CSSProperties>(() =>
  reducedMotion.value ? {} : { transform: `translate3d(${magnet.value.x}px, ${magnet.value.y}px, 0)` },
)

let shotTimer = 0
let revealFallback = 0
let motionQuery: MediaQueryList | null = null

/** Collect the blocks that slide in and out with the scroll. */
function registerReveal(element: Element | ComponentPublicInstance | null): void {
  if (!(element instanceof Element)) return
  revealTargets.add(element)
}

/**
 * Slide blocks in as they rise past a line near the bottom of the viewport,
 * and let them retract when they drop back below it. Measuring rects each time
 * keeps the two directions exactly symmetric.
 */
function updateReveal(): void {
  if (!revealArmed.value) return
  const trigger = window.innerHeight * 0.86
  for (const element of revealTargets) {
    element.classList.toggle('is-in', element.getBoundingClientRect().top < trigger)
  }
}

/**
 * Turn scroll position into journey progress. The track is taller than the
 * viewport and its stage is sticky, so the span between "track top reaches the
 * top of the screen" and "track bottom does" is exactly the animation.
 */
function updateJourney(): void {
  const section = journeyEl.value
  if (!section) return
  stageHeight.value = window.innerHeight
  if (reducedMotion.value) {
    progress.value = 1
    return
  }
  const rect = section.getBoundingClientRect()
  const travel = rect.height - window.innerHeight
  if (travel <= 0) {
    progress.value = rect.top <= 0 ? 1 : 0
    return
  }
  progress.value = Math.max(0, Math.min(1, -rect.top / travel))
}

function onScroll(): void {
  // Browsers already fire scroll at most once per frame, and this reads a
  // handful of rects; requestAnimationFrame here would only add a way for the
  // work to be skipped when frames are throttled.
  scrolled.value = window.scrollY > 12
  updateJourney()
  updateReveal()
}

/** Let the primary call to action lean a little toward the cursor. */
function trackMagnet(event: PointerEvent): void {
  const bounds = (event.currentTarget as HTMLElement).getBoundingClientRect()
  magnet.value = {
    x: (event.clientX - bounds.left - bounds.width / 2) * 0.2,
    y: (event.clientY - bounds.top - bounds.height / 2) * 0.28,
  }
}

function resetMagnet(): void {
  magnet.value = { x: 0, y: 0 }
}

function showShot(index: number): void {
  activeShot.value = index
  restartShotTimer()
}

function restartShotTimer(): void {
  window.clearInterval(shotTimer)
  if (reducedMotion.value) return
  shotTimer = window.setInterval(() => {
    activeShot.value = (activeShot.value + 1) % shots.length
  }, 5200)
}

onMounted(() => {
  motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  const onMotionChange = (event: MediaQueryListEvent): void => {
    reducedMotion.value = event.matches
    revealArmed.value = !event.matches
    restartShotTimer()
    onScroll()
  }
  motionQuery.addEventListener('change', onMotionChange)

  window.addEventListener('scroll', onScroll, { passive: true })
  window.addEventListener('resize', onScroll, { passive: true })
  restartShotTimer()

  onScroll()
  // Template refs on a v-for can land after this hook; run once more when they
  // have, so blocks already in view are revealed without a scroll.
  void nextTick(updateReveal)

  // If the refs never registered, stop hiding anything rather than leaving a
  // blank page behind.
  revealFallback = window.setTimeout(() => {
    if (revealTargets.size === 0) revealArmed.value = false
  }, 2000)

  onBeforeUnmount(() => {
    motionQuery?.removeEventListener('change', onMotionChange)
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll)
  window.removeEventListener('resize', onScroll)
  window.clearInterval(shotTimer)
  window.clearTimeout(revealFallback)
  revealTargets.clear()
})
</script>
