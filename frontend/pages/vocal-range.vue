<template>
  <div class="min-h-screen flex flex-col bg-canvas relative">
    <!-- Background mesh -->
    <div class="fixed inset-0 pointer-events-none bg-[radial-gradient(ellipse_55%_45%_at_15%_15%,rgba(21,128,61,0.07)_0%,transparent_60%),radial-gradient(ellipse_40%_55%_at_85%_85%,rgba(74,222,128,0.05)_0%,transparent_60%)] z-0" />

    <!-- Header -->
    <header class="sticky top-0 z-20 flex items-center gap-4 px-6 py-3.5 border-b border-green-200 bg-canvas/90 backdrop-blur-md">
      <NuxtLink
        to="/"
        class="flex items-center gap-1.5 font-mono text-[0.72rem] text-ink-faint hover:text-green-700 transition-colors no-underline shrink-0"
      >
        <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" class="w-4 h-4">
          <path d="M10 12 L5 8 L10 4"/>
        </svg>
        Back
      </NuxtLink>
      <div class="flex-1 min-w-0 flex flex-col gap-0.5">
        <h1 class="font-display text-base font-bold tracking-tight text-ink truncate m-0">Vocal Range Setup</h1>
        <span class="font-mono text-[0.65rem] text-ink-faint truncate">{{ store.audioFile?.name ?? 'Song' }}</span>
      </div>
      <!-- Step indicator -->
      <div class="flex items-center gap-1.5 shrink-0">
        <div
          v-for="(label, i) in steps"
          :key="i"
          class="flex items-center gap-1"
        >
          <div
            class="w-5 h-5 rounded-full font-mono text-[0.6rem] font-bold flex items-center justify-center transition-all duration-300"
            :class="currentStep > i
              ? 'bg-green-600 text-white'
              : currentStep === i
                ? 'bg-green-100 border-2 border-green-500 text-green-700'
                : 'bg-green-50 border border-green-200 text-ink-faint'"
          >{{ i + 1 }}</div>
          <div v-if="i < steps.length - 1" class="w-4 h-px bg-green-200" />
        </div>
      </div>
    </header>

    <main class="flex-1 flex flex-col items-center justify-start gap-6 px-4 py-8 relative z-10 max-w-2xl w-full mx-auto">

      <!-- ── Step 0: Song range overview ─────────────────────────────────── -->
      <transition name="slide-fade" mode="out-in">
        <section v-if="currentStep === 0" key="step0" class="w-full flex flex-col gap-5 animate-fade-up">
          <div class="flex flex-col gap-1">
            <h2 class="font-display text-xl font-bold text-ink m-0">Song Range</h2>
            <p class="font-mono text-[0.72rem] text-ink-faint m-0">
              This song spans these notes. We'll detect your vocal range and suggest the best transpose.
            </p>
          </div>

          <!-- Song range card -->
          <div class="bg-green-50 border border-green-200 rounded-2xl p-5 flex flex-col gap-4">
            <div class="flex items-end justify-between gap-4">
              <div class="flex flex-col gap-0.5">
                <span class="font-mono text-[0.6rem] text-ink-faint uppercase tracking-[0.08em]">Lowest note</span>
                <span class="font-display text-3xl font-extrabold text-green-700 tracking-tight">{{ songRange.minNote }}</span>
              </div>
              <!-- Visual range bar -->
              <div class="flex-1 flex flex-col items-center gap-1.5">
                <div class="w-full h-3 bg-green-200 rounded-full relative overflow-hidden">
                  <div class="absolute inset-y-0 left-0 right-0 bg-gradient-to-r from-green-400 to-green-600 rounded-full" />
                </div>
                <span class="font-mono text-[0.6rem] text-ink-faint">{{ songRange.semitones }} semitones</span>
              </div>
              <div class="flex flex-col gap-0.5 items-end">
                <span class="font-mono text-[0.6rem] text-ink-faint uppercase tracking-[0.08em]">Highest note</span>
                <span class="font-display text-3xl font-extrabold text-green-700 tracking-tight">{{ songRange.maxNote }}</span>
              </div>
            </div>
            <div class="flex items-center gap-2 pt-1 border-t border-green-200">
              <span class="font-mono text-[0.65rem] text-ink-faint">{{ store.noteEvents.length }} notes · {{ formatTime(store.duration) }}</span>
            </div>
          </div>

          <button
            class="w-full py-3.5 rounded-xl font-mono text-sm font-semibold bg-green-600 hover:bg-green-700 text-white transition-colors flex items-center justify-center gap-2"
            @click="currentStep = 1"
          >
            <svg viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
              <path d="M10 2a5 5 0 0 0-5 5v3H4a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5a2 2 0 0 0-2-2h-1V7a5 5 0 0 0-5-5zm0 2a3 3 0 0 1 3 3v3H7V7a3 3 0 0 1 3-3zm0 10a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3z"/>
            </svg>
            Detect My Vocal Range
          </button>
          <button
            class="w-full py-2.5 rounded-xl font-mono text-[0.75rem] text-ink-faint hover:text-green-700 hover:bg-green-50 transition-colors border border-green-200"
            @click="skipToKaraoke"
          >
            Skip — use no transpose
          </button>
        </section>

        <!-- ── Step 1: Record vocal range ────────────────────────────────── -->
        <section v-else-if="currentStep === 1" key="step1" class="w-full flex flex-col gap-5 animate-fade-up">
          <div class="flex flex-col gap-1">
            <h2 class="font-display text-xl font-bold text-ink m-0">Sing Your Range</h2>
            <p class="font-mono text-[0.72rem] text-ink-faint m-0">
              Sing from your lowest comfortable note up to your highest. The app will track your range in real-time.
            </p>
          </div>

          <!-- Live pitch display -->
          <div class="bg-green-50 border border-green-200 rounded-2xl p-5 flex flex-col gap-4">
            <!-- Visualizer rings when recording -->
            <div class="flex justify-center">
              <div class="relative w-28 h-28 flex items-center justify-center">
                <!-- Pulse rings -->
                <div
                  v-if="isRecording"
                  class="absolute inset-0 rounded-full border-2 border-green-400 animate-ping opacity-30"
                />
                <div
                  v-if="isRecording"
                  class="absolute inset-2 rounded-full border border-green-300 animate-ping opacity-20"
                  style="animation-delay: 0.3s"
                />
                <button
                  class="relative z-10 w-20 h-20 rounded-full flex items-center justify-center transition-all duration-200 font-mono text-xs font-bold"
                  :class="isRecording
                    ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-200'
                    : 'bg-green-600 hover:bg-green-700 text-white shadow-lg shadow-green-200'"
                  @click="toggleRecording"
                >
                  <svg v-if="!isRecording" viewBox="0 0 24 24" fill="currentColor" class="w-8 h-8">
                    <path d="M12 1a4 4 0 0 1 4 4v7a4 4 0 0 1-8 0V5a4 4 0 0 1 4-4zm7 11a1 1 0 0 1 1 1 8 8 0 0 1-7 7.94V23h2a1 1 0 1 1 0 2H9a1 1 0 1 1 0-2h2v-2.06A8 8 0 0 1 4 13a1 1 0 0 1 2 0 6 6 0 0 0 12 0 1 1 0 0 1 1-1z"/>
                  </svg>
                  <div v-else class="w-6 h-6 bg-white rounded-sm" />
                </button>
              </div>
            </div>

            <!-- Live note display -->
            <div class="text-center flex flex-col gap-1">
              <div class="font-mono text-[0.6rem] text-ink-faint uppercase tracking-[0.08em]">
                {{ isRecording ? 'Hearing' : 'Press mic to start' }}
              </div>
              <div
                class="font-display text-4xl font-extrabold tracking-tight transition-all duration-150"
                :class="liveNote ? 'text-green-600' : 'text-green-200'"
              >
                {{ liveNote || '—' }}
              </div>
            </div>

            <!-- Detected range so far -->
            <div v-if="detectedRange" class="flex items-center justify-between pt-3 border-t border-green-200">
              <div class="flex flex-col gap-0.5">
                <span class="font-mono text-[0.58rem] text-ink-faint uppercase tracking-[0.07em]">Lowest</span>
                <span class="font-display text-xl font-extrabold text-green-700">{{ detectedRange.minNote }}</span>
              </div>
              <div class="flex flex-col items-center gap-0.5">
                <span class="font-mono text-[0.58rem] text-ink-faint">{{ detectedRange.maxMidi - detectedRange.minMidi }} semitones</span>
                <div class="w-20 h-1.5 bg-green-200 rounded-full overflow-hidden">
                  <div class="h-full bg-green-500 rounded-full transition-all duration-300" :style="{ width: rangeBarPct + '%' }" />
                </div>
              </div>
              <div class="flex flex-col gap-0.5 items-end">
                <span class="font-mono text-[0.58rem] text-ink-faint uppercase tracking-[0.07em]">Highest</span>
                <span class="font-display text-xl font-extrabold text-green-700">{{ detectedRange.maxNote }}</span>
              </div>
            </div>
            <div v-else class="pt-3 border-t border-green-200 text-center font-mono text-[0.65rem] text-ink-faint">
              Sing to start detecting your range…
            </div>

            <!-- Error -->
            <p v-if="micError" class="font-mono text-[0.7rem] text-red-500 text-center">{{ micError }}</p>
          </div>

          <div class="flex gap-3">
            <button
              class="flex-1 py-2.5 rounded-xl font-mono text-[0.75rem] text-ink-faint hover:text-ink hover:bg-green-50 transition-colors border border-green-200"
              @click="currentStep = 0"
            >
              ← Back
            </button>
            <button
              class="flex-1 py-3 rounded-xl font-mono text-sm font-semibold transition-colors"
              :class="detectedRange
                ? 'bg-green-600 hover:bg-green-700 text-white'
                : 'bg-green-100 text-green-400 cursor-not-allowed'"
              :disabled="!detectedRange"
              @click="goToTranspose"
            >
              See Recommended Transpose →
            </button>
          </div>
        </section>

        <!-- ── Step 2: Transpose selection ───────────────────────────────── -->
        <section v-else-if="currentStep === 2" key="step2" class="w-full flex flex-col gap-5 animate-fade-up">
          <div class="flex flex-col gap-1">
            <h2 class="font-display text-xl font-bold text-ink m-0">Set Transpose</h2>
            <p class="font-mono text-[0.72rem] text-ink-faint m-0">
              Based on your range we recommend a shift. Adjust manually if you prefer.
            </p>
          </div>

          <!-- Range comparison card -->
          <div class="bg-green-50 border border-green-200 rounded-2xl p-5 flex flex-col gap-4">
            <div class="grid grid-cols-2 gap-4">
              <div class="flex flex-col gap-2">
                <span class="font-mono text-[0.6rem] text-ink-faint uppercase tracking-[0.08em]">Song range</span>
                <div class="flex flex-col gap-0.5">
                  <span class="font-mono text-xs text-ink">{{ songRange.minNote }} – {{ songRange.maxNote }}</span>
                  <div class="h-2 bg-green-300 rounded-full" />
                </div>
              </div>
              <div class="flex flex-col gap-2">
                <span class="font-mono text-[0.6rem] text-ink-faint uppercase tracking-[0.08em]">Your voice</span>
                <div class="flex flex-col gap-0.5">
                  <span class="font-mono text-xs text-ink">{{ detectedRange?.minNote }} – {{ detectedRange?.maxNote }}</span>
                  <div class="h-2 bg-green-500 rounded-full" />
                </div>
              </div>
            </div>

            <!-- Transpose control — octave steps only -->
            <div class="flex flex-col gap-3 pt-3 border-t border-green-200">
              <div class="flex items-center justify-between">
                <span class="font-mono text-[0.65rem] text-ink-faint uppercase tracking-[0.07em]">Transpose (octaves)</span>
                <span
                  class="font-mono text-[0.65rem] font-semibold px-2 py-0.5 rounded-full"
                  :class="selectedTranspose === 0 ? 'bg-green-100 text-green-700' : 'bg-green-600 text-white'"
                >{{ octaveLabel(selectedTranspose) }}</span>
              </div>

              <!-- Octave selector buttons -->
              <div class="grid grid-cols-5 gap-1.5">
                <button
                  v-for="oct in octaveOptions"
                  :key="oct.value"
                  class="py-2.5 rounded-xl border font-mono text-[0.7rem] font-semibold transition-all duration-150 flex flex-col items-center gap-0.5"
                  :class="selectedTranspose === oct.value
                    ? 'bg-green-600 border-green-600 text-white shadow-sm'
                    : 'bg-white border-green-200 text-ink-faint hover:border-green-400 hover:text-green-700'"
                  @click="selectedTranspose = oct.value"
                >
                  <span>{{ oct.label }}</span>
                  <span class="text-[0.55rem] opacity-60">{{ oct.sub }}</span>
                </button>
              </div>

              <button
                v-if="selectedTranspose !== recommendedTranspose"
                class="font-mono text-[0.65rem] text-green-600 hover:text-green-800 transition-colors text-center"
                @click="selectedTranspose = recommendedTranspose"
              >
                Reset to recommended ({{ octaveLabel(recommendedTranspose) }})
              </button>
            </div>

            <!-- Resulting range preview -->
            <div class="flex items-center justify-between pt-3 border-t border-green-200">
              <div class="flex flex-col gap-0.5">
                <span class="font-mono text-[0.58rem] text-ink-faint uppercase tracking-[0.07em]">Song will start at</span>
                <span class="font-display text-lg font-extrabold text-green-700">{{ transposedSongMin }}</span>
              </div>
              <div class="flex flex-col items-center gap-0.5">
                <span class="font-mono text-[0.58rem] text-ink-faint">shifted {{ selectedTranspose > 0 ? 'up' : selectedTranspose < 0 ? 'down' : '—' }}</span>
              </div>
              <div class="flex flex-col gap-0.5 items-end">
                <span class="font-mono text-[0.58rem] text-ink-faint uppercase tracking-[0.07em]">Song will end at</span>
                <span class="font-display text-lg font-extrabold text-green-700">{{ transposedSongMax }}</span>
              </div>
            </div>
          </div>

          <div class="flex gap-3">
            <button
              class="flex-1 py-2.5 rounded-xl font-mono text-[0.75rem] text-ink-faint hover:text-ink hover:bg-green-50 transition-colors border border-green-200"
              @click="currentStep = 1"
            >
              ← Re-sing
            </button>
            <button
              class="flex-1 py-3.5 rounded-xl font-mono text-sm font-semibold bg-green-600 hover:bg-green-700 text-white transition-colors flex items-center justify-center gap-2"
              @click="confirm"
            >
              Confirm & Sing
              <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" class="w-4 h-4">
                <path d="M6 4 L11 8 L6 12"/>
              </svg>
            </button>
          </div>
        </section>
      </transition>
    </main>
  </div>
