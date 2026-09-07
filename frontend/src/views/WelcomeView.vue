<template>
  <main class="lp" :class="{ 'lp--still': reducedMotion, 'lp--reveal': revealArmed }">
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

    <section class="lp-hero">
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
          从一项子任务开始，进度沿着任务树一路汇聚，<br />
          直到整个项目被点亮。
        </p>

        <div class="lp-hero__actions lp-reveal" style="--step: 4">
          <RouterLink
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

      <!-- The product's core idea, animated: a leaf task is finished, the
           colour travels up the connector, its module fills, and finally the
           whole project is complete. Everything lives inside one viewBox, so
           the artwork scales as a single piece on any screen. -->
      <div class="lp-stage" role="img" :aria-label="stageLabel">
        <div class="lp-window">
          <div class="lp-window__bar" aria-hidden="true">
            <i class="lp-window__dot lp-window__dot--red" />
            <i class="lp-window__dot lp-window__dot--amber" />
            <i class="lp-window__dot lp-window__dot--green" />
            <span class="lp-window__title">项目任务树</span>
          </div>

          <svg class="lp-tree" viewBox="0 0 760 470" aria-hidden="true">
            <defs>
              <!-- The completed colour never sits still: the gradient drifts
                   across the card and a soft highlight sweeps over it, so the
                   fill reads as liquid rather than a flat swatch. -->
              <linearGradient id="lpLiquid" x1="0" y1="1" x2="1" y2="0">
                <stop offset="0%" stop-color="#ffb37a" />
                <stop offset="26%" stop-color="#ff8ecb" />
                <stop offset="54%" stop-color="#b48cff" />
                <stop offset="78%" stop-color="#7cc4ff" />
                <stop offset="100%" stop-color="#7fe6dd" />
              </linearGradient>

              <linearGradient id="lpSheen" x1="0" y1="0" x2="1" y2="0.3">
                <stop offset="0%" stop-color="#ffffff" stop-opacity="0" />
                <stop offset="42%" stop-color="#ffffff" stop-opacity=".5" />
                <stop offset="58%" stop-color="#ffffff" stop-opacity=".5" />
                <stop offset="100%" stop-color="#ffffff" stop-opacity="0" />
              </linearGradient>
            </defs>

            <!-- Connectors: a hairline always, plus a bright overlay that
                 draws itself once the node it leaves is finished. -->
            <g class="lp-links">
              <g v-for="link in links" :key="link.id">
                <path :d="link.d" class="lp-link" />
                <path
                  :d="link.d"
                  class="lp-link-live"
                  :class="{ 'is-lit': isDone(link.from) }"
                  pathLength="1"
                />
                <circle
                  :cx="link.dotX"
                  :cy="link.dotY"
                  r="3.4"
                  class="lp-link-dot"
                  :class="{ 'is-lit': isDone(link.from) }"
                />
              </g>
            </g>

            <g
              v-for="node in nodes"
              :key="node.id"
              class="lp-node"
              :class="[`lp-node--${node.kind}`, { 'is-done': isDone(node.id) }]"
            >
              <rect
                :x="node.x"
                :y="node.y"
                :width="node.w"
                :height="node.h"
                :rx="node.kind === 'root' ? 20 : 16"
                class="lp-node__glass"
              />
              <clipPath :id="`lp-clip-${node.id}`">
                <rect
                  :x="node.x"
                  :y="node.y"
                  :width="node.w"
                  :height="node.h"
                  :rx="node.kind === 'root' ? 20 : 16"
                  class="lp-node__clip"
                />
              </clipPath>
              <g class="lp-node__fill" :clip-path="`url(#lp-clip-${node.id})`">
                <rect
                  :x="node.x - node.w * 0.55"
                  :y="node.y"
                  :width="node.w * 2.1"
                  :height="node.h"
                  class="lp-node__liquid"
                />
                <rect
                  :x="node.x - node.w * 0.9"
                  :y="node.y - 4"
                  :width="node.w * 0.62"
                  :height="node.h + 8"
                  class="lp-node__sheen"
                />
              </g>

              <text :x="node.x + 16" :y="node.y + METRICS[node.kind].label" class="lp-node__label">
                {{ node.label }}
              </text>
              <text :x="node.x + 16" :y="node.y + METRICS[node.kind].title" class="lp-node__title">
                {{ node.title }}
              </text>
              <text :x="node.x + 16" :y="node.y + METRICS[node.kind].meta" class="lp-node__hours">
                {{ isDone(node.id) ? '100%' : node.hours }}
              </text>

              <rect
                :x="node.x + node.w - 64"
                :y="node.y + 11"
                width="50"
                height="17"
                rx="8.5"
                class="lp-node__pill"
              />
              <text :x="node.x + node.w - 39" :y="node.y + 23" class="lp-node__pill-text">
                {{ isDone(node.id) ? '已完成' : '进行中' }}
              </text>

              <path :d="checkPath(node)" class="lp-node__check" pathLength="1" />
            </g>
          </svg>
        </div>

        <p class="lp-stage__caption" aria-live="polite">
          <span class="lp-stage__dot" aria-hidden="true" />
          {{ stageCaption }}
        </p>
      </div>
    </section>

    <section id="preview" class="lp-preview">
      <header :ref="registerReveal" class="lp-section-head lp-slide">
        <p class="lp-kicker">产品一览</p>
        <h2>三个界面，一条完整的时间线</h2>
      </header>

      <div :ref="registerReveal" class="lp-preview__stage lp-slide">
        <div class="lp-window lp-window--shot">
          <div class="lp-window__bar" aria-hidden="true">
            <i class="lp-window__dot lp-window__dot--red" />
            <i class="lp-window__dot lp-window__dot--amber" />
            <i class="lp-window__dot lp-window__dot--green" />
            <span class="lp-window__title">{{ slides[activeSlide]!.title }}</span>
          </div>
          <!-- All three stay mounted and cross-fade by class: a keyed
               <Transition> leaves the picture invisible whenever its enter
               transition does not run. -->
          <div class="lp-shot-frame">
            <img
              v-for="(slide, index) in slides"
              :key="slide.id"
              class="lp-shot"
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

    <section class="lp-features" aria-label="核心能力">
      <article
        v-for="(item, index) in highlights"
        :key="item.title"
        :ref="registerReveal"
        class="lp-feature lp-slide"
        :style="{ '--step': index }"
      >
        <div class="lp-feature__art" aria-hidden="true" v-html="item.art" />
        <h3>{{ item.title }}</h3>
        <p>{{ item.text }}</p>
      </article>
    </section>

    <section class="lp-closing">
      <div :ref="registerReveal" class="lp-closing__card lp-slide">
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
    art: `<svg viewBox="0 0 120 84"><rect class="a" x="4" y="30" width="34" height="24" rx="8"/><rect class="b" x="62" y="8" width="52" height="22" rx="8"/><rect class="b" x="62" y="54" width="52" height="22" rx="8"/><path class="l" d="M38 42C50 42 50 19 62 19" pathLength="1"/><path class="l" d="M38 42C50 42 50 65 62 65" pathLength="1"/></svg>`,
  },
  {
    title: '记录投入',
    text: '专注计时自动归集到任务与当日清单，不用手动记账。',
    art: `<svg viewBox="0 0 120 84"><circle class="t" cx="60" cy="44" r="28"/><circle class="r" cx="60" cy="44" r="28" pathLength="1"/><path class="h" d="M60 28v16l11 7"/></svg>`,
  },
  {
    title: '看见趋势',
    text: '日、周、月多粒度回看节奏，及时调整下一轮计划。',
    art: `<svg viewBox="0 0 120 84"><rect class="c" x="12" y="46" width="14" height="26" rx="6"/><rect class="c" x="35" y="32" width="14" height="40" rx="6"/><rect class="c" x="58" y="20" width="14" height="52" rx="6"/><rect class="c" x="81" y="38" width="14" height="34" rx="6"/></svg>`,
  },
] as const

