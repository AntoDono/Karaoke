/**
 * Captures the microphone, runs real-time pitch detection via pitchfinder,
 * and pushes results to the Karaoke store.
 *
 * Uses an AnalyserNode + requestAnimationFrame loop (not deprecated
 * ScriptProcessorNode) so it works reliably in all modern browsers
 * and produces no audio feedback.
 */

const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
const A4_MIDI = 69
const A4_HZ   = 440

function hzToMidi(hz: number): number {
  return Math.round(A4_MIDI + 12 * Math.log2(hz / A4_HZ))
}

function midiToName(midi: number): string {
  const octave = Math.floor(midi / 12) - 1
  return `${NOTE_NAMES[midi % 12]}${octave}`
}

export function useMicRecorder() {
  const store = useKaraokeStore()

  const error   = ref<string | null>(null)
  const isReady = ref(false)

  let audioCtx:    AudioContext     | null = null
  let stream:      MediaStream      | null = null
  let analyser:    AnalyserNode     | null = null
  let source:      MediaStreamAudioSourceNode | null = null
  let buffer:      Float32Array     | null = null
  let raf:         number           | null = null
  let detectPitch: ((buf: Float32Array) => number | null) | null = null

  async function start() {
    error.value = null
    try {
      // Lazy-import pitchfinder (SSR-safe)
      const { default: Pitchfinder } = await import('pitchfinder')

      stream   = await navigator.mediaDevices.getUserMedia({ audio: true, video: false })
      audioCtx = new AudioContext()

      // Chrome/Safari create the context in "suspended" state — explicitly resume
      if (audioCtx.state === 'suspended') await audioCtx.resume()

      detectPitch = Pitchfinder.YIN({ sampleRate: audioCtx.sampleRate })

      source   = audioCtx.createMediaStreamSource(stream)
      analyser = audioCtx.createAnalyser()
      analyser.fftSize = 2048
      buffer   = new Float32Array(analyser.fftSize)

      // NOTE: we don't connect analyser to destination — that would cause
      // feedback through the speakers. AnalyserNode still processes input.
      source.connect(analyser)

      // Throttle debug logs — print every 30 frames (~½ sec)
      let debugCounter = 0

      const loop = () => {
        if (!analyser || !buffer || !detectPitch) return

        analyser.getFloatTimeDomainData(buffer)

        let rms = 0
        for (let i = 0; i < buffer.length; i++) rms += buffer[i] * buffer[i]
        rms = Math.sqrt(rms / buffer.length)

        // Very low silence gate (0.002) — your voice should easily exceed this
        if (rms > 0.002) {
          const pitch = detectPitch(buffer)

          if (debugCounter++ % 30 === 0) {
            console.log('[mic] rms=%s pitch=%s', rms.toFixed(4), pitch)
          }

          if (pitch && pitch > 50 && pitch < 2000) {
            const midi = hzToMidi(pitch)
            const name = midiToName(midi)
            store.setLivePitch(pitch, midi, name)

            const active = store.activeNote
            if (store.isPlaying && active) {
              store.recordPitchSample(active.event.midi === midi)
            }
          } else {
            store.setLivePitch(0, 0, '')
          }
        } else {
          if (debugCounter++ % 30 === 0) {
            console.log('[mic] silent rms=%s', rms.toFixed(4))
          }
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
    detectPitch = null

    store.setMicActive(false)
    store.setLivePitch(0, 0, '')
    isReady.value = false
  }

  function toggle() {
    if (store.isMicActive) stop()
    else start()
  }

  onUnmounted(stop)

  return { start, stop, toggle, isReady, error }
}
