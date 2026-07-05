const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

export function hzToMidiFloat(hz: number): number {
  if (hz <= 0) return 0
  return 69 + 12 * Math.log2(hz / 440)
}

export function midiToName(midi: number): string {
  if (midi <= 0) return ''
  return `${NOTE_NAMES[midi % 12]}${Math.floor(midi / 12) - 1}`
}

export function shiftedNote(midi: number, semitones: number): string {
  const shifted = Math.max(0, Math.min(127, midi + semitones))
  return midiToName(shifted)
}

export function formatTime(sec: number): string {
  if (!isFinite(sec) || sec < 0) return '0:00'
  const s = Math.floor(sec)
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
}

export function formatBytes(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