type NodeKind = 'root' | 'module' | 'leaf'

interface TreeNode {
  id: string
  kind: NodeKind
  label: string
  title: string
  hours: string
  x: number
  y: number
  w: number
  h: number
  /** Position in the completion sequence; the root finishes last. */
  order: number
}

/**
 * Baselines inside a card, measured from its top edge. Written out per kind
 * rather than derived, because deriving them from the card height is exactly
 * what pushed the title and the hours onto the same line.
 */
const METRICS: Record<NodeKind, { label: number; title: number; meta: number; check: number }> = {
  root: { label: 26, title: 58, meta: 84, check: 38 },
  module: { label: 23, title: 50, meta: 74, check: 30 },
  leaf: { label: 22, title: 48, meta: 72, check: 28 },
}

const nodes: TreeNode[] = [
  { id: 'root', kind: 'root', label: '项目', title: 'DayFlow 发布', hours: '50h', x: 12, y: 186, w: 204, h: 100, order: 7 },
  { id: 'mod-a', kind: 'module', label: '模块', title: '体验设计', hours: '22h', x: 274, y: 84, w: 182, h: 88, order: 3 },
  { id: 'mod-b', kind: 'module', label: '模块', title: '数据能力', hours: '28h', x: 274, y: 292, w: 182, h: 88, order: 6 },
  { id: 'leaf-a1', kind: 'leaf', label: '任务', title: '界面原型', hours: '6h', x: 548, y: 28, w: 196, h: 84, order: 1 },
  { id: 'leaf-a2', kind: 'leaf', label: '任务', title: '任务树动效', hours: '10h', x: 548, y: 122, w: 196, h: 84, order: 2 },
  { id: 'leaf-b1', kind: 'leaf', label: '任务', title: '时间统计', hours: '8h', x: 548, y: 240, w: 196, h: 84, order: 4 },
  { id: 'leaf-b2', kind: 'leaf', label: '任务', title: '数据同步', hours: '20h', x: 548, y: 334, w: 196, h: 84, order: 5 },
]