</template>

<script setup lang="ts">
const store  = useKaraokeStore()
const router = useRouter()
const route  = useRoute()
const config = useRuntimeConfig()

const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
function midiToName(midi: number): string {
  const octave = Math.floor(midi / 12) - 1
  return `${NOTE_NAMES[midi % 12]}${octave}`
}

// If the store has no data, try to re-fetch it (page refresh scenario)
const isLoading = ref(false)
onMounted(async () => {
  if (store.analysisResult) return

  const jobId = route.query.job as string | undefined
  if (!jobId) { router.replace('/'); return }

  isLoading.value = true
  try {
    const job = await $fetch<{ status: string; result: any; error?: string }>(
      `${config.public.apiBase}/api/jobs/${jobId}`
    )
    if (job.status === 'complete' && job.result) {
      store.updateJobStatus('complete', 'Done', job.result)
    } else {
      router.replace('/')
    }
  } catch {
    router.replace('/')
  } finally {
    isLoading.value = false
  }
})

// ── Steps ───────────────────────────────────────────────────────────────────
const steps = ['Song', 'Sing', 'Transpose']
const currentStep = ref(0)

// ── Song range ──────────────────────────────────────────────────────────────
const songRange = computed(() => {
  const notes = store.noteEvents
  if (!notes.length) return { minMidi: 48, maxMidi: 72, minNote: 'C3', maxNote: 'C5', semitones: 24 }
  let min = notes[0]!.midi, max = notes[0]!.midi
  for (const n of notes) {
    if (n.midi < min) min = n.midi
    if (n.midi > max) max = n.midi
  }
  return {
    minMidi: min,
    maxMidi: max,
    minNote: midiToName(min),
    maxNote: midiToName(max),
    semitones: max - min,
  }
})

