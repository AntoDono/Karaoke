<template>
  <section id="stack" class="relative py-24 md:py-32 border-t border-moss-800/12 bg-rice-100">

    <div class="max-w-7xl mx-auto px-6 md:px-10 grid grid-cols-12 gap-6 md:gap-10">

      <!-- Left: title -->
      <div class="col-span-12 md:col-span-5">
        <div class="font-mono text-[0.62rem] uppercase tracking-[0.24em] text-moss-700 mb-4">§ Under the hood</div>
        <h2 class="font-display font-black leading-[0.9] tracking-tightest text-moss-900" style="font-size: clamp(2.2rem, 5.5vw, 4rem)">
          Two consistent measurements<span class="text-moss-500">.</span>
        </h2>
        <p class="mt-6 font-display text-xl text-ink-soft leading-snug max-w-md">
          Every scoring decision comes from a single pitch estimator, so the target melody and your live voice speak the same language.
        </p>
      </div>

      <!-- Right: technical rows -->
      <div class="col-span-12 md:col-span-7">
        <dl class="border-t border-moss-800/15">
          <div v-for="row in rows" :key="row.label"
               class="grid grid-cols-12 gap-4 py-6 border-b border-moss-800/12 items-baseline">
            <dt class="col-span-4 md:col-span-3 font-mono text-[0.65rem] uppercase tracking-[0.16em] text-moss-700">
              {{ row.label }}
            </dt>
            <dd class="col-span-8 md:col-span-9">
              <div class="font-display font-bold text-xl md:text-2xl text-moss-900 leading-tight">{{ row.value }}</div>
              <div class="text-ink-soft mt-1 text-sm">{{ row.note }}</div>
            </dd>
          </div>
        </dl>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const rows = [
  { label: 'Vocal separation', value: 'Demucs (htdemucs)',
    note: 'Runs once per upload. GPU-accelerated on CUDA / MPS, CPU fallback for everything else.' },
  { label: 'Pitch tracker', value: 'FCPE @ 16 kHz, 10 ms hop',
    note: 'Fast Context-based Pitch Estimation. Same model instance shared across every request for consistency.' },
  { label: 'Lyrics', value: 'Gemini API + Google Search',
    note: 'Fetched in a background thread the moment you press upload. Cleaned before display.' },
  { label: 'Live channel', value: 'WebSocket, int16 PCM',
    note: '100 ms chunks streamed from an AudioWorklet. Each connection is a fresh grading session.' },
  { label: 'Grading', value: '±50 cents = correct, ±25 = exact',
    note: 'Comparison is done in cents instead of raw semitones so vibrato and slides don\'t get punished.' },
]
</script>
