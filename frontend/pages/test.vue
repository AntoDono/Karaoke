<template>
  <div class="min-h-screen flex flex-col bg-canvas relative">
    <div class="fixed inset-0 pointer-events-none bg-[radial-gradient(ellipse_55%_45%_at_15%_15%,rgba(21,128,61,0.07)_0%,transparent_60%)] z-0" />

    <!-- Header -->
    <header class="sticky top-0 z-20 flex items-center gap-4 px-6 py-3.5 border-b border-green-200 bg-canvas/90 backdrop-blur-md">
      <NuxtLink to="/" class="flex items-center gap-1.5 font-mono text-[0.72rem] text-ink-faint hover:text-green-700 transition-colors no-underline shrink-0">
        <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" class="w-4 h-4"><path d="M10 12 L5 8 L10 4"/></svg>
        Back
      </NuxtLink>
      <h1 class="font-display text-base font-bold tracking-tight text-ink m-0">Pitch Detection Test</h1>
      <span class="font-mono text-[0.65rem] text-ink-faint">Sing an octave to verify the system</span>
    </header>

    <main class="flex-1 flex flex-col items-center gap-6 px-4 py-8 relative z-10 max-w-3xl w-full mx-auto">

      <!-- Mic toggle -->
      <div class="flex flex-col items-center gap-3">
        <button
          class="w-16 h-16 rounded-full flex items-center justify-center transition-all duration-200 shadow-lg"
          :class="isMicActive
            ? 'bg-red-500 hover:bg-red-600 text-white shadow-red-200'
            : 'bg-green-600 hover:bg-green-700 text-white shadow-green-200'"
          @click="toggle"
        >
          <svg v-if="!isMicActive" viewBox="0 0 24 24" fill="currentColor" class="w-7 h-7">
            <path d="M12 1a4 4 0 0 1 4 4v7a4 4 0 0 1-8 0V5a4 4 0 0 1 4-4zm7 11a1 1 0 0 1 1 1 8 8 0 0 1-7 7.94V23h2a1 1 0 1 1 0 2H9a1 1 0 1 1 0-2h2v-2.06A8 8 0 0 1 4 13a1 1 0 0 1 2 0 6 6 0 0 0 12 0 1 1 0 0 1 1-1z"/>
          </svg>
          <div v-else class="w-5 h-5 bg-white rounded-sm" />
        </button>
        <span class="font-mono text-[0.7rem] text-ink-faint">{{ isMicActive ? 'Listening…' : 'Tap to start mic' }}</span>
        <p v-if="error" class="font-mono text-[0.7rem] text-red-500">{{ error }}</p>
      </div>

      <!-- RMS meter -->
      <div class="w-full max-w-md flex flex-col gap-1">
        <div class="flex justify-between font-mono text-[0.58rem] text-ink-faint">
          <span>Input level</span>
          <span>{{ isMicActive ? (rmsLevel * 100).toFixed(0) + '%' : '—' }}</span>
        </div>
        <div class="h-2 bg-green-100 border border-green-200 rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-75"
            :class="rmsLevel > 0.8 ? 'bg-red-400' : rmsLevel > 0.4 ? 'bg-yellow-400' : 'bg-green-500'"
            :style="{ width: (rmsLevel * 100) + '%' }"
          />
        </div>
      </div>

      <!-- Main detection display -->
      <div class="w-full max-w-md bg-green-50 border border-green-200 rounded-2xl p-6 flex flex-col gap-4">

        <!-- Big note name -->
        <div class="text-center flex flex-col gap-1">
          <div
            class="font-display text-7xl font-extrabold tracking-tight transition-all duration-100"
            :class="committedNote ? 'text-green-700' : 'text-green-200'"
          >
            {{ committedNote || '—' }}
          </div>
          <div class="flex justify-center gap-4 font-mono text-[0.65rem] text-ink-faint">
            <span>MIDI {{ committedMidi || '—' }}</span>
            <span>·</span>
            <span>{{ rawHz > 0 ? rawHz.toFixed(1) + ' Hz' : '— Hz' }}</span>
            <span>·</span>
            <span>{{ rawHz > 0 ? hzToMidi(rawHz) + ' raw' : '— raw' }}</span>
          </div>
        </div>

        <!-- Smoothing buffer visualiser -->
        <div class="flex flex-col gap-1.5">
          <span class="font-mono text-[0.58rem] text-ink-faint uppercase tracking-[0.07em]">
            Smoothing buffer (last {{ BUFFER_SIZE }} frames, need {{ COMMIT_MAJORITY }} to commit)
          </span>
          <div class="flex gap-1">
            <div
              v-for="(slot, i) in bufferDisplay"
              :key="i"
              class="flex-1 h-8 rounded-md flex items-center justify-center font-mono text-[0.58rem] font-bold transition-all duration-100"
              :class="slot
                ? slot === committedNote
                  ? 'bg-green-600 text-white'
                  : 'bg-green-200 text-green-800'
                : 'bg-green-50 border border-green-100 text-green-200'"
            >
              {{ slot || '·' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Chromatic keyboard — two octaves centred on detected note's octave -->
      <div class="w-full max-w-2xl flex flex-col gap-2">
        <span class="font-mono text-[0.65rem] text-ink-faint uppercase tracking-[0.07em]">
          Chromatic keyboard — {{ octaveLabel }}
        </span>
        <div class="relative h-24 flex gap-px select-none">
          <div
            v-for="key in keys"
            :key="key.midi"
            class="relative flex flex-col justify-end items-center pb-1.5 rounded-b-md transition-all duration-75 cursor-default"
            :class="[
              key.isBlack
                ? 'z-10 w-[6%] h-[60%] -mx-[3%] bg-ink'
                : 'flex-1 h-full border border-green-200',
              key.midi === committedMidi && isMicActive
                ? key.isBlack
                  ? 'bg-green-500'
                  : 'bg-green-400 border-green-400'
                : key.isBlack
                  ? 'bg-ink hover:bg-green-900'
                  : 'bg-white hover:bg-green-50',
            ]"
          >
            <span
              v-if="!key.isBlack"
              class="font-mono text-[0.5rem] leading-none"
              :class="key.midi === committedMidi && isMicActive ? 'text-ink font-bold' : 'text-ink-faint'"
            >
              {{ key.label }}
            </span>
          </div>
        </div>
      </div>

      <!-- Note history log -->
      <div class="w-full max-w-md flex flex-col gap-2">
        <div class="flex items-center justify-between">
          <span class="font-mono text-[0.65rem] text-ink-faint uppercase tracking-[0.07em]">Note log</span>
          <button
            class="font-mono text-[0.6rem] text-green-600 hover:text-green-800 transition-colors"
            @click="noteLog.length = 0"
          >clear</button>
        </div>
        <div class="bg-green-50 border border-green-200 rounded-xl p-3 min-h-[60px] flex flex-wrap gap-1.5 content-start">
          <span
            v-for="(entry, i) in noteLog"
            :key="i"
            class="font-mono text-[0.65rem] px-1.5 py-0.5 rounded bg-green-200 text-green-800"
          >{{ entry }}</span>
          <span v-if="!noteLog.length" class="font-mono text-[0.65rem] text-ink-faint">Sing notes to see them appear here…</span>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup lang="ts">
import { hzToMidi, midiToName } from '~/composables/pitchDetector'

const BUFFER_SIZE     = 8
const COMMIT_MAJORITY = 5

const store = useKaraokeStore()
const { toggle, error, rawHz, rmsLevel } = useMicRecorder()

const isMicActive  = computed(() => store.isMicActive)
const committedNote = computed(() => store.liveNoteName)
const committedMidi = computed(() => store.liveMidi)

// ── Smoothing buffer visualiser ──────────────────────────────────────────────
// Mirror the buffer state by watching committed note changes
const bufferDisplay = ref<(string | null)[]>(Array(BUFFER_SIZE).fill(null))
const internalHistory = ref<string[]>([])

watch(() => store.liveF0, (hz) => {
  if (!isMicActive.value) return
  if (hz > 0) {
    const midi = hzToMidi(hz)
    const name = midiToName(midi)
    internalHistory.value.push(name)
    if (internalHistory.value.length > BUFFER_SIZE) internalHistory.value.shift()
  } else {
    internalHistory.value = []
  }
  const display = [...internalHistory.value]
  while (display.length < BUFFER_SIZE) display.unshift(null as any)
  bufferDisplay.value = display
})

watch(isMicActive, (active) => {
  if (!active) {
    internalHistory.value = []
    bufferDisplay.value = Array(BUFFER_SIZE).fill(null)
  }
})

// ── Note history log ─────────────────────────────────────────────────────────
const noteLog = reactive<string[]>([])
let lastLogged = ''

watch(committedNote, (note) => {
  if (note && note !== lastLogged) {
    lastLogged = note
    noteLog.push(note)
    if (noteLog.length > 40) noteLog.shift()
  }
})

// ── Chromatic keyboard — 2 octaves centred on detected note ──────────────────
const NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
const BLACK_KEYS = new Set([1,3,6,8,10])

const centreOctave = computed(() => {
  if (committedMidi.value > 0) return Math.floor(committedMidi.value / 12) - 1
  return 3  // default C3–B4
})

const octaveLabel = computed(() =>
  `C${centreOctave.value} – B${centreOctave.value + 1}`
)

const keys = computed(() => {
  const startMidi = (centreOctave.value + 1) * 12   // C of centreOctave
  const result = []
  for (let midi = startMidi; midi < startMidi + 24; midi++) {
    const semitone = midi % 12
    const isBlack  = BLACK_KEYS.has(semitone)
    const octave   = Math.floor(midi / 12) - 1
    const label    = semitone === 0 ? `C${octave}` : NOTE_NAMES[semitone] ?? ''
    result.push({ midi, isBlack, label })
  }
  return result
})
</script>
