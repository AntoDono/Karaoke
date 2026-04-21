import type { JobResponse, AnalyzeResponse } from '~/types'

const POLL_INTERVAL_MS = 2000
const TERMINAL_STATUSES = new Set(['complete', 'failed'])

export function useAnalysis() {
  const store = useKaraokeStore()
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase as string

  const isUploading = ref(false)
  const isPolling = ref(false)
  let pollTimer: ReturnType<typeof setTimeout> | null = null

  async function uploadAndAnalyze(file: File): Promise<void> {
    isUploading.value = true
    store.setAudioFile(file)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const resp = await $fetch<AnalyzeResponse>(`${apiBase}/api/analyze`, {
        method: 'POST',
        body: formData,
      })

      store.setJob(resp.job_id)
      startPolling(resp.job_id)
    } catch (err: any) {
      store.updateJobStatus('failed', undefined, undefined, err?.message ?? 'Upload failed')
    } finally {
      isUploading.value = false
    }
  }

  function startPolling(jobId: string): void {
    isPolling.value = true
    poll(jobId)
  }

  async function poll(jobId: string): Promise<void> {
    try {
      const job = await $fetch<JobResponse>(`${apiBase}/api/jobs/${jobId}`)
      store.updateJobStatus(job.status, job.progress, job.result, job.error ?? undefined)

      if (TERMINAL_STATUSES.has(job.status)) {
        stopPolling()
      } else {
        pollTimer = setTimeout(() => poll(jobId), POLL_INTERVAL_MS)
      }
    } catch {
      // Retry on transient network errors
      pollTimer = setTimeout(() => poll(jobId), POLL_INTERVAL_MS * 2)
    }
  }

  function stopPolling(): void {
    isPolling.value = false
    if (pollTimer !== null) {
      clearTimeout(pollTimer)
      pollTimer = null
    }
  }

  onUnmounted(stopPolling)

  return { uploadAndAnalyze, isUploading, isPolling, stopPolling }
}
