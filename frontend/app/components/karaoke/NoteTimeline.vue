<template>
  <div ref="wrap" class="relative w-full h-full bg-cream-50 border border-moss-800/12 rounded-3xl overflow-hidden shadow-soft">
    <canvas ref="canvas" class="absolute inset-0 w-full h-full" />

    <!-- Fixed left-edge playhead — time arrow at top, pitch arrow slides on the line -->
    <div
      class="playhead absolute top-0 bottom-0 pointer-events-none z-10"
      :style="{ left: PLAYHEAD_X + 'px' }"
    >
      <svg
        class="absolute -top-1 -translate-x-1/2 left-1/2"
        width="18"
        height="14"
        viewBox="0 0 18 14"
        fill="none"
        aria-hidden="true"
      >
        <path
          d="M9 0 L17 12 H1 Z"
          fill="#0F3D26"
          stroke="#0F3D26"
          stroke-width="0.5"
        />
      </svg>
      <div class="playhead-line absolute top-3 bottom-0 left-1/2 -translate-x-1/2 w-[2px] bg-moss-900" />
    </div>

    <!-- Live pitch cursor — arrow slides vertically (updated imperatively in rAF) -->
    <div
      ref="pitchCursor"
      class="pitch-cursor absolute pointer-events-none z-20"
      :style="{ left: (PLAYHEAD_X - 1) + 'px', opacity: 0 }"
    >
      <svg width="16" height="20" viewBox="0 0 16 20" aria-hidden="true">
        <path
          class="pitch-arrow-body"
          d="M0 4 L12 10 L0 16 Z"
          fill="#0F3D26"
          stroke="#0F3D26"
          stroke-width="1"
          stroke-linejoin="round"
        />
      </svg>
      <div class="pitch-crosshair absolute top-1/2 left-[14px] h-px bg-moss-900/30" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { NoteEvent } from '~/types'

const store = useSessionStore()

const wrap = ref<HTMLDivElement | null>(null)
const canvas = ref<HTMLCanvasElement | null>(null)
const pitchCursor = ref<HTMLDivElement | null>(null)

const VIEW_SECS_AHEAD = 3.5
const VIEW_SECS_BEHIND = 1.2
// Fixed left-edge playhead — notes must align here when their start time == displayTime.
const PLAYHEAD_X = 18

let width = 0
let height = 0
let dpr = 1
let pxPerSec = 1

// Cached static grid (horizontal stripes + octave labels)
let gridLayer: OffscreenCanvas | HTMLCanvasElement | null = null
let gridKey = ''

// Precomputed note rects in world time coordinates
interface NoteRect {
  start: number
  end: number
  midi: number
  event: NoteEvent
}
let noteRects: NoteRect[] = []
let notesKey = ''

// Adaptive cursor glide — snappy on interval jumps, smooth on vibrato
const TAU_VIBRATO = 0.09
const TAU_JUMP = 0.028
const JUMP_THRESHOLD = 0.42
const MAX_RATE_VIBRATO = 14
const MAX_RATE_JUMP = 48

let smoothMidi = 0
let smoothVoiced = false
let liveColor = '#0F3D26'
let liveStroke = '#0F3D26'
let lastFrameMs = 0

// Layout cache
let rangeMin = 48
let rangeMax = 72

function midiToY(m: number): number {
  const span = Math.max(1, rangeMax - rangeMin)
  const frac = (m - rangeMin) / span
  const usable = height - 20
  return 10 + (1 - frac) * usable
}

function computeRange() {
  const notes = store.noteEvents
  const t = store.transpose
  if (!notes.length) {
    rangeMin = 48 + t
    rangeMax = 72 + t
    return
  }
  let lo = notes[0]!.midi + t
  let hi = notes[0]!.midi + t
  for (const n of notes) {
    const m = n.midi + t
    if (m < lo) lo = m
    if (m > hi) hi = m
  }
  rangeMin = Math.max(0, lo - 3)
  rangeMax = Math.min(127, hi + 3)
}