const nodeById = new Map(nodes.map((node) => [node.id, node]))

/** One connector, drawn child → parent: the direction completion travels. */
function buildLink(fromId: string, toId: string) {
  const from = nodeById.get(fromId)!
  const to = nodeById.get(toId)!
  const x1 = from.x
  const y1 = from.y + from.h / 2
  const x2 = to.x + to.w
  const y2 = to.y + to.h / 2
  return {
    id: `${fromId}-${toId}`,
    from: fromId,
    d: `M${x1} ${y1}C${x1 - 46} ${y1}, ${x2 + 46} ${y2}, ${x2} ${y2}`,
    dotX: (x1 + x2) / 2,
    dotY: (y1 + y2) / 2,
  }
}

const links = [
  buildLink('leaf-a1', 'mod-a'),
  buildLink('leaf-a2', 'mod-a'),
  buildLink('leaf-b1', 'mod-b'),
  buildLink('leaf-b2', 'mod-b'),
  buildLink('mod-a', 'root'),
  buildLink('mod-b', 'root'),
]

const LAST_ORDER = 7
const STEP_MS = 900
const HOLD_STEPS = 3

/** A tick in the card's lower-right corner, clear of every text row. */
function checkPath(node: TreeNode): string {
  const size = METRICS[node.kind].check
  const cx = node.x + node.w - (node.kind === 'root' ? 46 : 38)
  const cy = node.y + node.h * 0.62
  return `M${cx - size / 2} ${cy} l${size * 0.3} ${size * 0.31} l${size * 0.58} -${size * 0.62}`
}

const stageStep = ref(0)
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
const activeSlide = ref(0)
const statsVisible = ref(false)
const statsEl = ref<HTMLElement | null>(null)
const revealTargets = new Set<Element>()
const magnet = ref({ x: 0, y: 0 })

function isDone(nodeId: string): boolean {
  const node = nodeById.get(nodeId)
  return node ? stageStep.value >= node.order : false
}

