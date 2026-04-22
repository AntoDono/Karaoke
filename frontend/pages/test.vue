<template>
  <div class="min-h-screen flex flex-col bg-canvas relative">

    <!-- Atmospheric background -->
    <div class="fixed inset-0 pointer-events-none z-0">
      <div class="absolute top-[-15vh] right-[-10vw] w-[50vw] h-[50vw] rounded-full"
           style="background: radial-gradient(circle, rgba(34,197,94,0.07) 0%, transparent 65%)" />
      <div class="absolute bottom-[-10vh] left-[-8vw] w-[38vw] h-[38vw] rounded-full"
           style="background: radial-gradient(circle, rgba(74,222,128,0.05) 0%, transparent 65%)" />
      <div class="absolute inset-0 opacity-[0.02]"
           style="background-image: linear-gradient(rgba(21,128,61,1) 1px, transparent 1px), linear-gradient(90deg, rgba(21,128,61,1) 1px, transparent 1px); background-size: 52px 52px;" />
    </div>

    <!-- Header -->
    <header class="sticky top-0 z-20 flex items-center gap-4 px-5 py-3 border-b border-green-200/80 bg-canvas/92 backdrop-blur-md">
      <div class="flex items-center gap-3 shrink-0">
        <NuxtLink to="/" class="flex items-center gap-1.5 font-mono text-[0.68rem] text-ink-faint hover:text-green-700 transition-colors no-underline group">
          <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" class="w-3.5 h-3.5 transition-transform group-hover:-translate-x-0.5">
            <path d="M10 12 L5 8 L10 4"/>
          </svg>
          Back
        </NuxtLink>
        <div class="w-px h-4 bg-green-200" />
        <div class="flex items-end gap-[2px]" style="height: 14px">
          <span class="bar w-[2px] rounded-full bg-green-500" style="--base-h: 5px; animation-duration: 1.3s" />
          <span class="bar w-[2px] rounded-full bg-green-500" style="--base-h: 10px; animation-duration: 1.05s; animation-delay: 0.12s" />
          <span class="bar w-[2px] rounded-full bg-green-600" style="--base-h: 14px; animation-duration: 0.9s; animation-delay: 0.2s" />
          <span class="bar w-[2px] rounded-full bg-green-500" style="--base-h: 9px; animation-duration: 1.15s; animation-delay: 0.08s" />
          <span class="bar w-[2px] rounded-full bg-green-400" style="--base-h: 4px; animation-duration: 1.4s; animation-delay: 0.28s" />
        </div>
      </div>
      <div class="flex-1 min-w-0 flex flex-col gap-0.5">
        <h1 class="font-display text-[0.95rem] font-bold tracking-tight text-ink m-0 leading-tight">Pitch Detection Test</h1>
        <span class="font-mono text-[0.6rem] text-ink-faint">Sing an octave to verify the system</span>
      </div>
      <div
        class="font-mono text-[0.58rem] tracking-[0.1em] uppercase px-2.5 py-1 rounded-full border flex items-center gap-1.5 shrink-0 transition-colors"
        :class="isMicActive ? 'border-green-400 bg-green-100 text-green-700' : 'border-green-200 bg-green-50 text-ink-faint'"
      >
        <span class="w-1.5 h-1.5 rounded-full transition-colors" :class="isMicActive ? 'bg-green-500 animate-pulse' : 'bg-green-300'" />
        {{ isMicActive ? 'Listening' : 'Idle' }}
      </div>
    </header>

    <main class="flex-1 flex flex-col items-center gap-6 px-4 py-8 relative z-10 max-w-3xl w-full mx-auto">

      <!-- Mic toggle + RMS -->
      <div class="w-full max-w-md flex flex-col items-center gap-4">
        <button
          class="w-14 h-14 rounded-full flex items-center justify-center transition-all duration-200 shadow-lg active:scale-95"
          :class="isMicActive
            ? 'bg-red-500 hover:bg-red-600 text-white shadow-red-200'
            : 'bg-green-600 hover:bg-green-700 text-white shadow-green-200'"
          @click="toggle"
        >
          <svg v-if="!isMicActive" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
            <path d="M12 1a4 4 0 0 1 4 4v7a4 4 0 0 1-8 0V5a4 4 0 0 1 4-4zm7 11a1 1 0 0 1 1 1 8 8 0 0 1-7 7.94V23h2a1 1 0 1 1 0 2H9a1 1 0 1 1 0-2h2v-2.06A8 8 0 0 1 4 13a1 1 0 0 1 2 0 6 6 0 0 0 12 0 1 1 0 0 1 1-1z"/>
          </svg>
          <div v-else class="w-4 h-4 bg-white rounded-sm" />
        </button>
        <span class="font-mono text-[0.65rem] text-ink-faint">{{ isMicActive ? 'Listening…' : 'Tap to start mic' }}</span>
        <p v-if="error" class="font-mono text-[0.68rem] text-red-500 text-center">{{ error }}</p>

        <!-- RMS meter -->
        <div class="w-full flex flex-col gap-1.5">
          <div class="flex justify-between font-mono text-[0.55rem] text-ink-faint">
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
      </div>

      <!-- Main pitch display -->
      <div class="w-full max-w-md bg-green-50 border border-green-200 rounded-2xl p-6 flex flex-col gap-5">

        <!-- Big note -->
        <div class="text-center flex flex-col gap-2">
          <div
            class="font-display font-extrabold tracking-[-0.04em] transition-all duration-100 leading-none"
            style="font-size: clamp(5rem, 20vw, 8rem)"
            :class="committedNote ? 'text-green-700' : 'text-green-200'"
          >
            {{ committedNote || '—' }}
          </div>
          <div class="flex justify-center gap-3 font-mono text-[0.62rem] text-ink-faint flex-wrap">
            <span>MIDI&thinsp;{{ committedMidi || '—' }}</span>
            <span class="text-green-200">·</span>
            <span>{{ rawHz > 0 ? rawHz.toFixed(1) + ' Hz' : '— Hz' }}</span>
            <span class="text-green-200">·</span>
            <span>{{ rawHz > 0 ? hzToMidi(rawHz) + ' raw' : '— raw' }}</span>
          </div>
        </div>

        <!-- Smoothing buffer -->
        <div class="flex flex-col gap-2">
          <span class="font-mono text-[0.55rem] text-ink-faint uppercase tracking-[0.1em]">
            Smoothing buffer ({{ BUFFER_SIZE }} frames · need {{ COMMIT_MAJORITY }} to commit)
          </span>
          <div class="flex gap-1">
            <div
              v-for="(slot, i) in bufferDisplay"
              :key="i"
              class="flex-1 h-9 rounded-lg flex items-center justify-center font-mono text-[0.55rem] font-bold transition-all duration-100"
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

      <!-- Chromatic keyboard -->
      <div class="w-full max-w-2xl flex flex-col gap-2">
        <span class="font-mono text-[0.6rem] text-ink-faint uppercase tracking-[0.08em]">
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
              class="font-mono text-[0.48rem] leading-none"
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
          <span class="font-mono text-[0.6rem] text-ink-faint uppercase tracking-[0.08em]">Note log</span>
          <button
            class="font-mono text-[0.58rem] text-green-600 hover:text-green-800 transition-colors"
            @click="noteLog.length = 0"
          >clear</button>
        </div>
        <div class="bg-green-50 border border-green-200 rounded-xl p-3 min-h-[56px] flex flex-wrap gap-1.5 content-start">
          <span
            v-for="(entry, i) in noteLog"
            :key="i"
            class="font-mono text-[0.62rem] px-1.5 py-0.5 rounded-md bg-green-200 text-green-800"
          >{{ entry }}</span>
          <span v-if="!noteLog.length" class="font-mono text-[0.62rem] text-ink-faint">Sing notes to see them appear here…</span>
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

