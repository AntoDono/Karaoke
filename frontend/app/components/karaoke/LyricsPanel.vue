<template>
  <aside class="bg-cream-50 border border-moss-800/12 rounded-3xl overflow-hidden shadow-soft h-full min-h-0 flex flex-col">
    <header class="px-6 pt-5 pb-3 border-b border-moss-800/10 shrink-0">
      <div class="font-mono text-[0.6rem] uppercase tracking-[0.2em] text-moss-700 mb-1">§ Lyrics</div>
      <div class="font-display font-bold text-lg text-moss-900 truncate">{{ store.title || 'Untitled' }}</div>
      <div class="font-mono text-[0.65rem] uppercase tracking-[0.14em] text-ink-faint">{{ store.artist || '—' }}</div>
    </header>

    <div class="lyric-scroll ruled overflow-y-auto overscroll-contain flex-1 min-h-0 px-6 py-5 font-display text-[1.05rem] leading-[1.6rem] text-ink whitespace-pre-line">
      <template v-if="store.lyrics">{{ store.lyrics }}</template>

      <div v-else-if="store.lyricsStatus === 'pending'" class="flex items-center gap-2 text-ink-faint font-mono text-xs uppercase tracking-widest">
        <span class="w-1.5 h-1.5 rounded-full bg-moss-500 animate-pulse" />
        Fetching lyrics…
      </div>
      <div v-else class="text-ink-faint font-mono text-xs uppercase tracking-widest">
        {{ store.lyricsStatus === 'not_found' ? 'No lyrics found for this song.' : 'Lyrics unavailable.' }}
      </div>
    </div>

    <footer class="border-t border-moss-800/10 px-6 py-3 flex items-center justify-between shrink-0">
      <span class="font-mono text-[0.55rem] uppercase tracking-[0.18em] text-ink-faint">via Gemini</span>
      <span class="font-mono text-[0.55rem] uppercase tracking-[0.18em] text-ink-faint">Scroll to follow</span>
    </footer>
  </aside>
</template>

<script setup lang="ts">
const store = useSessionStore()
</script>
