<template>
  <section class="relative py-24 md:py-32 overflow-hidden">
    <div class="absolute inset-x-0 top-1/2 -translate-y-1/2 h-[75%] mx-6 md:mx-10 rounded-[36px] bg-moss-800 shadow-card overflow-hidden">
      <div class="absolute -top-24 -right-16 w-[24rem] h-[24rem] rounded-full"
           style="background: radial-gradient(circle, rgba(245,200,106,0.28) 0%, transparent 65%)" />
      <div class="absolute -bottom-16 -left-16 w-[18rem] h-[18rem] rounded-full"
           style="background: radial-gradient(circle, rgba(111,181,127,0.28) 0%, transparent 65%)" />
    </div>

    <div class="relative z-10 max-w-7xl mx-auto px-10 md:px-14 py-16 md:py-24 grid grid-cols-12 gap-6 md:gap-10 items-center">
      <div class="col-span-12 md:col-span-8">
        <div class="font-mono text-[0.6rem] uppercase tracking-[0.24em] text-cream-100/70 mb-4">§ Your turn</div>
        <h2 class="font-display font-black leading-[0.9] tracking-tightest text-cream-50" style="font-size: clamp(2.6rem, 7vw, 5.5rem)">
          <span class="block">Bring a song.</span>
          <span class="block italic" style="font-variation-settings: 'SOFT' 100, 'WONK' 1">
            We'll bring the map<span class="text-cream-100">.</span>
          </span>
        </h2>
      </div>

      <div class="col-span-12 md:col-span-4 flex md:justify-end">
        <NuxtLink to="/analyze"
          class="group inline-flex items-center gap-3 pl-8 pr-4 py-4 rounded-full bg-cream-50 text-moss-900 no-underline font-mono uppercase tracking-[0.16em] text-[0.75rem] hover:bg-cream-100 transition-colors shadow-card">
          Upload a track
          <span class="w-10 h-10 rounded-full bg-moss-800 text-cream-50 flex items-center justify-center font-black text-xl leading-none group-hover:rotate-45 transition-transform">↗</span>
        </NuxtLink>
      </div>
    </div>
  </section>
</template>
