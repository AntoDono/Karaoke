<template>
  <div class="absolute inset-0 pointer-events-none z-10">
    <Transition name="note-badge">
      <div
        v-if="activeNote && display"
        :key="display.name"
        class="absolute top-4 left-1/2 -translate-x-1/2 bg-ink text-green-400 rounded-lg px-3 py-1.5 flex flex-col items-center gap-1 min-w-[72px] shadow-[0_4px_20px_rgba(0,0,0,0.3),0_0_12px_rgba(74,222,128,0.2)]"
      >
        <span class="font-mono text-lg font-semibold leading-none tracking-tight">{{ display.name }}</span>
        <span class="font-mono text-[0.6rem] text-green-200 tracking-wide opacity-70">MIDI {{ display.midi }}</span>
        <div class="w-full h-0.5 bg-white/15 rounded-sm overflow-hidden">
          <div class="h-full bg-green-500 rounded-sm transition-[width] duration-75" :style="{ width: (activeNote.progress * 100) + '%' }" />
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

const store = useKaraokeStore()

const activeNote = computed(() => store.activeNote)

// Apply transpose to the displayed note name and MIDI number
const display = computed(() => {
  const note = store.activeNote
  if (!note) return null
  const midi = Math.max(0, Math.min(127, note.event.midi + store.transpose))
  const name = `${NOTE_NAMES[midi % 12]}${Math.floor(midi / 12) - 1}`
  return { midi, name }
})
</script>

<style scoped>
.note-badge-enter-active,
.note-badge-leave-active { transition: opacity 0.15s, transform 0.15s; }
.note-badge-enter-from   { opacity: 0; transform: translateX(-50%) translateY(-4px); }
.note-badge-leave-to     { opacity: 0; transform: translateX(-50%) translateY(4px);  }
</style>
