import { defineStore } from 'pinia'
import type { AnalysisResult, DetectedRange, JobStatus, LyricsStatus, NoteEvent } from '~/types'

export const useSessionStore = defineStore('session', () => {
  // ── Job / analysis ────────────────────────────────────────────────────
  const jobId = ref<string | null>(null)
  const jobStatus = ref<JobStatus | null>(null)
  const jobProgress = ref('')
  const jobError = ref<string | null>(null)

  const analysis = ref<AnalysisResult | null>(null)
  const noteEvents = computed<NoteEvent[]>(() => analysis.value?.notes ?? [])
  const duration = computed(() => analysis.value?.duration ?? 0)
  const device = computed(() => analysis.value?.device ?? '')
  const vocalsUrl = computed(() => analysis.value?.vocals_url ?? null)

  const title = ref('')
  const artist = ref('')
  const lyrics = ref<string | null>(null)
  const lyricsStatus = ref<LyricsStatus>('pending')

  // ── Local audio (kept as blob URL until page reload) ─────────────────
  const audioFile = ref<File | null>(null)
  const audioUrl = ref<string | null>(null)

  // ── Playback ─────────────────────────────────────────────────────────
  const currentTime = ref(0)   // raw playhead from HTMLAudioElement
  const displayTime = ref(0)   // rAF-smoothed playhead for UI
  const isPlaying = ref(false)

  // ── Transpose + vocal range ──────────────────────────────────────────
  const transpose = ref(0)
  const vocalRange = ref<DetectedRange | null>(null)

  // ── Live pitch + grading (from WS) ───────────────────────────────────
  const liveHz = ref(0)
  const liveMidi = ref(0)
  const liveNote = ref('')
  const liveVoiced = ref(false)
  const liveDisplayMidi = ref(0)   // fractional MIDI for smooth cursor
  const liveDisplayVoiced = ref(false)

  const expectedMidi = ref(0)
  const expectedNote = ref('')
  const centsOff = ref(0)
  const isCorrect = ref(false)
  const isExact = ref(false)

  const score = ref(0)
  const accuracy = ref(0)
  const notesHit = ref(0)
  const notesJudged = ref(0)
  const notesMissed = ref(0)
  const notesExact = ref(0)
  const totalNotes = ref(0)
  const combo = ref(0)
  const maxCombo = ref(0)
  const points = ref(0)
  const multiplier = ref(1)

  // ── Song lifecycle ───────────────────────────────────────────────────
  const songFinished = ref(false)

  // ── Derived: active note at the smoothed playhead ────────────────────
  const activeNote = computed<{ event: NoteEvent; progress: number } | null>(() => {
    const t = displayTime.value
    const notes = noteEvents.value
    for (let i = 0; i < notes.length; i++) {
      const n = notes[i]!
      if (t >= n.start && t <= n.end) {
        const p = (t - n.start) / Math.max(0.0001, n.end - n.start)
        return { event: n, progress: Math.min(1, Math.max(0, p)) }
      }
      if (n.start > t) break
    }
    return null
  })

  // ── Actions ──────────────────────────────────────────────────────────
  function setJob(id: string, meta: { title: string; artist: string }) {
    jobId.value = id
    jobStatus.value = 'queued'
    jobProgress.value = 'Queued'
    jobError.value = null
    title.value = meta.title
    artist.value = meta.artist
  }

  function updateJob(payload: {
    status: JobStatus
    progress?: string
    result?: AnalysisResult
    error?: string
    title?: string
    artist?: string
    lyrics?: string | null
    lyrics_status?: LyricsStatus
  }) {
    jobStatus.value = payload.status
    if (payload.progress !== undefined) jobProgress.value = payload.progress
    if (payload.result) analysis.value = payload.result
    if (payload.error) jobError.value = payload.error
    if (payload.title) title.value = payload.title
    if (payload.artist) artist.value = payload.artist
    if (payload.lyrics !== undefined) lyrics.value = payload.lyrics
    if (payload.lyrics_status) lyricsStatus.value = payload.lyrics_status
  }

  function setAudioFile(file: File) {
    audioFile.value = file
    if (audioUrl.value) URL.revokeObjectURL(audioUrl.value)
    audioUrl.value = URL.createObjectURL(file)
  }

  function setTranspose(semitones: number) {
    const snapped = Math.round(semitones / 12) * 12
    transpose.value = Math.max(-24, Math.min(24, snapped))
  }

  function setVocalRange(r: DetectedRange) {
    vocalRange.value = r
  }

  function applyPitchMsg(msg: {
    hz: number
    midi: number
    note: string
    voiced: boolean
    display_hz?: number
    display_midi?: number
    display_note?: string
    display_voiced?: boolean
  }) {
    liveHz.value = msg.hz
    liveMidi.value = msg.midi
    liveNote.value = msg.note
    liveVoiced.value = msg.voiced
    liveDisplayMidi.value = msg.display_midi ?? msg.midi
    liveDisplayVoiced.value = msg.display_voiced ?? msg.voiced
  }

  function applyGradeMsg(msg: {
    expected_midi: number
    expected_note: string
    correct: boolean
    exact: boolean
    cents_off: number
    active: boolean
    score: number
    accuracy?: number
    points: number
    notes_hit?: number
    notes_judged?: number
    notes_missed?: number
    notes_exact?: number
    total_notes?: number
    combo: number
    max_combo: number
    multiplier: number
  }) {
    expectedMidi.value = msg.expected_midi
    expectedNote.value = msg.expected_note
    centsOff.value = msg.cents_off
    isCorrect.value = msg.correct
    isExact.value = msg.exact
    score.value = msg.accuracy ?? msg.score
    accuracy.value = msg.accuracy ?? msg.score
    points.value = msg.points
    notesHit.value = msg.notes_hit ?? notesHit.value
    notesJudged.value = msg.notes_judged ?? notesJudged.value
    notesMissed.value = msg.notes_missed ?? notesMissed.value
    notesExact.value = msg.notes_exact ?? notesExact.value
    totalNotes.value = msg.total_notes ?? totalNotes.value
    combo.value = msg.combo
    maxCombo.value = msg.max_combo
    multiplier.value = msg.multiplier
  }

  function resetLive() {
    liveHz.value = 0
    liveMidi.value = 0
    liveNote.value = ''
    liveVoiced.value = false
    liveDisplayMidi.value = 0
    liveDisplayVoiced.value = false
    expectedMidi.value = 0
    expectedNote.value = ''
    centsOff.value = 0
    isCorrect.value = false
    isExact.value = false
    score.value = 0
    accuracy.value = 0
    notesHit.value = 0
    notesJudged.value = 0
    notesMissed.value = 0
    notesExact.value = 0
    totalNotes.value = noteEvents.value.length
    combo.value = 0
    maxCombo.value = 0
    points.value = 0
    multiplier.value = 1
    songFinished.value = false
  }

  function resetForNewSession() {
    jobId.value = null
    jobStatus.value = null
    jobProgress.value = ''
    jobError.value = null
    analysis.value = null
    title.value = ''
    artist.value = ''
    lyrics.value = null
    lyricsStatus.value = 'pending'
    audioFile.value = null
    if (audioUrl.value) {
      URL.revokeObjectURL(audioUrl.value)
      audioUrl.value = null
    }
    currentTime.value = 0
    displayTime.value = 0
    isPlaying.value = false
    transpose.value = 0
    vocalRange.value = null
    resetLive()
  }

  return {
    jobId, jobStatus, jobProgress, jobError,
    analysis, noteEvents, duration, device, vocalsUrl,
    title, artist, lyrics, lyricsStatus,
    audioFile, audioUrl,
    currentTime, displayTime, isPlaying,
    transpose, vocalRange,
    liveHz, liveMidi, liveNote, liveVoiced, liveDisplayMidi, liveDisplayVoiced,
    expectedMidi, expectedNote, centsOff, isCorrect, isExact,
    score, accuracy, notesHit, notesJudged, notesMissed, notesExact, totalNotes,
    combo, maxCombo, points, multiplier,
    songFinished, activeNote,
    setJob, updateJob, setAudioFile, setTranspose, setVocalRange,
    applyPitchMsg, applyGradeMsg, resetLive, resetForNewSession,
  }
})
