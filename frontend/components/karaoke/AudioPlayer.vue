<template>
  <div class="bg-green-50 border border-green-200 rounded-2xl px-5 py-4">
    <audio ref="audioElRef" :src="store.audioUrl ?? undefined" preload="auto" class="hidden" />

    <div class="flex items-center gap-4">
      <!-- Play/Pause -->
      <button
        class="w-10 h-10 rounded-full flex items-center justify-center shrink-0 transition-all duration-150"
        :class="isReady ? 'bg-green-500 text-white hover:bg-green-700 hover:scale-105' : 'bg-green-300 text-white cursor-not-allowed'"
        :disabled="!isReady"
        @click="toggle"
        :aria-label="store.isPlaying ? 'Pause' : 'Play'"
      >
        <svg v-if="!store.isPlaying" viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5">
          <path d="M8 5.14v14l11-7-11-7z"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5">
          <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
        </svg>
      </button>

      <!-- Seek bar -->
      <div
        class="flex-1 h-1.5 bg-green-200 rounded-full relative cursor-pointer overflow-visible"
        @click="onSeekClick"
        @mousemove="onSeekHover"
        @mouseleave="hoverFraction = null"
      >
        <div
          class="h-full bg-gradient-to-r from-green-700 to-green-500 rounded-full transition-[width] duration-100 pointer-events-none"
          :style="{ width: progressPct + '%' }"
        />
        <div
          v-if="hoverFraction !== null"
          class="absolute -top-1 w-0.5 h-3.5 bg-green-400 rounded-sm -translate-x-1/2 pointer-events-none opacity-80"
          :style="{ left: (hoverFraction * 100) + '%' }"
        />
      </div>

      <!-- Time -->
      <span class="font-mono text-[0.72rem] text-ink-faint whitespace-nowrap shrink-0">
        {{ formatTime(store.currentTime) }} / {{ formatTime(store.duration) }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
const store = useKaraokeStore()
const { attach, toggle, seekByFraction, seek, play, isReady } = useAudioPlayer()

const audioElRef    = ref<HTMLAudioElement | null>(null)
const hoverFraction = ref<number | null>(null)

onMounted(() => { if (audioElRef.value) attach(audioElRef.value) })

// Restart song when SongResults requests it
watch(() => store.pendingRestart, (v) => {
  if (v) {
    seek(0)
    play()
    store.setPendingRestart(false)
  }
})

const progressPct = computed(() =>
  store.duration > 0 ? (store.currentTime / store.duration) * 100 : 0
)

function onSeekClick(e: MouseEvent) {
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
  seekByFraction((e.clientX - rect.left) / rect.width)
}

function onSeekHover(e: MouseEvent) {
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
  hoverFraction.value = (e.clientX - rect.left) / rect.width
}

function formatTime(sec: number): string {
  const s = Math.floor(sec)
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
}
</script>
