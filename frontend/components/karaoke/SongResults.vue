<template>
  <Transition name="results">
    <div
      v-if="store.songFinished"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
      style="background: rgba(10,15,10,0.82); backdrop-filter: blur(12px);"
    >
      <div class="relative w-full max-w-md bg-canvas border border-green-200 rounded-3xl shadow-2xl overflow-hidden">

        <!-- Top accent bar -->
        <div class="h-1 w-full" :style="{ background: ratingGradient }" />

        <!-- Content -->
        <div class="px-8 py-8 flex flex-col items-center gap-6">

          <!-- Song name -->
          <p class="font-mono text-[0.65rem] text-ink-faint uppercase tracking-[0.12em] text-center truncate w-full">
            {{ store.audioFile?.name ?? 'Song' }}
          </p>

          <!-- Rating ring -->
          <div class="relative flex items-center justify-center">
            <svg viewBox="0 0 120 120" class="w-32 h-32" aria-hidden="true">
              <circle cx="60" cy="60" r="52" fill="none" stroke="#D1FAE5" stroke-width="5"/>
              <circle
                cx="60" cy="60" r="52"
                fill="none"
                :stroke="ratingColor"
                stroke-width="5"
                stroke-linecap="round"
                stroke-dasharray="326.73"
                :stroke-dashoffset="ringOffset"
                transform="rotate(-90 60 60)"
                style="transition: stroke-dashoffset 1s cubic-bezier(.22,.68,0,1.2)"
              />
            </svg>
            <div class="absolute inset-0 flex flex-col items-center justify-center gap-0.5">
              <span
                class="font-display font-black leading-none"
                :class="ratingTextClass"
                style="font-size: 2.8rem"
              >{{ rating }}</span>
              <span class="font-mono text-[0.58rem] uppercase tracking-widest text-ink-faint">{{ ratingLabel }}</span>
            </div>
          </div>

          <!-- Stats grid -->
          <div class="w-full grid grid-cols-2 gap-2.5">
            <div
              v-for="stat in stats"
              :key="stat.label"
              class="bg-green-50 border border-green-100 rounded-xl px-3.5 py-2.5 flex flex-col gap-1"
            >
              <span class="font-mono text-[0.52rem] uppercase tracking-[0.1em] text-ink-faint">{{ stat.label }}</span>
              <span class="font-mono text-[0.9rem] font-bold leading-none" :class="stat.colorClass ?? 'text-ink'">
                {{ stat.value }}
              </span>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-3 w-full">
            <button
              class="flex-1 flex items-center justify-center gap-2 bg-green-500 hover:bg-green-600 active:bg-green-700 text-white font-mono text-[0.75rem] font-bold tracking-wide rounded-xl py-3 transition-colors"
              @click="playAgain"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 shrink-0">
                <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
              </svg>
              Play Again
            </button>
            <NuxtLink
              to="/"
              class="flex items-center justify-center gap-1.5 border border-green-300 hover:bg-green-50 text-green-700 font-mono text-[0.75rem] font-semibold rounded-xl px-4 py-3 transition-colors no-underline"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" class="w-3.5 h-3.5">
                <path d="M3 12l9-9 9 9M5 10v9a1 1 0 001 1h4v-5h4v5h4a1 1 0 001-1v-9"/>
              </svg>
              Home
            </NuxtLink>
          </div>

        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
const store = useKaraokeStore()

// ── Rating scale ─────────────────────────────────────────────────────────────
const RATINGS = [
  { min: 70, letter: 'S', label: 'Perfect',   color: '#a855f7', gradient: 'linear-gradient(90deg,#a855f7,#7c3aed)' },
  { min: 55, letter: 'A', label: 'Excellent',  color: '#22c55e', gradient: 'linear-gradient(90deg,#22c55e,#16a34a)' },
  { min: 40, letter: 'B', label: 'Good',       color: '#3b82f6', gradient: 'linear-gradient(90deg,#3b82f6,#2563eb)' },
  { min: 25, letter: 'C', label: 'Decent',     color: '#eab308', gradient: 'linear-gradient(90deg,#eab308,#ca8a04)' },
  { min: 10, letter: 'D', label: 'Keep going', color: '#f97316', gradient: 'linear-gradient(90deg,#f97316,#ea580c)' },
  { min: 0,  letter: 'F', label: 'Try again',  color: '#ef4444', gradient: 'linear-gradient(90deg,#ef4444,#dc2626)' },
] as const

const FALLBACK_RATING = RATINGS[RATINGS.length - 1]!

const ratingEntry = computed(() =>
  RATINGS.find(r => store.score >= r.min) ?? FALLBACK_RATING
)
const rating         = computed(() => ratingEntry.value.letter)
const ratingLabel    = computed(() => ratingEntry.value.label)
const ratingColor    = computed(() => ratingEntry.value.color)
const ratingGradient = computed(() => ratingEntry.value.gradient)

const ratingTextClass = computed(() => {
  const map: Record<string, string> = {
    S: 'text-purple-500', A: 'text-green-600', B: 'text-blue-500',
    C: 'text-yellow-500', D: 'text-orange-500', F: 'text-red-500',
  }
  return map[rating.value] ?? 'text-ink'
})

const ringOffset = computed(() => 326.73 * (1 - store.score / 100))

// ── Stats ─────────────────────────────────────────────────────────────────────
const exactPct = computed(() =>
  store.scoredFrames > 0 ? Math.round((store.exactFrames / store.scoredFrames) * 100) : 0
)

const stats = computed(() => [
  {
    label: 'Accuracy',
    value: `${store.score}%`,
    colorClass: store.score >= 70 ? 'text-purple-500' : store.score >= 55 ? 'text-green-600' : store.score >= 40 ? 'text-blue-500' : store.score >= 25 ? 'text-yellow-600' : 'text-red-500',
  },
  {
    label: 'Points',
    value: store.points.toLocaleString(),
    colorClass: 'text-green-700',
  },
  {
    label: 'Best combo',
    value: `${store.maxCombo}x`,
    colorClass: 'text-ink',
  },
  {
    label: 'Exact notes',
    value: `${exactPct.value}%`,
    colorClass: exactPct.value >= 50 ? 'text-green-600' : 'text-ink',
  },
])

// ── Actions ───────────────────────────────────────────────────────────────────
function playAgain() {
  store.resetScore()            // clears score/combo/points + sets songFinished=false
  store.setPendingRestart(true) // AudioPlayer.vue watches this and calls seek(0)+play()
}
</script>

<style scoped>
.results-enter-active {
  transition: opacity 0.35s ease, transform 0.35s cubic-bezier(.22,.68,0,1.2);
}
.results-leave-active {
  transition: opacity 0.2s ease;
}
.results-enter-from {
  opacity: 0;
  transform: scale(0.94);
}
.results-leave-to {
  opacity: 0;
}
</style>
