<template>
  <nav class="relative z-30 flex items-center justify-between px-6 md:px-10 pt-6 pb-4">
    <LayoutBrandMark :size="34" />

    <div class="hidden md:flex items-center gap-8 font-mono text-[0.68rem] uppercase tracking-[0.18em] text-ink-soft">
      <NuxtLink to="/#how" class="hover:text-moss-700 no-underline">How it works</NuxtLink>
      <NuxtLink to="/#stack" class="hover:text-moss-700 no-underline">Under the hood</NuxtLink>
      <NuxtLink to="/analyze" class="hover:text-moss-700 no-underline">Studio</NuxtLink>
    </div>

    <NuxtLink
      to="/analyze"
      class="inline-flex items-center gap-2 pl-4 pr-3 py-2 rounded-full bg-moss-800 text-cream-50 no-underline text-[0.72rem] font-mono uppercase tracking-[0.14em] hover:bg-moss-700 transition-colors shadow-soft"
    >
      New Session
      <span class="w-6 h-6 rounded-full bg-cream-100 text-moss-800 inline-flex items-center justify-center font-black text-[0.85rem] leading-none">↗</span>
    </NuxtLink>
  </nav>
</template>
