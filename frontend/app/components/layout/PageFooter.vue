<template>
  <footer class="relative z-10 border-t border-moss-800/15 mt-24">
    <div class="max-w-7xl mx-auto px-6 md:px-10 py-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
      <div class="flex items-center gap-3">
        <LayoutBrandMark :size="28" />
        <span class="font-mono text-[0.6rem] uppercase tracking-[0.18em] text-ink-faint">
          © {{ year }} Cardinal Audio
        </span>
      </div>

      <div class="flex items-center gap-6 font-mono text-[0.6rem] uppercase tracking-[0.18em] text-ink-faint">
        <span>Demucs + FCPE + Gemini</span>
        <span class="w-1 h-1 rounded-full bg-moss-500/50" />
        <span>Built with Nuxt</span>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const year = new Date().getFullYear()
</script>