const stageCaption = computed(() => {
  if (stageStep.value >= LAST_ORDER) return '项目完成 · 50 小时全部兑现'
  if (stageStep.value >= 4) return '第二个模块正在汇聚…'
  if (stageStep.value >= 3) return '模块「体验设计」已完成'
  if (stageStep.value >= 1) return '子任务完成，进度沿任务树上传'
  return '从一项子任务开始'
})

const stageLabel =
  '动画：任务树中的子任务逐个完成并被渐变色填充，颜色沿连接线汇聚到所属模块，最后整个项目被填满并打勾'

const stats = [
  { label: '每天可分配', target: 24, unit: '小时', zero: '0', rendered: ref('0') },
  { label: '记录粒度', target: 1, unit: '秒', zero: '0', rendered: ref('0') },
  { label: '离线可用', target: 100, unit: '%', zero: '0', rendered: ref('0') },
]

const magneticStyle = computed<CSSProperties>(() =>
  reducedMotion.value
    ? {}
    : { transform: `translate3d(${magnet.value.x}px, ${magnet.value.y}px, 0)` },
)

let slideTimer = 0
let stageTimer = 0
let revealFallback = 0
let motionQuery: MediaQueryList | null = null

/**
 * Collect the blocks that slide in and out with the scroll. Template refs on
 * a v-for hand back the element on mount and null on unmount.
 */
function registerReveal(element: Element | ComponentPublicInstance | null): void {
  if (!(element instanceof Element)) return
  revealTargets.add(element)
}

/**
 * Slide blocks in as they rise past a line near the bottom of the viewport,
 * and let them retract when they drop back below it. Measuring rects on each
 * frame keeps the two directions exactly symmetric, which is the whole point
 * of the effect — an IntersectionObserver would need paired margins to do the
 * same and still only reports at threshold crossings.
 */
function updateReveal(): void {
  if (!revealArmed.value) return
  const trigger = window.innerHeight * 0.86
  for (const element of revealTargets) {
    element.classList.toggle('is-in', element.getBoundingClientRect().top < trigger)
  }
  if (!statsVisible.value && statsEl.value) {
    if (statsEl.value.getBoundingClientRect().top < trigger) {
      statsVisible.value = true
      runCounters()
    }
  }
}

function onScroll(): void {
  // Browsers already fire scroll at most once per frame, and this reads six
  // rects; wrapping it in requestAnimationFrame only adds a way for the work
  // to be skipped entirely when frames are throttled.
  scrolled.value = window.scrollY > 12
  updateReveal()
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

/**
 * Walk the tree from leaves to root, hold the finished state for a moment,
 * then start over. Reduced motion gets the finished tree with no cycling.
 */
function restartStageTimer(): void {
  window.clearInterval(stageTimer)
  if (reducedMotion.value) {
    stageStep.value = LAST_ORDER
    return
  }
  stageStep.value = 0
  stageTimer = window.setInterval(() => {
    stageStep.value = stageStep.value >= LAST_ORDER + HOLD_STEPS ? 0 : stageStep.value + 1
  }, STEP_MS)
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
  const onMotionChange = (event: MediaQueryListEvent): void => {
    reducedMotion.value = event.matches
    revealArmed.value = !event.matches
    restartSlideTimer()
    restartStageTimer()
  }
  motionQuery.addEventListener('change', onMotionChange)

  window.addEventListener('scroll', onScroll, { passive: true })
  restartSlideTimer()
  restartStageTimer()
  updateReveal()
  // Template refs on a v-for can land after this hook; run once more when
  // they have, so blocks already in view are revealed without a scroll.
  void nextTick(updateReveal)

  // If the refs never registered, stop hiding anything rather than leaving a
  // blank page behind.
  revealFallback = window.setTimeout(() => {
    if (revealTargets.size === 0) revealArmed.value = false
  }, 2000)

  window.addEventListener('resize', onScroll, { passive: true })
  updateReveal()

  onBeforeUnmount(() => {
    motionQuery?.removeEventListener('change', onMotionChange)
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll)
  window.removeEventListener('resize', onScroll)
  window.clearInterval(slideTimer)
  window.clearInterval(stageTimer)
  window.clearTimeout(revealFallback)
  revealTargets.clear()
})
</script>
