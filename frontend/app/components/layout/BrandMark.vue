<template>
  <NuxtLink to="/" class="inline-flex items-center gap-2.5 no-underline text-moss-800 hover:text-moss-600 transition-colors">
    <!-- Ornamental "K" mark: a serif K wrapped in a printer's tick -->
    <span class="relative inline-flex items-center justify-center" :style="{ width: sizePx + 'px', height: sizePx + 'px' }">
      <span class="absolute inset-0 rounded-full border-[1.25px] border-moss-800/30" />
      <span class="absolute inset-1 rounded-full border-[1.25px] border-moss-800/15" />
      <span class="relative font-display font-black leading-none" :style="{ fontSize: (sizePx * 0.55) + 'px', letterSpacing: '-0.06em' }"
            style="font-variation-settings: 'SOFT' 100, 'WONK' 1">K</span>
    </span>
    <span v-if="showText" class="font-display font-black tracking-tightest leading-none text-moss-900" :style="{ fontSize: textSize + 'px' }">
      Karaoke<span class="text-moss-500">.</span>
    </span>
  </NuxtLink>
</template>

<script setup lang="ts">
const props = defineProps<{ size?: number; showText?: boolean }>()
const sizePx = computed(() => props.size ?? 34)
const textSize = computed(() => Math.round(sizePx.value * 0.7))
const showText = computed(() => props.showText ?? true)
</script>