// ── Mic / range detector ────────────────────────────────────────────────────
const { start: startMic, stop: stopMic, reset: resetMic, isRecording, error: micError, detectedRange, liveMidi: _liveMidi, liveNote } = useVocalRangeDetector()

const rangeBarPct = computed(() => {
  if (!detectedRange.value) return 0
  // Normalise against a 44-semitone human-useful range (E2–C6)
  return Math.min(100, Math.round(((detectedRange.value.maxMidi - detectedRange.value.minMidi) / 44) * 100))
})

async function toggleRecording() {
  if (isRecording.value) {
    stopMic()
  } else {
    await startMic()
  }
}

// Stop mic when leaving step 1
watch(currentStep, (step, prev) => {
  if (prev === 1 && step !== 1 && isRecording.value) stopMic()
})

// ── Transpose recommendation — octave-only (multiples of 12) ────────────────
const recommendedTranspose = computed(() => {
  const range = detectedRange.value
  if (!range) return 0
  const songCenter = (songRange.value.minMidi + songRange.value.maxMidi) / 2
  const userCenter = (range.minMidi + range.maxMidi) / 2
  const raw = userCenter - songCenter
  // Round to nearest octave, clamp to ±2 octaves
  const snapped = Math.round(raw / 12) * 12
  return Math.max(-24, Math.min(24, snapped))
})

