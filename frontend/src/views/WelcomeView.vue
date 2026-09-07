<template>
  <main class="hx" :class="{ 'hx--still': reducedMotion, 'hx--reveal': revealArmed }">
    <!-- Volumetric field: a few very large liquid-glass spheres drifting far
         behind everything else. Decorative, transform-only, never in the way. -->
    <div class="hx-field" aria-hidden="true">
      <span class="hx-sphere hx-sphere--one" />
      <span class="hx-sphere hx-sphere--two" />
      <span class="hx-sphere hx-sphere--three" />
      <span class="hx-sphere hx-sphere--four" />
      <span class="hx-aurora" />
    </div>

    <header class="hx-nav" :class="{ 'is-stuck': scrolled }">
      <div class="hx-shell hx-nav__inner">
        <AppLogo />
        <nav class="hx-nav__actions" aria-label="账户入口">
          <RouterLink class="hx-quiet" :to="{ name: 'login' }">登录</RouterLink>
          <RouterLink class="hx-cta hx-cta--sm" :to="{ name: 'login', query: { mode: 'register' } }">
            免费开始
          </RouterLink>
        </nav>
      </div>
    </header>

    <section class="hx-hero">
      <div class="hx-shell hx-hero__inner">
        <div class="hx-copy">
          <p class="hx-eyebrow hx-rise" style="--i: 0">
            <span class="hx-live" aria-hidden="true" />
            正在运转的生产力网络
          </p>
          <h1 class="hx-title">
            <span class="hx-rise" style="--i: 1">每一分钟</span>
            <span class="hx-rise" style="--i: 2">都在推进项目</span>
          </h1>
          <p class="hx-lead hx-rise" style="--i: 3">
            项目、任务与专注计时连成一张网。<br />
            时间在其中流动，进度随之向前。
          </p>
          <div class="hx-actions hx-rise" style="--i: 4">
            <RouterLink
              class="hx-cta hx-cta--lg"
              :style="magnetStyle"
              :to="{ name: 'login', query: { mode: 'register' } }"
              @pointermove.passive="trackMagnet"
              @pointerleave="resetMagnet"
            >
              <span>免费开始</span>
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h13M13 6l6 6-6 6" /></svg>
            </RouterLink>
            <a class="hx-quiet hx-quiet--arrow" href="#preview">看看 DayFlow</a>
          </div>
        </div>

        <!-- The living network. Cards, links, particles and the timeline all
             live in one viewBox, so the whole scene scales as a single piece
             and the particles can never drift off the curves they ride. -->
        <div class="hx-stage" role="img" :aria-label="stageLabel">
          <svg class="hx-net" viewBox="0 0 980 620" :style="parallaxStyle">
            <defs>
              <linearGradient id="hxFlow" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stop-color="#4A7DFF" stop-opacity="0" />
                <stop offset="42%" stop-color="#50E3FF" stop-opacity=".85" />
                <stop offset="100%" stop-color="#7CFFD0" stop-opacity=".25" />
              </linearGradient>
              <linearGradient id="hxProgress" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stop-color="#4A7DFF" />
                <stop offset="55%" stop-color="#50E3FF" />
                <stop offset="100%" stop-color="#7CFFD0" />
              </linearGradient>
              <linearGradient id="hxRing" x1="0" y1="1" x2="1" y2="0">
                <stop offset="0%" stop-color="#B9A4FF" />
                <stop offset="50%" stop-color="#50E3FF" />
                <stop offset="100%" stop-color="#7CFFD0" />
              </linearGradient>
              <radialGradient id="hxHalo">
                <stop offset="0%" stop-color="#50E3FF" stop-opacity=".38" />
                <stop offset="100%" stop-color="#50E3FF" stop-opacity="0" />
              </radialGradient>
            </defs>

            <!-- Long-range planning, sitting furthest back. -->
            <g class="hx-timeline">
              <g v-for="(mark, index) in timeline" :key="mark.label" :style="{ '--i': index }">
                <line :x1="mark.x" y1="66" :x2="mark.x" y2="566" class="hx-timeline__rule" />
                <text :x="mark.x" y="46" class="hx-timeline__label">{{ mark.label }}</text>
              </g>
            </g>

            <g class="hx-links">
              <path v-for="link in links" :key="link.id" :d="link.d" class="hx-link" />
              <path
                v-for="link in links"
                :key="`lit-${link.id}`"
                :d="link.d"
                class="hx-link-lit"
                :class="{ 'is-lit': isDone(link.to) }"
                pathLength="1"
              />
            </g>

            <!-- Time, made visible: light travelling the same curves. -->
            <g class="hx-particles">
              <circle
                v-for="dot in particles"
                :key="dot.id"
                r="3"
                class="hx-dot"
                :style="{
                  offsetPath: `path('${dot.d}')`,
                  animationDelay: `${dot.delay}s`,
                  animationDuration: `${dot.duration}s`,
                }"
              />
            </g>

            <!-- The focus session: the centre of gravity for everything else. -->
            <g class="hx-focus" :class="{ 'is-running': true }">
              <circle cx="152" cy="310" r="128" class="hx-focus__halo" />
              <rect x="52" y="232" width="200" height="156" rx="26" class="hx-card__glass" />
              <rect x="52" y="232" width="200" height="156" rx="26" class="hx-focus__sheen" />

              <circle cx="92" cy="292" r="22" class="hx-focus__track" />
              <circle cx="92" cy="292" r="22" class="hx-focus__ring" pathLength="1" />

              <text x="126" y="286" class="hx-focus__kicker">专注中</text>
              <text x="126" y="304" class="hx-focus__state">深度工作</text>

              <text x="72" y="352" class="hx-focus__clock">{{ focusClock }}</text>
              <text x="72" y="372" class="hx-focus__meta">本次专注 · 界面原型</text>
            </g>

            <g
              v-for="node in nodes"
              :key="node.id"
              class="hx-node"
              :class="[`hx-node--${node.kind}`, { 'is-done': isDone(node.id) }]"
            >
              <rect
                :x="node.x"
                :y="node.y"
                :width="node.w"
                :height="node.h"
                rx="20"
                class="hx-card__glass"
              />

              <text :x="node.x + 18" :y="node.y + 26" class="hx-node__kind">{{ node.kind === 'milestone' ? '里程碑' : node.kind === 'project' ? '项目' : '任务' }}</text>
              <text :x="node.x + 18" :y="node.y + 50" class="hx-node__title">{{ node.title }}</text>

              <text :x="node.x + 18" :y="node.y + 74" class="hx-node__hours">
                <tspan class="hx-node__done">{{ isDone(node.id) ? node.total : node.done }}</tspan>
                <tspan class="hx-node__total"> / {{ node.total }}h</tspan>
              </text>

              <circle
                :cx="node.x + node.w - 24"
                :cy="node.y + 22"
                r="4.5"
                class="hx-node__status"
              />

              <rect
                :x="node.x + 18"
                :y="node.y + node.h - 20"
                :width="node.w - 36"
                height="5"
                rx="2.5"
                class="hx-node__track"
              />
              <!-- Full width, scaled: a transform animates, a width does not. -->
              <rect
                :x="node.x + 18"
                :y="node.y + node.h - 20"
                :width="node.w - 36"
                height="5"
                rx="2.5"
                class="hx-node__bar"
                :style="{ transform: `scaleX(${isDone(node.id) ? 1 : node.done / node.total})` }"
              />

              <!-- Revealed on hover, so the resting state stays uncluttered. -->
              <text :x="node.x + 18" :y="node.y + node.h + 20" class="hx-node__detail">
                {{ node.detail }}
              </text>
            </g>
          </svg>

          <p class="hx-stage__note" aria-live="polite">
            <span class="hx-live" aria-hidden="true" />
            {{ stageNote }}
          </p>
        </div>
      </div>
    </section>

    <section class="hx-band">
      <div class="hx-shell">
        <article
          v-for="(item, index) in pillars"
          :key="item.title"
          :ref="registerReveal"
          class="hx-pillar hx-slide"
          :style="{ '--i': index }"
        >
          <span class="hx-pillar__dot" aria-hidden="true" />
          <h3>{{ item.title }}</h3>
          <p>{{ item.text }}</p>
        </article>
      </div>
    </section>

    <section id="preview" class="hx-preview">
      <div class="hx-shell">
        <header :ref="registerReveal" class="hx-head hx-slide">
          <p class="hx-kicker">产品一览</p>
          <h2>三个界面，一条完整的时间线</h2>
        </header>

        <div :ref="registerReveal" class="hx-preview__grid hx-slide">
          <div class="hx-window">
            <div class="hx-window__bar" aria-hidden="true">
              <i /><i /><i />
              <span>{{ shots[activeShot]!.title }}</span>
            </div>
            <div class="hx-window__frame">
              <img
                v-for="(shot, index) in shots"
                :key="shot.id"
                class="hx-window__shot"
                :class="{ 'is-active': activeShot === index }"
                :src="shot.image"
                :alt="shot.alt"
                :aria-hidden="activeShot === index ? undefined : 'true'"
                decoding="async"
              />
            </div>
          </div>

          <ul class="hx-tabs">
            <li v-for="(shot, index) in shots" :key="shot.id">
              <button
                type="button"
                :class="{ 'is-active': activeShot === index }"
                :aria-current="activeShot === index ? 'true' : undefined"
                @click="showShot(index)"
              >
                <strong>{{ shot.kicker }}</strong>
                <span>{{ shot.title }}</span>
                <i class="hx-tabs__timer" aria-hidden="true" />
              </button>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <section class="hx-closing">
      <div class="hx-shell">
        <div :ref="registerReveal" class="hx-closing__card hx-slide">
          <h2>让今天的专注，落在项目上</h2>
          <p>注册即用，数据存在你自己的空间里。</p>
          <RouterLink class="hx-cta hx-cta--lg" :to="{ name: 'login', query: { mode: 'register' } }">
            <span>免费开始</span>
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h13M13 6l6 6-6 6" /></svg>
          </RouterLink>
        </div>
      </div>
    </section>

    <footer class="hx-footer">
      <div class="hx-shell hx-footer__inner">
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