function rebuildGrid() {
  const key = `${width}|${height}|${rangeMin}|${rangeMax}`
  if (key === gridKey && gridLayer) return
  gridKey = key

  const c = typeof OffscreenCanvas !== 'undefined'
    ? new OffscreenCanvas(Math.floor(width * dpr), Math.floor(height * dpr))
    : document.createElement('canvas')
  c.width = Math.floor(width * dpr)
  c.height = Math.floor(height * dpr)
  const ctx = c.getContext('2d')!
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

  // Black-key stripes
  for (let m = rangeMin; m <= rangeMax; m++) {
    const y = midiToY(m)
    const nextY = midiToY(m - 1)
    if ([1, 3, 6, 8, 10].includes(m % 12)) {
      ctx.fillStyle = 'rgba(15,61,38,0.06)'
      ctx.fillRect(0, y - (nextY - y), width, nextY - y)
    }
  }

  // Horizontal lines
  for (let m = rangeMin; m <= rangeMax + 1; m++) {
    const y = midiToY(m)
    ctx.strokeStyle = m % 12 === 0 ? 'rgba(15,61,38,0.15)' : 'rgba(15,61,38,0.05)'
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(width, y)
    ctx.stroke()
  }

  // Octave labels
  ctx.font = "500 10px 'JetBrains Mono', ui-monospace, monospace"
  ctx.textBaseline = 'middle'
  ctx.textAlign = 'left'
  for (let m = rangeMin; m <= rangeMax; m++) {
    if (m % 12 === 0) {
      ctx.fillStyle = 'rgba(15,61,38,0.5)'
      ctx.fillText(`C${m / 12 - 1}`, 6, midiToY(m))
    }
  }

  gridLayer = c
}

function rebuildNotes() {
  const notes = store.noteEvents
  const t = store.transpose
  const key = `${notes.length}|${t}|${notes[0]?.start ?? 0}|${notes[notes.length - 1]?.end ?? 0}`
  if (key === notesKey) return
  notesKey = key

  noteRects = notes.map(n => ({
    start: n.start,
    end: n.end,
    midi: n.midi + t,
    event: n,
  }))
}

function findFirstVisible(minT: number): number {
  let lo = 0
  let hi = noteRects.length
  while (lo < hi) {
    const mid = (lo + hi) >> 1
    if (noteRects[mid]!.end < minT) lo = mid + 1
    else hi = mid
  }
  return lo
}

function resize() {
  const el = wrap.value
  const cvs = canvas.value
  if (!el || !cvs) return
  const rect = el.getBoundingClientRect()
  width = rect.width
  height = rect.height
  dpr = Math.min(2, window.devicePixelRatio || 1)
  pxPerSec = width / (VIEW_SECS_AHEAD + VIEW_SECS_BEHIND)
  cvs.width = Math.floor(width * dpr)
  cvs.height = Math.floor(height * dpr)
  gridKey = ''
  notesKey = ''
  computeRange()
  rebuildGrid()
  rebuildNotes()

  const crosshair = pitchCursor.value?.querySelector('.pitch-crosshair') as HTMLElement | null
  if (crosshair) crosshair.style.width = `${Math.max(0, width - PLAYHEAD_X - 14)}px`
}

function drawTimeGrid(ctx: CanvasRenderingContext2D, displayTime: number) {
  const startSec = Math.floor(displayTime - VIEW_SECS_BEHIND)
  const endSec = Math.ceil(displayTime + VIEW_SECS_AHEAD)
  const offsetX = PLAYHEAD_X - displayTime * pxPerSec

  ctx.strokeStyle = 'rgba(15,61,38,0.06)'
  ctx.lineWidth = 1
  ctx.beginPath()
  for (let s = startSec; s <= endSec; s++) {
    const x = s * pxPerSec + offsetX
    ctx.moveTo(x, 0)
    ctx.lineTo(x, height)
  }
  ctx.stroke()
}

function drawNotes(ctx: CanvasRenderingContext2D, displayTime: number, activeEvent: NoteEvent | null) {
  if (!noteRects.length) return

  const minVisT = displayTime - VIEW_SECS_BEHIND
  const maxVisT = displayTime + VIEW_SECS_AHEAD
  const offsetX = PLAYHEAD_X - displayTime * pxPerSec
  const noteH = 16
  const noteHalf = noteH / 2

  const startIdx = findFirstVisible(minVisT)

  for (let i = startIdx; i < noteRects.length; i++) {
    const n = noteRects[i]!
    if (n.start > maxVisT) break

    const x0 = n.start * pxPerSec + offsetX
    const w = Math.max(3, (n.end - n.start) * pxPerSec)
    const y = midiToY(n.midi) - noteHalf
    const isActive = n.event === activeEvent

    if (isActive) {
      ctx.fillStyle = 'rgba(245,200,106,0.35)'
      ctx.fillRect(x0 - 4, y - 4, w + 8, noteH + 8)
      ctx.fillStyle = '#F5C86A'
      ctx.fillRect(x0, y, w, noteH)
      ctx.strokeStyle = '#8B6412'
    } else {
      ctx.fillStyle = '#2D8F52'
      ctx.fillRect(x0, y, w, noteH)
      ctx.strokeStyle = '#155230'
    }

    ctx.lineWidth = 1.5
    ctx.beginPath()
    ctx.moveTo(x0 + 0.5, y)
    ctx.lineTo(x0 + 0.5, y + noteH)
    ctx.stroke()
  }
}

