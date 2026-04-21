<template>
  <div
    class="relative border-2 border-dashed border-green-300 rounded-2xl bg-green-50 cursor-pointer transition-all duration-200 p-12 text-center select-none overflow-hidden hover:border-green-500 hover:bg-green-100 hover:scale-[1.005]"
    :class="{
      'border-green-500 bg-green-100 scale-[1.005] animate-pulse-border': isDragOver,
      'pointer-events-none opacity-70': isUploading,
    }"
    @dragenter.prevent="isDragOver = true"
    @dragover.prevent="isDragOver = true"
    @dragleave.prevent="onDragLeave"
    @drop.prevent="onDrop"
    @click="triggerFileInput"
  >
    <!-- Radial glow overlay — can't do with Tailwind -->
    <div class="absolute inset-0 pointer-events-none opacity-0 transition-opacity duration-200 hover:opacity-100 bg-[radial-gradient(ellipse_at_50%_0%,rgba(34,197,94,0.08)_0%,transparent_70%)]" />

    <input
      ref="fileInputRef"
      type="file"
      accept="audio/*"
      class="hidden"
      @change="onFileInput"
    />

    <div class="flex flex-col items-center gap-5">
      <!-- Icon -->
      <div class="text-green-600 w-16 h-10 flex items-center justify-content-center">
        <svg v-if="!isUploading" viewBox="0 0 64 40" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-16 h-10">
          <rect x="0"  y="16" width="4" height="8"  rx="2" fill="currentColor" opacity="0.3"/>
          <rect x="8"  y="10" width="4" height="20" rx="2" fill="currentColor" opacity="0.5"/>
          <rect x="16" y="4"  width="4" height="32" rx="2" fill="currentColor" opacity="0.8"/>
          <rect x="24" y="8"  width="4" height="24" rx="2" fill="currentColor"/>
          <rect x="32" y="0"  width="4" height="40" rx="2" fill="currentColor"/>
          <rect x="40" y="8"  width="4" height="24" rx="2" fill="currentColor"/>
          <rect x="48" y="4"  width="4" height="32" rx="2" fill="currentColor" opacity="0.8"/>
          <rect x="56" y="10" width="4" height="20" rx="2" fill="currentColor" opacity="0.5"/>
        </svg>
        <div v-else class="w-8 h-8 rounded-full border-[3px] border-green-200 border-t-green-500 animate-spin-slow mx-auto" aria-label="Uploading…" />
      </div>

      <div class="flex flex-col gap-1.5">
        <p class="font-display text-xl font-bold text-ink tracking-tight">
          {{ isUploading ? 'Uploading…' : isDragOver ? 'Release to analyze' : 'Drop your audio here' }}
        </p>
        <p class="font-mono text-xs text-ink-faint">
          {{ isUploading ? 'Sending to analysis pipeline' : 'or click to browse · MP3, WAV, FLAC, M4A' }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ isUploading: boolean }>()
const emit  = defineEmits<{ (e: 'file', f: File): void }>()

const isDragOver   = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

function onDragLeave(e: DragEvent) {
  if (!(e.currentTarget as HTMLElement).contains(e.relatedTarget as Node)) {
    isDragOver.value = false
  }
}

function onDrop(e: DragEvent) {
  isDragOver.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) emitFile(file)
}

function onFileInput(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) emitFile(file)
}

function triggerFileInput() {
  if (!props.isUploading) fileInputRef.value?.click()
}

function emitFile(file: File) {
  if (!file.type.startsWith('audio/') && file.type !== 'video/mp4') return
  emit('file', file)
}
</script>
