<template>
  <div class="relative bg-cream-50 border border-moss-800/12 rounded-[28px] p-6 md:p-8 shadow-card overflow-hidden">
    <!-- Header row -->
    <div class="flex items-center justify-between mb-5">
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-moss-500 animate-pulse" />
        <span class="font-mono text-[0.6rem] uppercase tracking-[0.2em] text-moss-800">Live · piano roll</span>
      </div>
      <span class="font-mono text-[0.6rem] uppercase tracking-[0.2em] text-ink-faint">Bohemian Rhapsody · Queen</span>
    </div>

    <!-- Piano roll — decorative -->
    <div class="relative h-[220px] md:h-[260px] bg-rice-50 rounded-2xl overflow-hidden border border-moss-800/10">
      <!-- Horizontal staff lines -->
      <div v-for="n in 8" :key="n" class="absolute left-0 right-0 border-t border-moss-800/8"
           :style="{ top: `${(n * 100) / 9}%` }" />

      <!-- Fake note blocks -->
      <div v-for="(note, i) in notes" :key="i"
           class="absolute rounded-md transition-all duration-500"
           :style="{
             left: `${note.left}%`,
             top: `${note.top}%`,
             width: `${note.width}%`,
             height: '9%',
             background: note.color,
             boxShadow: note.active ? '0 4px 16px rgba(45,143,82,0.4)' : 'none',
             transform: note.active ? 'scale(1.03)' : 'scale(1)',
           }" />

      <!-- Sweeping playhead -->
      <div class="absolute top-0 bottom-0 w-[2px] bg-moss-800/70 pointer-events-none"
           :style="{ left: playhead + '%', boxShadow: '0 0 12px rgba(15,61,38,0.35)' }">
        <div class="absolute -top-1 left-1/2 -translate-x-1/2 w-3 h-3 rotate-45 bg-moss-800" />
      </div>
    </div>

    <!-- Stats row -->
    <div class="mt-5 grid grid-cols-3 gap-3">
      <div class="rounded-xl border border-moss-800/10 bg-white/60 px-3 py-2.5">
        <div class="font-mono text-[0.55rem] uppercase tracking-[0.16em] text-ink-faint">Live pitch</div>
        <div class="font-display font-black text-lg text-moss-700 leading-tight">{{ liveNote }}</div>
      </div>
      <div class="rounded-xl border border-moss-800/10 bg-white/60 px-3 py-2.5">
        <div class="font-mono text-[0.55rem] uppercase tracking-[0.16em] text-ink-faint">Score</div>
        <div class="font-display font-black text-lg text-moss-700 leading-tight">{{ score }}%</div>
      </div>
      <div class="rounded-xl border border-moss-800/10 bg-white/60 px-3 py-2.5">
        <div class="font-mono text-[0.55rem] uppercase tracking-[0.16em] text-ink-faint">Combo</div>
        <div class="font-display font-black text-lg text-moss-700 leading-tight">×{{ combo }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const notesTemplate = [
  { left: 5,  top: 30, width: 10, color: 'rgba(45,143,82,0.9)' },
  { left: 17, top: 42, width: 7,  color: 'rgba(45,143,82,0.9)' },
  { left: 26, top: 24, width: 12, color: 'rgba(45,143,82,0.9)' },
  { left: 40, top: 55, width: 8,  color: 'rgba(245,200,106,0.9)' },
  { left: 50, top: 47, width: 14, color: 'rgba(45,143,82,0.9)' },
  { left: 66, top: 36, width: 10, color: 'rgba(45,143,82,0.9)' },
  { left: 78, top: 62, width: 9,  color: 'rgba(45,143,82,0.9)' },
  { left: 89, top: 40, width: 8,  color: 'rgba(45,143,82,0.9)' },
]

const playhead = ref(10)
const liveNoteVals = ['C4','D4','E4','G4','F4','A4','B4','C5','A4','G4']
const idx = ref(0)
const liveNote = computed(() => liveNoteVals[idx.value % liveNoteVals.length])
const score = ref(87)
const combo = ref(12)

const notes = computed(() =>
  notesTemplate.map(n => ({
    ...n,
    active: playhead.value >= n.left && playhead.value <= n.left + n.width,
  }))
)

let raf: number | null = null
let last = performance.now()
function tick(now: number) {
  const dt = now - last
  last = now
  playhead.value = playhead.value + (dt / 1000) * 20
  if (playhead.value > 100) {
    playhead.value = 0
    idx.value += 3
    score.value = 82 + Math.floor(Math.random() * 15)
    combo.value = 8 + Math.floor(Math.random() * 20)
  } else if (Math.random() < 0.02) {
    idx.value++
  }
  raf = requestAnimationFrame(tick)
}
onMounted(() => { raf = requestAnimationFrame(tick) })
onUnmounted(() => { if (raf) cancelAnimationFrame(raf) })
</script>
