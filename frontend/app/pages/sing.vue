<template>
  <div class="h-screen bg-rice relative overflow-hidden flex flex-col">
    <KaraokeSessionHeader :is-open="socket.isOpen.value">
      <template #right>
        <button
          class="ml-2 inline-flex items-center gap-2 px-3.5 py-2 rounded-full border font-mono uppercase tracking-[0.16em] text-[0.62rem] transition-colors"
          :class="micOn
            ? 'border-moss-500 bg-moss-800 text-cream-50 hover:bg-moss-700'
            : 'border-moss-800/12 bg-cream-50 text-moss-800 hover:border-moss-500'"
          @click="toggleMic"
        >
          <span class="w-1.5 h-1.5 rounded-full" :class="micOn ? 'bg-cream-100 animate-pulse' : 'bg-moss-500'" />
          {{ micOn ? 'Mic on' : 'Turn mic on' }}
        </button>
      </template>
    </KaraokeSessionHeader>

    <!-- Loading -->
    <div v-if="loading" class="flex-1 flex flex-col items-center justify-center gap-4">
      <div class="w-10 h-10 rounded-full border-2 border-moss-800/20 border-t-moss-700 animate-spin" />
      <span class="font-mono text-xs uppercase tracking-widest text-ink-faint">Loading song…</span>
    </div>

    <!-- Error -->
    <div v-else-if="loadError" class="flex-1 flex flex-col items-center justify-center gap-3 px-8 text-center">
      <div class="font-display font-black text-3xl text-red-700">Couldn't load this song.</div>
      <p class="text-ink-soft">{{ loadError }}</p>
      <NuxtLink to="/analyze" class="font-mono text-xs uppercase tracking-widest text-moss-700 underline">Start over</NuxtLink>
    </div>

    <!-- Main -->
    <main v-else class="flex-1 min-h-0 max-w-[1400px] w-full mx-auto px-4 md:px-6 lg:px-8 pt-4 pb-6 grid gap-4 overflow-hidden"
          :class="showLyrics ? 'lg:grid-cols-[1fr_320px] lg:grid-rows-1' : 'lg:grid-cols-1'">
      <div class="min-w-0 min-h-0 flex flex-col gap-4 overflow-hidden">
        <KaraokeScoreHud />

        <div class="flex-1 min-h-0 relative">
          <KaraokeNoteTimeline />
        </div>

        <KaraokeAudioTransport :audio="audioEl" @transpose="onTranspose" />

        <!-- Hidden audio element — original upload (or vocals stem fallback) -->
        <audio ref="audioRef" :src="audioSrc ?? undefined" preload="auto" class="sr-only" />
      </div>

      <KaraokeLyricsPanel v-if="showLyrics" class="min-h-0 h-full max-h-[38vh] lg:max-h-none overflow-hidden" />
    </main>

    <!-- End-of-song overlay -->
    <transition name="fade">
      <div v-if="store.songFinished" class="fixed inset-0 z-40 bg-moss-900/70 backdrop-blur-sm flex items-center justify-center px-6">
        <div class="bg-rice rounded-3xl p-10 md:p-12 max-w-lg w-full shadow-card animate-rise text-center">
          <div class="font-mono text-[0.62rem] uppercase tracking-[0.24em] text-moss-700 mb-4">§ Results</div>

          <div
            class="font-display font-black text-7xl md:text-8xl leading-none mb-2"
            :class="gradeColor"
          >
            {{ letterGrade }}
          </div>
          <div class="font-mono text-xs uppercase tracking-[0.2em] text-ink-faint mb-6">{{ gradeLabel }}</div>

          <h2 class="font-display font-black text-3xl md:text-4xl text-moss-900 leading-none tracking-tight mb-8 tabular-nums">
            {{ formatPoints(store.points) }}<span class="text-moss-500 text-xl font-mono uppercase tracking-widest ml-2">pts</span>
          </h2>

          <div class="grid grid-cols-2 gap-3 mb-8 text-left">
            <div class="rounded-2xl border border-moss-800/12 px-4 py-3 bg-cream-50">
              <div class="font-mono text-[0.55rem] uppercase tracking-[0.18em] text-ink-faint">Notes hit</div>
              <div class="font-display font-black text-2xl text-moss-800 tabular-nums">
                {{ store.notesHit }}<span class="text-moss-500/50 text-lg">/{{ store.totalNotes }}</span>
              </div>
            </div>
            <div class="rounded-2xl border border-moss-800/12 px-4 py-3 bg-cream-50">
              <div class="font-mono text-[0.55rem] uppercase tracking-[0.18em] text-ink-faint">Accuracy</div>
              <div class="font-display font-black text-2xl text-moss-800 tabular-nums">{{ store.accuracy }}%</div>
            </div>
            <div class="rounded-2xl border border-moss-800/12 px-4 py-3 bg-cream-50">
              <div class="font-mono text-[0.55rem] uppercase tracking-[0.18em] text-ink-faint">Best combo</div>
              <div class="font-display font-black text-2xl text-moss-800">×{{ store.maxCombo }}</div>
            </div>
            <div class="rounded-2xl border border-moss-800/12 px-4 py-3 bg-cream-50">
              <div class="font-mono text-[0.55rem] uppercase tracking-[0.18em] text-ink-faint">Perfect</div>
              <div class="font-display font-black text-2xl text-moss-800 tabular-nums">{{ store.notesExact }}</div>
            </div>
          </div>

          <div class="flex gap-3">
            <button class="flex-1 py-3 rounded-2xl bg-moss-800 text-cream-50 font-mono uppercase tracking-[0.16em] text-xs hover:bg-moss-700 transition-colors" @click="restart">
              Sing it again
            </button>
            <NuxtLink to="/analyze" class="flex-1 py-3 rounded-2xl bg-cream-50 border border-moss-800/12 text-moss-800 font-mono uppercase tracking-[0.16em] text-xs no-underline text-center hover:bg-cream-100 hover:border-moss-500 transition-colors">
              New song
            </NuxtLink>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