function updatePitchCursor(cy: number, visible: boolean) {
  const el = pitchCursor.value
  if (!el) return
  el.style.opacity = visible ? '1' : '0'
  el.style.transform = `translate3d(0, ${cy - 10}px, 0)`
  const body = el.querySelector('.pitch-arrow-body') as SVGPathElement | null
  if (body) {
    body.setAttribute('fill', liveColor)
    body.setAttribute('stroke', liveStroke)
  }
}

function findActiveNote(displayTime: number): NoteEvent | null {
  for (let i = 0; i < noteRects.length; i++) {
    const n = noteRects[i]!
    if (displayTime >= n.start && displayTime <= n.end) return n.event
    if (n.start > displayTime) break
  }
  return null
}

function draw() {
  const cvs = canvas.value
  if (!cvs || width <= 0) return
  const ctx = cvs.getContext('2d')
  if (!ctx) return

  rebuildNotes()

  const displayTime = store.displayTime
  const activeEvent = findActiveNote(displayTime)

  // Adaptive smoothing — use grade Hz when display lags on a big leap
  const nowMs = performance.now()
  const dt = lastFrameMs ? Math.min(0.05, (nowMs - lastFrameMs) / 1000) : 1 / 60
  lastFrameMs = nowMs

  let target = store.liveDisplayMidi
  if (store.liveHz > 0) {
    const gradeMidi = hzToMidiFloat(store.liveHz)
    if (Math.abs(gradeMidi - smoothMidi) > JUMP_THRESHOLD) {
      target = gradeMidi
    }
  }

  if (store.liveDisplayVoiced && target > 0) {
    const delta = target - smoothMidi
    const absDelta = Math.abs(delta)
    const jumping = absDelta >= JUMP_THRESHOLD
    const tau = jumping ? TAU_JUMP : TAU_VIBRATO
    const maxRate = jumping ? MAX_RATE_JUMP : MAX_RATE_VIBRATO
    const alpha = 1 - Math.exp(-dt / tau)

    if (!smoothVoiced) {
      smoothMidi = target
    } else {
      const maxStep = maxRate * dt
      const stepped = smoothMidi + Math.sign(delta) * Math.min(absDelta, maxStep)
      smoothMidi = stepped + (target - stepped) * alpha
    }
    smoothVoiced = true
  } else if (!store.liveDisplayVoiced) {
    smoothVoiced = false
  }

  if (store.expectedNote) {
    liveColor = store.isExact ? '#F5C86A' : store.isCorrect ? '#2D8F52' : '#C24238'
    liveStroke = store.isExact ? '#B8821F' : store.isCorrect ? '#0F3D26' : '#7F2B25'
  } else {
    liveColor = '#0F3D26'
    liveStroke = '#0F3D26'
  }

  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  ctx.clearRect(0, 0, width, height)

  if (gridLayer) {
    ctx.drawImage(gridLayer as CanvasImageSource, 0, 0, width, height)
  }

  drawTimeGrid(ctx, displayTime)
  drawNotes(ctx, displayTime, activeEvent)
  updatePitchCursor(midiToY(smoothMidi), smoothVoiced && smoothMidi > 0)
}

let raf: number | null = null
function frame() {
  draw()
  raf = requestAnimationFrame(frame)
}

watch(() => [store.transpose, store.noteEvents.length] as const, () => {
  computeRange()
  gridKey = ''
  notesKey = ''
  rebuildGrid()
  rebuildNotes()
})

let ro: ResizeObserver | null = null
onMounted(() => {
  resize()
  ro = new ResizeObserver(resize)
  if (wrap.value) ro.observe(wrap.value)
  raf = requestAnimationFrame(frame)
})
onUnmounted(() => {
  if (raf) cancelAnimationFrame(raf)
  ro?.disconnect()
})
</script>

<style scoped>
.playhead-line {
  box-shadow: 0 0 14px rgba(15, 61, 38, 0.35);
}

.pitch-cursor {
  top: 0;
  will-change: transform;
  transition: opacity 120ms ease;
}

.pitch-cursor svg {
  filter: drop-shadow(0 1px 4px rgba(15, 61, 38, 0.2));
}

.pitch-crosshair {
  pointer-events: none;
}

.playhead svg {
  filter: drop-shadow(0 1px 3px rgba(15, 61, 38, 0.25));
  animation: playhead-bob 2.4s ease-in-out infinite;
}

@keyframes playhead-bob {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(1px); }
}
</style>
