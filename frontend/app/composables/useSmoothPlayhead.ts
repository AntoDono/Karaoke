/**
 * High-resolution playhead using performance.now() anchors.
 *
 * HTMLAudioElement.currentTime only updates ~4×/s via `timeupdate`, which
 * makes note blocks jump. We extrapolate smoothly between those corrections
 * using a perf-time anchor so motion is linear at 60 fps.
 */

export function useSmoothPlayhead(audio: Ref<HTMLAudioElement | null>) {
  const store = useSessionStore()

  let raf: number | null = null
  let playing = false
  let rate = 1

  // Anchor: displayTime = anchorMedia + (now - anchorPerf) / 1000 * rate
  let anchorMedia = 0
  let anchorPerf = 0

  function syncAnchors(mediaTime: number) {
    anchorMedia = mediaTime
    anchorPerf = performance.now()
    store.displayTime = mediaTime
    store.currentTime = mediaTime
  }

  function onTimeUpdate() {
    if (!audio.value || !playing) return
    const actual = audio.value.currentTime
    store.currentTime = actual
    // Only re-anchor when drift exceeds ~30 ms — avoids micro-stutters
    const predicted = anchorMedia + ((performance.now() - anchorPerf) / 1000) * rate
    if (Math.abs(actual - predicted) > 0.03) {
      anchorMedia = actual
      anchorPerf = performance.now()
    }
  }

  function onPlay() {
    if (!audio.value) return
    playing = true
    store.isPlaying = true
    syncAnchors(audio.value.currentTime)
    rate = audio.value.playbackRate
  }

  function onPause() {
    playing = false
    store.isPlaying = false
    if (audio.value) syncAnchors(audio.value.currentTime)
  }

  function onSeeked() {
    if (!audio.value) return
    syncAnchors(audio.value.currentTime)
  }

  function onRateChange() {
    if (!audio.value) return
    // Re-anchor at current predicted position with new rate
    const now = performance.now()
    const predicted = anchorMedia + ((now - anchorPerf) / 1000) * rate
    rate = audio.value.playbackRate
    anchorMedia = predicted
    anchorPerf = now
  }

  function onEnded() {
    playing = false
    store.isPlaying = false
    store.songFinished = true
  }

  function tick() {
    if (playing && audio.value) {
      const extrapolated = anchorMedia + ((performance.now() - anchorPerf) / 1000) * rate
      // Nudge toward element time so scroll never runs ahead of audio
      const actual = audio.value.currentTime
      store.displayTime = extrapolated + (actual - extrapolated) * 0.25
      store.currentTime = actual
    }
    raf = requestAnimationFrame(tick)
  }

  function attach(el: HTMLAudioElement) {
    el.addEventListener('timeupdate', onTimeUpdate)
    el.addEventListener('play', onPlay)
    el.addEventListener('pause', onPause)
    el.addEventListener('seeked', onSeeked)
    el.addEventListener('ratechange', onRateChange)
    el.addEventListener('ended', onEnded)
    rate = el.playbackRate
    syncAnchors(el.currentTime)
    if (!raf) raf = requestAnimationFrame(tick)
  }

  function detach() {
    const el = audio.value
    if (!el) return
    el.removeEventListener('timeupdate', onTimeUpdate)
    el.removeEventListener('play', onPlay)
    el.removeEventListener('pause', onPause)
    el.removeEventListener('seeked', onSeeked)
    el.removeEventListener('ratechange', onRateChange)
    el.removeEventListener('ended', onEnded)
  }

  watch(audio, (el, oldEl) => {
    if (oldEl) detach()
    if (el) attach(el)
  })

  onUnmounted(() => {
    detach()
    if (raf) cancelAnimationFrame(raf)
    raf = null
  })

  return {}
}
