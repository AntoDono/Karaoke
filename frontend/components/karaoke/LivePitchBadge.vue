<template>
  <div
    v-if="store.isMicActive"
    class="flex items-center gap-2 px-2.5 py-1.5 bg-ink rounded-lg font-mono shrink-0"
  >
    <!-- Animated dot -->
    <span class="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse shrink-0" />

    <!-- Note name -->
    <span class="text-green-400 font-semibold text-sm leading-none tracking-tight min-w-[2.5rem]">
      {{ store.liveNoteName || '—' }}
    </span>

    <!-- Hz -->
    <span v-if="store.liveF0 > 0" class="text-green-200/60 text-[0.6rem] leading-none">
      {{ store.liveF0.toFixed(0) }}Hz
    </span>
  </div>
</template>

<script setup lang="ts">
const store = useKaraokeStore()
</script>
