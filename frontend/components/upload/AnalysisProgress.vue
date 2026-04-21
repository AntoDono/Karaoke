<template>
  <div class="bg-green-50 border border-green-200 rounded-2xl p-6 flex flex-col gap-5 animate-fade-up">

    <!-- Header -->
    <div class="flex justify-between items-center gap-4">
      <span class="font-mono text-xs text-ink-muted flex-1 truncate">{{ stageLabel }}</span>
      <span
        class="font-mono text-[0.65rem] font-semibold tracking-widest px-2 py-0.5 rounded shrink-0"
        :class="statusClass"
      >{{ statusText }}</span>
    </div>

    <!-- Step track -->
    <div class="flex items-start relative" role="progressbar" :aria-valuenow="stepIndex" :aria-valuemax="steps.length - 1">
      <!-- Connector line -->
      <div class="absolute top-2 left-2 right-2 h-px bg-green-200 z-0" />

      <div
        v-for="(step, i) in steps"
        :key="step.key"
        class="flex-1 flex flex-col items-center gap-1.5 relative z-10"
      >
        <!-- Dot -->
        <div
          class="w-4 h-4 rounded-full border-2 flex items-center justify-center transition-all duration-200"
          :class="{
            'bg-green-600 border-green-600': i < stepIndex,
            'border-green-500 bg-white': i === stepIndex,
            'border-green-200 bg-white': i > stepIndex,
          }"
        >
          <svg v-if="i < stepIndex" viewBox="0 0 10 10" fill="none" class="w-2.5 h-2.5">
            <path d="M2 5 L4.5 7.5 L8 3" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <div v-else-if="i === stepIndex" class="w-1.5 h-1.5 rounded-full bg-green-500 animate-dot-pulse" />
        </div>
        <!-- Label -->
        <span
          class="font-mono text-[0.6rem] uppercase tracking-wide"
          :class="i <= stepIndex ? 'text-green-700 font-semibold' : 'text-ink-faint'"
        >{{ step.label }}</span>
      </div>
    </div>

    <!-- Error -->
    <div v-if="store.jobStatus === 'failed'" class="flex items-start gap-2 font-mono text-xs text-red-600 bg-red-50 rounded-lg px-3 py-2.5 leading-relaxed">
      <span class="font-black text-sm shrink-0">!</span>
      <span>{{ store.jobError ?? 'Analysis failed. Please try again.' }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { JobStatus } from '~/types'

const store = useKaraokeStore()

const steps = [
  { key: 'separating', label: 'Vocals'   },
  { key: 'tracking',   label: 'Pitch'    },
  { key: 'quantizing', label: 'Notes'    },
  { key: 'segmenting', label: 'Segments' },
  { key: 'complete',   label: 'Done'     },
]

const stepIndex = computed(() => {
  const idx = steps.findIndex(s => s.key === store.jobStatus)
  return idx === -1 ? 0 : idx
})

const stageLabel = computed(() => store.jobProgress || 'Initialising…')

const statusText = computed(() => {
  const map: Record<JobStatus, string> = {
    queued:     'QUEUED',
    separating: 'RUNNING',
    tracking:   'RUNNING',
    quantizing: 'RUNNING',
    segmenting: 'RUNNING',
    complete:   'COMPLETE',
    failed:     'FAILED',
  }
  return store.jobStatus ? map[store.jobStatus] : 'QUEUED'
})

const statusClass = computed(() => {
  if (['separating','tracking','quantizing','segmenting'].includes(store.jobStatus ?? ''))
    return 'text-green-600 bg-green-100'
  if (store.jobStatus === 'complete')
    return 'text-green-700 bg-green-200'
  if (store.jobStatus === 'failed')
    return 'text-red-600 bg-red-100'
  return 'text-ink-faint bg-green-50'
})
</script>
