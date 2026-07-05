<template>
  <div
    class="relative bg-cream-50 border-2 border-dashed rounded-3xl p-10 md:p-12 transition-all duration-200"
    :class="[
      isDragging ? 'border-moss-600 bg-cream-100 scale-[1.01]' : 'border-moss-800/25',
      selectedFile ? 'border-moss-500' : '',
    ]"
    @dragover.prevent="onDragOver"
    @dragleave.prevent="onDragLeave"
    @drop.prevent="onDrop"
  >
    <input
      ref="fileInput"
      type="file"
      accept="audio/*,video/mp4"
      class="sr-only"
      @change="onFileChange"
    />

    <!-- Idle state -->
    <div v-if="!selectedFile" class="flex flex-col items-center text-center gap-4">
      <div class="w-16 h-16 rounded-full border border-moss-800/20 flex items-center justify-center bg-white">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-7 h-7 text-moss-700" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 3v14M6 9l6-6 6 6" />
          <path d="M4 17v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3" />
        </svg>
      </div>
      <div>
        <h3 class="font-display font-bold text-2xl text-moss-900 mb-1">Drop an audio file</h3>
        <p class="text-ink-soft">or <button type="button" class="text-moss-700 font-semibold underline decoration-moss-500/50 underline-offset-2" @click="fileInput?.click()">browse from your device</button></p>
      </div>
      <p class="font-mono text-[0.6rem] uppercase tracking-[0.18em] text-ink-faint">
        MP3 · WAV · FLAC · M4A · OGG · up to 200 MB
      </p>
    </div>

    <!-- Selected file chip -->
    <div v-else class="flex items-center gap-4">
      <div class="w-14 h-14 rounded-2xl bg-moss-800 text-cream-50 flex items-center justify-center font-display font-black text-xl shrink-0">
        ♫
      </div>
      <div class="flex-1 min-w-0">
        <div class="font-display font-bold text-lg text-moss-900 truncate">{{ selectedFile.name }}</div>
        <div class="font-mono text-[0.65rem] uppercase tracking-[0.14em] text-ink-faint">
          {{ formatBytes(selectedFile.size) }} · ready
        </div>
      </div>
      <button
        type="button"
        class="text-ink-faint hover:text-moss-700 transition-colors p-2"
        aria-label="Remove file"
        @click="clear"
      >
        <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" class="w-5 h-5" stroke-linecap="round">
          <path d="M5 5l10 10M15 5L5 15" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatBytes } from '~/composables/usePitchUtils'

const props = defineProps<{ modelValue: File | null }>()
const emit = defineEmits<{ (e: 'update:modelValue', file: File | null): void }>()

const selectedFile = computed({
  get: () => props.modelValue,
  set: (v: File | null) => emit('update:modelValue', v),
})

const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)

function onDragOver() { isDragging.value = true }
function onDragLeave() { isDragging.value = false }

function onDrop(e: DragEvent) {
  isDragging.value = false
  const f = e.dataTransfer?.files?.[0]
  if (f) selectedFile.value = f
}

function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  const f = target.files?.[0]
  if (f) selectedFile.value = f
}

function clear() {
  selectedFile.value = null
  if (fileInput.value) fileInput.value.value = ''
}
</script>
