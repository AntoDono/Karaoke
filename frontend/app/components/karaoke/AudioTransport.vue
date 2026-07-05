<template>
  <div class="bg-cream-50 border border-moss-800/12 rounded-3xl px-5 py-4 shadow-soft flex items-center gap-4">
    <!-- Play / Pause -->
    <button
      class="w-12 h-12 rounded-full bg-moss-800 hover:bg-moss-700 text-cream-50 flex items-center justify-center transition-colors active:scale-95 shrink-0"
      @click="toggle"
    >
      <svg v-if="!store.isPlaying" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5 ml-0.5">
        <path d="M4 3v14l14-7L4 3z" />
      </svg>
      <svg v-else viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
        <path d="M5 3h4v14H5zM11 3h4v14h-4z" />
      </svg>
    </button>

    <!-- Time -->
    <div class="font-mono text-xs text-ink-soft tabular-nums w-12 shrink-0">{{ elapsed }}</div>

    <!-- Seek bar -->
    <div class="flex-1 relative h-2 bg-moss-800/10 rounded-full cursor-pointer group" @click="seekAt($event)">
      <div class="absolute top-0 bottom-0 left-0 bg-moss-700 rounded-full transition-[width] duration-150"
           :style="{ width: pct + '%' }" />
      <div class="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-3 h-3 bg-moss-800 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
           :style="{ left: pct + '%' }" />
    </div>

    <div class="font-mono text-xs text-ink-soft tabular-nums w-12 text-right shrink-0">{{ total }}</div>

    <!-- Transpose -->
    <div class="flex items-center gap-0.5 bg-moss-800/6 rounded-full px-1 py-1 shrink-0">
      <button class="w-7 h-7 rounded-full text-moss-800 hover:bg-white transition-colors font-mono text-sm leading-none disabled:opacity-30"
              :disabled="store.transpose <= -24" @click="setT(store.transpose - 12)">−</button>
      <div class="px-2 min-w-[46px] text-center font-mono text-[0.62rem] font-semibold text-moss-800">
        {{ transposeLabel }}
      </div>
      <button class="w-7 h-7 rounded-full text-moss-800 hover:bg-white transition-colors font-mono text-sm leading-none disabled:opacity-30"
              :disabled="store.transpose >= 24" @click="setT(store.transpose + 12)">+</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatTime } from '~/composables/usePitchUtils'

const props = defineProps<{ audio: HTMLAudioElement | null }>()
const emit = defineEmits<{ (e: 'transpose', semis: number): void }>()

const store = useSessionStore()

const pct = computed(() => {
  const d = store.duration
  if (!d) return 0
  return Math.min(100, Math.max(0, (store.displayTime / d) * 100))
})

const elapsed = computed(() => formatTime(store.displayTime))
const total = computed(() => formatTime(store.duration))

const transposeLabel = computed(() => {
  const t = store.transpose
  if (t === 0) return '0 oct'
  return `${t > 0 ? '+' : ''}${t / 12} oct`
})

function toggle() {
  const el = props.audio
  if (!el) return
  if (el.paused) void el.play()
  else el.pause()
}

function seekAt(ev: MouseEvent) {
  const el = props.audio
  if (!el || !store.duration) return
  const rect = (ev.currentTarget as HTMLElement).getBoundingClientRect()
  const frac = Math.min(1, Math.max(0, (ev.clientX - rect.left) / rect.width))
  el.currentTime = frac * store.duration
}

function setT(v: number) {
  store.setTranspose(v)
  emit('transpose', store.transpose)
}
</script>
