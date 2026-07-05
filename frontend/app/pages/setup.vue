<template>
  <div class="min-h-screen bg-rice relative overflow-x-hidden flex flex-col">
    <LayoutPageNav />

    <main class="flex-1 max-w-3xl w-full mx-auto px-6 md:px-10 pt-8 pb-16">

      <!-- Header -->
      <div class="mb-8">
        <div class="font-mono text-[0.62rem] uppercase tracking-[0.24em] text-moss-700 mb-3">
          § Setup · step {{ step + 1 }} of 3
        </div>
        <h1 class="font-display font-black leading-[0.9] tracking-tightest text-moss-900" style="font-size: clamp(2rem, 5.5vw, 3.5rem)">
          {{ stepTitles[step] }}<span class="text-moss-500">.</span>
        </h1>
        <p v-if="store.title" class="font-mono text-[0.72rem] uppercase tracking-[0.14em] text-ink-faint mt-4">
          {{ store.title }} · {{ store.artist }}
        </p>
      </div>

      <!-- Step indicator -->
      <div class="flex items-center gap-2 mb-10">
        <template v-for="(_, i) in stepTitles" :key="i">
          <div class="h-1 flex-1 rounded-full transition-colors"
               :class="i <= step ? 'bg-moss-800' : 'bg-moss-800/15'" />
        </template>
      </div>

      <!-- Loading state (fetching job) -->
      <div v-if="loading" class="py-20 flex flex-col items-center gap-4">
        <div class="w-10 h-10 rounded-full border-2 border-moss-800/20 border-t-moss-700 animate-spin" />
        <span class="font-mono text-xs uppercase tracking-widest text-ink-faint">Loading analysis…</span>
      </div>

      <!-- Step 0 — Song range -->
      <section v-else-if="step === 0" class="animate-rise">
        <div class="bg-cream-50 border border-moss-800/12 rounded-3xl p-8 shadow-soft">
          <div class="grid grid-cols-3 gap-6 items-end">
            <div>
              <div class="font-mono text-[0.58rem] uppercase tracking-[0.2em] text-ink-faint">Lowest</div>
              <div class="font-display font-black text-4xl md:text-5xl text-moss-800 leading-none">{{ songRange.minNote }}</div>
            </div>
            <div class="flex flex-col items-center gap-2">
              <div class="h-2 w-full bg-moss-800/12 rounded-full overflow-hidden">
                <div class="h-full bg-gradient-to-r from-moss-500 to-moss-700 rounded-full" style="width: 100%" />
              </div>
              <div class="font-mono text-[0.58rem] uppercase tracking-[0.18em] text-ink-faint">
                {{ songRange.semitones }} semitones
              </div>
            </div>
            <div class="text-right">
              <div class="font-mono text-[0.58rem] uppercase tracking-[0.2em] text-ink-faint">Highest</div>
              <div class="font-display font-black text-4xl md:text-5xl text-moss-800 leading-none">{{ songRange.maxNote }}</div>
            </div>
          </div>

          <div class="mt-8 pt-6 border-t border-moss-800/10 text-ink-soft">
            This is the range the original singer covered. We'll figure out where your voice sits, then shift the whole song to match.
          </div>
        </div>

        <div class="mt-6 flex flex-col gap-3">
          <button class="w-full py-4 rounded-2xl bg-moss-800 text-cream-50 font-mono uppercase tracking-[0.16em] text-sm hover:bg-moss-700 transition-colors shadow-soft" @click="step = 1">
            Detect my range →
          </button>
          <button class="w-full py-3 rounded-2xl border border-moss-800/15 text-ink-soft font-mono uppercase tracking-[0.16em] text-xs hover:text-moss-700 transition-colors" @click="skipToSing">
            Skip — sing at the original key
          </button>
        </div>
      </section>

      <!-- Step 1 — Detect voice range -->
      <section v-else-if="step === 1" class="animate-rise">
        <div class="bg-cream-50 border border-moss-800/12 rounded-3xl p-8 shadow-soft">
          <div class="flex flex-col items-center gap-6">
            <button
              class="relative w-28 h-28 rounded-full flex items-center justify-center transition-all shadow-card active:scale-95"
              :class="listening ? 'bg-red-600 hover:bg-red-500 text-white' : 'bg-moss-800 hover:bg-moss-700 text-cream-50'"
              @click="toggleListening"
            >
              <span v-if="listening" class="absolute inset-0 rounded-full border-2 border-red-400 animate-ping opacity-40" />
              <svg v-if="!listening" viewBox="0 0 24 24" fill="currentColor" class="w-10 h-10">
                <path d="M12 1a4 4 0 0 1 4 4v7a4 4 0 0 1-8 0V5a4 4 0 0 1 4-4Zm7 11a1 1 0 0 1 1 1 8 8 0 0 1-7 7.94V23h2a1 1 0 1 1 0 2H9a1 1 0 1 1 0-2h2v-2.06A8 8 0 0 1 4 13a1 1 0 0 1 2 0 6 6 0 0 0 12 0 1 1 0 0 1 1-1Z"/>
              </svg>
              <div v-else class="w-6 h-6 bg-white rounded" />
            </button>

            <div class="text-center">
              <div class="font-mono text-[0.58rem] uppercase tracking-[0.2em] text-ink-faint mb-2">
                {{ listening ? 'Listening' : 'Press to start' }}
              </div>
              <div class="font-display font-black text-6xl md:text-7xl leading-none transition-colors"
                   :class="store.liveVoiced ? 'text-moss-700' : 'text-moss-800/25'">
                {{ store.liveNote || '—' }}
              </div>
            </div>

            <div v-if="detected" class="w-full pt-6 border-t border-moss-800/10 grid grid-cols-3 gap-4 items-end">
              <div>
                <div class="font-mono text-[0.55rem] uppercase tracking-[0.18em] text-ink-faint">Lowest</div>
                <div class="font-display font-black text-2xl text-moss-800">{{ detected.minNote }}</div>
              </div>
              <div class="flex flex-col items-center gap-2">
                <div class="h-1.5 w-full bg-moss-800/12 rounded-full overflow-hidden">
                  <div class="h-full bg-moss-600 rounded-full transition-all" :style="{ width: rangePct + '%' }" />
                </div>
                <div class="font-mono text-[0.55rem] uppercase tracking-[0.18em] text-ink-faint">
                  {{ detected.maxMidi - detected.minMidi }} semitones
                </div>
              </div>
              <div class="text-right">
                <div class="font-mono text-[0.55rem] uppercase tracking-[0.18em] text-ink-faint">Highest</div>
                <div class="font-display font-black text-2xl text-moss-800">{{ detected.maxNote }}</div>
              </div>
            </div>

            <p v-else class="text-ink-soft text-center max-w-xs">
              Sing from your lowest comfortable note up to the highest one. We'll track your range as you go.
            </p>

            <p v-if="wsError" class="text-red-700 font-mono text-xs">{{ wsError }}</p>
          </div>
        </div>

        <div class="mt-6 flex gap-3">
          <button class="flex-1 py-3 rounded-2xl border border-moss-800/15 text-ink-soft font-mono uppercase tracking-[0.16em] text-xs hover:text-moss-700 transition-colors" @click="step = 0">← Back</button>
          <button
            class="flex-1 py-3.5 rounded-2xl font-mono uppercase tracking-[0.16em] text-sm transition-colors"
            :class="detected ? 'bg-moss-800 text-cream-50 hover:bg-moss-700 shadow-soft' : 'bg-cream-100 text-ink-faint cursor-not-allowed'"
            :disabled="!detected"
            @click="goToTranspose"
          >Choose transpose →</button>
        </div>
      </section>

      <!-- Step 2 — Transpose -->
      <section v-else-if="step === 2" class="animate-rise">
        <div class="bg-cream-50 border border-moss-800/12 rounded-3xl p-8 shadow-soft">
          <div class="grid grid-cols-2 gap-6 pb-6 border-b border-moss-800/10">
            <div>
              <div class="font-mono text-[0.58rem] uppercase tracking-[0.2em] text-ink-faint mb-2">Song range</div>
              <div class="font-display text-lg text-moss-900 mb-2">{{ songRange.minNote }} – {{ songRange.maxNote }}</div>
              <div class="h-2 rounded-full bg-moss-300" />
            </div>
            <div>
              <div class="font-mono text-[0.58rem] uppercase tracking-[0.2em] text-ink-faint mb-2">Your voice</div>
              <div class="font-display text-lg text-moss-900 mb-2">{{ detected?.minNote }} – {{ detected?.maxNote }}</div>
              <div class="h-2 rounded-full bg-moss-700" />
            </div>
          </div>

          <div class="pt-6">
            <div class="flex items-center justify-between mb-4">
              <span class="font-mono text-[0.6rem] uppercase tracking-[0.2em] text-ink-faint">Transpose</span>
              <span class="font-mono text-[0.62rem] font-semibold px-3 py-1 rounded-full"
                    :class="selectedT === 0 ? 'bg-cream-100 text-moss-800' : 'bg-moss-800 text-cream-50'">
                {{ octaveLabel(selectedT) }}
              </span>
            </div>

            <div class="grid grid-cols-5 gap-2">
              <button
                v-for="opt in octaveOptions"
                :key="opt.value"
                class="py-3 rounded-2xl border font-mono text-[0.7rem] font-semibold transition-all"
                :class="selectedT === opt.value
                  ? 'bg-moss-800 border-moss-800 text-cream-50'
                  : 'bg-white border-moss-800/12 text-ink-soft hover:border-moss-500 hover:text-moss-700'"
                @click="selectedT = opt.value"
              >{{ opt.label }}</button>
            </div>

            <button
              v-if="selectedT !== recommendedT"
              class="mt-4 w-full text-center font-mono text-[0.6rem] uppercase tracking-[0.14em] text-moss-700 hover:text-moss-600"
              @click="selectedT = recommendedT"
            >
              Reset to recommended ({{ octaveLabel(recommendedT) }})
            </button>
          </div>

          <div class="mt-6 pt-6 border-t border-moss-800/10 grid grid-cols-2 gap-6">
            <div>
              <div class="font-mono text-[0.55rem] uppercase tracking-[0.18em] text-ink-faint">Song will start at</div>
              <div class="font-display font-black text-2xl text-moss-800">{{ transposedMin }}</div>
            </div>
            <div class="text-right">
              <div class="font-mono text-[0.55rem] uppercase tracking-[0.18em] text-ink-faint">and end at</div>
              <div class="font-display font-black text-2xl text-moss-800">{{ transposedMax }}</div>
            </div>
          </div>
        </div>

        <div class="mt-6 flex gap-3">
          <button class="flex-1 py-3 rounded-2xl border border-moss-800/15 text-ink-soft font-mono uppercase tracking-[0.16em] text-xs hover:text-moss-700 transition-colors" @click="step = 1">← Re-sing</button>
          <button class="flex-1 py-3.5 rounded-2xl bg-moss-800 text-cream-50 font-mono uppercase tracking-[0.16em] text-sm hover:bg-moss-700 transition-colors shadow-soft" @click="confirm">
            Sing this song →
          </button>
        </div>
      </section>

    </main>

    <LayoutPageFooter />
  </div>
