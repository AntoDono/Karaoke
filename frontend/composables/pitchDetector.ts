/**
 * Zero-dependency pitch detector using normalised autocorrelation.
 *
 * Algorithm: compute the Normalised Square Difference Function (NSDF) —
 * equivalent to normalised autocorrelation — over the range of lags that
 * correspond to the vocal / instrument frequency range. The lag with the
 * highest NSDF value above a confidence threshold is refined with parabolic
 * interpolation to give sub-sample period accuracy.
 *
 * Complexity: O(maxLag × n) ≈ 730 × 1300 ≈ 950 K ops/frame @ 44 100 Hz.
 * This runs well within a 16 ms rAF budget in any modern browser.
 *
 * Tunable constants
 * ─────────────────
 * MIN_HZ / MAX_HZ   — ignore pitches outside this range (vocal bounds)
 * CONFIDENCE_THRESH — minimum NSDF peak required to report a pitch.
 *                     Lower = more detections but noisier; raise if you get
 *                     lots of spurious notes in silence.
 */

const MIN_HZ          = 60    // ~B1
const MAX_HZ          = 1200  // ~D6
const CONFIDENCE_THRESH = 0.35 // 0–1; raise to filter weak / ambiguous pitches

const NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
const A4_MIDI    = 69
const A4_HZ      = 440

export function hzToMidi(hz: number): number {
  return Math.round(A4_MIDI + 12 * Math.log2(hz / A4_HZ))
}

export function midiToName(midi: number): string {
  return `${NOTE_NAMES[midi % 12]}${Math.floor(midi / 12) - 1}`
}

/**
 * Detects the fundamental frequency of the audio in `buf`.
 * Returns Hz, or null when the signal is inaudible or aperiodic.
 */
export function detectPitch(buf: Float32Array, sampleRate: number): number | null {
  const n      = buf.length
  const minLag = Math.ceil(sampleRate / MAX_HZ)
  const maxLag = Math.floor(sampleRate / MIN_HZ)

  if (maxLag >= n) return null

  // Total signal energy (denominator reference for NSDF)
  let energy0 = 0
  for (let i = 0; i < n; i++) energy0 += (buf[i] ?? 0) ** 2
  if (energy0 < 1e-6) return null  // silence

  // Sliding energy of the lagged window starts at lag = 0
  let energyLag = 0
  for (let i = 0; i < maxLag; i++) energyLag += (buf[i] ?? 0) ** 2

  let bestLag  = -1
  let bestNsdf = CONFIDENCE_THRESH

  for (let lag = minLag; lag <= maxLag; lag++) {
    // Roll the sliding lagged-window energy forward by one sample
    energyLag -= (buf[lag - 1] ?? 0) ** 2

    // Unnormalised autocorrelation at this lag
    let corr = 0
    const limit = n - lag
    for (let i = 0; i < limit; i++) corr += (buf[i] ?? 0) * (buf[i + lag] ?? 0)

    const denom = energy0 + energyLag
    const nsdf  = denom > 0 ? (2 * corr) / denom : 0

    if (nsdf > bestNsdf) {
      bestNsdf = nsdf
      bestLag  = lag
    }
  }

  if (bestLag === -1) return null

  // Parabolic interpolation — refines the period to sub-sample accuracy
  // using the three NSDF values around the peak lag.
  // We re-compute correlation at bestLag-1 and bestLag+1 for this.
  const lagM1 = bestLag - 1
  const lagP1 = bestLag + 1

  let corrM1 = 0, corrBest = 0, corrP1 = 0
  const limitBest = n - bestLag
  for (let i = 0; i < limitBest; i++) {
    const s = buf[i] ?? 0
    if (lagM1 >= 0)   corrM1   += s * (buf[i + lagM1] ?? 0)
                      corrBest += s * (buf[i + bestLag] ?? 0)
    if (lagP1 <= maxLag) corrP1 += s * (buf[i + lagP1] ?? 0)
  }

  const a = (corrM1 + corrP1 - 2 * corrBest) / 2
  const b = (corrP1 - corrM1) / 2
  const refinedLag = a !== 0 ? bestLag - b / (2 * a) : bestLag

  return sampleRate / refinedLag
}
