import { defineStore } from 'pinia'
import type { NoteEvent, AnalysisResult, JobStatus, ActiveNote, VocalRange } from '~/types'

export const useKaraokeStore = defineStore('karaoke', () => {
  // ── Job state ───────────────────────────────────────────────────────────────
  const jobId = ref<string | null>(null)
  const jobStatus = ref<JobStatus | null>(null)
  const jobProgress = ref<string>('')
  const jobError = ref<string | null>(null)

  // ── Analysis result ─────────────────────────────────────────────────────────
  const analysisResult = ref<AnalysisResult | null>(null)
  const noteEvents = computed(() => analysisResult.value?.notes ?? [])
  const duration = computed(() => analysisResult.value?.duration ?? 0)
  const device = computed(() => analysisResult.value?.device ?? '')

  // ── Audio source ────────────────────────────────────────────────────────────
  const audioUrl  = ref<string | null>(null)   // object URL for the original upload
  const vocalsUrl = ref<string | null>(null)   // backend URL for the isolated vocal stem
  const audioFile = ref<File | null>(null)

  // ── Playback ────────────────────────────────────────────────────────────────
  const currentTime = ref(0)
  const isPlaying = ref(false)

  // ── Mic / live pitch ────────────────────────────────────────────────────────
  const liveF0 = ref(0)           // Hz, 0 = unvoiced
  const liveMidi = ref(0)         // quantised MIDI note
  const liveNoteName = ref('')    // e.g. "C4"
  const isMicActive = ref(false)

  // ── Transpose & vocal range ──────────────────────────────────────────────────
  const transpose  = ref(0)                          // semitones; positive = up
  const vocalRange = ref<VocalRange | null>(null)

  // ── Score ────────────────────────────────────────────────────────────────────
  const score = ref(0)             // 0–100
  const scoredFrames = ref(0)
  const correctFrames = ref(0)

  // ── Derived: active note at playhead ────────────────────────────────────────
  const activeNote = computed<ActiveNote | null>(() => {
    const t = currentTime.value
    const event = noteEvents.value.find(n => t >= n.start && t <= n.end)
    if (!event) return null
    const progress = (t - event.start) / (event.end - event.start)
    return { event, progress: Math.min(1, Math.max(0, progress)) }
  })

  // ── Actions ─────────────────────────────────────────────────────────────────
  function setJob(id: string) {
    jobId.value = id
    jobStatus.value = 'queued'
    jobError.value = null
    jobProgress.value = ''
  }

  function updateJobStatus(status: JobStatus, progress?: string, result?: AnalysisResult, error?: string) {
    jobStatus.value = status
    if (progress !== undefined) jobProgress.value = progress
    if (result) {
      analysisResult.value = result
      if (result.vocals_url) vocalsUrl.value = result.vocals_url
    }
    if (error) jobError.value = error
  }

  function setAudioFile(file: File) {
    audioFile.value = file
    if (audioUrl.value) URL.revokeObjectURL(audioUrl.value)
    audioUrl.value = URL.createObjectURL(file)
  }

  function setCurrentTime(t: number) {
    currentTime.value = t
  }

  function setPlaying(v: boolean) {
    isPlaying.value = v
  }

  function setLivePitch(f0Hz: number, midi: number, noteName: string) {
    liveF0.value = f0Hz
    liveMidi.value = midi
    liveNoteName.value = noteName
  }

  function setMicActive(v: boolean) {
    isMicActive.value = v
    if (!v) {
      liveF0.value = 0
      liveMidi.value = 0
      liveNoteName.value = ''
    }
  }

  function setTranspose(octaves: number) {
    // Transpose is octave-only — snap to nearest multiple of 12, clamped ±2 octaves
    const snapped = Math.round(octaves / 12) * 12
    transpose.value = Math.max(-24, Math.min(24, snapped))
  }

  function setVocalRange(range: VocalRange) {
    vocalRange.value = range
  }

  function recordPitchSample(isCorrect: boolean) {
    scoredFrames.value++
    if (isCorrect) correctFrames.value++
    score.value = scoredFrames.value > 0
      ? Math.round((correctFrames.value / scoredFrames.value) * 100)
      : 0
  }

  function resetSession() {
    jobId.value = null
    jobStatus.value = null
    jobProgress.value = ''
    jobError.value = null
    analysisResult.value = null
    currentTime.value = 0
    isPlaying.value = false
    liveF0.value = 0
    liveMidi.value = 0
    liveNoteName.value = ''
    isMicActive.value = false
    score.value = 0
    scoredFrames.value = 0
    correctFrames.value = 0
    transpose.value = 0
    vocalRange.value = null
    if (audioUrl.value) {
      URL.revokeObjectURL(audioUrl.value)
      audioUrl.value = null
    }
    vocalsUrl.value = null
    audioFile.value = null
  }

  return {
    // state
    jobId, jobStatus, jobProgress, jobError,
    analysisResult, noteEvents, duration, device,
    audioUrl, vocalsUrl, audioFile,
    currentTime, isPlaying,
    liveF0, liveMidi, liveNoteName, isMicActive,
    score, scoredFrames, correctFrames,
    transpose, vocalRange,
    // computed
    activeNote,
    // actions
    setJob, updateJobStatus,
    setAudioFile, setCurrentTime, setPlaying,
    setLivePitch, setMicActive, recordPitchSample,
    setTranspose, setVocalRange,
    resetSession,
  }
})