const pillars = [
  { title: '结构清楚', text: '项目、模块、任务三层拆解，复杂计划也看得见边界。' },
  { title: '时间可见', text: '专注计时自动归集到任务与当日清单，不用手动记账。' },
  { title: '进度自证', text: '统计只认这里计到的时间，完成率不靠感觉。' },
] as const

const timeline = [
  { label: '今天', x: 152 },
  { label: '本周', x: 428 },
  { label: '冲刺', x: 604 },
  { label: '里程碑', x: 780 },
  { label: '发布', x: 900 },
] as const

type NodeKind = 'task' | 'project' | 'milestone'

interface NetNode {
  id: string
  kind: NodeKind
  title: string
  done: number
  total: number
  detail: string
  x: number
  y: number
  w: number
  h: number
  /** Where this node sits in the progress sequence. */
  order: number
}

const nodes: NetNode[] = [
  { id: 'task-a', kind: 'task', title: '界面原型', done: 6, total: 8, detail: '今日投入 2h 10m · 剩余 2h', x: 330, y: 92, w: 196, h: 112, order: 1 },
  { id: 'task-b', kind: 'task', title: '数据同步', done: 14, total: 20, detail: '今日投入 1h 30m · 剩余 6h', x: 330, y: 404, w: 196, h: 112, order: 2 },
  { id: 'proj-a', kind: 'project', title: '体验设计', done: 22, total: 30, detail: '4 项任务 · 本周 +8h', x: 580, y: 156, w: 186, h: 112, order: 3 },
  { id: 'proj-b', kind: 'project', title: '数据能力', done: 18, total: 28, detail: '5 项任务 · 本周 +6h', x: 580, y: 348, w: 186, h: 112, order: 4 },
  { id: 'launch', kind: 'milestone', title: '发布 1.0', done: 40, total: 58, detail: '预计 3 月 12 日达成', x: 812, y: 250, w: 150, h: 112, order: 5 },
]

