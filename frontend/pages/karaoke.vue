<template>
  <div class="min-h-screen flex flex-col bg-canvas relative">
    <!-- Background mesh -->
    <div class="fixed inset-0 pointer-events-none bg-[radial-gradient(ellipse_50%_40%_at_10%_10%,rgba(21,128,61,0.06)_0%,transparent_60%),radial-gradient(ellipse_30%_50%_at_90%_90%,rgba(74,222,128,0.04)_0%,transparent_60%)] z-0" />

    <!-- Header -->
    <header class="sticky top-0 z-20 flex items-center gap-4 px-6 py-3.5 border-b border-green-200 bg-canvas/90 backdrop-blur-md flex-wrap">
      <NuxtLink to="/" class="flex items-center gap-1.5 font-mono text-[0.72rem] text-ink-faint hover:text-green-700 transition-colors no-underline shrink-0">
        <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" class="w-4 h-4">
          <path d="M10 12 L5 8 L10 4"/>
        </svg>
        Back
      </NuxtLink>

      <div class="flex-1 min-w-0 flex flex-col gap-0.5">
        <h1 class="font-display text-base font-bold tracking-tight text-ink truncate m-0">
          {{ store.audioFile?.name ?? 'Karaoke' }}
        </h1>
        <span class="font-mono text-[0.65rem] text-ink-faint flex items-center gap-1.5 flex-wrap">
          {{ noteCount }} notes · {{ formatTime(store.duration) }}
          <span v-if="store.device" class="text-green-600 font-semibold">· {{ store.device }}</span>
          <a
            v-if="store.vocalsUrl"
            :href="`${config.public.apiBase}${store.vocalsUrl}`"
            target="_blank"
            class="inline-flex items-center gap-1 px-1.5 py-0.5 bg-green-100 border border-green-300 rounded text-green-700 font-semibold no-underline hover:bg-green-200 transition-colors"
          >
            <span class="w-1 h-1 rounded-full bg-green-500" />
            vocals.wav ↓
          </a>
        </span>
      </div>

      <!-- Transpose control — octave steps only -->
      <div class="flex items-center gap-1 shrink-0 bg-green-50 border border-green-200 rounded-lg px-1 py-1">
        <button
          class="w-6 h-6 flex items-center justify-center rounded font-mono text-sm text-green-700 hover:bg-green-200 transition-colors leading-none disabled:opacity-30"
          :disabled="store.transpose <= -24"
          title="Down one octave"
          @click="store.setTranspose(store.transpose - 12)"
        >−</button>
        <button
          class="px-2 py-0.5 font-mono text-[0.65rem] font-semibold text-green-700 rounded hover:bg-green-200 transition-colors min-w-[44px] text-center leading-none"
          title="Click to reset transpose"
          @click="store.setTranspose(0)"
        >
          {{ transposeHeaderLabel }}
        </button>
        <button
          class="w-6 h-6 flex items-center justify-center rounded font-mono text-sm text-green-700 hover:bg-green-200 transition-colors leading-none disabled:opacity-30"
          :disabled="store.transpose >= 24"
          title="Up one octave"
          @click="store.setTranspose(store.transpose + 12)"
        >+</button>
      </div>

      <div class="flex items-center gap-3 shrink-0">
        <KaraokeScoreDisplay />
        <KaraokeLivePitchBadge />
        <KaraokeMicRecorder />
      </div>
    </header>

    <!-- Loading overlay (re-fetching after SSR/refresh) -->
    <div v-if="isLoading" class="flex-1 flex items-center justify-center gap-3 font-mono text-sm text-ink-faint">
      <div class="w-4 h-4 rounded-full border-2 border-green-200 border-t-green-500 animate-spin-slow" />
      Loading analysis…
    </div>

    <!-- Error state -->
    <div v-else-if="loadError" class="flex-1 flex flex-col items-center justify-center gap-4 px-6">
      <p class="font-mono text-sm text-red-500">{{ loadError }}</p>
      <NuxtLink to="/" class="font-mono text-xs text-green-700 underline">Try again</NuxtLink>
    </div>

    <!-- Main -->
    <main v-else class="flex-1 flex flex-col gap-0 px-6 py-5 relative z-10 max-w-[1200px] w-full mx-auto box-border">

      <!-- Piano roll -->
      <section class="flex-1 relative mb-5">
        <KaraokeNoteTimeline class="w-full h-full min-h-[380px]" />
        <KaraokeNoteCursor />
      </section>

      <!-- Transport + stats -->
      <section class="flex flex-col gap-3">
        <KaraokeAudioPlayer />

        <div v-if="store.noteEvents.length" class="flex gap-2 flex-wrap">
          <div
            v-for="stat in stats"
            :key="stat.label"
            class="flex-1 min-w-[80px] bg-green-50 border border-green-200 rounded-lg px-3 py-2 flex flex-col gap-0.5 font-mono"
          >
            <span class="text-[0.58rem] text-ink-faint uppercase tracking-[0.07em]">{{ stat.label }}</span>
            <span class="text-[0.9rem] font-semibold tracking-tight" :class="stat.class ?? 'text-ink'">
              {{ stat.value }}
            </span>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
const store  = useKaraokeStore()
const router = useRouter()
const route  = useRoute()
const config = useRuntimeConfig()

const isLoading = ref(false)
const loadError = ref<string | null>(null)

onMounted(async () => {
  if (store.analysisResult) return   // store already has data — normal flow

  const jobId = route.query.job as string | undefined
  if (!jobId) { router.replace('/'); return }

  // Store is empty (SSR hydration, page refresh, etc.) — re-fetch from API
  isLoading.value = true
  try {
    const job = await $fetch<{ status: string; result: any; error?: string }>(
      `${config.public.apiBase}/api/jobs/${jobId}`
    )
    if (job.status === 'complete' && job.result) {
      store.updateJobStatus('complete', 'Done', job.result)
    } else if (job.status === 'failed') {
      loadError.value = job.error ?? 'Analysis failed'
    } else {
      // Job exists but isn't done yet — send back to watch progress
      router.replace(`/?job=${jobId}`)
    }
  } catch {
    router.replace('/')
  } finally {
    isLoading.value = false
  }
})

const noteCount = computed(() => store.noteEvents.length)

const transposeHeaderLabel = computed(() => {
  const t = store.transpose
  if (t === 0) return '0 oct'
  const octs = t / 12
  return `${octs > 0 ? '+' : ''}${octs} oct`
})

const NOTE_NAMES_KARAOKE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
function transposedNote(midi: number, semitones: number): string {
  const shifted = Math.max(0, Math.min(127, midi + semitones))
  return `${NOTE_NAMES_KARAOKE[shifted % 12]}${Math.floor(shifted / 12) - 1}`
}

const stats = computed(() => [
  {
    label: 'Current',
    value: store.activeNote
      ? (store.transpose !== 0 ? transposedNote(store.activeNote.event.midi, store.transpose) : store.activeNote.event.note)
      : '—',
  },
  { label: 'Singing',  value: store.liveNoteName || '—', class: store.liveNoteName ? 'text-green-600' : 'text-ink' },
  {
    label: 'Score',
    value: `${store.score}%`,
    class: store.score >= 80 ? 'text-green-700' : store.score >= 50 ? 'text-yellow-600' : store.scoredFrames > 0 ? 'text-red-600' : 'text-ink',
  },
  { label: 'Notes',  value: noteCount.value.toString() },
  { label: 'Device', value: store.device || '—', class: 'text-green-600 uppercase text-[0.7rem]' },
])

function formatTime(sec: number): string {
  const s = Math.floor(sec)
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
}
</script>
