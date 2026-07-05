<template>
  <section class="relative overflow-hidden paper-grain">
    <!-- Warm radial glows -->
    <div class="absolute -top-40 -right-40 w-[45rem] h-[45rem] rounded-full pointer-events-none"
         style="background: radial-gradient(circle, rgba(45,143,82,0.14) 0%, transparent 65%)" />
    <div class="absolute top-1/2 -left-40 w-[30rem] h-[30rem] rounded-full pointer-events-none"
         style="background: radial-gradient(circle, rgba(245,200,106,0.22) 0%, transparent 65%)" />

    <div class="relative z-10 max-w-7xl mx-auto px-6 md:px-10 pt-8 md:pt-16 pb-20 md:pb-28">

      <!-- Editorial dateline strip -->
      <div class="flex items-center gap-4 font-mono text-[0.6rem] uppercase tracking-[0.24em] text-ink-faint mb-10 animate-rise" style="animation-delay: 0.05s">
        <span class="w-8 h-px bg-ink-faint/50" />
        <span>Vol. 01 · Issue 003</span>
        <span class="w-1 h-1 rounded-full bg-moss-500" />
        <span>Practice Room</span>
        <span class="w-1 h-1 rounded-full bg-moss-500" />
        <span class="text-moss-700">Now taking uploads</span>
      </div>

      <!-- Massive display headline — editorial with a wonky character -->
      <h1 class="font-display font-black text-moss-900 leading-[0.82] tracking-tightest select-none animate-rise"
          style="font-size: clamp(3.6rem, 13vw, 10rem); animation-delay: 0.1s">
        <span class="block">Sing</span>
        <span class="block italic" style="font-variation-settings: 'SOFT' 100, 'WONK' 1">
          what you hear<span class="text-moss-500">.</span>
        </span>
      </h1>

      <!-- Two-column asymmetric layout under headline -->
      <div class="mt-10 md:mt-14 grid grid-cols-12 gap-6 md:gap-10">
        <!-- Left: description -->
        <div class="col-span-12 md:col-span-6 lg:col-span-5 animate-rise" style="animation-delay: 0.18s">
          <p class="font-display text-2xl md:text-[1.7rem] leading-snug text-ink">
            Upload any track. We strip the instrumental, map the melody note by note, then grade you note by note as you sing along.
          </p>

          <div class="mt-8 flex flex-wrap items-center gap-3">
            <NuxtLink
              to="/analyze"
              class="group inline-flex items-center gap-3 pl-6 pr-4 py-3.5 rounded-full bg-moss-800 text-cream-50 no-underline font-mono uppercase tracking-[0.16em] text-[0.72rem] hover:bg-moss-700 transition-colors shadow-card"
            >
              Start a session
              <span class="w-8 h-8 rounded-full bg-cream-100 text-moss-800 flex items-center justify-center font-black text-lg leading-none group-hover:rotate-45 transition-transform">↗</span>
            </NuxtLink>
            <a href="#how" class="font-mono text-[0.72rem] uppercase tracking-[0.16em] text-ink-soft hover:text-moss-700 no-underline px-4 py-3">
              How it works ↓
            </a>
          </div>
        </div>

        <!-- Right: ornament — animated wave + stat pull-quote -->
        <div class="col-span-12 md:col-span-6 lg:col-span-7 relative animate-rise" style="animation-delay: 0.28s">
          <LandingHeroWave />
        </div>
      </div>

      <!-- Bottom ticker rule -->
      <div class="mt-16 md:mt-20 border-t border-moss-800/15 pt-5 flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-4 font-mono text-[0.6rem] uppercase tracking-[0.22em] text-ink-faint">
          <span>C4</span><span class="w-1 h-1 rounded-full bg-moss-500" />
          <span>F#3</span><span class="w-1 h-1 rounded-full bg-moss-500" />
          <span>A♭5</span><span class="w-1 h-1 rounded-full bg-moss-500" />
          <span>—</span><span class="w-1 h-1 rounded-full bg-moss-500" />
          <span>whatever you can hit</span>
        </div>
        <div class="font-mono text-[0.6rem] uppercase tracking-[0.22em] text-ink-faint">
          Est. 2026 &nbsp;·&nbsp; No accounts &nbsp;·&nbsp; Runs on your machine
        </div>
      </div>
    </div>
  </section>
</template>