const nodeById = new Map(nodes.map((node) => [node.id, node]))

function edge(fromX: number, fromY: number, toX: number, toY: number): string {
  const bend = Math.max(48, (toX - fromX) * 0.45)
  return `M${fromX} ${fromY}C${fromX + bend} ${fromY}, ${toX - bend} ${toY}, ${toX} ${toY}`
}

function linkTo(toId: string, fromX: number, fromY: number) {
  const to = nodeById.get(toId)!
  return {
    id: `focus-${toId}`,
    to: toId,
    d: edge(fromX, fromY, to.x, to.y + to.h / 2),
  }
}

function linkBetween(fromId: string, toId: string) {
  const from = nodeById.get(fromId)!
  const to = nodeById.get(toId)!
  return {
    id: `${fromId}-${toId}`,
    to: toId,
    d: edge(from.x + from.w, from.y + from.h / 2, to.x, to.y + to.h / 2),
  }
}

const links = [
  linkTo('task-a', 252, 300),
  linkTo('task-b', 252, 320),
  linkBetween('task-a', 'proj-a'),
  linkBetween('task-b', 'proj-b'),
  linkBetween('proj-a', 'launch'),
  linkBetween('proj-b', 'launch'),
]

const DOTS_PER_LINK = 3
const particles = links.flatMap((link, linkIndex) =>
  Array.from({ length: DOTS_PER_LINK }, (_, index) => ({
    id: `${link.id}-${index}`,
    d: link.d,
    delay: Number((linkIndex * 0.42 + index * 1.5).toFixed(2)),
    duration: 4.5 + (linkIndex % 3) * 0.5,
  })),
)

