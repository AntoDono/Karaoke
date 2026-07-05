<template>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-2.5">
    <div class="rounded-2xl border border-moss-800/12 bg-cream-50 px-4 py-3">
      <div class="font-mono text-[0.55rem] uppercase tracking-[0.18em] text-ink-faint">Score</div>
      <div class="font-display font-black text-2xl leading-none mt-1 text-moss-800 tabular-nums">
        {{ formatPoints(store.points) }}
      </div>
    </div>
    <div class="rounded-2xl border border-moss-800/12 bg-cream-50 px-4 py-3">
      <div class="font-mono text-[0.55rem] uppercase tracking-[0.18em] text-ink-faint">Combo</div>
      <div class="font-display font-black text-2xl leading-none mt-1 text-moss-800">
        ×{{ store.combo }}<span v-if="store.multiplier > 1" class="text-cream-400 text-sm ml-1">·{{ store.multiplier }}x</span>
      </div>
    </div>
    <div class="rounded-2xl border border-moss-800/12 bg-cream-50 px-4 py-3">
      <div class="font-mono text-[0.55rem] uppercase tracking-[0.18em] text-ink-faint">Hits</div>
      <div class="font-display font-black text-2xl leading-none mt-1 text-moss-800 tabular-nums">
        {{ store.notesHit }}<span class="text-moss-500/60 text-lg">/{{ store.totalNotes || '—' }}</span>
      </div>
    </div>
    <div class="rounded-2xl border px-4 py-3 transition-colors"
         :class="liveCard">
      <div class="font-mono text-[0.55rem] uppercase tracking-[0.18em]" :class="liveLabelClass">You</div>
      <div class="font-display font-black text-2xl leading-none mt-1 flex items-baseline gap-2" :class="liveTextClass">
        {{ store.liveNote || '—' }}
        <span v-if="store.liveVoiced" class="font-mono text-[0.6rem] font-normal opacity-70">
          {{ formatCents(store.centsOff) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const store = useSessionStore()

const liveCard = computed(() => {
  if (!store.expectedNote) return 'border-moss-800/12 bg-cream-50'
  if (store.isExact) return 'border-cream-400 bg-cream-100'
  if (store.isCorrect) return 'border-moss-500 bg-cream-50'
  return 'border-red-300 bg-red-50'
})
const liveLabelClass = computed(() => {
  if (!store.expectedNote) return 'text-ink-faint'
  if (store.isExact) return 'text-cream-400'
  if (store.isCorrect) return 'text-moss-700'
  return 'text-red-700'
})
const liveTextClass = computed(() => {
  if (!store.expectedNote) return 'text-moss-800'
  if (store.isExact) return 'text-cream-400'
  if (store.isCorrect) return 'text-moss-700'
  return 'text-red-700'
})

function formatPoints(n: number) {
  return n.toLocaleString()
}

function formatCents(c: number) {
  if (!isFinite(c) || c === 0) return ''
  const sign = c > 0 ? '+' : ''
  return `${sign}${c.toFixed(0)}¢`
}
</script>
