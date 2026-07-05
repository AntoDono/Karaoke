<template>
  <div class="bg-cream-50 border border-moss-800/12 rounded-3xl p-8 md:p-10 shadow-card">
    <div class="flex items-center gap-3 font-mono text-[0.6rem] uppercase tracking-[0.22em] text-moss-700 mb-6">
      <span class="w-2 h-2 rounded-full bg-moss-500 animate-pulse" />
      Working on it
    </div>

    <h3 class="font-display font-black text-3xl md:text-4xl text-moss-900 tracking-tight leading-tight mb-2">
      {{ progressLabel }}
    </h3>
    <p class="text-ink-soft mb-6">
      <template v-if="isUploading">
        Sending your file to the server — large tracks can take a few minutes.
      </template>
      <template v-else>
        Hang tight — analysis usually takes 30 to 90 seconds after upload.
      </template>
    </p>

    <!-- Upload progress bar -->
    <div v-if="isUploading" class="mb-8">
      <div class="h-2 bg-moss-800/10 rounded-full overflow-hidden">
        <div
          class="h-full bg-moss-600 rounded-full transition-all duration-300"
          :style="{ width: Math.max(uploadProgress, 2) + '%' }"
        />
      </div>
      <div class="mt-2 font-mono text-[0.6rem] uppercase tracking-[0.16em] text-ink-faint text-right">
        {{ uploadProgress }}% uploaded
      </div>
    </div>

    <!-- Vertical stage tracker -->
    <ol class="space-y-1">
      <li v-for="stage in stages" :key="stage.key"
          class="flex items-center gap-4 py-3 px-4 rounded-2xl border transition-colors"
          :class="stageClass(stage.key)">
        <div class="w-8 h-8 rounded-full flex items-center justify-center font-mono font-bold text-xs shrink-0 transition-colors"
             :class="stageDotClass(stage.key)">
          <span v-if="stageState(stage.key) === 'done'">✓</span>
          <span v-else-if="stageState(stage.key) === 'active'" class="w-2 h-2 rounded-full bg-cream-50 animate-pulse" />
          <span v-else>{{ stage.number }}</span>
        </div>
        <div class="flex-1">
          <div class="font-display font-bold text-lg text-moss-900 leading-tight">{{ stage.label }}</div>
          <div class="text-ink-soft text-sm">{{ stage.hint }}</div>
        </div>
      </li>
    </ol>

    <div v-if="lyricsStatus !== 'pending' || jobDone"
         class="mt-6 flex items-center gap-3 py-3 px-4 rounded-2xl border border-moss-800/12 bg-white/40">
      <div class="w-8 h-8 rounded-full bg-cream-100 border border-moss-800/15 flex items-center justify-center font-display font-black text-moss-800 shrink-0">L</div>
      <div class="flex-1">
        <div class="font-display font-bold text-moss-900 leading-tight">Lyrics</div>
        <div class="text-ink-soft text-sm">{{ lyricsLine }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { JobStatus, LyricsStatus } from '~/types'

const props = defineProps<{
  status: JobStatus | null
  progress: string
  lyricsStatus: LyricsStatus
  uploadProgress?: number
  isUploading?: boolean
}>()

const stages = [
  { key: 'separating',  number: '01', label: 'Isolate vocals',   hint: 'Demucs strips away the instrumental' },
  { key: 'tracking',    number: '02', label: 'Track pitch',      hint: 'FCPE reads the fundamental every 10 ms' },
  { key: 'quantizing',  number: '03', label: 'Quantize notes',   hint: 'Smooth vibrato and snap to semitones' },
  { key: 'segmenting',  number: '04', label: 'Segment events',   hint: 'Collapse frames into timed notes' },
] as const

const order = stages.map(s => s.key) as string[]

function stageState(key: string): 'done' | 'active' | 'pending' {
  const s = props.status
  if (!s) return 'pending'
  if (s === 'complete') return 'done'
  if (s === key) return 'active'
  const currentIdx = order.indexOf(s)
  const targetIdx = order.indexOf(key)
  if (currentIdx > targetIdx) return 'done'
  return 'pending'
}

function stageClass(key: string): string {
  const st = stageState(key)
  if (st === 'active') return 'border-moss-500 bg-white'
  if (st === 'done') return 'border-moss-800/8 bg-transparent'
  return 'border-moss-800/8 bg-transparent'
}

function stageDotClass(key: string): string {
  const st = stageState(key)
  if (st === 'active') return 'bg-moss-800 text-cream-50'
  if (st === 'done') return 'bg-moss-500 text-cream-50'
  return 'bg-cream-100 text-ink-faint border border-moss-800/12'
}

const jobDone = computed(() => props.status === 'complete')

const progressLabel = computed(() => {
  if (props.isUploading) return props.progress || 'Uploading file…'
  if (props.status === 'failed') return 'Something went wrong'
  if (props.status === 'complete') return 'Ready to sing'
  return props.progress || 'Warming up…'
})

const uploadProgress = computed(() => props.uploadProgress ?? 0)
const isUploading = computed(() => props.isUploading ?? false)

const lyricsLine = computed(() => {
  switch (props.lyricsStatus) {
    case 'pending':   return 'Fetching lyrics…'
    case 'found':     return 'Lyrics attached'
    case 'not_found': return 'No lyrics found — you can still sing'
    case 'error':     return 'Lyrics lookup failed — you can still sing'
  }
  return ''
})
</script>