const LAST_ORDER = 5
const STEP_MS = 1500
const HOLD_STEPS = 3

const stageStep = ref(0)
const focusSeconds = ref(45 * 60 + 23)
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
const revealTargets = new Set<Element>()
const pointer = ref({ x: 0.5, y: 0.5, active: false })
const magnet = ref({ x: 0, y: 0 })

function isDone(nodeId: string): boolean {
  const node = nodeById.get(nodeId)
  return node ? stageStep.value >= node.order : false
}

const focusClock = computed(() => {
  const minutes = Math.floor(focusSeconds.value / 60)
  const seconds = focusSeconds.value % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
})

const stageNote = computed(() => {
  if (stageStep.value >= LAST_ORDER) return '里程碑「发布 1.0」进度已更新'
  if (stageStep.value >= 3) return '项目进度随任务完成一起上移'
  if (stageStep.value >= 1) return '专注时间正流向今天的任务'
  return '专注计时进行中，网络待命'
})

const stageLabel =
  '动画：一个正在运行的专注计时向外发出光点，光点沿曲线流经任务、项目直到发布里程碑，沿途的进度条随之增长'

const parallaxStyle = computed<CSSProperties>(() => {
  if (reducedMotion.value || !pointer.value.active) return {}
  const x = (pointer.value.x - 0.5) * 14
  const y = (pointer.value.y - 0.5) * 10
  return { transform: `translate3d(${-x}px, ${-y}px, 0)` }
})

const magnetStyle = computed<CSSProperties>(() =>
  reducedMotion.value ? {} : { transform: `translate3d(${magnet.value.x}px, ${magnet.value.y}px, 0)` },
)

let shotTimer = 0
let stageTimer = 0
let clockTimer = 0
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

function onScroll(): void {
  // Browsers already fire scroll at most once per frame, and this reads a
  // handful of rects; requestAnimationFrame here would only add a way for the
  // work to be skipped when frames are throttled.
  scrolled.value = window.scrollY > 12
  updateReveal()
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

/**
 * Walk progress outward from the focus session — task, task, project, project,
 * milestone — hold the finished network briefly, then start over. Reduced
 * motion gets the settled state with no cycling.
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

onMounted(() => {
  motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  const onMotionChange = (event: MediaQueryListEvent): void => {
    reducedMotion.value = event.matches
    revealArmed.value = !event.matches
    restartShotTimer()
    restartStageTimer()
  }
  motionQuery.addEventListener('change', onMotionChange)

  window.addEventListener('scroll', onScroll, { passive: true })
  window.addEventListener('resize', onScroll, { passive: true })
  window.addEventListener('pointermove', trackPointer, { passive: true })
  window.addEventListener('pointerleave', resetPointer)

  restartShotTimer()
  restartStageTimer()
  if (!reducedMotion.value) {
    clockTimer = window.setInterval(() => {
      focusSeconds.value += 1
    }, 1000)
  }

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
  window.removeEventListener('pointermove', trackPointer)
  window.removeEventListener('pointerleave', resetPointer)
  window.clearInterval(shotTimer)
  window.clearInterval(stageTimer)
  window.clearInterval(clockTimer)
  window.clearTimeout(revealFallback)
  revealTargets.clear()
})
</script>