</template>

<script setup lang="ts">
import { midiToName } from '~/composables/usePitchUtils'
import type { DetectedRange } from '~/types'

const store = useSessionStore()
const router = useRouter()
const route = useRoute()
const { fetchJob } = useAnalysis()

const stepTitles = ['The song sits here', 'Sing your range', 'Pick a transpose']
const step = ref(0)
const loading = ref(false)

const detected = ref<DetectedRange | null>(store.vocalRange)
const wsError = ref<string | null>(null)
const listening = ref(false)

const socket = useLiveSocket({
  onRange(m) {
    detected.value = {
      minMidi: m.min_midi,
      maxMidi: m.max_midi,
      minNote: m.min_note,
      maxNote: m.max_note,
    }
  },
  onError(msg) { wsError.value = msg },
})

const mic = useMicStream({
  onChunk(pcm) { socket.sendBinary(pcm) },
})

// ── Song range from analysis
const songRange = computed(() => {
  const notes = store.noteEvents
  if (!notes.length) return { minMidi: 48, maxMidi: 72, minNote: 'C3', maxNote: 'C5', semitones: 24 }
  let min = notes[0]!.midi, max = notes[0]!.midi
  for (const n of notes) { if (n.midi < min) min = n.midi; if (n.midi > max) max = n.midi }
  return { minMidi: min, maxMidi: max, minNote: midiToName(min), maxNote: midiToName(max), semitones: max - min }
})

