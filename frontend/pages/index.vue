<template>
  <div class="min-h-screen flex items-center justify-center bg-canvas px-4 py-8 relative">
    <!-- Radial mesh background -->
    <div class="fixed inset-0 pointer-events-none bg-[radial-gradient(ellipse_60%_50%_at_20%_20%,rgba(21,128,61,0.07)_0%,transparent_60%),radial-gradient(ellipse_40%_60%_at_80%_80%,rgba(74,222,128,0.05)_0%,transparent_60%)] z-0" />

    <main class="w-full max-w-lg flex flex-col items-center gap-8 relative z-10">
      <!-- Header -->
      <header class="text-center flex flex-col items-center gap-2 animate-fade-up">
        <div class="flex items-center gap-2.5 text-green-700">
          <svg viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-7 h-7">
            <rect x="2"  y="10" width="3" height="8"  rx="1.5" fill="currentColor" opacity="0.4"/>
            <rect x="7"  y="6"  width="3" height="16" rx="1.5" fill="currentColor" opacity="0.65"/>
            <rect x="12" y="2"  width="3" height="24" rx="1.5" fill="currentColor"/>
            <rect x="17" y="6"  width="3" height="16" rx="1.5" fill="currentColor" opacity="0.65"/>
            <rect x="22" y="10" width="3" height="8"  rx="1.5" fill="currentColor" opacity="0.4"/>
          </svg>
          <span class="font-display text-[1.8rem] font-extrabold text-ink tracking-tight">Karaoke</span>
        </div>
        <p class="font-mono text-[0.72rem] text-ink-faint uppercase tracking-[0.08em]">
          vocal analysis · pitch tracking · sing along
        </p>
      </header>

      <!-- Card -->
      <section class="w-full flex flex-col gap-3" style="animation-delay: 0.1s">
        <UploadDropZone v-if="!isAnalyzing" :isUploading="isUploading" @file="onFile" />
        <UploadAnalysisProgress v-if="isAnalyzing" />

        <!-- File chip -->
        <div v-if="store.audioFile && !isAnalyzing" class="flex items-center gap-2 px-3 py-1.5 bg-green-100 border border-green-300 rounded-lg font-mono text-[0.7rem] text-ink-muted animate-fade-up">
          <svg viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5 text-green-600 shrink-0">
            <path d="M4 1h6l4 4v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1z" opacity="0.3"/>
            <path d="M9 1v4h4" fill="none" stroke="currentColor" stroke-width="1"/>
          </svg>
          <span class="flex-1 truncate">{{ store.audioFile.name }}</span>
          <span class="text-ink-faint shrink-0">{{ formatBytes(store.audioFile.size) }}</span>
        </div>
      </section>

      <!-- Feature pills -->
      <ul class="flex flex-wrap gap-2 justify-center animate-fade-up list-none p-0 m-0" style="animation-delay: 0.2s">
        <li
          v-for="f in features"
          :key="f"
          class="flex items-center gap-1.5 px-2.5 py-1 bg-green-50 border border-green-200 rounded-full font-mono text-[0.65rem] text-ink-faint"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-green-500 shrink-0" />
          {{ f }}
        </li>
      </ul>

      <!-- Device badge -->
      <div
        v-if="store.device"
        class="font-mono text-[0.65rem] font-semibold tracking-[0.1em] px-3 py-1 rounded-full border border-green-300 text-green-700 bg-green-100 flex items-center gap-1.5 animate-fade-up"
      >
        <span>⚡</span>{{ store.device.toUpperCase() }}
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
const store = useKaraokeStore()
const { uploadAndAnalyze, isUploading } = useAnalysis()
const router = useRouter()

const isAnalyzing = computed(() =>
  ['queued','separating','tracking','quantizing','segmenting'].includes(store.jobStatus ?? '')
)

const features = [
  'Demucs vocal separation',
  'pYIN pitch tracking',
  'Note quantization',
  'MIDI note events',
  'Real-time mic scoring',
]

async function onFile(file: File) {
  await uploadAndAnalyze(file)
}

watch(() => store.jobStatus, (status) => {
  if (status === 'complete') router.push(`/karaoke?job=${store.jobId}`)
})

function formatBytes(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
</script>
