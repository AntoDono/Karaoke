<template>
  <div class="min-h-screen flex flex-col bg-canvas relative">

    <!-- Atmospheric background -->
    <div class="fixed inset-0 pointer-events-none z-0">
      <div class="absolute top-[-18vh] right-[-10vw] w-[55vw] h-[55vw] rounded-full"
           style="background: radial-gradient(circle, rgba(34,197,94,0.07) 0%, transparent 65%)" />
      <div class="absolute bottom-[-12vh] left-[-8vw] w-[42vw] h-[42vw] rounded-full"
           style="background: radial-gradient(circle, rgba(74,222,128,0.05) 0%, transparent 65%)" />
      <div class="absolute inset-0 opacity-[0.02]"
           style="background-image: linear-gradient(rgba(21,128,61,1) 1px, transparent 1px), linear-gradient(90deg, rgba(21,128,61,1) 1px, transparent 1px); background-size: 52px 52px;" />
    </div>

    <!-- Header -->
    <header class="sticky top-0 z-20 flex items-center gap-4 px-5 py-3 border-b border-green-200/80 bg-canvas/92 backdrop-blur-md">
      <!-- Back + logo -->
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

      <!-- Title -->
      <div class="flex-1 min-w-0 flex flex-col gap-0.5">
        <h1 class="font-display text-[0.95rem] font-bold tracking-tight text-ink truncate m-0 leading-tight">Vocal Range Setup</h1>
        <span class="font-mono text-[0.6rem] text-ink-faint truncate">{{ store.audioFile?.name ?? 'Song' }}</span>
      </div>

      <!-- Step indicator -->
      <div class="flex items-center gap-1 shrink-0">
        <template v-for="(label, i) in steps" :key="i">
          <div
            class="w-5 h-5 rounded-full font-mono text-[0.58rem] font-bold flex items-center justify-center transition-all duration-300"
            :class="currentStep > i
              ? 'bg-green-600 text-white'
              : currentStep === i
                ? 'bg-green-100 border-2 border-green-500 text-green-700'
                : 'bg-green-50 border border-green-200 text-ink-faint'"
          >{{ i + 1 }}</div>
          <div v-if="i < steps.length - 1" class="w-3 h-px" :class="currentStep > i ? 'bg-green-400' : 'bg-green-200'" />
        </template>
      </div>
    </header>

    <main class="flex-1 flex flex-col items-center justify-start gap-6 px-4 py-8 relative z-10 max-w-2xl w-full mx-auto">

      <!-- Step transitions -->
      <transition name="slide-fade" mode="out-in">

        <!-- ── Step 0: Song range overview ─────────────────────────────────── -->
        <section v-if="currentStep === 0" key="step0" class="w-full flex flex-col gap-5 animate-fade-up">
          <div class="flex flex-col gap-1">
            <h2 class="font-display font-extrabold tracking-tight text-ink m-0" style="font-size: clamp(1.5rem, 5vw, 2rem)">Song Range</h2>
            <p class="font-mono text-[0.7rem] text-ink-faint m-0 leading-relaxed">
              This song spans these notes. We'll detect your vocal range and suggest the best transpose.
            </p>
          </div>

          <!-- Song range card -->
          <div class="bg-green-50 border border-green-200 rounded-2xl p-5 flex flex-col gap-4">
            <div class="flex items-end justify-between gap-4">
              <div class="flex flex-col gap-0.5">
                <span class="font-mono text-[0.58rem] text-ink-faint uppercase tracking-[0.1em]">Lowest note</span>
                <span class="font-display text-4xl font-extrabold text-green-700 tracking-tight leading-none">{{ songRange.minNote }}</span>
              </div>
              <!-- Visual range bar -->
              <div class="flex-1 flex flex-col items-center gap-2">
                <div class="w-full h-2.5 bg-green-100 rounded-full relative overflow-hidden border border-green-200">
                  <div class="absolute inset-y-0 left-0 right-0 bg-gradient-to-r from-green-400 via-green-500 to-green-600 rounded-full" />
                </div>
                <span class="font-mono text-[0.58rem] text-ink-faint">{{ songRange.semitones }} semitones</span>
              </div>
              <div class="flex flex-col gap-0.5 items-end">
                <span class="font-mono text-[0.58rem] text-ink-faint uppercase tracking-[0.1em]">Highest note</span>
                <span class="font-display text-4xl font-extrabold text-green-700 tracking-tight leading-none">{{ songRange.maxNote }}</span>
              </div>
            </div>
            <div class="flex items-center gap-2 pt-2 border-t border-green-200">
              <span class="w-1.5 h-1.5 rounded-full bg-green-400 shrink-0" />
              <span class="font-mono text-[0.62rem] text-ink-faint">{{ store.noteEvents.length }} notes · {{ formatTime(store.duration) }}</span>
            </div>
          </div>

          <button
            class="w-full py-3.5 rounded-xl font-mono text-[0.8rem] font-semibold bg-green-600 hover:bg-green-700 active:scale-[0.99] text-white transition-all duration-150 flex items-center justify-center gap-2 shadow-sm shadow-green-200"
            @click="currentStep = 1"
          >
            <svg viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4 shrink-0">
              <path d="M10 2a5 5 0 0 0-5 5v3H4a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5a2 2 0 0 0-2-2h-1V7a5 5 0 0 0-5-5zm0 2a3 3 0 0 1 3 3v3H7V7a3 3 0 0 1 3-3zm0 10a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3z"/>
            </svg>
            Detect My Vocal Range
          </button>
          <button
            class="w-full py-2.5 rounded-xl font-mono text-[0.72rem] text-ink-faint hover:text-green-700 hover:bg-green-50 active:scale-[0.99] transition-all border border-green-200"
            @click="skipToKaraoke"
          >
            Skip — use no transpose
          </button>
        </section>

        <!-- ── Step 1: Record vocal range ────────────────────────────────── -->
        <section v-else-if="currentStep === 1" key="step1" class="w-full flex flex-col gap-5 animate-fade-up">
          <div class="flex flex-col gap-1">
            <h2 class="font-display font-extrabold tracking-tight text-ink m-0" style="font-size: clamp(1.5rem, 5vw, 2rem)">Sing Your Range</h2>
            <p class="font-mono text-[0.7rem] text-ink-faint m-0 leading-relaxed">
              Sing from your lowest comfortable note up to your highest. The app will track your range in real-time.
            </p>
          </div>

          <!-- Live pitch display card -->
          <div class="bg-green-50 border border-green-200 rounded-2xl p-6 flex flex-col gap-5">
            <!-- Mic button -->
            <div class="flex justify-center">
              <div class="relative flex items-center justify-center" style="width: 120px; height: 120px">
                <!-- Outer pulse rings -->
                <div v-if="isRecording" class="absolute inset-0 rounded-full border-2 border-green-400 animate-ping opacity-20" />
                <div v-if="isRecording" class="absolute inset-3 rounded-full border border-green-300 animate-ping opacity-15" style="animation-delay: 0.4s" />
                <!-- Glow halo -->
                <div
                  class="absolute inset-4 rounded-full transition-all duration-500"
                  :class="isRecording ? 'shadow-[0_0_32px_8px_rgba(34,197,94,0.25)]' : 'shadow-none'"
                />
                <button
                  class="relative z-10 w-20 h-20 rounded-full flex items-center justify-center transition-all duration-200 font-mono font-bold active:scale-95"
                  :class="isRecording
                    ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-200'
                    : 'bg-green-600 hover:bg-green-700 text-white shadow-lg shadow-green-200'"
                  @click="toggleRecording"
                >
                  <svg v-if="!isRecording" viewBox="0 0 24 24" fill="currentColor" class="w-8 h-8">
                    <path d="M12 1a4 4 0 0 1 4 4v7a4 4 0 0 1-8 0V5a4 4 0 0 1 4-4zm7 11a1 1 0 0 1 1 1 8 8 0 0 1-7 7.94V23h2a1 1 0 1 1 0 2H9a1 1 0 1 1 0-2h2v-2.06A8 8 0 0 1 4 13a1 1 0 0 1 2 0 6 6 0 0 0 12 0 1 1 0 0 1 1-1z"/>
                  </svg>
                  <div v-else class="w-5 h-5 bg-white rounded" />
                </button>
              </div>
            </div>

            <!-- Live note -->
            <div class="text-center flex flex-col gap-1">
              <span class="font-mono text-[0.58rem] text-ink-faint uppercase tracking-[0.12em]">
                {{ isRecording ? 'Hearing' : 'Press mic to start' }}
              </span>
              <div
                class="font-display font-extrabold tracking-tight transition-all duration-100 leading-none"
                style="font-size: clamp(3rem, 12vw, 5rem)"
                :class="liveNote ? 'text-green-600' : 'text-green-200'"
              >
                {{ liveNote || '—' }}
              </div>
            </div>

            <!-- Detected range -->
            <div v-if="detectedRange" class="flex items-center justify-between pt-4 border-t border-green-200">
              <div class="flex flex-col gap-0.5">
                <span class="font-mono text-[0.55rem] text-ink-faint uppercase tracking-[0.08em]">Lowest</span>
                <span class="font-display text-2xl font-extrabold text-green-700 tracking-tight">{{ detectedRange.minNote }}</span>
              </div>
              <div class="flex flex-col items-center gap-1.5">
                <span class="font-mono text-[0.55rem] text-ink-faint">{{ detectedRange.maxMidi - detectedRange.minMidi }} semitones</span>
                <div class="w-24 h-1.5 bg-green-100 rounded-full overflow-hidden border border-green-200">
                  <div class="h-full bg-gradient-to-r from-green-400 to-green-600 rounded-full transition-all duration-300" :style="{ width: rangeBarPct + '%' }" />
                </div>
              </div>
              <div class="flex flex-col gap-0.5 items-end">
                <span class="font-mono text-[0.55rem] text-ink-faint uppercase tracking-[0.08em]">Highest</span>
                <span class="font-display text-2xl font-extrabold text-green-700 tracking-tight">{{ detectedRange.maxNote }}</span>
              </div>
            </div>
            <div v-else class="pt-4 border-t border-green-200 text-center font-mono text-[0.62rem] text-ink-faint">
              Sing to start detecting your range…
            </div>

            <p v-if="micError" class="font-mono text-[0.68rem] text-red-500 text-center">{{ micError }}</p>
          </div>

          <div class="flex gap-3">
            <button
              class="flex-1 py-2.5 rounded-xl font-mono text-[0.72rem] text-ink-faint hover:text-ink hover:bg-green-50 active:scale-[0.99] transition-all border border-green-200"
              @click="currentStep = 0"
            >← Back</button>
            <button
              class="flex-1 py-3 rounded-xl font-mono text-[0.8rem] font-semibold transition-all active:scale-[0.99]"
              :class="detectedRange
                ? 'bg-green-600 hover:bg-green-700 text-white shadow-sm shadow-green-200'
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
            <h2 class="font-display font-extrabold tracking-tight text-ink m-0" style="font-size: clamp(1.5rem, 5vw, 2rem)">Set Transpose</h2>
            <p class="font-mono text-[0.7rem] text-ink-faint m-0 leading-relaxed">
              Based on your range we recommend a shift. Adjust manually if you prefer.
            </p>
          </div>

          <div class="bg-green-50 border border-green-200 rounded-2xl p-5 flex flex-col gap-4">
            <!-- Range comparison -->
            <div class="grid grid-cols-2 gap-4">
              <div class="flex flex-col gap-2">
                <span class="font-mono text-[0.58rem] text-ink-faint uppercase tracking-[0.1em]">Song range</span>
                <div class="flex flex-col gap-1.5">
                  <span class="font-mono text-xs text-ink font-medium">{{ songRange.minNote }} – {{ songRange.maxNote }}</span>
                  <div class="h-2 bg-green-300 rounded-full" />
                </div>
              </div>
              <div class="flex flex-col gap-2">
                <span class="font-mono text-[0.58rem] text-ink-faint uppercase tracking-[0.1em]">Your voice</span>
                <div class="flex flex-col gap-1.5">
                  <span class="font-mono text-xs text-ink font-medium">{{ detectedRange?.minNote }} – {{ detectedRange?.maxNote }}</span>
                  <div class="h-2 bg-green-600 rounded-full" />
                </div>
              </div>
            </div>

            <!-- Transpose control -->
            <div class="flex flex-col gap-3 pt-4 border-t border-green-200">
              <div class="flex items-center justify-between">
                <span class="font-mono text-[0.62rem] text-ink-faint uppercase tracking-[0.08em]">Transpose (octaves)</span>
                <span
                  class="font-mono text-[0.62rem] font-semibold px-2.5 py-0.5 rounded-full transition-colors"
                  :class="selectedTranspose === 0 ? 'bg-green-100 text-green-700' : 'bg-green-600 text-white'"
                >{{ octaveLabel(selectedTranspose) }}</span>
              </div>

              <!-- Octave buttons -->
              <div class="grid grid-cols-5 gap-1.5">
                <button
                  v-for="oct in octaveOptions"
                  :key="oct.value"
                  class="py-2.5 rounded-xl border font-mono text-[0.68rem] font-semibold transition-all duration-150 flex flex-col items-center gap-0.5 active:scale-95"
                  :class="selectedTranspose === oct.value
                    ? 'bg-green-600 border-green-600 text-white shadow-sm'
                    : 'bg-white border-green-200 text-ink-faint hover:border-green-400 hover:text-green-700'"
                  @click="selectedTranspose = oct.value"
                >
                  <span>{{ oct.label }}</span>
                  <span class="text-[0.52rem] opacity-60">{{ oct.sub }}</span>
                </button>
              </div>

              <button
                v-if="selectedTranspose !== recommendedTranspose"
                class="font-mono text-[0.62rem] text-green-600 hover:text-green-800 transition-colors text-center"
                @click="selectedTranspose = recommendedTranspose"
              >
                Reset to recommended ({{ octaveLabel(recommendedTranspose) }})
              </button>
            </div>

            <!-- Resulting range preview -->
            <div class="flex items-center justify-between pt-4 border-t border-green-200">
              <div class="flex flex-col gap-0.5">
                <span class="font-mono text-[0.55rem] text-ink-faint uppercase tracking-[0.08em]">Song will start at</span>
                <span class="font-display text-xl font-extrabold text-green-700 tracking-tight">{{ transposedSongMin }}</span>
              </div>
              <div class="flex flex-col items-center gap-0.5">
                <span class="font-mono text-[0.55rem] text-ink-faint">
                  {{ selectedTranspose > 0 ? `+${selectedTranspose / 12} oct` : selectedTranspose < 0 ? `${selectedTranspose / 12} oct` : 'no shift' }}
                </span>
                <div class="w-8 h-px bg-green-300" />
              </div>
              <div class="flex flex-col gap-0.5 items-end">
                <span class="font-mono text-[0.55rem] text-ink-faint uppercase tracking-[0.08em]">Song will end at</span>
                <span class="font-display text-xl font-extrabold text-green-700 tracking-tight">{{ transposedSongMax }}</span>
              </div>
            </div>
          </div>

          <div class="flex gap-3">
            <button
              class="flex-1 py-2.5 rounded-xl font-mono text-[0.72rem] text-ink-faint hover:text-ink hover:bg-green-50 active:scale-[0.99] transition-all border border-green-200"
              @click="currentStep = 1"
            >← Re-sing</button>
            <button
              class="flex-1 py-3.5 rounded-xl font-mono text-[0.8rem] font-semibold bg-green-600 hover:bg-green-700 active:scale-[0.99] text-white transition-all flex items-center justify-center gap-2 shadow-sm shadow-green-200"
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

