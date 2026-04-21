<template>
  <div class="timeline-wrap" ref="wrapRef">
    <canvas ref="canvasRef" class="timeline-canvas" />
  </div>
</template>

<script setup lang="ts">
import type { NoteEvent } from '~/types'

const store = useKaraokeStore()

const wrapRef   = ref<HTMLDivElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)

// Cached context — only obtained once, re-scaled on resize
let ctx: CanvasRenderingContext2D | null = null
let dpr = 1
let canvasW = 0   // logical px (post-DPR)
let canvasH = 0

const PIANO_WIDTH  = 52
const VISIBLE_SECS = 10
const CURSOR_X_PCT = 0.3
const ROW_PADDING  = 2  // semitone padding above/below note range

// ── Dynamic MIDI range from actual note events ───────────────────────────────
const midiRange = computed(() => {
  const notes = store.noteEvents
  if (!notes.length) return { min: 48, max: 72 }   // C3–C5 default
  let min = notes[0].midi, max = notes[0].midi
  for (const n of notes) {
    if (n.midi < min) min = n.midi
    if (n.midi > max) max = n.midi
  }
  return { min: Math.max(0, min - ROW_PADDING), max: Math.min(127, max + ROW_PADDING) }
})

// rowHeight computed per-draw from canvas height so every note fits on screen
function getRowHeight(): number {
  const total = midiRange.value.max - midiRange.value.min + 1
  return canvasH / total
}

function midiToY(midi: number, rowH: number): number {
  return (midiRange.value.max - midi) * rowH
}

// ── Colours ───────────────────────────────────────────────────────────────────
const C = {
  greenDeep:  '#15803d',
  greenVivid: '#22c55e',
  greenLime:  '#4ade80',
  ink:        '#0a0f0a',
  inkFaint:   '#6B8F72',
  bg:         '#FAFFF9',
  bgCard:     '#F0FBF4',
  border:     '#D1FAE5',
}

// ── Resize ────────────────────────────────────────────────────────────────────
function resize() {
  const canvas = canvasRef.value
  const wrap   = wrapRef.value
  if (!canvas || !wrap) return

  dpr     = window.devicePixelRatio || 1
  canvasW = wrap.clientWidth
  canvasH = wrap.clientHeight

  canvas.width        = canvasW * dpr
  canvas.height       = canvasH * dpr
  canvas.style.width  = canvasW + 'px'
  canvas.style.height = canvasH + 'px'

  ctx = canvas.getContext('2d')!
  ctx.scale(dpr, dpr)
}

// ── Draw ──────────────────────────────────────────────────────────────────────
function draw() {
  if (!ctx || canvasW === 0) return

  const W    = canvasW
  const H    = canvasH
  const t    = store.currentTime
  const rowH = getRowHeight()

  const pxPerSec = (W - PIANO_WIDTH) / VISIBLE_SECS
  const cursorX  = PIANO_WIDTH + (W - PIANO_WIDTH) * CURSOR_X_PCT
  const timeLeft = t - (cursorX - PIANO_WIDTH) / pxPerSec
  const { min: MIDI_MIN, max: MIDI_MAX } = midiRange.value

  ctx.clearRect(0, 0, W, H)

  // ── Background ──────────────────────────────────────────────────────────────
  ctx.fillStyle = C.bg
  ctx.fillRect(0, 0, W, H)

  // ── Row bands (black-key tint) ───────────────────────────────────────────────
  ctx.fillStyle = 'rgba(0,0,0,0.025)'
  for (let midi = MIDI_MIN; midi <= MIDI_MAX; midi++) {
    if ([1,3,6,8,10].includes(midi % 12)) {
      ctx.fillRect(PIANO_WIDTH, midiToY(midi, rowH), W - PIANO_WIDTH, rowH)
    }
  }

  // ── Octave grid lines (single path batch) ────────────────────────────────────
  ctx.beginPath()
  ctx.strokeStyle = C.border
  ctx.lineWidth   = 1
  for (let midi = MIDI_MIN; midi <= MIDI_MAX; midi++) {
    if (midi % 12 === 0) {
      const y = midiToY(midi, rowH) + rowH
      ctx.moveTo(PIANO_WIDTH, y)
      ctx.lineTo(W, y)
    }
  }
  ctx.stroke()

  // ── Vertical time grid ───────────────────────────────────────────────────────
  ctx.beginPath()
  ctx.strokeStyle = C.border
  ctx.lineWidth   = 0.5
  const firstBeat = Math.ceil(timeLeft)
  for (let sec = firstBeat; sec < timeLeft + VISIBLE_SECS + 1; sec++) {
    const x = PIANO_WIDTH + (sec - timeLeft) * pxPerSec
    if (x < PIANO_WIDTH || x > W) continue
    ctx.moveTo(x, 0)
    ctx.lineTo(x, H)
  }
  ctx.stroke()

  // Timestamp labels (separate pass — font ops are expensive inside batch)
  ctx.fillStyle  = C.inkFaint
  ctx.font       = '9px "IBM Plex Mono", monospace'
  ctx.textAlign  = 'center'
  for (let sec = firstBeat; sec < timeLeft + VISIBLE_SECS + 1; sec++) {
    const x = PIANO_WIDTH + (sec - timeLeft) * pxPerSec
    if (x < PIANO_WIDTH || x > W) continue
    ctx.fillText(formatTime(sec), x, H - 4)
  }

  // ── Note bars (only visible window) ──────────────────────────────────────────
  const timeRight = timeLeft + VISIBLE_SECS
  for (const note of store.noteEvents) {
    if (note.end < timeLeft || note.start > timeRight) continue

    const x1     = PIANO_WIDTH + (note.start - timeLeft) * pxPerSec
    const x2     = PIANO_WIDTH + (note.end   - timeLeft) * pxPerSec
    const y      = midiToY(note.midi, rowH)
    const w      = Math.max(x2 - x1, 2)
    const active = t >= note.start && t <= note.end

    drawNoteBar(x1, y, w, rowH, note, active)
  }

  // ── Piano keys ────────────────────────────────────────────────────────────────
  drawPianoKeys(rowH, MIDI_MIN, MIDI_MAX)

  // ── Playhead ──────────────────────────────────────────────────────────────────
  drawCursor(cursorX)
}

