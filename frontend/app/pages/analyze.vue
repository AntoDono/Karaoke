<template>
  <div class="min-h-screen bg-rice relative overflow-x-hidden flex flex-col">
    <LayoutPageNav />

    <main class="flex-1 max-w-3xl w-full mx-auto px-6 md:px-10 pt-8 pb-16">

      <div class="mb-10">
        <div class="font-mono text-[0.62rem] uppercase tracking-[0.24em] text-moss-700 mb-3">§ Studio · new session</div>
        <h1 class="font-display font-black leading-[0.9] tracking-tightest text-moss-900" style="font-size: clamp(2.4rem, 6.5vw, 4.5rem)">
          Bring us a song<span class="text-moss-500">.</span>
        </h1>
        <p class="font-display text-xl md:text-2xl text-ink-soft mt-4">
          We'll isolate the voice, map every note, and pull the lyrics.
        </p>
      </div>

      <!-- Upload form -->
      <form v-if="!analyzing" @submit.prevent="submit" class="space-y-5">
        <UploadDropZone v-model="file" />

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label class="block">
            <span class="font-mono text-[0.6rem] uppercase tracking-[0.18em] text-moss-700 block mb-2">Song title</span>
            <input
              v-model="title"
              type="text"
              required
              placeholder="Bohemian Rhapsody"
              class="w-full px-4 py-3 rounded-2xl bg-cream-50 border border-moss-800/12 font-display text-lg text-moss-900 placeholder-ink-faint focus:border-moss-500 focus:outline-none transition-colors"
            />
          </label>
          <label class="block">
            <span class="font-mono text-[0.6rem] uppercase tracking-[0.18em] text-moss-700 block mb-2">Artist</span>
            <input
              v-model="artist"
              type="text"
              required
              placeholder="Queen"
              class="w-full px-4 py-3 rounded-2xl bg-cream-50 border border-moss-800/12 font-display text-lg text-moss-900 placeholder-ink-faint focus:border-moss-500 focus:outline-none transition-colors"
            />
          </label>
        </div>

        <div v-if="errorMsg" class="text-red-700 font-mono text-sm bg-red-50 border border-red-200 rounded-xl px-4 py-3">
          {{ errorMsg }}
        </div>

        <button
          type="submit"
          :disabled="!canSubmit"
          class="w-full py-4 rounded-2xl bg-moss-800 text-cream-50 font-mono uppercase tracking-[0.16em] text-sm hover:bg-moss-700 active:scale-[0.99] disabled:bg-ink-faint/40 disabled:cursor-not-allowed transition-all shadow-soft flex items-center justify-center gap-3"
        >
          <span v-if="isUploading" class="inline-flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-cream-50 animate-pulse" />
            Uploading…
          </span>
          <span v-else class="inline-flex items-center gap-3">
            Analyze
            <span class="w-8 h-8 rounded-full bg-cream-100 text-moss-800 flex items-center justify-center font-black text-lg leading-none">↗</span>
          </span>
        </button>
      </form>

      <!-- Progress -->
      <div v-else>
        <UploadProgressPanel
          :status="store.jobStatus"
          :progress="store.jobProgress"
          :lyrics-status="store.lyricsStatus"
          :upload-progress="uploadProgress"
          :is-uploading="isUploading"
        />

        <div v-if="store.jobStatus === 'failed'" class="mt-4">
          <p v-if="store.jobError || errorMsg" class="text-red-700 font-mono text-sm bg-red-50 border border-red-200 rounded-xl px-4 py-3 mb-3">
            {{ store.jobError || errorMsg }}
          </p>
          <button class="font-mono text-sm text-moss-700 underline underline-offset-2" @click="reset">Start over</button>
        </div>
      </div>
    </main>

    <LayoutPageFooter />
  </div>
</template>

<script setup lang="ts">
const store = useSessionStore()
const router = useRouter()
const route = useRoute()
const { uploadAndAnalyze, isUploading, uploadProgress, stopPolling } = useAnalysis()

const file = ref<File | null>(null)
const title = ref('')
const artist = ref('')
const errorMsg = ref<string | null>(null)

function clearAnalyzePage() {
  stopPolling()
  store.resetForNewSession()
  file.value = null
  title.value = ''
  artist.value = ''
  errorMsg.value = null
}

watch(() => route.path, (path) => {
  if (path === '/analyze') clearAnalyzePage()
}, { immediate: true })

const canSubmit = computed(() =>
  !!file.value && !!title.value.trim() && !!artist.value.trim() && !isUploading.value
)

const analyzing = computed(() =>
  isUploading.value ||
  ['queued', 'separating', 'tracking', 'quantizing', 'segmenting', 'complete', 'failed'].includes(store.jobStatus ?? '')
)

async function submit() {
  if (!file.value) return
  errorMsg.value = null
  try {
    await uploadAndAnalyze(file.value, title.value.trim(), artist.value.trim())
  } catch (e: any) {
    errorMsg.value = e?.data?.detail ?? e?.message ?? 'Upload failed'
  }
}

function reset() {
  clearAnalyzePage()
}

// Auto-advance once analysis and lyrics are ready
watch(
  () => [store.jobStatus, store.lyricsStatus] as const,
  ([status, lyricsStatus]) => {
    if (status === 'complete' && store.jobId && lyricsStatus !== 'pending') {
      setTimeout(() => router.push(`/setup?job=${store.jobId}`), 500)
    }
  },
)
</script>
