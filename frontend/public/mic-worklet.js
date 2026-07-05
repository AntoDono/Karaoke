/**
 * AudioWorklet that captures mono float32 samples, downsamples to 16 kHz,
 * converts to int16, and posts chunks of ~25 ms back to the main thread.
 */

const OUT_SR = 16000;
const CHUNK_SAMPLES = 400; // 25 ms at 16 kHz

class MicProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this._inRate = sampleRate;
    this._ratio = this._inRate / OUT_SR;
    this._acc = 0;
    this._buf = [];
    this._out = new Int16Array(CHUNK_SAMPLES);
    this._outIdx = 0;
    this._rmsSum = 0;
    this._rmsCount = 0;
  }

  process(inputs) {
    const input = inputs[0];
    if (!input || !input[0]) return true;
    const ch = input[0];

    for (let i = 0; i < ch.length; i++) {
      this._rmsSum += ch[i] * ch[i];
      this._rmsCount++;
    }

    // Simple linear-interpolation downsample from native SR → 16 kHz.
    // Sufficient because we don't need pristine audio, just F0-accurate.
    let pos = this._acc;
    while (pos < ch.length) {
      const lo = Math.floor(pos);
      const hi = Math.min(lo + 1, ch.length - 1);
      const frac = pos - lo;
      const sample = ch[lo] * (1 - frac) + ch[hi] * frac;
      const clamped = Math.max(-1, Math.min(1, sample));
      this._out[this._outIdx++] = clamped < 0 ? clamped * 0x8000 : clamped * 0x7FFF;

      if (this._outIdx >= CHUNK_SAMPLES) {
        const rms = Math.sqrt(this._rmsSum / Math.max(1, this._rmsCount));
        this.port.postMessage({ pcm: this._out.buffer.slice(0), rms }, [this._out.buffer]);
        this._out = new Int16Array(CHUNK_SAMPLES);
        this._outIdx = 0;
        this._rmsSum = 0;
        this._rmsCount = 0;
      }

      pos += this._ratio;
    }
    this._acc = pos - ch.length;
    return true;
  }
}

registerProcessor('mic-processor', MicProcessor);
