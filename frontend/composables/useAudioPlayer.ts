/**
 * Wraps an HTMLAudioElement and syncs playback state to the Karaoke store.
 * Pass the reactive audioUrl from the store; the composable will reload
 * the element whenever the URL changes.
 */
export function useAudioPlayer() {
  const store = useKaraokeStore()

  const audioRef = ref<HTMLAudioElement | null>(null)
  const isReady = ref(false)
  const isSeeking = ref(false)

  // RAF loop — syncs store.currentTime at 60fps while audio is playing
  let raf: number | null = null

  function startTimeSync(el: HTMLAudioElement) {
    if (raf !== null) return
    const loop = () => {
      if (!isSeeking.value) store.setCurrentTime(el.currentTime)
      raf = requestAnimationFrame(loop)
    }
    raf = requestAnimationFrame(loop)
  }

  function stopTimeSync() {
    if (raf !== null) { cancelAnimationFrame(raf); raf = null }
  }

  function attach(el: HTMLAudioElement) {
    audioRef.value = el

    el.addEventListener('play',  () => { store.setPlaying(true);  startTimeSync(el) })
    el.addEventListener('pause', () => { store.setPlaying(false); stopTimeSync() })
    el.addEventListener('ended', () => {
      store.setPlaying(false)
      stopTimeSync()
      store.setCurrentTime(0)
      store.setSongFinished(true)
    })
    el.addEventListener('canplaythrough', () => { isReady.value = true })
    el.addEventListener('loadstart',      () => { isReady.value = false })
  }

  function play() {
    audioRef.value?.play()
  }

  function pause() {
    audioRef.value?.pause()
  }

  function toggle() {
    if (store.isPlaying) pause()
    else play()
  }

  function seek(seconds: number) {
    const el = audioRef.value
    if (!el) return
    isSeeking.value = true
    el.currentTime = Math.max(0, Math.min(seconds, el.duration || 0))
    store.setCurrentTime(el.currentTime)
    isSeeking.value = false
  }

  function seekByFraction(fraction: number) {
    const el = audioRef.value
    if (!el) return
    seek((el.duration || 0) * Math.max(0, Math.min(1, fraction)))
  }

  /** Load a new src URL into the element */
  function load(url: string) {
    const el = audioRef.value
    if (!el) return
    el.src = url
    el.load()
    isReady.value = false
  }

  // Load original uploaded audio when available
  watch(() => store.audioUrl, (url) => {
    if (url) load(url)
  })

  onUnmounted(stopTimeSync)

  return { audioRef, attach, play, pause, toggle, seek, seekByFraction, isReady }
}