// ── Note bar — NO shadowBlur (too expensive), use brighter colour for active ──
function drawNoteBar(
  x: number, y: number, w: number, h: number,
  note: NoteEvent, active: boolean,
) {
  if (!ctx) return
  const r = Math.min(h / 2, 4)

  // Solid gradient — created once per bar, no shadow
  const grad = ctx.createLinearGradient(x, y, x, y + h)
  if (active) {
    grad.addColorStop(0, C.greenLime)
    grad.addColorStop(1, C.greenVivid)
  } else {
    grad.addColorStop(0, C.greenVivid)
    grad.addColorStop(1, C.greenDeep)
  }

  ctx.fillStyle = grad
  roundRect(x + 1, y + 1, w - 2, h - 2, r)
  ctx.fill()

  // Label
  if (w > 28) {
    ctx.fillStyle = active ? C.ink : 'rgba(255,255,255,0.9)'
    ctx.font      = `${active ? '600' : '500'} 9px "IBM Plex Mono", monospace`
    ctx.textAlign = 'left'
    ctx.fillText(note.note, x + 4, y + h - 3)
  }
}

function drawPianoKeys(rowH: number, midiMin: number, midiMax: number) {
  if (!ctx) return
  ctx.fillStyle = C.bgCard
  ctx.fillRect(0, 0, PIANO_WIDTH, canvasH)

  ctx.beginPath()
  ctx.strokeStyle = C.border
  ctx.lineWidth   = 1
  ctx.moveTo(PIANO_WIDTH, 0)
  ctx.lineTo(PIANO_WIDTH, canvasH)
  ctx.stroke()

  ctx.font      = '500 8px "IBM Plex Mono", monospace'
  ctx.textAlign = 'right'

  for (let midi = midiMin; midi <= midiMax; midi++) {
    const y       = midiToY(midi, rowH)
    const isBlack = [1,3,6,8,10].includes(midi % 12)
    const isC     = midi % 12 === 0

    ctx.fillStyle = isBlack ? '#2a3a2a' : 'white'
    ctx.fillRect(0, y + 0.5, PIANO_WIDTH - (isBlack ? 12 : 0), rowH - 1)

    if (isC) {
      ctx.fillStyle = C.greenDeep
      ctx.fillText(`C${Math.floor(midi / 12) - 1}`, PIANO_WIDTH - 2, y + rowH - 2)
    }
  }
}

function drawCursor(x: number) {
  if (!ctx) return
  const grad = ctx.createLinearGradient(0, 0, 0, canvasH)
  grad.addColorStop(0,   'rgba(74,222,128,0)')
  grad.addColorStop(0.2, 'rgba(74,222,128,0.2)')
  grad.addColorStop(0.5, 'rgba(74,222,128,0.45)')
  grad.addColorStop(0.8, 'rgba(74,222,128,0.2)')
  grad.addColorStop(1,   'rgba(74,222,128,0)')
  ctx.fillStyle = grad
  ctx.fillRect(x - 6, 0, 12, canvasH)

  ctx.beginPath()
  ctx.strokeStyle = C.greenLime
  ctx.lineWidth   = 1.5
  ctx.moveTo(x, 0)
  ctx.lineTo(x, canvasH)
  ctx.stroke()
}

function roundRect(x: number, y: number, w: number, h: number, r: number) {
  if (!ctx) return
  if (ctx.roundRect) {
    // Native API — faster than manual quadratic curves
    ctx.beginPath()
    ctx.roundRect(x, y, w, h, r)
  } else {
    ctx.beginPath()
    ctx.moveTo(x + r, y)
    ctx.lineTo(x + w - r, y)
    ctx.quadraticCurveTo(x + w, y, x + w, y + r)
    ctx.lineTo(x + w, y + h - r)
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h)
    ctx.lineTo(x + r, y + h)
    ctx.quadraticCurveTo(x, y + h, x, y + h - r)
    ctx.lineTo(x, y + r)
    ctx.quadraticCurveTo(x, y, x + r, y)
    ctx.closePath()
  }
}

function formatTime(sec: number): string {
  const s = Math.floor(Math.abs(sec))
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
}

// ── RAF loop ──────────────────────────────────────────────────────────────────
let raf: number | null = null

function startLoop() {
  const loop = () => { draw(); raf = requestAnimationFrame(loop) }
  raf = requestAnimationFrame(loop)
}

function stopLoop() {
  if (raf !== null) { cancelAnimationFrame(raf); raf = null }
}

onMounted(() => {
  resize()
  startLoop()
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  stopLoop()
  window.removeEventListener('resize', resize)
})
</script>

<style scoped>
.timeline-wrap {
  width: 100%;
  height: 100%;
  min-height: 320px;
  background: var(--bg);
  border-radius: 16px;
  border: 1px solid var(--border);
  overflow: hidden;
  position: relative;
}
.timeline-canvas {
  display: block;
  width: 100%;
  height: 100%;
}
</style>