const selectedTranspose = ref(0)

const octaveOptions = [
  { value: -24, label: '−2 oct', sub: '−24st' },
  { value: -12, label: '−1 oct', sub: '−12st' },
  { value:   0, label:  'none',  sub:   '0st'  },
  { value:  12, label: '+1 oct', sub: '+12st'  },
  { value:  24, label: '+2 oct', sub: '+24st'  },
]

function octaveLabel(semitones: number): string {
  if (semitones === 0) return 'no transpose'
  const octs = semitones / 12
  return `${octs > 0 ? '+' : ''}${octs} octave${Math.abs(octs) === 1 ? '' : 's'}`
}

function goToTranspose() {
  if (!detectedRange.value) return
  selectedTranspose.value = recommendedTranspose.value
  currentStep.value = 2
}

// ── Transposed song preview ─────────────────────────────────────────────────
const transposedSongMin = computed(() =>
  midiToName(Math.max(0, Math.min(127, songRange.value.minMidi + selectedTranspose.value)))
)
const transposedSongMax = computed(() =>
  midiToName(Math.max(0, Math.min(127, songRange.value.maxMidi + selectedTranspose.value)))
)

// ── Navigation ──────────────────────────────────────────────────────────────
function confirm() {
  if (detectedRange.value) {
    store.setVocalRange({
      minMidi: detectedRange.value.minMidi,
      maxMidi: detectedRange.value.maxMidi,
      minNote: detectedRange.value.minNote,
      maxNote: detectedRange.value.maxNote,
    })
  }
  store.setTranspose(selectedTranspose.value)
  router.push(`/karaoke?job=${store.jobId}`)
}

function skipToKaraoke() {
  store.setTranspose(0)
  router.push(`/karaoke?job=${store.jobId}`)
}

function formatTime(sec: number): string {
  const s = Math.floor(sec)
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
}

onUnmounted(() => {
  if (isRecording.value) stopMic()
})
</script>

<style scoped>
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.25s ease;
}
.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(16px);
}
.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-16px);
}
</style>
