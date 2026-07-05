import type { AnalyzeResponse, JobResponse } from '~/types'

const POLL_MS = 1500
const TERMINAL = new Set(['complete', 'failed'])

function postFormWithProgress(
  url: string,
  form: FormData,
  onProgress: (pct: number) => void,
): Promise<AnalyzeResponse> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', url)
    xhr.responseType = 'json'

    xhr.upload.onprogress = (ev) => {
      if (ev.lengthComputable && ev.total > 0) {
        onProgress(Math.round((ev.loaded / ev.total) * 100))
      }
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(xhr.response as AnalyzeResponse)
        return
      }
      const detail = xhr.response?.detail
      const msg = typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
          ? detail.map((d: { msg?: string }) => d.msg).filter(Boolean).join(', ')
          : `Upload failed (${xhr.status})`
      reject(new Error(msg))
    }

    xhr.onerror = () => reject(new Error('Network error — is the backend running on port 8000?'))
    xhr.ontimeout = () => reject(new Error('Upload timed out'))
    xhr.send(form)
  })
}

export function useAnalysis() {
  const store = useSessionStore()
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase as string

  const isUploading = ref(false)
  const uploadProgress = ref(0)   // 0–100
  const isPolling = ref(false)
  let timer: ReturnType<typeof setTimeout> | null = null
  let lyricsTimer: ReturnType<typeof setTimeout> | null = null

  async function uploadAndAnalyze(file: File, title: string, artist: string) {
    isUploading.value = true
    uploadProgress.value = 0
    store.setAudioFile(file)
    store.jobStatus = 'queued'
    store.jobProgress = 'Uploading file…'

    try {
      const form = new FormData()
      form.append('file', file)
      form.append('title', title)
      form.append('artist', artist)

      const resp = await postFormWithProgress(
        `${apiBase}/api/analyze`,
        form,
        (pct) => {
          uploadProgress.value = pct
          store.jobProgress = `Uploading file… ${pct}%`
        },
      )

      store.setJob(resp.job_id, { title, artist })
      store.jobProgress = 'Queued'
      startPolling(resp.job_id)
      return resp.job_id
    } catch (err: any) {
      store.updateJob({ status: 'failed', error: err?.message ?? 'Upload failed' })
      throw err
    } finally {
      isUploading.value = false
      uploadProgress.value = 0
    }
  }

  function startPolling(jobId: string) {
    isPolling.value = true
    poll(jobId)
  }

  async function poll(jobId: string) {
    try {
      const job = await $fetch<JobResponse>(`${apiBase}/api/jobs/${jobId}`)
      store.updateJob({
        status: job.status,
        progress: job.progress,
        result: job.result,
        error: job.error,
        title: job.title,
        artist: job.artist,
        lyrics: job.lyrics ?? null,
        lyrics_status: job.lyrics_status,
      })

      const jobDone = TERMINAL.has(job.status)
      const lyricsPending = job.lyrics_status === 'pending'

      if (jobDone && !lyricsPending) {
        stopPolling()
      } else {
        timer = setTimeout(() => poll(jobId), POLL_MS)
      }
    } catch {
      timer = setTimeout(() => poll(jobId), POLL_MS * 2)
    }
  }

  function stopPolling() {
    isPolling.value = false
    if (timer !== null) {
      clearTimeout(timer)
      timer = null
    }
  }

  function stopLyricsPolling() {
    if (lyricsTimer !== null) {
      clearTimeout(lyricsTimer)
      lyricsTimer = null
    }
  }

  async function refreshJob(jobId: string) {
    const job = await $fetch<JobResponse>(`${apiBase}/api/jobs/${jobId}`)
    store.updateJob({
      status: job.status,
      progress: job.progress,
      result: job.result,
      error: job.error,
      title: job.title,
      artist: job.artist,
      lyrics: job.lyrics ?? null,
      lyrics_status: job.lyrics_status,
    })
    if (!store.jobId) store.jobId = jobId
    return job
  }

  function startLyricsPolling(jobId: string) {
    stopLyricsPolling()

    const tick = async () => {
      if (store.lyricsStatus !== 'pending') {
        stopLyricsPolling()
        return
      }
      try {
        const job = await refreshJob(jobId)
        if (job.lyrics_status !== 'pending') {
          stopLyricsPolling()
          return
        }
      } catch {
        // keep trying
      }
      lyricsTimer = setTimeout(tick, POLL_MS)
    }

    lyricsTimer = setTimeout(tick, POLL_MS)
  }

  async function fetchJob(jobId: string) {
    const job = await refreshJob(jobId)
    if (job.lyrics_status === 'pending') {
      startLyricsPolling(jobId)
    }
    return job
  }

  onUnmounted(() => {
    stopPolling()
    stopLyricsPolling()
  })

  return {
    uploadAndAnalyze,
    startPolling,
    stopPolling,
    startLyricsPolling,
    stopLyricsPolling,
    fetchJob,
    refreshJob,
    isUploading,
    uploadProgress,
    isPolling,
  }
}
