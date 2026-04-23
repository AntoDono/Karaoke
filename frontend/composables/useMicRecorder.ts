/**
 * Microphone pitch detection — zero dependencies.
 *
 * Uses a normalised autocorrelation (parabolic-interpolated) directly on the
 * Web Audio AnalyserNode buffer. No external library needed.
 *
 * Flicker suppression:
 *   1. RMS silence gate — rejects breath/room noise before detection runs.
 *   2. Rolling mode buffer — the most common MIDI note over the last N frames
 *      is the candidate, not the raw per-frame result.
 *   3. Commit hysteresis — the candidate must hold its majority position across
 *      COMMIT_MAJORITY frames before the display switches.
 */

import { detectPitch, hzToMidi, midiToName } from '~/composables/pitchDetector'

const RMS_GATE        = 0.012  // below this → treat as silence
const BUFFER_SIZE     = 8      // rolling window (frames) for mode smoothing
const COMMIT_MAJORITY = 5      // frames the winner must hold before committing
const MIN_HZ          = 60
const MAX_HZ          = 1200

export function useMicRecorder() {
  const store = useKaraokeStore()

  const error    = ref<string | null>(null)
  const isReady  = ref(false)
  const rawHz    = ref(0)    // latest raw detected Hz (pre-smoothing), for debug
  const rmsLevel = ref(0)    // current RMS (0–1), for debug meter

  let audioCtx: AudioContext                     | null = null
  let stream:   MediaStream                      | null = null
  let analyser: AnalyserNode                     | null = null
  let source:   MediaStreamAudioSourceNode       | null = null
  let buffer:   Float32Array                     | null = null
  let raf:      number                           | null = null

  async function start() {
    error.value = null
    try {
      stream   = await navigator.mediaDevices.getUserMedia({ audio: true, video: false })
      audioCtx = new AudioContext()

      if (audioCtx.state === 'suspended') await audioCtx.resume()

      source   = audioCtx.createMediaStreamSource(stream)
      analyser = audioCtx.createAnalyser()
      analyser.fftSize = 4096
      buffer   = new Float32Array(analyser.fftSize)

      // No destination connection → no speaker feedback
      source.connect(analyser)

      const midiHistory: number[] = []
      let committedMidi = 0

      const loop = () => {
        if (!analyser || !buffer) return

        analyser.getFloatTimeDomainData(buffer as Float32Array<ArrayBuffer>)

        // RMS silence gate
        let rms = 0
        for (let i = 0; i < buffer.length; i++) rms += (buffer[i] ?? 0) ** 2
        rms = Math.sqrt(rms / buffer.length)

        rmsLevel.value = Math.min(1, rms / 0.1)

        if (rms > RMS_GATE) {
          const hz = detectPitch(buffer, audioCtx!.sampleRate)
          rawHz.value = hz ?? 0

          if (hz && hz >= MIN_HZ && hz <= MAX_HZ) {
            const rawMidi = hzToMidi(hz)

            // Rolling mode buffer
            midiHistory.push(rawMidi)
            if (midiHistory.length > BUFFER_SIZE) midiHistory.shift()

            const counts = new Map<number, number>()
            for (const m of midiHistory) counts.set(m, (counts.get(m) ?? 0) + 1)

            let bestMidi = rawMidi, bestCount = 0
            for (const [m, c] of counts) {
              if (c > bestCount) { bestCount = c; bestMidi = m }
            }

            if (bestCount >= COMMIT_MAJORITY && bestMidi !== committedMidi) {
              committedMidi = bestMidi
              store.setLivePitch(hz, bestMidi, midiToName(bestMidi))
            }

            // Score against committed (stable) MIDI
            const active = store.activeNote
            if (store.isPlaying && active && committedMidi !== 0) {
              const expectedMidi = active.event.midi + store.transpose
              const diff = Math.abs(expectedMidi - committedMidi)
              store.recordPitchSample(diff <= 1, diff === 0)
            }
          } else {
            rawHz.value = 0
            midiHistory.length = 0
            committedMidi = 0
            store.setLivePitch(0, 0, '')
          }
        } else {
          rawHz.value = 0
          midiHistory.length = 0
          committedMidi = 0
          store.setLivePitch(0, 0, '')
        }

        raf = requestAnimationFrame(loop)
      }
      raf = requestAnimationFrame(loop)

      store.setMicActive(true)
      isReady.value = true
    } catch (e: any) {
      error.value = e?.message ?? 'Microphone access denied'
      store.setMicActive(false)
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
    store.setMicActive(false)
    store.setLivePitch(0, 0, '')
    rawHz.value    = 0
    rmsLevel.value = 0
    isReady.value  = false
  }

  function toggle() {
    if (store.isMicActive) stop()
    else start()
  }

  onUnmounted(stop)

  return { start, stop, toggle, isReady, error, rawHz, rmsLevel }
}
