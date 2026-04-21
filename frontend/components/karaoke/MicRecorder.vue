<template>
  <div class="flex items-center gap-3">
    <button
      class="relative w-11 h-11 rounded-full border-2 flex items-center justify-center cursor-pointer shrink-0 transition-all duration-200"
      :class="{
        'border-green-500 bg-green-100 text-green-700': store.isMicActive,
        'border-green-300 bg-green-50 text-ink-muted hover:border-green-500 hover:text-green-700': !store.isMicActive && !error,
        'border-red-400 text-red-500': !!error,
      }"
      @click="toggle"
      :title="store.isMicActive ? 'Stop microphone' : 'Start microphone'"
    >
      <svg viewBox="0 0 24 24" fill="none" class="w-[18px] h-[18px]" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="9" y="2" width="6" height="11" rx="3"/>
        <path d="M5 10a7 7 0 0 0 14 0"/>
        <line x1="12" y1="19" x2="12" y2="22"/>
        <line x1="9"  y1="22" x2="15" y2="22"/>
      </svg>
      <!-- Pulse ring when active -->
      <span v-if="store.isMicActive" class="absolute inset-[-4px] rounded-full border-2 border-green-500 animate-ring-pulse pointer-events-none" />
    </button>

    <div class="flex flex-col gap-0.5">
      <span class="font-mono text-[0.95rem] font-semibold text-ink tracking-tight">
        {{ store.isMicActive ? (store.liveNoteName || '—') : 'MIC OFF' }}
      </span>
      <span v-if="store.isMicActive && store.liveF0 > 0" class="font-mono text-[0.65rem] text-ink-faint">
        {{ store.liveF0.toFixed(1) }} Hz
      </span>
      <span v-if="error" class="font-mono text-[0.65rem] text-red-500">{{ error }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
const store = useKaraokeStore()
const { toggle, error } = useMicRecorder()
</script>
