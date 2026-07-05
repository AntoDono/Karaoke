<template>
  <section id="how" class="relative py-24 md:py-32">
    <div class="max-w-7xl mx-auto px-6 md:px-10">

      <!-- Section header — editorial pull -->
      <div class="grid grid-cols-12 gap-6 mb-16 md:mb-20">
        <div class="col-span-12 md:col-span-4">
          <div class="font-mono text-[0.62rem] uppercase tracking-[0.24em] text-moss-700">§ How it works</div>
        </div>
        <div class="col-span-12 md:col-span-8">
          <h2 class="font-display font-black leading-[0.9] tracking-tightest text-moss-900" style="font-size: clamp(2.4rem, 6vw, 4.5rem)">
            Four passes over your audio<span class="text-moss-500">.</span>
          </h2>
          <p class="mt-6 font-display text-xl md:text-2xl text-ink-soft max-w-2xl leading-snug">
            The heavy lifting happens once, up front, on the machine running the server. After that, singing is just a websocket carrying microphone samples.
          </p>
        </div>
      </div>

      <!-- Steps grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5 md:gap-6">
        <LandingStepCard
          v-for="(step, i) in steps"
          :key="step.title"
          :index="i + 1"
          :title="step.title"
          :subtitle="step.subtitle"
          :body="step.body"
          :tech="step.tech"
        />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const steps = [
  {
    title: 'Isolate the voice',
    subtitle: 'Demucs strips away drums, bass, and instruments',
    body: 'A neural source-separation model runs over the mix and returns a clean vocal stem — the same signal we\'ll grade you against, and the reference you can loop while you rehearse.',
    tech: 'Demucs · htdemucs',
  },
  {
    title: 'Read the melody',
    subtitle: 'FCPE extracts the fundamental frequency, 100 times a second',
    body: 'A fast neural pitch estimator walks the isolated vocal and reports the singer\'s fundamental note at every 10 ms tick. That contour is the raw material for the map.',
    tech: 'FCPE · torchfcpe',
  },
  {
    title: 'Quantize to notes',
    subtitle: 'Smooth the vibrato, snap to semitones, merge into events',
    body: 'A median filter absorbs vibrato swings, a mode filter picks a single semitone per run, and short blips get dropped as artifacts. What comes out is a list of notes with start and end times.',
    tech: 'librosa · scipy',
  },
  {
    title: 'Sing & grade in real time',
    subtitle: 'Your microphone rides the same FCPE pipeline',
    body: 'Mic audio is streamed to the server as 16 kHz PCM. The same model that mapped the target notes now reads your pitch and compares them in cents — no algorithm mismatch, no unfair scoring.',
    tech: 'WebSocket · same FCPE',
  },
]
</script>
