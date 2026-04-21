export type JobStatus =
  | 'queued'
  | 'separating'
  | 'tracking'
  | 'quantizing'
  | 'segmenting'
  | 'complete'
  | 'failed'

export interface NoteEvent {
  note: string       // e.g. "C4", "F#3"
  midi: number       // MIDI note number
  start: number      // onset in seconds
  end: number        // offset in seconds
  confidence: number // 0–1
}

export interface AnalysisResult {
  duration: number
  sample_rate: number
  notes: NoteEvent[]
  device: string          // "cuda" | "mps" | "cpu"
  vocals_url?: string     // e.g. /api/jobs/{id}/vocals
}

export interface JobResponse {
  job_id: string
  status: JobStatus
  progress?: string
  result?: AnalysisResult
  error?: string
}

export interface AnalyzeResponse {
  job_id: string
  message: string
}

/** Active note at the current playhead position */
export interface ActiveNote {
  event: NoteEvent
  /** Progress through the note: 0 = start, 1 = end */
  progress: number
}