const store = useSessionStore()
const router = useRouter()
const route = useRoute()
const config = useRuntimeConfig()
const { fetchJob } = useAnalysis()

const loading = ref(false)
const loadError = ref<string | null>(null)

const audioRef = ref<HTMLAudioElement | null>(null)
const audioEl = computed(() => audioRef.value)
useSmoothPlayhead(audioEl)

// ── Audio source ──────────────────────────────────────────────────────
const audioSrc = computed(() => {
  if (store.audioUrl) return store.audioUrl
  if (store.vocalsUrl) return `${config.public.apiBase}${store.vocalsUrl}`
  return null
})

const showLyrics = computed(() =>
  store.lyricsStatus === 'found' || store.lyricsStatus === 'pending' || !!store.lyrics
)

function formatPoints(n: number) {
  return n.toLocaleString()
}

const letterGrade = computed(() => {
  const a = store.accuracy
  if (a >= 95) return 'S'
  if (a >= 85) return 'A'
  if (a >= 70) return 'B'
  if (a >= 50) return 'C'
  if (a >= 30) return 'D'
  return 'F'
})

const gradeLabel = computed(() => {
  const g = letterGrade.value
  const labels: Record<string, string> = {
    S: 'Superb', A: 'Excellent', B: 'Great', C: 'Good', D: 'Fair', F: 'Keep practicing',
  }
  return labels[g] ?? ''
})

const gradeColor = computed(() => {
  const g = letterGrade.value
  if (g === 'S' || g === 'A') return 'text-cream-400'
  if (g === 'B' || g === 'C') return 'text-moss-700'
  return 'text-red-700'
})

// ── Live socket ───────────────────────────────────────────────────────
let pendingGrade: Extract<import('~/types').WsIn, { type: 'grade' }> | null = null
let gradeRaf: number | null = null

function flushGradeUpdates() {
  if (pendingGrade) {
    store.applyGradeMsg(pendingGrade)
    pendingGrade = null
  }
  gradeRaf = requestAnimationFrame(flushGradeUpdates)
}

const socket = useLiveSocket({
  onPitch(m) { store.applyPitchMsg(m) },
  onGrade(m) { pendingGrade = m },
  onError(msg) { loadError.value = msg },
})

watch(() => store.songFinished, (done) => {
  if (done && socket.isOpen.value) {
    socket.send({ type: 'sync', current_time: store.displayTime })
  }
})

const mic = useMicStream({
  onChunk(pcm) { socket.sendBinary(pcm) },
})

const micOn = ref(false)

async function toggleMic() {
  if (micOn.value) {
    micOn.value = false
    await mic.stop()
    socket.close()
    return
  }
  try {
    socket.connect()
    store.totalNotes = store.noteEvents.length
    socket.send({ type: 'init', job_id: store.jobId!, transpose: store.transpose, mode: 'grade' })
    await mic.start()
    micOn.value = true
  } catch (e: any) {
    loadError.value = e?.message ?? 'Could not start microphone'
    micOn.value = false
    socket.close()
  }
}

function onTranspose(semis: number) {
  if (socket.isOpen.value) {
    socket.send({ type: 'transpose', semitones: semis })
  }
}

// ── Sync playhead to backend at ~10 Hz ───────────────────────────────
let syncTimer: ReturnType<typeof setInterval> | null = null
onMounted(() => {
  gradeRaf = requestAnimationFrame(flushGradeUpdates)
  syncTimer = setInterval(() => {
    if (socket.isOpen.value && store.isPlaying) {
      socket.send({ type: 'sync', current_time: store.displayTime })
    }
  }, 50)
})
onUnmounted(() => {
  if (gradeRaf) cancelAnimationFrame(gradeRaf)
  if (syncTimer) clearInterval(syncTimer)
  if (micOn.value) void mic.stop()
  socket.close()
})

// ── Load job on mount; keep lyrics in sync if still fetching ─────────
onMounted(async () => {
  const jobId = (route.query.job as string | undefined) ?? store.jobId ?? undefined
  if (!jobId) return router.replace('/analyze')

  const needsJobFetch = !store.analysis || store.lyricsStatus === 'pending'
  if (!needsJobFetch) return

  loading.value = true
  try {
    const job = await fetchJob(jobId)
    if (job.status !== 'complete') return router.replace('/analyze')
  } catch (e: any) {
    loadError.value = e?.message ?? 'Failed to load song'
  } finally {
    loading.value = false
  }
})

function restart() {
  store.resetLive()
  store.totalNotes = store.noteEvents.length
  if (audioRef.value) {
    audioRef.value.currentTime = 0
    void audioRef.value.play()
  }
  if (socket.isOpen.value) socket.send({ type: 'reset_score' })
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
