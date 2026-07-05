/**
 * Microphone → 16 kHz int16 PCM chunk stream.
 *
 * The heavy lifting (downsample + int16 packing) happens in an AudioWorklet
 * so the main thread stays free for UI rendering.
 */

interface MicOptions {
  onChunk: (pcm: ArrayBuffer, rms: number) => void
}

export function useMicStream({ onChunk }: MicOptions) {
  const isRunning = ref(false)
  const level = ref(0)          // 0–1 for a VU-meter style display
  const error = ref<string | null>(null)

  let ctx: AudioContext | null = null
  let stream: MediaStream | null = null
  let source: MediaStreamAudioSourceNode | null = null
  let node: AudioWorkletNode | null = null
  let smoothTimer: ReturnType<typeof setInterval> | null = null

  async function start() {
    if (isRunning.value) return
    error.value = null
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: false,
          noiseSuppression: true,
          autoGainControl: true,
        },
      })
      ctx = new AudioContext()
      if (ctx.state === 'suspended') await ctx.resume()

      await ctx.audioWorklet.addModule('/mic-worklet.js')
      source = ctx.createMediaStreamSource(stream)
      node = new AudioWorkletNode(ctx, 'mic-processor', { numberOfInputs: 1, numberOfOutputs: 0 })

      let latestRms = 0
      node.port.onmessage = (ev) => {
        const { pcm, rms } = ev.data as { pcm: ArrayBuffer; rms: number }
        latestRms = rms
        onChunk(pcm, rms)
      }

      source.connect(node)

      smoothTimer = setInterval(() => {
        // Soft attack/decay for the VU meter
        const target = Math.min(1, latestRms * 6)
        level.value = level.value + (target - level.value) * 0.3
      }, 50)

      isRunning.value = true
    } catch (e: any) {
      error.value = e?.message ?? 'Microphone access denied'
      await stop()
      throw e
    }
  }

  async function stop() {
    if (smoothTimer) { clearInterval(smoothTimer); smoothTimer = null }
    try { node?.disconnect() } catch {}
    try { source?.disconnect() } catch {}
    stream?.getTracks().forEach(t => t.stop())
    if (ctx && ctx.state !== 'closed') await ctx.close()

    node = null
    source = null
    stream = null
    ctx = null
    isRunning.value = false
    level.value = 0
  }

  onUnmounted(() => { void stop() })

  return { start, stop, isRunning, level, error }
}