const steps = ['Song', 'Sing', 'Transpose']
const currentStep = ref(0)

const songRange = computed(() => {
  const notes = store.noteEvents
  if (!notes.length) return { minMidi: 48, maxMidi: 72, minNote: 'C3', maxNote: 'C5', semitones: 24 }
  let min = notes[0]!.midi, max = notes[0]!.midi
  for (const n of notes) {
    if (n.midi < min) min = n.midi
    if (n.midi > max) max = n.midi
  }
  return { minMidi: min, maxMidi: max, minNote: midiToName(min), maxNote: midiToName(max), semitones: max - min }
})

const { start: startMic, stop: stopMic, isRecording, error: micError, detectedRange, liveNote } = useVocalRangeDetector()

const rangeBarPct = computed(() => {
  if (!detectedRange.value) return 0
  return Math.min(100, Math.round(((detectedRange.value.maxMidi - detectedRange.value.minMidi) / 44) * 100))
})

async function toggleRecording() {
  if (isRecording.value) stopMic()
  else await startMic()
}

watch(currentStep, (step, prev) => {
  if (prev === 1 && step !== 1 && isRecording.value) stopMic()
})

const recommendedTranspose = computed(() => {
  const range = detectedRange.value
  if (!range) return 0
  const songCenter = (songRange.value.minMidi + songRange.value.maxMidi) / 2
  const userCenter = (range.minMidi + range.maxMidi) / 2
  const snapped = Math.round((userCenter - songCenter) / 12) * 12
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

const transposedSongMin = computed(() =>
  midiToName(Math.max(0, Math.min(127, songRange.value.minMidi + selectedTranspose.value)))
)
const transposedSongMax = computed(() =>
  midiToName(Math.max(0, Math.min(127, songRange.value.maxMidi + selectedTranspose.value)))
)

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

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.22s ease;
}
.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(14px);
}
.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-14px);
}
</style>
