/**
 * Microphone vocal range detector — zero dependencies.
 *
 * Tracks the lowest and highest stable MIDI notes the user sings over a
 * session. Uses the same normalised-autocorrelation detector and rolling-mode
 * smoothing as useMicRecorder, but does NOT write to the Karaoke store.
 */

import { detectPitch, hzToMidi, midiToName } from '~/composables/pitchDetector'

// Reasonable human vocal range guard (E2 → C6)
const VOCAL_MIDI_MIN = 40
const VOCAL_MIDI_MAX = 84

const RMS_GATE        = 0.012
const BUFFER_SIZE     = 8
const COMMIT_MAJORITY = 5

export interface DetectedRange {
  minMidi: number
  maxMidi: number
  minNote: string
  maxNote: string
}

export function useVocalRangeDetector() {
  const isRecording   = ref(false)
  const error         = ref<string | null>(null)
  const detectedRange = ref<DetectedRange | null>(null)
  const liveMidi      = ref(0)
  const liveNote      = ref('')

  let audioCtx: AudioContext               | null = null
  let stream:   MediaStream                | null = null
  let analyser: AnalyserNode               | null = null
  let source:   MediaStreamAudioSourceNode | null = null
  let buffer:   Float32Array               | null = null
  let raf:      number                     | null = null

  let sessionMinMidi = Infinity
  let sessionMaxMidi = -Infinity

  function updateRange(midi: number) {
    let changed = false
    if (midi < sessionMinMidi) { sessionMinMidi = midi; changed = true }
    if (midi > sessionMaxMidi) { sessionMaxMidi = midi; changed = true }
    if (changed && sessionMinMidi !== Infinity) {
      detectedRange.value = {
        minMidi: sessionMinMidi,
        maxMidi: sessionMaxMidi,
        minNote: midiToName(sessionMinMidi),
        maxNote: midiToName(sessionMaxMidi),
      }
    }
  }

  async function start() {
    error.value       = null
    sessionMinMidi    = Infinity
    sessionMaxMidi    = -Infinity
    detectedRange.value = null
    liveMidi.value    = 0
    liveNote.value    = ''

    try {
      stream   = await navigator.mediaDevices.getUserMedia({ audio: true, video: false })
      audioCtx = new AudioContext()
      if (audioCtx.state === 'suspended') await audioCtx.resume()

      source   = audioCtx.createMediaStreamSource(stream)
      analyser = audioCtx.createAnalyser()
      analyser.fftSize = 2048
      buffer   = new Float32Array(analyser.fftSize)
      source.connect(analyser)

      isRecording.value = true

      const midiHistory: number[] = []
      let committedMidi = 0

      const loop = () => {
        if (!analyser || !buffer) return

        analyser.getFloatTimeDomainData(buffer as Float32Array<ArrayBuffer>)

        let rms = 0
        for (let i = 0; i < buffer.length; i++) rms += (buffer[i] ?? 0) ** 2
        rms = Math.sqrt(rms / buffer.length)

        if (rms > RMS_GATE) {
          const hz = detectPitch(buffer, audioCtx!.sampleRate)

          if (hz) {
            const rawMidi = hzToMidi(hz)
            if (rawMidi >= VOCAL_MIDI_MIN && rawMidi <= VOCAL_MIDI_MAX) {
              midiHistory.push(rawMidi)
              if (midiHistory.length > BUFFER_SIZE) midiHistory.shift()

              const counts = new Map<number, number>()
              for (const m of midiHistory) counts.set(m, (counts.get(m) ?? 0) + 1)

              let bestMidi = rawMidi, bestCount = 0
              for (const [m, c] of counts) {
                if (c > bestCount) { bestCount = c; bestMidi = m }
              }

              if (bestCount >= COMMIT_MAJORITY && bestMidi !== committedMidi) {
                committedMidi    = bestMidi
                liveMidi.value   = bestMidi
                liveNote.value   = midiToName(bestMidi)
                updateRange(bestMidi)
              }
            }
          } else {
            midiHistory.length = 0
            committedMidi = 0
            liveMidi.value = 0
            liveNote.value = ''
          }
        } else {
          midiHistory.length = 0
          committedMidi = 0
          liveMidi.value = 0
          liveNote.value = ''
        }

        raf = requestAnimationFrame(loop)
      }
      raf = requestAnimationFrame(loop)
    } catch (e: any) {
      error.value = e?.message ?? 'Microphone access denied'
      isRecording.value = false
    }
  }

  function stop() {
    if (raf !== null) { cancelAnimationFrame(raf); raf = null }
    source?.disconnect()
    analyser?.disconnect()
    source = analyser = null
    buffer = null
    stream?.getTracks().forEach(t => t.stop())
    stream = null
    audioCtx?.close()
    audioCtx = null
    isRecording.value = false
    liveMidi.value = 0
    liveNote.value = ''
  }

  function reset() {
    stop()
    sessionMinMidi = Infinity
    sessionMaxMidi = -Infinity
    detectedRange.value = null
    error.value = null
  }

  onUnmounted(stop)

  return { start, stop, reset, isRecording, error, detectedRange, liveMidi, liveNote }
}
