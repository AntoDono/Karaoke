<template>
  <div class="flex items-center gap-3">
    <!-- SVG ring -->
    <div class="relative w-12 h-12 shrink-0">
      <svg viewBox="0 0 48 48" class="w-12 h-12" aria-hidden="true">
        <circle cx="24" cy="24" r="20" fill="none" stroke="#D1FAE5" stroke-width="3"/>
        <circle
          cx="24" cy="24" r="20"
          fill="none"
          :stroke="ringColor"
          stroke-width="3"
          stroke-linecap="round"
          stroke-dasharray="125.66"
          :stroke-dashoffset="dashOffset"
          transform="rotate(-90 24 24)"
          class="transition-all duration-300"
        />
      </svg>
      <span class="absolute inset-0 flex items-center justify-center font-mono text-[0.7rem] font-semibold text-ink">
        {{ displayScore }}
      </span>
    </div>

    <div class="flex flex-col gap-1">
      <!-- Accuracy row -->
      <div class="flex items-baseline gap-1.5">
        <span class="font-mono text-lg font-bold leading-none tracking-tight" :class="scoreColorClass">
          {{ store.score }}%
        </span>
        <span class="font-mono text-[0.6rem] text-ink-faint uppercase tracking-wider">accuracy</span>
      </div>

      <!-- Points + combo row -->
      <div class="flex items-center gap-2">
        <span class="font-mono text-[0.72rem] font-semibold text-ink leading-none">
          {{ store.points.toLocaleString() }} pts
        </span>
        <span
          v-if="store.combo > 0"
          class="inline-flex items-center gap-0.5 rounded px-1 py-0.5 text-[0.58rem] font-bold uppercase tracking-wide leading-none transition-colors"
          :class="multiplierClass"
        >
          {{ store.combo }}x
          <span v-if="store.comboMultiplier > 1" class="opacity-80">·×{{ store.comboMultiplier }}</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const store = useKaraokeStore()

const displayScore = computed(() =>
  !store.isMicActive && store.scoredFrames === 0 ? '--' : store.score.toString()
)

const dashOffset = computed(() => (2 * Math.PI * 20) * (1 - store.score / 100))

const ringColor = computed(() => {
  if (store.score >= 80) return '#22c55e'
  if (store.score >= 50) return '#eab308'
  return '#ef4444'
})

const scoreColorClass = computed(() => {
  if (store.score >= 80) return 'text-green-700'
  if (store.score >= 50) return 'text-yellow-600'
  if (store.scoredFrames > 0) return 'text-red-600'
  return 'text-ink'
})

const multiplierClass = computed(() => {
  if (store.comboMultiplier >= 4) return 'bg-purple-100 text-purple-700'
  if (store.comboMultiplier >= 3) return 'bg-orange-100 text-orange-700'
  if (store.comboMultiplier >= 2) return 'bg-yellow-100 text-yellow-700'
  return 'bg-green-100 text-green-700'
})
</script>