const isMicActive   = computed(() => store.isMicActive)
const committedNote = computed(() => store.liveNoteName)
const committedMidi = computed(() => store.liveMidi)

// Smoothing buffer visualiser
const bufferDisplay   = ref<(string | null)[]>(Array(BUFFER_SIZE).fill(null))
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

// Note history log
const noteLog = reactive<string[]>([])
let lastLogged = ''

watch(committedNote, (note) => {
  if (note && note !== lastLogged) {
    lastLogged = note
    noteLog.push(note)
    if (noteLog.length > 40) noteLog.shift()
  }
})

// Chromatic keyboard
const NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
const BLACK_KEYS = new Set([1,3,6,8,10])

const centreOctave = computed(() => {
  if (committedMidi.value > 0) return Math.floor(committedMidi.value / 12) - 1
  return 3
})

const octaveLabel = computed(() =>
  `C${centreOctave.value} – B${centreOctave.value + 1}`
)

const keys = computed(() => {
  const startMidi = (centreOctave.value + 1) * 12
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

<style scoped>
.bar {
  display: inline-block;
  height: var(--base-h, 10px);
  transform-origin: bottom;
  animation: barBounce var(--dur, 1s) ease-in-out infinite alternate;
}

@keyframes barBounce {
  0%   { transform: scaleY(0.2); }
  100% { transform: scaleY(1); }
}
</style>
