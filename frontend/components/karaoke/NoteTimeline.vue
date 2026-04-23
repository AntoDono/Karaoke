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
const CURSOR_X_PCT = 0
const ROW_PADDING  = 2  // semitone padding above/below note range

// ── Dynamic MIDI range from actual note events (shifted by transpose) ─────────
const midiRange = computed(() => {
  const notes = store.noteEvents
  const t = store.transpose
  if (!notes.length) return { min: 48 + t, max: 72 + t }   // C3–C5 default
  let min = notes[0]!.midi, max = notes[0]!.midi
  for (const n of notes) {
    if (n.midi < min) min = n.midi
    if (n.midi > max) max = n.midi
  }
  return {
    min: Math.max(0, min + t - ROW_PADDING),
    max: Math.min(127, max + t + ROW_PADDING),
  }
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
  const timeLeft = t
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
  const tp = store.transpose
  for (const note of store.noteEvents) {
    if (note.end < timeLeft || note.start > timeRight) continue

    const shiftedMidi = Math.max(0, Math.min(127, note.midi + tp))
    const x1     = PIANO_WIDTH + (note.start - timeLeft) * pxPerSec
    const x2     = PIANO_WIDTH + (note.end   - timeLeft) * pxPerSec
    const y      = midiToY(shiftedMidi, rowH)
    const w      = Math.max(x2 - x1, 2)
    const active = t >= note.start && t <= note.end

    drawNoteBar(x1, y, w, rowH, note, active, tp)
  }

  // ── Piano keys ────────────────────────────────────────────────────────────────
  drawPianoKeys(rowH, MIDI_MIN, MIDI_MAX, tp)

  // ── Tolerance bands (±1 semitone) around the active note ─────────────────────
  if (store.activeNote) {
    drawToleranceBands(store.activeNote.event.midi + tp, rowH, W)
  }

  // ── Live pitch arrow ──────────────────────────────────────────────────────────
  if (store.isMicActive && store.liveMidi > 0) {
    drawPitchArrow(store.liveMidi, rowH)
  }

  // ── Playhead at left edge of note area ────────────────────────────────────────
  drawPlayhead()
}

const NOTE_NAMES_TIMELINE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
function shiftedNoteName(midi: number): string {
  const clamped = Math.max(0, Math.min(127, midi))
  const octave  = Math.floor(clamped / 12) - 1
  return `${NOTE_NAMES_TIMELINE[clamped % 12]}${octave}`
}

// ── Note bar — NO shadowBlur (too expensive), use brighter colour for active ──
function drawNoteBar(
  x: number, y: number, w: number, h: number,
  note: NoteEvent, active: boolean, transpose: number = 0,
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

  // Label — show transposed note name when transpose is active
  if (w > 28) {
    const label = transpose !== 0 ? shiftedNoteName(note.midi + transpose) : note.note
    ctx.fillStyle = active ? C.ink : 'rgba(255,255,255,0.9)'
    ctx.font      = `${active ? '600' : '500'} 9px "IBM Plex Mono", monospace`
    ctx.textAlign = 'left'
    ctx.fillText(label, x + 4, y + h - 3)
  }
}

function drawPianoKeys(rowH: number, midiMin: number, midiMax: number, transpose: number = 0) {
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
    // For C labels, determine actual pitch accounting for transpose
    const isC     = midi % 12 === 0

    ctx.fillStyle = isBlack ? '#2a3a2a' : 'white'
    ctx.fillRect(0, y + 0.5, PIANO_WIDTH - (isBlack ? 12 : 0), rowH - 1)

    if (isC) {
      ctx.fillStyle = C.greenDeep
      ctx.fillText(`C${Math.floor(midi / 12) - 1}`, PIANO_WIDTH - 2, y + rowH - 2)
    }
  }

  // Transpose indicator badge at top of piano strip
  if (transpose !== 0) {
    const label = `${transpose > 0 ? '+' : ''}${transpose}`
    ctx.fillStyle = transpose > 0 ? '#15803d' : '#b45309'
    ctx.fillRect(2, 2, PIANO_WIDTH - 4, 14)
    ctx.fillStyle = 'white'
    ctx.font      = '700 8px "IBM Plex Mono", monospace'
    ctx.textAlign = 'center'
    ctx.fillText(label, PIANO_WIDTH / 2, 12)
    ctx.textAlign = 'right'
  }
}

