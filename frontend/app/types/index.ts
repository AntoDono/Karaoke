export type JobStatus =
  | 'queued'
  | 'separating'
  | 'tracking'
  | 'quantizing'
  | 'segmenting'
  | 'complete'
  | 'failed'

export type LyricsStatus = 'pending' | 'found' | 'not_found' | 'error'

export interface NoteEvent {
  note: string
  midi: number
  start: number
  end: number
  confidence: number
}

export interface AnalysisResult {
  duration: number
  sample_rate: number
  notes: NoteEvent[]
  device: string
  vocals_url?: string
}

export interface JobResponse {
  job_id: string
  status: JobStatus
  progress?: string
  result?: AnalysisResult
  error?: string
  title?: string
  artist?: string
  lyrics?: string
  lyrics_status: LyricsStatus
}

export interface AnalyzeResponse {
  job_id: string
  message: string
}

export interface DetectedRange {
  minMidi: number
  maxMidi: number
  minNote: string
  maxNote: string
}

/* ── WebSocket messages ─────────────────────────────────────────────── */

export type WsIn =
  | { type: 'ready';  session_id: string }
  | { type: 'pitch';
      hz: number;
      midi: number;
      note: string;
      voiced: boolean;
      display_hz?: number;
      display_midi?: number;
      display_note?: string;
      display_voiced?: boolean;
    }
  | { type: 'grade';
      expected_midi: number;
      expected_note: string;
      correct: boolean;
      exact: boolean;
      cents_off: number;
      active: boolean;
      score: number;
      accuracy?: number;
      points: number;
      notes_hit?: number;
      notes_judged?: number;
      notes_missed?: number;
      notes_exact?: number;
      total_notes?: number;
      combo: number;
      max_combo: number;
      multiplier: number;
    }
  | { type: 'range'; min_midi: number; max_midi: number; min_note: string; max_note: string }
  | { type: 'pong' }
  | { type: 'error'; message: string }

export type WsOut =
  | { type: 'init'; job_id?: string; transpose?: number; mode?: 'grade' | 'range' }
  | { type: 'sync'; current_time: number }
  | { type: 'transpose'; semitones: number }
  | { type: 'reset_score' }
  | { type: 'reset_range' }
  | { type: 'ping' }
