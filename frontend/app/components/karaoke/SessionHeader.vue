<template>
  <header class="sticky top-0 z-20 bg-rice/92 backdrop-blur-md border-b border-moss-800/12">
    <div class="max-w-[1400px] mx-auto px-5 md:px-8 py-3 flex items-center gap-4">
      <LayoutBrandMark :size="28" :show-text="false" />
      <NuxtLink to="/analyze" class="font-mono text-[0.6rem] uppercase tracking-[0.18em] text-ink-faint hover:text-moss-700 no-underline flex items-center gap-1">
        ←&nbsp;New session
      </NuxtLink>

      <div class="w-px h-4 bg-moss-800/15" />

      <div class="flex-1 min-w-0">
        <div class="font-display font-bold text-base md:text-lg text-moss-900 truncate leading-tight">{{ store.title || 'Untitled' }}</div>
        <div class="font-mono text-[0.55rem] uppercase tracking-[0.16em] text-ink-faint">
          {{ store.artist }} · {{ store.noteEvents.length }} notes · {{ formatTime(store.duration) }}
        </div>
      </div>

      <div class="hidden md:flex items-center gap-2">
        <span class="font-mono text-[0.55rem] uppercase tracking-[0.16em] text-ink-faint">Live via</span>
        <span class="font-mono text-[0.62rem] font-semibold px-2 py-1 rounded-full border border-moss-800/12 bg-cream-50 text-moss-800 flex items-center gap-1.5">
          <span class="w-1.5 h-1.5 rounded-full" :class="isOpen ? 'bg-moss-500 animate-pulse' : 'bg-ink-faint'" />
          {{ isOpen ? 'FCPE' : 'idle' }}
        </span>
      </div>

      <slot name="right" />
    </div>
  </header>
</template>

<script setup lang="ts">
import { formatTime } from '~/composables/usePitchUtils'
defineProps<{ isOpen: boolean }>()
const store = useSessionStore()
</script>