function drawToleranceBands(activeMidi: number, rowH: number, W: number) {
  if (!ctx) return

  // Top edge of the +1 semitone row (outer boundary of tolerance zone above)
  const yAbove = midiToY(activeMidi + 1, rowH)
  // Bottom edge of the -1 semitone row (outer boundary of tolerance zone below)
  const yBelow = midiToY(activeMidi - 1, rowH) + rowH

  ctx.save()
  ctx.strokeStyle = 'rgba(251, 146, 60, 0.85)'  // orange-400 @ 85%
  ctx.lineWidth   = 1.5
  ctx.setLineDash([5, 3])

  // Upper bound
  ctx.beginPath()
  ctx.moveTo(PIANO_WIDTH, yAbove)
  ctx.lineTo(W, yAbove)
  ctx.stroke()

  // Lower bound
  ctx.beginPath()
  ctx.moveTo(PIANO_WIDTH, yBelow)
  ctx.lineTo(W, yBelow)
  ctx.stroke()

  ctx.restore()
}

function drawPlayhead() {
  if (!ctx) return
  const x = PIANO_WIDTH
  const grad = ctx.createLinearGradient(0, 0, 0, canvasH)
  grad.addColorStop(0,   'rgba(74,222,128,0)')
  grad.addColorStop(0.2, 'rgba(74,222,128,0.15)')
  grad.addColorStop(0.5, 'rgba(74,222,128,0.35)')
  grad.addColorStop(0.8, 'rgba(74,222,128,0.15)')
  grad.addColorStop(1,   'rgba(74,222,128,0)')
  ctx.fillStyle = grad
  ctx.fillRect(x, 0, 6, canvasH)

  ctx.beginPath()
  ctx.strokeStyle = C.greenLime
  ctx.lineWidth   = 1.5
  ctx.moveTo(x, 0)
  ctx.lineTo(x, canvasH)
  ctx.stroke()
}

/**
 * Right-pointing arrow on the piano-strip edge that tracks the live sung pitch.
 * The arrow body sits inside the piano strip; the tip pokes just past the
 * border into the note area so it's clearly visible against both backgrounds.
 */
function drawPitchArrow(liveMidi: number, rowH: number) {
  if (!ctx) return

  const noteCentre = midiToY(liveMidi, rowH) + rowH / 2
  const tipX   = PIANO_WIDTH + 10   // tip of the arrow (into note area)
  const tailX  = PIANO_WIDTH - 22   // back of the arrow body
  const halfH  = Math.max(5, Math.min(10, rowH * 0.55))  // scales with row height

  // Determine how close the singer is to the active note (0 = exact, 1 = ±1 semitone, Infinity = off)
  const active = store.activeNote
  const diff   = active ? Math.abs(active.event.midi + store.transpose - liveMidi) : Infinity
  // Three color tiers: exact → bright green, near (±1) → muted green, off → yellow
  const arrowColor = diff === 0 ? C.greenLime : diff <= 1 ? '#86efac' : '#facc15'
  const glowInner  = diff === 0 ? 'rgba(74,222,128,0.35)' : diff <= 1 ? 'rgba(134,239,172,0.22)' : 'rgba(250,204,21,0.3)'

  // Glow halo behind the arrow
  const glow = ctx.createRadialGradient(PIANO_WIDTH, noteCentre, 0, PIANO_WIDTH, noteCentre, 24)
  glow.addColorStop(0,   glowInner)
  glow.addColorStop(1,   'rgba(0,0,0,0)')
  ctx.fillStyle = glow
  ctx.fillRect(tailX - 4, noteCentre - 24, tipX - tailX + 28, 48)

  // Arrow shape: a right-pointing chevron/arrowhead
  ctx.beginPath()
  ctx.moveTo(tailX,  noteCentre - halfH)  // top-left
  ctx.lineTo(tipX - halfH * 0.9, noteCentre - halfH) // top-right shoulder
  ctx.lineTo(tipX,   noteCentre)           // tip
  ctx.lineTo(tipX - halfH * 0.9, noteCentre + halfH) // bottom-right shoulder
  ctx.lineTo(tailX,  noteCentre + halfH)  // bottom-left
  ctx.closePath()
  ctx.fillStyle = arrowColor
  ctx.fill()

  // Note label inside the arrow body (only if rows are tall enough)
  if (rowH >= 10) {
    const NOTE_NAMES_ARR = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    const name = `${NOTE_NAMES_ARR[liveMidi % 12]}${Math.floor(liveMidi / 12) - 1}`
    ctx.fillStyle = diff === 0 ? C.ink : diff <= 1 ? '#166534' : '#713f12'
    ctx.font      = `700 ${Math.max(7, Math.min(9, rowH * 0.55)).toFixed(0)}px "IBM Plex Mono", monospace`
    ctx.textAlign = 'left'
    ctx.fillText(name, tailX + 2, noteCentre + 3)
    ctx.textAlign = 'right'
  }
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