// ── Load job on mount if needed
onMounted(async () => {
  if (store.analysis) return
  const jobId = route.query.job as string | undefined
  if (!jobId) return router.replace('/analyze')

  loading.value = true
  try {
    const job = await fetchJob(jobId)
    if (job.status !== 'complete') return router.replace('/analyze')
  } catch {
    router.replace('/analyze')
  } finally {
    loading.value = false
  }
})

// ── Listening controls
async function toggleListening() {
  if (listening.value) {
    listening.value = false
    await mic.stop()
    socket.close()
    return
  }
  wsError.value = null
  try {
    socket.connect()
    socket.send({ type: 'init', mode: 'range' })
    await mic.start()
    listening.value = true
  } catch (e: any) {
    wsError.value = e?.message ?? 'Could not start microphone'
    listening.value = false
    socket.close()
  }
}

watch(step, (s, prev) => {
  if (prev === 1 && s !== 1 && listening.value) {
    listening.value = false
    void mic.stop()
    socket.close()
  }
})

// ── Range bar
const rangePct = computed(() => {
  if (!detected.value) return 0
  const semis = detected.value.maxMidi - detected.value.minMidi
  return Math.min(100, Math.round((semis / 36) * 100))
})

// ── Recommended transpose
const recommendedT = computed(() => {
  if (!detected.value) return 0
  const songCenter = (songRange.value.minMidi + songRange.value.maxMidi) / 2
  const userCenter = (detected.value.minMidi + detected.value.maxMidi) / 2
  const snapped = Math.round((userCenter - songCenter) / 12) * 12
  return Math.max(-24, Math.min(24, snapped))
})

const selectedT = ref(0)
const octaveOptions = [
  { value: -24, label: '−2 oct' },
  { value: -12, label: '−1 oct' },
  { value:   0, label: 'none' },
  { value:  12, label: '+1 oct' },
  { value:  24, label: '+2 oct' },
]

function octaveLabel(semis: number): string {
  if (semis === 0) return 'no shift'
  const oct = semis / 12
  return `${oct > 0 ? '+' : ''}${oct} octave${Math.abs(oct) === 1 ? '' : 's'}`
}

function goToTranspose() {
  if (!detected.value) return
  selectedT.value = recommendedT.value
  step.value = 2
}

const transposedMin = computed(() => midiToName(Math.max(0, songRange.value.minMidi + selectedT.value)))
const transposedMax = computed(() => midiToName(Math.min(127, songRange.value.maxMidi + selectedT.value)))

function confirm() {
  if (detected.value) store.setVocalRange(detected.value)
  store.setTranspose(selectedT.value)
  router.push(`/sing?job=${store.jobId}`)
}

function skipToSing() {
  store.setTranspose(0)
  router.push(`/sing?job=${store.jobId}`)
}

onUnmounted(() => {
  if (listening.value) { void mic.stop() }
  socket.close()
})
</script>
