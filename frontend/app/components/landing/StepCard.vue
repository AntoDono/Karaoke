<template>
  <article
    class="relative group bg-cream-50 border border-moss-800/12 rounded-3xl p-7 md:p-8 shadow-soft hover:shadow-card transition-shadow overflow-hidden"
  >
    <!-- Massive numeral in background -->
    <span
      aria-hidden="true"
      class="absolute -right-4 -bottom-14 font-display font-black text-[13rem] leading-none text-moss-800/[0.045] select-none pointer-events-none"
      style="font-variation-settings: 'SOFT' 100, 'WONK' 1"
    >{{ String(index).padStart(2, '0') }}</span>

    <div class="relative z-10">
      <div class="flex items-center gap-3 font-mono text-[0.6rem] uppercase tracking-[0.22em] text-moss-700 mb-6">
        <span>Step {{ String(index).padStart(2, '0') }}</span>
        <span class="flex-1 h-px bg-moss-800/15" />
        <span class="text-ink-faint">{{ tech }}</span>
      </div>

      <h3 class="font-display font-black text-3xl md:text-4xl text-moss-900 tracking-tight leading-tight mb-2">
        {{ title }}
      </h3>
      <p class="font-display italic text-lg text-moss-700 mb-5">
        {{ subtitle }}
      </p>
      <p class="text-ink-soft leading-relaxed text-[0.95rem] max-w-md">
        {{ body }}
      </p>
    </div>
  </article>
</template>

<script setup lang="ts">
defineProps<{ index: number; title: string; subtitle: string; body: string; tech: string }>()
</script>
