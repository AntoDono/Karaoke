<template>
  <div class="min-h-screen flex flex-col bg-canvas relative overflow-x-hidden">

    <!-- Atmospheric background -->
    <div class="fixed inset-0 pointer-events-none z-0">
      <div class="absolute top-[-18vh] right-[-12vw] w-[60vw] h-[60vw] rounded-full"
           style="background: radial-gradient(circle, rgba(34,197,94,0.07) 0%, transparent 65%)" />
      <div class="absolute bottom-[-12vh] left-[-10vw] w-[44vw] h-[44vw] rounded-full"
           style="background: radial-gradient(circle, rgba(74,222,128,0.05) 0%, transparent 65%)" />
      <div class="absolute inset-0 opacity-[0.022]"
           style="background-image: linear-gradient(rgba(21,128,61,1) 1px, transparent 1px), linear-gradient(90deg, rgba(21,128,61,1) 1px, transparent 1px); background-size: 52px 52px;" />
    </div>

    <!-- Top nav -->
    <nav class="relative z-10 px-6 pt-6 flex items-center justify-between">
      <div class="flex items-center gap-2.5">
        <!-- Mini equalizer logo -->
        <div class="flex items-end gap-[2.5px]" style="height: 16px">
          <span class="bar w-[2.5px] rounded-full bg-green-600" style="--base-h: 6px; animation-duration: 1.3s" />
          <span class="bar w-[2.5px] rounded-full bg-green-600" style="--base-h: 11px; animation-duration: 1.05s; animation-delay: 0.12s" />
          <span class="bar w-[2.5px] rounded-full bg-green-500" style="--base-h: 16px; animation-duration: 0.95s; animation-delay: 0.22s" />
          <span class="bar w-[2.5px] rounded-full bg-green-600" style="--base-h: 10px; animation-duration: 1.15s; animation-delay: 0.07s" />
          <span class="bar w-[2.5px] rounded-full bg-green-700" style="--base-h: 5px; animation-duration: 1.4s; animation-delay: 0.3s" />
        </div>
        <span class="font-display font-extrabold text-sm tracking-tight text-ink">Karaoke</span>
      </div>

      <div v-if="store.device"
           class="font-mono text-[0.58rem] tracking-[0.14em] uppercase px-2.5 py-1 rounded-full border border-green-200 bg-green-50 text-green-700 flex items-center gap-1.5">
        <span class="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
        {{ store.device }}
      </div>
    </nav>

    <!-- Main content -->
    <main class="flex-1 flex flex-col items-center justify-center px-6 py-10 relative z-10">

      <!-- Giant title -->
      <div class="text-center animate-fade-up" style="animation-delay: 0s">
        <h1
          class="font-display font-extrabold tracking-[-0.05em] leading-[0.86] text-ink select-none"
          style="font-size: clamp(3.8rem, 15vw, 10.5rem)"
        >
          KARAOKE
        </h1>
      </div>

      <!-- Animated spectrum bar strip — decorative art under the title -->
      <div class="flex items-end gap-[3px] mt-3 mb-1 animate-fade-up" style="animation-delay: 0.07s">
        <span class="bar rounded-full bg-green-300" style="width:3px; --base-h:4px;  animation-duration:1.7s; animation-delay:0.00s; opacity:0.5" />
        <span class="bar rounded-full bg-green-400" style="width:3px; --base-h:7px;  animation-duration:1.4s; animation-delay:0.05s; opacity:0.6" />
        <span class="bar rounded-full bg-green-400" style="width:3px; --base-h:12px; animation-duration:1.1s; animation-delay:0.10s; opacity:0.7" />
        <span class="bar rounded-full bg-green-500" style="width:3px; --base-h:18px; animation-duration:0.9s; animation-delay:0.08s; opacity:0.8" />
        <span class="bar rounded-full bg-green-500" style="width:3px; --base-h:22px; animation-duration:0.8s; animation-delay:0.15s; opacity:0.9" />
        <span class="bar rounded-full bg-green-600" style="width:3px; --base-h:28px; animation-duration:0.75s; animation-delay:0.12s" />
        <span class="bar rounded-full bg-green-500" style="width:3px; --base-h:32px; animation-duration:0.7s; animation-delay:0.20s" />
        <span class="bar rounded-full bg-green-600" style="width:3px; --base-h:36px; animation-duration:0.65s; animation-delay:0.05s" />
        <span class="bar rounded-full bg-green-500" style="width:3px; --base-h:40px; animation-duration:0.6s; animation-delay:0.18s" />
        <span class="bar rounded-full bg-green-700" style="width:3px; --base-h:44px; animation-duration:0.58s; animation-delay:0.25s" />
        <span class="bar rounded-full bg-green-600" style="width:3px; --base-h:48px; animation-duration:0.62s; animation-delay:0.10s" />
        <span class="bar rounded-full bg-green-700" style="width:3px; --base-h:52px; animation-duration:0.55s; animation-delay:0.30s" />
        <span class="bar rounded-full bg-green-600" style="width:3px; --base-h:48px; animation-duration:0.62s; animation-delay:0.08s" />
        <span class="bar rounded-full bg-green-600" style="width:3px; --base-h:44px; animation-duration:0.58s; animation-delay:0.22s" />
        <span class="bar rounded-full bg-green-500" style="width:3px; --base-h:40px; animation-duration:0.6s; animation-delay:0.15s" />
        <span class="bar rounded-full bg-green-600" style="width:3px; --base-h:36px; animation-duration:0.65s; animation-delay:0.28s" />
        <span class="bar rounded-full bg-green-500" style="width:3px; --base-h:32px; animation-duration:0.7s; animation-delay:0.12s" />
        <span class="bar rounded-full bg-green-600" style="width:3px; --base-h:28px; animation-duration:0.75s; animation-delay:0.06s" />
        <span class="bar rounded-full bg-green-500" style="width:3px; --base-h:22px; animation-duration:0.8s; animation-delay:0.20s" />
        <span class="bar rounded-full bg-green-500" style="width:3px; --base-h:18px; animation-duration:0.9s; animation-delay:0.14s; opacity:0.9" />
        <span class="bar rounded-full bg-green-400" style="width:3px; --base-h:12px; animation-duration:1.1s; animation-delay:0.08s; opacity:0.7" />
        <span class="bar rounded-full bg-green-400" style="width:3px; --base-h:7px;  animation-duration:1.4s; animation-delay:0.04s; opacity:0.6" />
        <span class="bar rounded-full bg-green-300" style="width:3px; --base-h:4px;  animation-duration:1.7s; animation-delay:0.00s; opacity:0.5" />
      </div>

      <!-- Tagline -->
      <p class="font-mono text-[0.63rem] uppercase tracking-[0.2em] text-ink-faint mt-4 mb-10 animate-fade-up" style="animation-delay: 0.12s">
        vocal separation&ensp;·&ensp;pitch tracking&ensp;·&ensp;sing along
      </p>

      <!-- Upload zone -->
      <section class="w-full max-w-md animate-fade-up" style="animation-delay: 0.18s">
        <UploadDropZone v-if="!isAnalyzing" :isUploading="isUploading" @file="onFile" />
        <UploadAnalysisProgress v-if="isAnalyzing" />

        <!-- File chip -->
        <div
          v-if="store.audioFile && !isAnalyzing"
          class="mt-2.5 flex items-center gap-2 px-3 py-1.5 bg-green-100 border border-green-300 rounded-lg font-mono text-[0.68rem] text-ink-muted animate-fade-up"
        >
          <svg viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5 text-green-600 shrink-0">
            <path d="M4 1h6l4 4v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1z" opacity="0.3"/>
            <path d="M9 1v4h4" fill="none" stroke="currentColor" stroke-width="1"/>
          </svg>
          <span class="flex-1 truncate">{{ store.audioFile.name }}</span>
          <span class="text-ink-faint shrink-0">{{ formatBytes(store.audioFile.size) }}</span>
        </div>
      </section>

      <!-- Feature list — inline with separator ticks -->
      <div class="mt-8 flex items-center flex-wrap justify-center gap-y-2 animate-fade-up" style="animation-delay: 0.24s">
        <template v-for="(f, i) in features" :key="f">
          <span class="font-mono text-[0.58rem] uppercase tracking-[0.1em] text-ink-faint px-2.5">{{ f }}</span>
          <span v-if="i < features.length - 1" class="w-px h-2.5 bg-green-200 shrink-0" />
        </template>
      </div>
    </main>

    <!-- Footer rule -->
    <footer class="relative z-10 px-6 pb-5 flex items-center justify-center gap-3">
      <div class="h-px flex-1 max-w-[80px] bg-gradient-to-r from-transparent to-green-200" />
      <span class="font-mono text-[0.52rem] tracking-[0.16em] text-green-300 uppercase">Cardinal Audio</span>
      <div class="h-px flex-1 max-w-[80px] bg-gradient-to-l from-transparent to-green-200" />
    </footer>
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
  'Pitch tracking',
  'Note quantization',
  'MIDI note events',
  'Real-time mic scoring',
]

async function onFile(file: File) {
  await uploadAndAnalyze(file)
}

watch(() => store.jobStatus, (status) => {
  if (status === 'complete') router.push(`/vocal-range?job=${store.jobId}`)
})

function formatBytes(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
</script>

<style scoped>
/* Animated spectrum / equalizer bars */
.bar {
  display: inline-block;
  height: var(--base-h, 20px);
  transform-origin: bottom;
  animation: barBounce var(--dur, 1s) ease-in-out infinite alternate;
}

@keyframes barBounce {
  0%   { transform: scaleY(0.18); }
  100% { transform: scaleY(1); }
}
</style>
