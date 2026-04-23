<template>
  <div class="min-h-screen flex flex-col bg-canvas relative">

    <!-- Atmospheric background -->
    <div class="fixed inset-0 pointer-events-none z-0">
      <div class="absolute top-[-15vh] right-[-8vw] w-[50vw] h-[50vw] rounded-full"
           style="background: radial-gradient(circle, rgba(34,197,94,0.06) 0%, transparent 65%)" />
      <div class="absolute bottom-[-10vh] left-[-6vw] w-[36vw] h-[36vw] rounded-full"
           style="background: radial-gradient(circle, rgba(74,222,128,0.04) 0%, transparent 65%)" />
      <div class="absolute inset-0 opacity-[0.018]"
           style="background-image: linear-gradient(rgba(21,128,61,1) 1px, transparent 1px), linear-gradient(90deg, rgba(21,128,61,1) 1px, transparent 1px); background-size: 52px 52px;" />
    </div>

    <!-- Header -->
    <header class="sticky top-0 z-20 flex items-center gap-4 px-5 py-3 border-b border-green-200/80 bg-canvas/92 backdrop-blur-md flex-wrap">

      <!-- Logo + back -->
      <div class="flex items-center gap-3 shrink-0">
        <NuxtLink to="/" class="flex items-center gap-1.5 font-mono text-[0.68rem] text-ink-faint hover:text-green-700 transition-colors no-underline group">
          <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" class="w-3.5 h-3.5 transition-transform group-hover:-translate-x-0.5">
            <path d="M10 12 L5 8 L10 4"/>
          </svg>
          Back
        </NuxtLink>
        <div class="w-px h-4 bg-green-200" />
        <!-- Mini eq logo -->
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
        <h1 class="font-display text-[0.95rem] font-bold tracking-tight text-ink truncate m-0 leading-tight">
          {{ store.audioFile?.name ?? 'Karaoke' }}
        </h1>
        <span class="font-mono text-[0.6rem] text-ink-faint flex items-center gap-1.5 flex-wrap">
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

      <!-- Transpose control -->
      <div class="flex items-center gap-0.5 shrink-0 bg-green-50 border border-green-200 rounded-lg px-1 py-1">
        <button
          class="w-6 h-6 flex items-center justify-center rounded font-mono text-sm text-green-700 hover:bg-green-200 transition-colors leading-none disabled:opacity-30"
          :disabled="store.transpose <= -24"
          title="Down one octave"
          @click="store.setTranspose(store.transpose - 12)"
        >−</button>
        <button
          class="px-2 py-0.5 font-mono text-[0.62rem] font-semibold text-green-700 rounded hover:bg-green-200 transition-colors min-w-[44px] text-center leading-none"
          title="Click to reset transpose"
          @click="store.setTranspose(0)"
        >{{ transposeHeaderLabel }}</button>
        <button
          class="w-6 h-6 flex items-center justify-center rounded font-mono text-sm text-green-700 hover:bg-green-200 transition-colors leading-none disabled:opacity-30"
          :disabled="store.transpose >= 24"
          title="Up one octave"
          @click="store.setTranspose(store.transpose + 12)"
        >+</button>
      </div>

      <div class="flex items-center gap-2.5 shrink-0">
        <KaraokeScoreDisplay />
        <KaraokeLivePitchBadge />
        <KaraokeMicRecorder />
      </div>
    </header>

    <!-- Loading -->
    <div v-if="isLoading" class="flex-1 flex flex-col items-center justify-center gap-4 relative z-10">
      <div class="flex items-end gap-[3px]" style="height: 28px">
        <span class="bar w-[3px] rounded-full bg-green-400" style="--base-h: 10px; animation-duration: 1.1s" />
        <span class="bar w-[3px] rounded-full bg-green-500" style="--base-h: 18px; animation-duration: 0.9s; animation-delay: 0.1s" />
        <span class="bar w-[3px] rounded-full bg-green-600" style="--base-h: 28px; animation-duration: 0.75s; animation-delay: 0.2s" />
        <span class="bar w-[3px] rounded-full bg-green-500" style="--base-h: 18px; animation-duration: 0.9s; animation-delay: 0.1s" />
        <span class="bar w-[3px] rounded-full bg-green-400" style="--base-h: 10px; animation-duration: 1.1s" />
      </div>
      <span class="font-mono text-[0.7rem] text-ink-faint tracking-[0.08em]">Loading analysis…</span>
    </div>

    <!-- Error -->
    <div v-else-if="loadError" class="flex-1 flex flex-col items-center justify-center gap-4 px-6 relative z-10">
      <div class="w-10 h-10 rounded-full bg-red-50 border border-red-200 flex items-center justify-center text-red-500 font-mono font-black text-lg">!</div>
      <p class="font-mono text-sm text-red-500 text-center">{{ loadError }}</p>
      <NuxtLink to="/" class="font-mono text-xs text-green-700 px-4 py-2 rounded-lg border border-green-300 hover:bg-green-50 transition-colors no-underline">
        Try again
      </NuxtLink>
    </div>

    <!-- Main -->
    <main v-else class="flex-1 flex flex-col gap-0 px-5 py-4 relative z-10 max-w-[1200px] w-full mx-auto box-border">

      <!-- Piano roll -->
      <section class="flex-1 relative mb-4">
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
            class="flex-1 min-w-[80px] bg-green-50/80 border border-green-200 rounded-xl px-3 py-2.5 flex flex-col gap-1 font-mono backdrop-blur-sm"
          >
            <span class="text-[0.55rem] text-ink-faint uppercase tracking-[0.1em]">{{ stat.label }}</span>
            <span class="text-[0.88rem] font-semibold tracking-tight leading-none" :class="stat.class ?? 'text-ink'">
              {{ stat.value }}
            </span>
          </div>
        </div>
      </section>
    </main>
  </div>

  <!-- End-of-song results overlay -->
  <KaraokeSongResults />
</template>

<script setup lang="ts">
const store  = useKaraokeStore()
const router = useRouter()
const route  = useRoute()
const config = useRuntimeConfig()

const isLoading = ref(false)
const loadError = ref<string | null>(null)

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
    } else if (job.status === 'failed') {
      loadError.value = job.error ?? 'Analysis failed'
    } else {
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
